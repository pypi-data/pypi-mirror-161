import os
import redis

cache = redis.StrictRedis.from_url(os.environ['SPAPI_REDIS_URL'], decode_responses=True)
