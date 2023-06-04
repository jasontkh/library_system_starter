import os

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "postgresql://user:password@localhost:5432/database")
BUCKET_NAME = os.getenv("BUCKET_NAME", "demo-dododo3")
PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC", "projects/thematic-garage-386114/topics/dg-library")
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)