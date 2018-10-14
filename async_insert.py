# -*- coding: utf-8 -*-
# @Author  : pangguangde
# @File    : async_insert.py
# @Time    : 2018/10/13 下午6:46
# @Desc    :
import datetime
import json
import threading

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, current_app

from settings import REDIS_URL
from tasks.db_task import save_comment
from utils.common_util import get_common_logger

app = Flask(__name__)
sched = BackgroundScheduler()

lock = threading.Lock()

all_ids = set([])
first_run = datetime.datetime.now() + datetime.timedelta(seconds=60)

logger = get_common_logger('async_insert')
logger.info(REDIS_URL)


@sched.scheduled_job('interval', seconds=60, start_date=first_run, max_instances=1)
def release_cache():
    logger.info("======= release_cache ======")
    lock.acquire()
    all_ids.clear()
    lock.release()


@app.route('/async_insert', methods=['POST'])
def async_insert():
    data = json.loads(request.form['json_str'])
    lock.acquire()
    if data.get('id') not in all_ids:
        info = {
            'db_name': data.get('db_name'),
            'id': data.get('id'),
            'user_name': data.get('user_name'),
            'content': data.get('content'),
            'pub_time': data.get('pub_time'),
            'room_id': data.get('room_id'),
            'plat': data.get('plat'),
            'user_id': data.get('user_id')
        }
        logger.info('[{}]: {}'.format(data.get('user_name'), data.get('content')))
        save_comment.delay(info)
        all_ids.add(data.get('id'))
    lock.release()
    return json.dumps({'status': 200})


if __name__ == '__main__':
    sched.start()
    app.run(host='0.0.0.0', port=5533, threaded=True)
