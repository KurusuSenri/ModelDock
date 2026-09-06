from io import StringIO
import json
import traceback
import uuid
import os
import base64
import pandas as pd
from functools import wraps
from datetime import datetime, timedelta
from database import get_conn, close_conn
from flask_cors import CORS
from publisher import RabbitPublisher
from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["UPLOAD_FOLDER"] = "static/csv"
MODEL_STORAGE_DIR = "./resources/models"
CSV_STORAGE_DIR = "./resources/csvs"
RESULT_STORAGE_DIR = "./resources/results"

app.teardown_appcontext(close_conn)
CORS(app)

publisher = RabbitPublisher()


def get_user_by_token(token):
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("""SELECT * FROM users WHERE token = %s""", (token,))
        user = cursor.fetchone()
    if user and user["token_expiry"] > datetime.now():
        return user
    else:
        return None


def require_json_and_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get("Content-Type") != "application/json":
            return jsonify({"log_id": 400, "error": "Content-Type must be application/json"})

        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"log_id": 401, "error": "Authorization header is required"})

        user = get_user_by_token(token)
        if not user:
            return jsonify({"log_id": 401, "error": "Invalid token"})

        kwargs["user"] = user
        return f(*args, **kwargs)

    return decorated_function


if __name__ == "__main__":
    app.run(threaded=True)  # 启用多线程


@app.route("/api/login/", methods=["POST"])
def login():
    # 检查请求头
    if request.headers.get("Content-Type") != "application/json":
        return jsonify({"log_id": 400, "error": "Content-Type must be application/json"})

    payload = {"log_id": "",
               "error": "",
               "access_token": ""}

    # 解析请求参数
    try:
        data = request.get_json()
        user_id = data["user_id"]
        password = data["password"]

        # 验证用户名和密码
        conn = get_conn()
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT * FROM users WHERE user_id = %s""", (user_id,))
            user = cursor.fetchone()
        if user is None or password != user["password"]:
            payload["log_id"] = 403
            payload["error"] = f"Invalid credentials for user {user_id}"
            return jsonify(payload)

    except KeyError as e:
        payload["log_id"] = 400
        payload["error"] = f"Missing required field: {e} when logging in user {user_id}"
        return jsonify(payload)

    # Token 有效期设置为 30 分钟
    token = str(uuid.uuid4())
    with conn.cursor() as cursor:
        cursor.execute(
            """UPDATE users SET token = %s, token_expiry = %s WHERE user_id = %s""",
            (
                "Bearer " + token,
                datetime.now() + timedelta(minutes=30),
                user_id,
            ),
        )
        conn.commit()
    payload["log_id"] = 200
    payload["access_token"] = token
    return jsonify(payload)


@app.route("/api/logout/", methods=["POST"])
def logout():
    # 检查请求头
    if request.headers.get("Content-Type") != "application/json":
        return jsonify({"log_id": 400, "error": "Content-Type must be application/json"})
    if request.headers.get("Authorization") is None:
        return jsonify({"log_id": 401, "error": "Authorization header is required"})

    payload = {"log_id": "",
               "error": ""}

    # 解析请求参数
    try:
        conn = get_conn()
        user = get_user_by_token(request.headers.get("Authorization"))
        if not user:
            payload["log_id"] = 401
            payload["error"] = "Invalid token"
            return jsonify(payload)

        with conn.cursor() as cursor:
            cursor.execute(
                """UPDATE users SET token = NULL, token_expiry = NULL WHERE username = %s""",
                (user["username"],),
            )
        conn.commit()
        payload["log_id"] = 200
        return jsonify(payload)

    except KeyError as e:
        payload["log_id"] = 400
        payload["error"] = f"Missing required field: {e}"
        return jsonify(payload)


@app.route("/api/models/", methods=["POST"])
@require_json_and_auth
def register_model(user):
    payload = {
        "log_id": "",
        "model_id": "",
        "error": ""
    }
    try:
        # 解析请求参数
        data = request.get_json()
        model_content = data["model_content"]  # Base64 编码的模型文件
        model_desc = data["model_desc"]
        model_type = data["model_type"]
        model_column = data["model_column"]  # 列名数组
        model_label = data["model_label"]  # 分类后的标签
        json.loads(model_label)  # 仅验证，不保存解析结果

        # model Base64 解码并写入文件
        model_id = str(uuid.uuid4())
        model_filename = model_id
        filepath = os.path.join(MODEL_STORAGE_DIR, model_filename)
        binary_data = base64.b64decode(model_content.encode("utf-8"))
        with open(filepath, "wb") as f:
            f.write(binary_data)

        # pytorch 需要额外的 pipeline 预处理器文件
        if model_type == "PYTORCH":
            pipeline_content = data["pipeline_content"]
            # pipeline Base64 解码并写入文件
            pipeline_filename = str(uuid.uuid4())
            filepath = os.path.join(MODEL_STORAGE_DIR, pipeline_filename)

            binary_data = base64.b64decode(
                pipeline_content.encode("utf-8"))
            with open(filepath, "wb") as f:
                f.write(binary_data)

        else:
            pipeline_filename = ""

        conn = get_conn()
        with conn.cursor() as cursor:
            # 存储模型到数据库
            cursor.execute(
                """INSERT INTO models (model_id, model_column, model_label, model_date, model_desc, model_filename, model_type, pipeline_filename) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    model_id,
                    json.dumps(model_column),
                    model_label,
                    datetime.now(),
                    model_desc,
                    model_filename,
                    model_type,
                    pipeline_filename,
                ),
            )

            # 存储用户信息与模型的绑定
            cursor.execute(
                """INSERT INTO user_models (user_id, model_id) VALUES (%s, %s)""",
                (user["user_id"], model_id),
            )
        conn.commit()

        # 返回响应参数
        payload["log_id"] = 200
        payload["model_id"] = model_id
        return jsonify(payload)

    # 缺少字段
    except KeyError as e:
        payload["log_id"] = 400
        payload["error"] = f"Missing required field: {e}"
        return jsonify(payload)
    # JSON 解析错误
    except json.JSONDecodeError:
        payload["log_id"] = 400
        payload["error"] = "Invalid JSON"
        return jsonify(payload)
    except Exception as e:
        payload["log_id"] = 500
        payload["error"] = "".join(
            traceback.format_exception(type(e), e, e.__traceback__))
        return jsonify(payload)


