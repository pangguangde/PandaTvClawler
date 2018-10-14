# -*- coding: utf-8 -*-
# @Author  : pangguangde
# @File    : db_monitor.py
# @Time    : 2018/10/13 下午4:31
# @Desc    :
import datetime

from apscheduler.schedulers.background import BlockingScheduler

from utils.common_util import mysql_db

sched = BlockingScheduler()


@sched.scheduled_job('interval', seconds=3, start_date=datetime.datetime.now() + datetime.timedelta(seconds=3), max_instances=1)
@mysql_db.connection_context()
def foo():
    cur_time = datetime.datetime.now()
    end = cur_time.strftime('%Y-%m-%d %H:%M:%S')
    start = cur_time + datetime.timedelta(seconds=-3)
    print('-' * 80)
    r1 = mysql_db.execute_sql('select count(*) from panda_danmu where date_create between "{}" and "{}"'.format(start, end))
    print('{}: 3秒内弹幕数: {}'.format('panda', r1.fetchone()[0]))
    r2 = mysql_db.execute_sql('select count(*) from douyu_danmu where date_create between "{}" and "{}"'.format(start, end))
    print('{}: 3秒内弹幕数: {}'.format('douyu', r2.fetchone()[0]))
    r3 = mysql_db.execute_sql('select count(*) from  huya_danmu where date_create between "{}" and "{}"'.format(start, end))
    print('{}: 3秒内弹幕数: {}'.format('huya', r3.fetchone()[0]))


sched.start()