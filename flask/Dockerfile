FROM python:3.9-slim

# Install dependencies
WORKDIR /app
COPY requirements requirements
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements

# Flask at 5000
EXPOSE 5000
CMD ["flask", "run"]