@app.route("/api/models/<model_id>/", methods=["GET"])
@require_json_and_auth
def get_model(model_id, user):
    payload = {
        "log_id": "",
        "error": "",
        "result": {}
    }
    # 检查用户是否有权限访问该模型
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute(
            """SELECT * FROM user_models WHERE user_id = %s AND model_id = %s""",
            (user["user_id"], model_id),
        )
        user_model = cursor.fetchone()

    # 用户无权限或模型不存在
    if not user_model:
        payload["log_id"] = 403
        payload["error"] = f"User {user['user_id']} does not have access to model {model_id} or model does not exist"
        return jsonify(payload)

    with conn.cursor() as cursor:
        cursor.execute(
            """SELECT * FROM models WHERE model_id = %s""", (model_id,))
        model = cursor.fetchone()

    tasks = []
    with conn.cursor() as cursor:
        cursor.execute(
            """SELECT * FROM tasks WHERE model_id = %s""", (model_id,))
        for each in cursor.fetchall():
            tasks.append({
                "task_id": each["task_id"],
                "task_desc": each["task_desc"],
                "status": each["status"],
                "start_date": each["start_date"],
                "end_date": each["end_date"],
            })

    payload["result"] = {
        "model_id": model_id,
        "model_column": model["model_column"],
        "model_label": json.loads(model["model_label"]),
        "model_date": model["model_date"],
        "model_desc": model["model_desc"],
        "model_type": model["model_type"],
        "tasks": tasks,
    }
    payload["log_id"] = 200
    payload["model_id"] = model_id
    return jsonify(payload)


