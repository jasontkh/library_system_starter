import os

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "postgresql://user:password@localhost:5432/database")
BUCKET_NAME = os.getenv("BUCKET_NAME", "demo-bucket-dododo2")
PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC", "projects/bold-network-380012/topics/ocr-project")
