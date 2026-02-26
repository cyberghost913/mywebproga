from redis.asyncio import Redis
from redis import Redis as syncRedis

redis_client = Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

sync_redis_client = syncRedis(
    host='localhost',
    port=6379,
    decode_responses=True
)

async def get_redis() -> Redis:
    return redis_client

def get_sync_redis() -> syncRedis:
    return sync_redis_client