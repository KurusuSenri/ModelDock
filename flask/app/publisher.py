import pika, time, os

RABBIT_HOST = os.getenv("RABBIT_HOST", "rabbitmq")
RABBIT_USER = os.getenv("RABBIT_USER", "user")
RABBIT_PASS = os.environ["RABBIT_PASS"]

class RabbitPublisher:
    def __init__(self):
        self.credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        for i in range(5):
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=RABBIT_HOST,
                        credentials=self.credentials,
                        heartbeat=30,   # 更短的心跳
                        blocked_connection_timeout=60
                    )
                )
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue="tasks")
                print(" [*] Connected to RabbitMQ")
                return
            except Exception as e:
                print(f" [!] Connect failed: {e}, retry {i+1}/5")
                time.sleep(3)
        raise RuntimeError("Could not connect to RabbitMQ")

    def publish(self, body):
        try:
            if self.connection is None or self.connection.is_closed:
                self.connect()
            self.channel.basic_publish(exchange="", routing_key="tasks", body=body)
        except Exception as e:
            print(f" [!] Publish failed: {e}, reconnecting...")
            self.connect()
            self.channel.basic_publish(exchange="", routing_key="tasks", body=body)

