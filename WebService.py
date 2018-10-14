# -*- coding: utf-8 -*-
# @Author  : pangguangde
# @File    : WebService.py
# @Time    : 2018/9/8 下午1:22
# @Desc    :
import datetime
import json
import random
import subprocess
import time
import xmlrpc.client

import chartkick
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
from flask import Blueprint, Flask, render_template, request

from model import Danmu
from settings import NODE_PATH
from utils.common_util import get_common_logger, mysql_db, create_node_ini
from utils.redis_util import RedisHelper
from word_cloud_util import get_b64_pic

app = Flask(__name__, static_folder='static')

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
ck = Blueprint('ck_page', __name__, static_folder=chartkick.js(), static_url_path='/static')
app.register_blueprint(ck, url_prefix='/ck')
app.jinja_env.add_extension("chartkick.ext.charts")

rds_client = RedisHelper().client

logger = get_common_logger('WebService')
rpc_server = xmlrpc.client.Server('http://:@127.0.0.1:9001/RPC2')


@app.route("/")
def hello():
    return render_template('show.html', data=[
        {'data': [['2013-04-01 00:00:00 UTC', 52.9], ['2013-05-01 00:00:00 UTC', 50.7]], 'name': 'Chrome'},
        {'data': [['2013-04-01 00:00:00 UTC', 27.7], ['2013-05-01 00:00:00 UTC', 25.9]], 'name': 'Firefox'}])


# @app.route('/js/<path:path>')
# def send_js(path):
#     print(path)
#     return send_from_directory('js', path)

room_ids = set([])
pic_cache = {}

global_ts = None


