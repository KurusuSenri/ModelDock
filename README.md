# ModelDock

ModelDock is a small platform for uploading machine learning models and running
them with CSV data. After the task is finished, the user can see the prediction
result from the web page.

This project was made for learning and for trying a simple model serving
system. It is not a production platform.

## What it can do

- User login and logout
- Upload an ONNX model
- Upload a preprocessing pipeline for a PyTorch model
- Create a prediction task with a CSV file
- Run the task in a separate worker
- Check task status and download the result
- Save users, models, and tasks in MariaDB

## How it works

The project has several Docker services:

- **Apache** serves the simple web pages.
- **Flask** provides the API.
- **RabbitMQ** sends task messages from Flask to the worker.
- **MariaDB** stores users and task information.
- **Worker** loads the model and runs prediction.

The uploaded files and result files are shared between Flask and Worker
through `shared_data/resources`.

## Start it locally

First make the local environment file:

```bash
cp .env.example .env
```

Then edit `.env` and replace the example values. The important values are:

```env
DB_ROOT_PASSWORD=your-local-root-password
DB_PASS=your-local-database-password
RABBIT_PASS=your-local-rabbitmq-password
SECRET_KEY=your-local-secret-key
DEMO_USER=demo
DEMO_PASSWORD=demo
```

Start the services:

```bash
docker compose up --build
```

Open the web page:

```text
http://localhost:8080
```

The API is available at:

```text
http://localhost:5000
```

The RabbitMQ management page is available at:

```text
http://localhost:15672
```

Use the `user` account and the value of `RABBIT_PASS` to log in there.

## Demo login

The demo user is created when MariaDB is initialized for the first time.
The username and password come from `DEMO_USER` and `DEMO_PASSWORD` in `.env`.

If the database was already initialized, changing `.env` does not change the
old user. To create the demo user again, remove the local data and start again:

```bash
docker compose down
./clean.sh
docker compose up --build
```

This removes the local database, uploaded files, models, and result files.

## Project folders

```text
apache/       simple frontend pages
flask/        Flask API service
worker/       prediction worker
mariadb/      database schema and initialization
shared_data/  local model, CSV, and result storage
docs/         API notes
```

More API examples are in [`docs/api.md`](docs/api.md).

## Supported model flow

The frontend sends model and CSV files to the Flask API as Base64 data.
Flask saves the files and sends a task ID to RabbitMQ. The worker gets the
task ID, reads the model and CSV, runs the prediction, and saves a result CSV.

The result keeps the input columns and adds a prediction column named
`target`.

## Important note

This repository is for local demonstration. It still needs more work before
using it on the public internet, such as better password storage, stronger
authorization, HTTPS, input limits, and production server settings.

Do not commit `.env`, local database files, uploaded private data, or private
models.
