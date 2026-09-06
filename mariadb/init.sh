#!/bin/sh
set -eu

mariadb --protocol=socket -uroot -p"${MARIADB_ROOT_PASSWORD}" "${MARIADB_DATABASE}" <<SQL
INSERT IGNORE INTO users (user_id, username, password, created_at)
VALUES ('${DEMO_USER}', '${DEMO_USER}', '${DEMO_PASSWORD}', NOW());
SQL
