from datetime import datetime
import json
import os
import traceback
import uuid
import numpy as np
import pandas as pd
import pymysql
import pika
import time
import onnxruntime as ort
import onnx
import torch
import joblib

# RabbitMQ
RABBIT_HOST = os.getenv("RABBIT_HOST")
RABBIT_USER = os.getenv("RABBIT_USER")
RABBIT_PASS = os.getenv("RABBIT_PASS")
# MariaDB
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
# CSV, Model
MODEL_STORAGE_DIR = "./resources/models"
CSV_STORAGE_DIR = "./resources/csvs"
RESULT_STORAGE_DIR = "./resources/results"

def get_conn():
    # get mariadb connection
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

def log(msg):
    print(datetime.now(), msg)

def process_task(task_id):
    conn = None
    task_id = task_id.decode("utf-8")
    try:
        conn = get_conn()
        with conn.cursor() as cursor:
            cursor.execute("""SELECT * FROM tasks WHERE task_id = %s""", (task_id,))
            task = cursor.fetchone()
            cursor.execute("""SELECT * FROM models WHERE model_id = %s""", (task["model_id"],))
            model = cursor.fetchone()

        model_type = task["model_type"]
        model_filename = model["model_filename"]
        model_filepath = os.path.join(MODEL_STORAGE_DIR, model_filename)

        task_filename = task["task_filename"]
        task_filepath = os.path.join(CSV_STORAGE_DIR, task_filename)
        df = pd.read_csv(task_filepath, sep=",")

        if model_type == "PYTORCH":
            sess = ort.InferenceSession(model_filepath)

            # 重新排序列
            model_column = json.loads(model["model_column"])
            df_aligned = df[model_column]

            # 训练时候标准化的话现在也需要标准化
            pipeline_filename = model["pipeline_filename"]
            pipeline_filepath = os.path.join(MODEL_STORAGE_DIR, pipeline_filename)
            pipeline = joblib.load(pipeline_filepath)
            scaled = pipeline.transform(df_aligned).astype(np.float32)
            input_array = scaled.astype(np.float32)
            torch_input = {str(sess.get_inputs()[0].name): input_array}

            # 预测
            pred = sess.run(None, torch_input)[0]  # 输出是 ndarray

            # 对 logits 应用 sigmoid
            pred_prob = torch.sigmoid(torch.tensor(pred)).numpy()

            df["target"] = pred_prob.ravel()  # 展平成一维列
            result_filename = task_id
            result_loc = os.path.join(RESULT_STORAGE_DIR, result_filename)
            df.to_csv(result_loc)

            with conn.cursor() as cursor:
                cursor.execute(
                    """UPDATE tasks SET status = %s,
                                        end_date = %s,
                                        result_filename = %s
                        WHERE task_id = %s """,
                    ("DONE", datetime.now(), result_filename, task_id),
                )
                conn.commit()
        elif model_type == "SKLEARN":
            model = onnx.load(model_filepath)
            ort_session = ort.InferenceSession(model_filepath)
            feature_names = [input.name for input in model.graph.input]

            sklearn_input = {
                name: df[[name]].to_numpy().astype(np.float32) for name in feature_names
            }
            pred = ort_session.run(None, sklearn_input)
            df["target"] = [i[1] for i in pred[1]]

            result_filename = task_id
            result_loc = os.path.join(RESULT_STORAGE_DIR, result_filename)
            df.to_csv(result_loc)

            with conn.cursor() as cursor:
                cursor.execute(
                    """UPDATE tasks SET status = %s,
                                        end_date = %s,
                                        result_filename = %s
                        WHERE task_id = %s """,
                    ("DONE", datetime.now(), result_filename, task_id),)
                conn.commit()
        log(f" [x] Task saved to DB: {task_id}")
    except Exception as e:
        tb_str = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        log(f"Task {task_id} failed with error: {tb_str}")
        with conn.cursor() as cursor:
            cursor.execute(
                """UPDATE tasks SET status = %s,
                                    end_date = %s,
                                    error_message = %s
                    WHERE task_id = %s """,
                ("FAILED", datetime.now(), tb_str, task_id),
            )
            conn.commit()
        log(f" [!] Error with task: {task_id}")
    finally:
        if conn:
            conn.close()


def main():
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
    connection = None
    for i in range(10):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials)
            )
            print(" [*] Connected to RabbitMQ")
            break
        except Exception as e:
            print(f" [!] RabbitMQ not ready ({e}), retrying... ({i+1}/10)")
            time.sleep(3)

    if connection is None:
        raise RuntimeError("Could not connect to RabbitMQ")

    channel = connection.channel()
    channel.queue_declare(queue='tasks')

    def callback(ch, method, properties, body):
        print(f" [x] Received {body.decode()}")
        process_task(body)

    channel.basic_consume(queue='tasks', on_message_callback=callback, auto_ack=True)
    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == "__main__":
    main()