@app.route("/api/models/<model_id>/", methods=["DELETE"])
@require_json_and_auth
def delete_model(model_id, user):
    payload = {
        "log_id": "",
        "model_id": "",
        "error": ""
    }
    # 检查用户是否有权限访问该模型
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute(
            """SELECT * FROM user_models WHERE user_id = %s AND model_id = %s""",
            (user["user_id"], model_id),
        )
        user_model = cursor.fetchone()

    # 用户无权限或模型不存在
    if not user_model:
        payload["log_id"] = 403
        payload["error"] = f"User {user['user_id']} does not have access to model {model_id} or model does not exist"
        return jsonify(payload)

    with conn.cursor() as cursor:
        cursor.execute(
            """SELECT * FROM models WHERE model_id = %s""", (model_id,))
        model = cursor.fetchone()

    # 删除模型文件
    model_filename = model["model_filename"]
    filepath = os.path.join(MODEL_STORAGE_DIR, model_filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    with conn.cursor() as cursor:
        # 删除模型记录
        cursor.execute(
            """DELETE FROM models WHERE model_id = %s""", (model_id,))
    conn.commit()

    payload["log_id"] = 200
    payload["model_id"] = model_id
    return jsonify(payload)


@app.route("/api/models/<model_id>/tasks/", methods=["POST"])
@require_json_and_auth
def create_task(model_id, user):
    payload = {
        "log_id": "",
        "task_id": "",
        "error": ""
    }
    # 检查用户是否有权限访问该模型
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute(
            """SELECT * FROM user_models WHERE user_id = %s AND model_id = %s""",
            (user["user_id"], model_id),
        )
        user_model = cursor.fetchone()

    # 用户无权限或模型不存在
    if not user_model:
        payload["log_id"] = 403
        payload["error"] = f"User {user['user_id']} does not have access to model {model_id} or model does not exist"
        return jsonify(payload)

    try:
        data = request.get_json()
        task_desc = data["task_desc"]  # 任务描述
        task_csv = data["task_csv"]  # CSV 文件内容，使用了 Base64 编码
        model_id = data["model_id"]  # 使用的模型 ID
        user_id = user["user_id"]

        # 验证模型是否存在
        conn = get_conn()
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT * FROM models WHERE model_id = %s""", (model_id,)
            )
            model = cursor.fetchone()

        if not model:
            msg = f"Model with id {model_id} not found"
            return jsonify({"log_id": 404, "error": msg})

        model_type = model["model_type"]
        task_id = str(uuid.uuid4())

    # 缺少字段
    except KeyError as e:
        payload["log_id"] = 400
        payload["error"] = f"Missing required field: {e}"
        return jsonify(payload)
    # JSON 解析错误
    except json.JSONDecodeError:
        payload["log_id"] = 400
        payload["error"] = "Invalid JSON"
        return jsonify(payload)

    try:
        bin_csv_data = base64.b64decode(task_csv.encode("utf-8"))
        csv_data = bin_csv_data.decode("utf-8")
        # 读取 CSV，只读取表头，用于验证是否包含模型需要的列名
        print(type(csv_data), csv_data)
        df = pd.read_csv(StringIO(csv_data), nrows=0)
        # 要检查的列
        required_columns = json.loads(model["model_column"])
        # 判断是否都存在
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            payload["log_id"] = 400
            payload["error"] = f"Missing columns:{missing}"
            return jsonify(payload)

        task_filename = f"{str(uuid.uuid4())}.csv"
        filepath = os.path.join(CSV_STORAGE_DIR, task_filename)
        # CSV 无误，写入
        with open(filepath, "wb") as f:
            f.write(bin_csv_data)
    except Exception as e:
        tb_str = "".join(traceback.format_exception(
            type(e), e, e.__traceback__))
        payload["log_id"] = 400
        payload["error"] = f"Failed to save csv: {tb_str}"
        return jsonify(payload)

    # 存储任务到数据库
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute(
            """INSERT INTO tasks (task_id, model_id, task_desc, task_filename, status, start_date, end_date, model_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                task_id,
                model_id,
                task_desc,
                task_filename,
                "PENDING",
                datetime.now(),
                None,
                model_type,
            ),
        )

        # 保存用户与任务的绑定
        cursor.execute(
            """INSERT INTO user_tasks (user_id, task_id) VALUES (%s, %s)""",
            (user_id, task_id),
        )
    conn.commit()

    # 处理任务
    publisher.publish(task_id)

    # 返回响应参数
    payload["log_id"] = 200
    payload["task_id"] = task_id
    return jsonify(payload)


