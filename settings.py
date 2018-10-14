# -*- coding: utf-8 -*-
# @Author  : pangguangde
# @File    : settings.py
# @Time    : 2018/8/27 下午3:49
# @Desc    :

import os
import platform
import uuid


def get_mac_address():
    import uuid
    node = uuid.getnode()
    mac = uuid.UUID(int=node).hex[-12:]
    return mac

cur_mac = get_mac_address()

IS_DEV = True if platform.platform().find('Linux') == -1 else False
IS_TX1 = cur_mac == '5254003deb8b'

PROJECT_PATH = os.path.abspath(__file__).split('/settings')[0]
RES_PATH = PROJECT_PATH + '/res'
PHANTOMJS_PATH = RES_PATH + '/phantomjs' if IS_DEV else '/usr/local/bin/chromedriver'

MYSQL_HOST = 'cdb-ek0p4xfw.cd.tencentcdb.com'
MYSQL_USER = 'root'
MYSQL_PASSWD = 'BqbLY9N64mnJQKpj'
MYSQL_DB = 'test'
MYSQL_PORT = 10003

COUNTER = list(range(100))


REDIS_URL = 'redis://:Iv0ahcN0Duqf3Uq@118.25.88.176:6380/0' if not IS_TX1 \
       else 'redis://:Iv0ahcN0Duqf3Uq@172.17.0.7:6379/0'

if cur_mac == '5254003deb8b':
    NODE_PATH = '/home/ubuntu/guangde/panda-danmu'
elif cur_mac == '00e04c21e7cc':
    NODE_PATH = ''
elif cur_mac == '88e9fe552cc0':
    NODE_PATH = '/Users/pangguangde/WebstormProjects/panda-danmu'
