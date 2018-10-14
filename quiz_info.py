# -*- coding: utf-8 -*-
# @Author  : pangguangde
# @File    : quiz_info.py
# @Time    : 2018/9/3 下午9:17
# @Desc    :
import datetime
import json

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from playhouse.pool import PooledMySQLDatabase

from model import QuizHistory
from settings import *
from utils.common_util import get_common_logger, mysql_db, correct_exit

sched = BlockingScheduler()
logger = get_common_logger('root')
first_run = datetime.datetime.now() + datetime.timedelta(seconds=5)
mysql_db = mysql_db


@sched.scheduled_job('interval', seconds=95, start_date=first_run)
@mysql_db.connection_context()
@correct_exit(sched)
def run():
    print('-' * 100)
    # print('[check db connection]: is_closed={}'.format(mysql_db.is_closed()))
    # print('init db connection...')
    # mysql_db.connect()
    # print('[check db connection]: is_closed={}'.format(mysql_db.is_closed()))
    for target in json.load(open(b'res/targets.json', 'r+', encoding="utf-8")):
        room_id = target['roomid']
        host_id = target['hostid']
        owner = target['name']
        data = requests.get(
            url="http://roll.panda.tv/list_quiz_host",
            params={
                "app": "panda",
                "limit": "3",
                "hostid": host_id,
                "beginday": "2018-09-01",
            },
            headers={
                "Host": "roll.panda.tv",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Origin": "https://www.panda.tv",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
                "Referer": "https://www.panda.tv/{}".format(room_id),
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip",
            }
        ).json()
        logger.info('getting {} quiz info...'.format(room_id))
        is_latest = True
        for info in data['data']['quiz']:
            query = QuizHistory.select().where((QuizHistory.id == info['id']) & QuizHistory.is_finished)
            if not query.exists():
                qh = QuizHistory()
                qh.id = info['id']
                qh.room_id = room_id
                qh.host_id = host_id
                qh.owner = owner
                qh.title = info['name']

                qh.opt1_id = list(info['total'].keys())[1]
                qh.opt2_id = list(info['total'].keys())[0]
                if int(qh.opt1_id) > int(qh.opt2_id):
                    qh.opt1_id, qh.opt2_id = qh.opt2_id, qh.opt1_id
                qh.opt1 = info['teams_info'][qh.opt1_id]['option']['name']
                qh.odds1 = float(info['ratio'][qh.opt1_id])
                qh.total1 = info['total'][qh.opt1_id]

                qh.opt2 = info['teams_info'][qh.opt2_id]['option']['name']
                qh.odds2 = float(info['ratio'][qh.opt2_id])
                qh.total2 = info['total'][qh.opt2_id]

                qh.most_uid = info['mostusr'].get('rid')
                qh.most_uname = info['mostusr'].get('nickName')
                qh.most_price = info['mostusr'].get('total')
                qh.begin_date = datetime.datetime.strptime(info['beginday'] + ' ' + info['begintime'], '%Y-%m-%d %H:%M')

                try:
                    qh.end_time = datetime.datetime.strptime(info['endtime'], '%Y-%m-%d %H:%M:%S')
                except:
                    pass
                qh.winner = info.get('winner')
                if not is_latest:
                    qh.is_finished = True
                is_latest = False
                if qh.winner and len(qh.winner) > 2:
                    qh.winner = info['teams_info'][qh.winner]['option']['name']
                elif qh.is_finished:
                    qh.winner = '流盘'
                try:
                    qh.save(force_insert=True)
                    logger.info('id: [{}] insert!'.format(qh.id))
                except:
                    qh.save()
                    logger.info('id: [{}] updated!'.format(qh.id))
    # print('[check db connection]: is_closed={}'.format(mysql_db.is_closed()))
    # print('close db connection...')
    # mysql_db.close_all()
    # mysql_db.close()
    # print('[check db connection]: is_closed={}'.format(mysql_db.is_closed()))


sched.start()
# run()
# data = json.load(open('res/targets.json', 'r+'))
# print(data)