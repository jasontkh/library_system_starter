from redis import Redis

def get_related_documents(redis: Redis, document_id: int, num_docs: int = -1) -> list[int]:
    return redis.lrange(f"document:{document_id}:related", 0, num_docs)