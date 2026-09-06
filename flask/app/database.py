from flask import g
import pymysql
import os

DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = int(os.getenv("DB_PORT", ""))
DB_NAME = os.getenv("DB_NAME", "")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASS", "")

def get_conn():
    if "conn" not in g:
        g.conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor 
        )
    return g.conn

def close_conn(e=None):
    conn = g.pop("conn", None)
    if conn is not None:
        conn.close()
