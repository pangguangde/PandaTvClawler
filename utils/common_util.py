# -*- coding: utf-8 -*-
# @Author  : pangguangde
# @File    : common_util.py
# @Time    : 2018/8/27 下午3:49
# @Desc    :

import hashlib
import logging
import sys
import uuid

import jieba as jieba
from playhouse.pool import PooledMySQLDatabase
from qiniu import Auth, etag, put_file

from settings import *
mysql_db = PooledMySQLDatabase(
    MYSQL_DB,
    max_connections=50,
    host=MYSQL_HOST,
    user=MYSQL_USER,
    passwd=MYSQL_PASSWD,
    charset='utf8mb4',
    port=MYSQL_PORT
)


def get_common_logger(name):
    new_logger = logging.getLogger(name)
    if not new_logger.handlers:
        new_logger.setLevel(logging.DEBUG)
        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s [%(thread)d - %(name)s - %(funcName)s] %(levelname)s | %(message)s')
        ch.setFormatter(formatter)
        # 给logger添加handler
        new_logger.addHandler(ch)
    return new_logger


def md5(s):
    if type(s) == str:
        s = s.decode('utf8')
    m = hashlib.md5()
    m.update(s.encode("utf-8"))
    return m.hexdigest()


def random_file_name():
    c = COUNTER.pop(0)
    COUNTER.append(c)
    return '{}/tmp/tmp_{:0>2d}.png'.format(RES_PATH, c)


def get_img_url(local_path):
    """
    将图片传到七牛并获取外链
    :param local_path: 本地绝对路径
    :return:
    """
    # 需要填写你的 Access Key 和 Secret Key
    access_key = 'eIugjZLSl5-CSSQaZcGDkqL5A2q3ZBkbOBKX8w_v'
    secret_key = 'WpI4jjPhx6U0AKPD5v0liLFzehQ0qhqUDQJL5HEr'
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = 'pandatv'
    # 要上传文件的本地路径
    localfile = local_path
    # 上传到七牛后保存的文件名
    key = uuid.uuid4().hex + '.png'
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket=bucket_name, key=key)
    ret, info = put_file(token, key, localfile)
    print(localfile.split('/')[-1], key, info)
    # print(
    assert ret['key'] == key
    assert ret['hash'] == etag(localfile)
    return {'url': 'http://pe41pg10l.bkt.clouddn.com/' + key}


def create_node_ini(site, room_id):
    with open(RES_PATH + '/conf.d/{}_{}.ini'.format(site, room_id), 'w+', encoding='utf8') as fp:
        s = """; 设置进程的名称，使用 supervisorctl 来管理进程时需要使用该进程名
[program:{site}-{room_id}]
command=node {site}.js -r {room_id}
numprocs=2 ; 默认为1
process_name=%(program_name)s_%(process_num)02d ; 默认为 %(program_name)s，即 [program:x] 中的 x
directory={node_path} ; 执行 command 之前，先切换到工作目录
; 程序崩溃时自动重启，重启次数是有限制的，默认为3次
autostart=true
autorestart=true
redirect_stderr=true ; 重定向输出的日志
stdout_logfile = {node_path}/logs/{site}/{room_id}.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=2
loglevel=info
stopasgroup=true ;默认为false,进程被杀死时，是否向这个进程组发送stop信号，包括子进程
killasgroup=true ;默认为false，向进程组发送kill信号，包括子进程""".format(site=site, room_id=room_id, node_path=NODE_PATH)
        fp.write(s)


def correct_exit(sched):
    def decorator(func):
        def wrapper(*args, **kw):
            try:
                return func(*args, **kw)
            except:
                sched.shutdown()
        return wrapper
    return decorator


if __name__ == '__main__':
    # print(get_img_url('/Users/pangguangde/Downloads/IMG_4867.PNG'))

    # create_node_ini('panda', '371037')
    # create_node_ini('douyu', '288016')
    # create_node_ini('douyu', '424559')
    # create_node_ini('huya', '660000')
    import xmlrpc.client
    xmlrpc.client.Server('http://:@127.0.0.1:9001/RPC2')
