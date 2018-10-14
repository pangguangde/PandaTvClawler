# -*- coding: utf-8 -*-
# @Author  : pangguangde
# @File    : db_task.py
# @Time    : 2018/10/13 下午6:56
# @Desc    :

from celery import Celery
from peewee import IntegrityError

from settings import REDIS_URL
from utils.common_util import mysql_db

app = Celery('danmu', backend=REDIS_URL, broker=REDIS_URL)  # 配置好celery的backend和broker
app.conf.CELERY_CONCURRENCY = 10
print(REDIS_URL)

@app.task(ignore_result=True, queue='celery.danmu')
@mysql_db.connection_context()
def save_comment(info):
    print('-' * 80)
    query = mysql_db.execute_sql('select count(*) from {} where id ="{}"'.format(info['db_name'], info['id']))
    num = query.fetchone()[0]
    if num == 0:
        try:
            if 'plat' in info and info.get('plat'):
                mysql_db.execute_sql(
                    "INSERT INTO `{}` (`id`, `user_name`, `content`, `pub_time`, `room_id`, `plat`, `user_id`) VALUES "
                    "('{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(info['db_name'],
                                                                         info['id'],
                                                                         info['user_name'],
                                                                         info['content'],
                                                                         info['pub_time'],
                                                                         info['room_id'],
                                                                         info['plat'],
                                                                         info['user_id']))
            else:
                mysql_db.execute_sql(
                    "INSERT INTO `{}` (`id`, `user_name`, `content`, `pub_time`, `room_id`, `user_id`) VALUES "
                    "('{}', '{}', '{}', '{}', '{}', '{}');".format(info['db_name'],
                                                                   info['id'],
                                                                   info['user_name'],
                                                                   info['content'],
                                                                   info['pub_time'],
                                                                   info['room_id'],
                                                                   info['user_id']))
        except IntegrityError as e:
            pass

