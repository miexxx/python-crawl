# -*- coding: utf-8 -*-
import redis
redis_cli = redis.StrictRedis(host="localhost")
for n in range(1,20000):
    redis_cli.incr("lagou_count")