import redis
r = redis.Redis(host='localhost', port=6379, db=0)
r.zadd("doc1_recommendation", {"doc5": 0.1})




r.zadd("doc1_recommendation", {"doc2": 0.9, "doc3": 0.7})
r.zrange("doc1_recommendation", 0, -1)