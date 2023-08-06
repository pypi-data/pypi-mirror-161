# -*- coding: utf-8 -*-
import redis


def get_redis_client(redis_config):
    db_redis = redis.StrictRedis(connection_pool=redis.ConnectionPool(**redis_config, decode_responses=True)) if redis_config else None
    return db_redis