def get_rds_key1(room_id):
    global global_ts
    cur_time = min(int(time.time()), global_ts) + 5
    global_ts += 5
    return 'pandatv:b64_pic:{room_id}_{time_interval}'.format(room_id=room_id, time_interval=cur_time // 5)


def get_rds_key0(room_id):
    cur_time = int(time.time()) - 4
    return 'pandatv:b64_pic:{room_id}_{time_interval}'.format(room_id=room_id, time_interval=cur_time // 5)


@app.route('/word_cloud')
@mysql_db.connection_context()
def show_word_cloud():
    room_id = request.args.get('RoomId')
    cur_time = datetime.datetime.now()
    try:
        b64_str = pic_cache[room_id]['list'].pop(-1)
        pic_cache[room_id]['time'] = cur_time.strftime(DATETIME_FORMAT)
    except:
        b64_str = ''
    room_ids.add(room_id)
    return render_template('word_cloud.html', room_id=room_id, b64_str=b64_str)


sched = BackgroundScheduler()


@sched.scheduled_job('interval', seconds=5, start_date=datetime.datetime.now() + datetime.timedelta(seconds=3), max_instances=1)
@mysql_db.connection_context()
def add_pic_to_list():
    for room_id in room_ids:
        print('add_pic_to_list: {}'.format(room_id))
        cur_time = datetime.datetime.now()
        danmu_list = Danmu.get_recent_danmu(room_id=room_id, time=cur_time)
        print('danmu num: {}'.format(len(danmu_list)))
        danmus = ' '.join(danmu_list)
        b64_str = get_b64_pic(danmus).decode()
        if room_id not in pic_cache:
            pic_cache[room_id] = {'time': cur_time.strftime(DATETIME_FORMAT), 'list': [b64_str]}
        else:
            pic_cache[room_id]['list'].append(b64_str)


first_run = datetime.datetime.now() + datetime.timedelta(minutes=1)


@sched.scheduled_job('interval', seconds=60, start_date=first_run, max_instances=1)
def release_pic_cache():
    if pic_cache:
        print('release_pic_cache')
    for k, v in pic_cache.items():
        last_time = datetime.datetime.strptime(v['time'], DATETIME_FORMAT)
        if (datetime.datetime.now() - last_time).seconds > 60:
            del pic_cache[k]
            print(pic_cache.get(k, k + 'has been removed!'))
            room_ids.remove(k)


def in_monitoring(site, room_id):
    try:
        info = rpc_server.supervisor.getProcessInfo('{site}-{room_id}:{site}-{room_id}_00'.format(site=site, room_id=room_id))
        return info['statename'] == 'RUNNING'
    except:
        return False


@sched.scheduled_job('interval', seconds=180, start_date=datetime.datetime.now() + datetime.timedelta(seconds=3), max_instances=1)
def check_room_status_panda():
    targets = json.load(open(b'res/targets.json', 'r+', encoding="utf-8"))
    scan_ids = ['371037'] + [item['roomid'] for item in targets]
    logger.info(scan_ids)
    for r_id in scan_ids:
        create_node_ini('panda', r_id)
        r = requests.get('https://www.panda.tv/api_room_v2?roomid={}'.format(r_id))
        d = r.json()
        if d['data']['roominfo']['status'] == '2' and int(d['data']['roominfo']['person_num']) > 500:
            if not in_monitoring('panda', r_id):
                logger.info('{} 开启监控: {}'.format(r_id.ljust(7), d['data']['hostinfo']['name']))
                rpc_server.supervisor.startProcessGroup('panda-{}'.format(r_id))
            else:
                logger.info('{} 正在监控: {}'.format(r_id.ljust(7), d['data']['hostinfo']['name']))
        else:
            if in_monitoring('panda', r_id):
                rpc_server.supervisor.stopProcessGroup('panda-{}'.format(r_id))
            logger.info('{} 还未开播: {}'.format(r_id.ljust(7), d['data']['hostinfo']['name']))
        time.sleep(random.uniform(1, 5))


@sched.scheduled_job('interval', seconds=300, start_date=datetime.datetime.now() + datetime.timedelta(seconds=3), max_instances=1)
def check_room_status_douyu():
    scan_ids = ['288016', '424559', '252140', '4908245', '5068351', '2040718', '12847', '5067522', '5569952', '5631401', '5569971', '5630739', '5569903', '8733']
    logger.info(scan_ids)
    for r_id in scan_ids:
        create_node_ini('douyu', r_id)
        r = requests.get('https://www.douyu.com/ztCache/WebM/room/{}'.format(r_id))
        d = r.json()
        room_info = json.loads(d['$ROOM'])
        if room_info['show_status'] == 1:
            if not in_monitoring('douyu', r_id):
                logger.info('{} 开启监控: {}'.format(r_id.ljust(7), room_info['room_name']))
                rpc_server.supervisor.startProcessGroup('douyu-{}'.format(r_id))
            else:
                logger.info('{} 正在监控: {}'.format(r_id.ljust(7), room_info['room_name']))
        else:
            if in_monitoring('douyu', r_id):
                rpc_server.supervisor.stopProcessGroup('douyu-{}'.format(r_id))
            logger.info('{} 还未开播: {}'.format(r_id.ljust(7), room_info['room_name']))
        time.sleep(random.uniform(1, 5))


@sched.scheduled_job('interval', seconds=200, start_date=datetime.datetime.now() + datetime.timedelta(seconds=3), max_instances=1)
def check_room_status_huya():
    scan_ids = ['660000', '666888', '521521']
    logger.info(scan_ids)
    for r_id in scan_ids:
        create_node_ini('huya', r_id)
        r = requests.get('https://www.huya.com/{}'.format(r_id))

        soup = BeautifulSoup(r.text)

        if 'liveStatus-on' in soup.body.attrs['class']:
            if not in_monitoring('huya', r_id):
                logger.info('{} 开启监控: {}'.format(r_id.ljust(7), soup.h3.text))
                rpc_server.supervisor.startProcessGroup('huya-{}'.format(r_id))
            else:
                logger.info('{} 正在监控: {}'.format(r_id.ljust(7), soup.h3.text))
        else:
            if in_monitoring('huya', r_id):
                rpc_server.supervisor.stopProcessGroup('huya-{}'.format(r_id))
            logger.info('{} 还未开播: {}'.format(r_id.ljust(7), soup.h3.text))
        time.sleep(random.uniform(1, 7))


if __name__ == '__main__':
    # key = get_rds_key('1234')
    # rds_client.set(key, '1234')
    # rds_client.expire(key, 120)
    sched.start()
    app.run(host='0.0.0.0', port=2333, threaded=True)
