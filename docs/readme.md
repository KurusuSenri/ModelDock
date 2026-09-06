## 初始化

根目录下有 `clean.sh`，会清除 MariaDB 的所有文件，以及上传的 CSV，模型，和生成的计算结果

## 启动

在根目录下，

`docker-compose build && docker-compose up`

## 结构

### Apache

浏览器前端，通过访问位于 localhost:7890 的 flask 与 API 交互

### MariaDB

用于 API 服务器的数据存储，数据库结构参见 `mariadb/init.sql`。该 SQL 会在数据库首次初始化时执行

数据库映射在 `mariadb/mariadb_data/`

### Flask

作为 API 服务器

API 接口文档参见 `docs/api.md`

用户信息，任务信息，模型信息使用 MariaDB 存储，上传的 CSV 和模型存储在 `shared_data/csvs/` 和 `shared_data/models/`

Flask 不参与模型的运算，而是在收到计算请求后将 `task_id` 发送到 RabbitMQ 的消息队列中，并由 Worker 处理

### RabbitMQ

消息队列，用于 Flask 和 Worker 之间的通信。除了用户名和密码外使用 `rabbitmq:3-management` 镜像的默认配置

### Worker

模型的运行时

连接到 RabbitMQ 后待机，当有新的 `task_id` 传入时会从 MariaDB 中读取相关信息并计算，任务信息写回数据库

任务的计算结果为包含上传任务时的 CSV 的所有列，以及作为预测概率的新的一列的 CSV，存储在 `shared_data/results/`

