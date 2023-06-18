import os

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "postgresql://user:password@localhost:5432/database")
BUCKET_NAME = os.getenv("BUCKET_NAME", "dg-library-2302-klaus")
PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC", "projects/thematic-garage-386114/topics/dg-library-system")
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)