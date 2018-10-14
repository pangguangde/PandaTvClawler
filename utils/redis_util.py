# -*- coding: utf-8 -*-
# @Author  : pangguangde
# @File    : redis_util.py
# @Time    : 2018/10/11 上午11:24
# @Desc    :

import redis

from settings import REDIS_URL


class RedisHelper(object):
    _inst = redis.from_url(REDIS_URL)

    @property
    def client(self):
        return self._inst
