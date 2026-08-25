import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def get_cached_seats(event_id: int):
    data = redis_client.get(f"event:{event_id}:seats")
    if data:
        return json.loads(data)
    return None

def set_cached_seats(event_id: int, seats: list, ttl_seconds: int = 30):
    redis_client.setex(f"event:{event_id}:seats", ttl_seconds, json.dumps(seats))

def invalidate_seats_cache(event_id: int):
    redis_client.delete(f"event:{event_id}:seats")