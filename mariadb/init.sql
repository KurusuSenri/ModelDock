use database;

CREATE TABLE IF NOT EXISTS models (
    model_id VARCHAR(60) PRIMARY KEY,
    model_column TEXT NOT NULL,
    model_label TEXT NOT NULL,
    model_date datetime NOT NULL,
    model_desc TEXT NOT NULL,
    model_type VARCHAR(60) NOT NULL,
    model_filename VARCHAR(60) NOT NULL,
    pipeline_filename VARCHAR(60) NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(60) PRIMARY KEY,
    username VARCHAR(60) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at datetime NOT NULL,
    token TEXT,
    token_expiry datetime
);

CREATE TABLE IF NOT EXISTS logs (
    log_id VARCHAR(60) PRIMARY KEY,
    datetime datetime NOT NULL,
    user_id VARCHAR(60) NOT NULL,
    message TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tasks (
    task_id VARCHAR(60) PRIMARY KEY,
    model_id VARCHAR(60) NOT NULL,
    task_desc TEXT NOT NULL,
    task_filename VARCHAR(60) NOT NULL,
    status VARCHAR(60) NOT NULL,
    start_date datetime NOT NULL,
    end_date datetime,
    result_filename VARCHAR(60),
    error_message TEXT,
    model_type VARCHAR(60) NOT NULL,
    FOREIGN KEY (model_id) REFERENCES models(model_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_models (
    user_id VARCHAR(60) NOT NULL,
    model_id VARCHAR(60) NOT NULL,
    PRIMARY KEY (user_id, model_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES models(model_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_tasks (
    user_id VARCHAR(60) NOT NULL,
    task_id VARCHAR(60) NOT NULL,
    PRIMARY KEY (user_id, task_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE
);
