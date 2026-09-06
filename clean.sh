#!/bin/sh
# 清空 mariadb_data 以及上传的 csvs，models 和计算出的 results
DIRS=(
  "./mariadb/mariadb_data"
  "./shared_data/resources/csvs"
  "./shared_data/resources/models"
  "./shared_data/resources/results"
)

for DIR in "${DIRS[@]}"; do
  if [ -d "$DIR" ]; then
    rm -rf "${DIR:?}"/{*,.[!.]*,..?*}
    echo "${DIR} cleaned"
  else
    echo "${DIR} does not exist"
  fi
done