# -*- coding: utf-8 -*-
# @Author  : pangguangde
# @File    : model.py
# @Time    : 2018/8/27 下午3:49
# @Desc    :
import datetime

from peewee import CharField, DateTimeField, FloatField, IntegerField, Model, SQL, BooleanField

from utils.common_util import mysql_db


class QuizHistory(Model):
    id = CharField(64, primary_key=True)
    title = CharField(32, constraints=[SQL("COMMENT '内容'")])

    opt1 = CharField(16, constraints=[SQL("COMMENT '选项1'")])
    opt1_id = CharField(16, constraints=[SQL("COMMENT '选项1 ID'")])
    odds1 = FloatField(constraints=[SQL("COMMENT '赔率1'")])
    total1 = IntegerField(constraints=[SQL("COMMENT '总投注1'")])

    opt2 = CharField(16, constraints=[SQL("COMMENT '选项2'")])
    opt2_id = CharField(16, constraints=[SQL("COMMENT '选项2 ID'")])
    odds2 = FloatField(constraints=[SQL("COMMENT '赔率2'")])
    total2 = IntegerField(constraints=[SQL("COMMENT '总投注2'")])

    most_uid = CharField(32, constraints=[SQL("COMMENT '最高投注的id'")])
    most_uname = CharField(64, constraints=[SQL("COMMENT '最高投注的名字'")])
    most_price = IntegerField(constraints=[SQL("COMMENT '最高投注数目'")])

    begin_date = DateTimeField(constraints=[SQL("COMMENT '开始时间'")])
    end_time = DateTimeField(constraints=[SQL("COMMENT '结束时间'")])

    winner = CharField(16, constraints=[SQL("COMMENT '赢的opt_id'")])
    is_finished = BooleanField(constraints=[SQL("COMMENT '是否已结束'")])

    room_id = CharField(32, constraints=[SQL("COMMENT '房间号'")])
    owner = CharField(64, constraints=[SQL("COMMENT '直播间名字'")])
    host_id = CharField(64, constraints=[SQL("COMMENT '类似房间id'")])

    date_create = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP  COMMENT '创建时间'")])

    class Meta:
        database = mysql_db
        table_name = 'quiz'


class Danmu(Model):
    id = CharField(50, primary_key=True)
    user_name = CharField(32)
    content = CharField(128)
    pub_time = DateTimeField()
    room_id = CharField(16)
    plat = CharField(16)
    user_id = CharField(20)
    date_create = DateTimeField()

    class Meta:
        database = mysql_db
        table_name = 'panda_danmu'

    @staticmethod
    def get_recent_danmu(room_id='7000', time=None):
        time = time or datetime.datetime.now()
        start = (time - datetime.timedelta(seconds=120)).strftime('%Y-%m-%d %H:%M:%S')
        end = time.strftime('%Y-%m-%d %H:%M:%S')
        return [
            item.content for item in Danmu.select(Danmu.content).where(
                (Danmu.room_id == room_id) &
                Danmu.pub_time.between(start, end)
            ) if item.content != '[:晕]'
        ]

    @staticmethod
    def get_danmu(room_id='7000', start=None, end=None):
        return [
            item.content for item in Danmu.select(Danmu.content).where(
                (Danmu.room_id == room_id) &
                Danmu.pub_time.between(start, end)
            ) if item.content != '[:晕]'
        ]


if not QuizHistory.table_exists():
    QuizHistory.create_table(safe=True)
    print('[INFO]: table create success!')


if __name__ == '__main__':
    # us = UserSession()
    # us.site = 'didi'
    # us.status = 0
    # us.session = '{}'
    # us.phone = ''
    # us.save()
    # danmu = Danmu()
    # for item in danmu.get_recent_danmu():
    #     print(item)
    import time
    t1 = time.time()
    print(len(Danmu.get_recent_danmu(time=datetime.datetime(2018, 9, 10, 20))))
    print(time.time() - t1)