@app.route("/api/tasks/<task_id>/", methods=["GET"])
@require_json_and_auth
def get_task(task_id, user):
    payload = {
        "log_id": "",
        "error": "",
        "result": {}
    }
    # 检查用户是否有权限访问该任务
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute(
            """SELECT * FROM user_tasks WHERE user_id = %s AND task_id = %s""",
            (user["user_id"], task_id),
        )
        user_task = cursor.fetchone()

    # 无权限或任务不存在
    if not user_task:
        payload["log_id"] = 403
        payload["error"] = f"User {user['user_id']} does not have access to task {task_id} or task does not exist"
        return jsonify(payload)

    with conn.cursor() as cursor:
        cursor.execute(
            """SELECT * FROM tasks WHERE task_id = %s""", (task_id,))
        task = cursor.fetchone()
        cursor.execute("""SELECT model_label FROM models WHERE model_id = %s""",
                       (task["model_id"],))
        model_label = cursor.fetchone()["model_label"]

    result = {
        "model_id": task["model_id"],
        "task_id": task_id,
        "task_desc": task["task_desc"],
        "status": task["status"],
        "model_label": model_label,
        "start_date": task["start_date"],
        "end_date": task["end_date"],
        "result": "",
        "error_message": task["error_message"],
    }
    if task["status"] == "DONE":
        # 读取 Result CSV 文件内容
        filepath = os.path.join(RESULT_STORAGE_DIR, task_id)
        with open(filepath, "rb") as csv_file:
            csv_data = csv_file.read()
            result["result"] = base64.b64encode(
                csv_data).decode("utf-8")
    payload["log_id"] = 200
    payload["result"] = result
    return jsonify(payload)


@app.route("/api/tasks/", methods=["GET"])
@require_json_and_auth
def get_all_tasks(user):
    payload = {
        "log_id": "",
        "error": "",
        "result": []
    }
    # 检查用户的所有任务
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT t.*
            FROM user_tasks ut
            JOIN tasks t ON ut.task_id = t.task_id
            WHERE ut.user_id = %s;""",
            (user["user_id"],),
        )
        user_tasks_quiries = cursor.fetchall()

    for row in user_tasks_quiries:
        task = {
            "task_id": row["task_id"],
            "status": row["status"],
            "model_id": row["model_id"],
            "task_desc": row["task_desc"],
            "start_date": row["start_date"],
            "end_date": row["end_date"],
            "error_message": row["error_message"],
        }

        payload["result"].append(task)

    payload["log_id"] = 200
    return jsonify(payload)


@app.route("/api/models/", methods=["GET"])
@require_json_and_auth
def get_all_models(user):
    payload = {
        "log_id": "",
        "error": "",
        "result": []
    }
    # 检查用户的所有模型
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute(
            """SELECT m.* FROM user_models um JOIN models m ON um.model_id = m.model_id WHERE um.user_id = %s""",
            (user["user_id"]))
        user_models_quiries = cursor.fetchall()

    for row in user_models_quiries:
        model = {
            "model_id": row["model_id"],
            "model_column": row["model_column"],
            "model_label": json.loads(row["model_label"]),
            "model_date": row["model_date"],
            "model_desc": row["model_desc"],
            "model_type": row["model_type"],
        }
        payload["result"].append(model)
    payload["log_id"] = 200
    return jsonify(payload)


@app.route("/api/tasks/<task_id>/", methods=["DELETE"])
@require_json_and_auth
def delete_task(task_id, user):
    payload = {
        "log_id": "",
        "error": ""
    }
    # 检查用户是否有权限访问该任务
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute(
            """SELECT * FROM user_tasks WHERE user_id = %s AND task_id = %s""",
            (user["user_id"], task_id),
        )
        user_task = cursor.fetchone()

    # 无权限或任务不存在
    if not user_task:
        payload["log_id"] = 403
        payload["error"] = f"User {user['user_id']} does not have access to task {task_id} or task does not exist"
        return jsonify(payload)

    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute(
            """SELECT * FROM tasks WHERE task_id = %s""", (task_id,))
        task = cursor.fetchone()

    if task:
        # 删除任务文件
        task_filename = task["task_filename"]
        filepath = os.path.join(CSV_STORAGE_DIR, task_filename)
        if os.path.exists(filepath):
            os.remove(filepath)

        # 删除结果文件
        if task["status"] == "DONE":
            result_filename = task["result_filename"]
            result_filepath = os.path.join(
                RESULT_STORAGE_DIR, result_filename)
            if os.path.exists(result_filepath):
                os.remove(result_filepath)

        with conn.cursor() as cursor:
            # 从数据库中删除任务记录
            cursor.execute(
                """DELETE FROM tasks WHERE task_id = %s""", (task_id,))
        conn.commit()

        payload["log_id"] = 200
        return jsonify(payload)
