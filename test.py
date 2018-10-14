import datetime
import random

import jieba
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# import matplotlib.dates as mdate
# import matplotlib.pyplot as plt
# plt.style.use('ggplot')
# import pandas as pd
# import numpy as np
#
# #随机生成两个dataframe
# d1 = pd.DataFrame(columns=['x', 'y'])
# d1['x'] = [datetime.datetime.now().strftime('%Y-%m-%d')]
# d1['y'] = np.random.normal(0, 1, 1)
# d2 = pd.DataFrame(columns=['x', 'y'])
# d2['x'] = [(datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')]
# d2['y'] = np.random.normal(2, 1, 1)
#
# fig = plt.figure(figsize=(100, 150))
# ax1 = fig.add_subplot(111)
# ax1.xaxis.set_major_formatter(mdate.DateFormatter('%Y-%m-%d'))
#
# #分别画出scatter图，但是设置不同的颜色
# plt.scatter(d1['x'], d1['y'], color='red', label='lose')
# plt.scatter(d2['x'], d2['y'], color='green', label='win')
#
# #设置图例
# plt.legend(loc=(1, 0))
#
# #显示图片
# plt.show()




import matplotlib.pyplot as plt
from matplotlib.dates import AutoDateLocator, DateFormatter, DayLocator
from matplotlib.font_manager import FontProperties

from model import QuizHistory
from settings import RES_PATH

myfont = FontProperties(fname='/System/Library/Fonts/STHeiti Medium.ttc', size=40)


def draw_win_lose(title, win, lose):
    plt.plot_date(lose[0], lose[1], color=(1, 0, 0, 0.65))
    plt.plot_date(win[0], win[1], color='green')

    ax = plt.gca()
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))  #设置时间显示格式
    ax.xaxis.set_major_locator(DayLocator())       #设置时间间隔
    ax.grid(axis='x', linestyle='-.')
    ax.grid(axis='y', linestyle=':')

    hour_max = int(max(max(win[1]), max(lose[1]))) + 1
    hour_min = int(min(min(win[1]), min(lose[1]))) - 1
    print(hour_max, hour_min)
    plt.ylim(hour_min, hour_max)
    ax.set_yticks(range(hour_min, hour_max))

    plt.xticks(rotation=90, ha='center')
    label = ['lose', 'win']
    plt.legend(label, loc=(1, 0))

    ax.set_title(title, fontsize=24, fontproperties=myfont)
    ax.set_xlabel('date')
    ax.set_ylabel('hour')

    cf = plt.gcf()
    cf.set_size_inches(20, 20)

    plt.savefig(RES_PATH + '/images/' + title)
    plt.close()


w = [[], []]
l = [[], []]
for info in QuizHistory.select().where(
        (QuizHistory.room_id == '10086') & (QuizHistory.title == '7杀或者前7') & (QuizHistory.winner is not None)):
    t = info.begin_date
    # print(info.begin_date, info.winner)
    if info.winner == '可以':
        w[0].append(info.begin_date.date())
        w[1].append(t.hour + t.minute / 60.0)
    elif info.winner == '不可以':
        l[0].append(info.begin_date.date())
        l[1].append(t.hour + t.minute / 60.0)
draw_win_lose('东东吃鸡', w, l)


w = [[], []]
l = [[], []]
for info in QuizHistory.select().where(
        (QuizHistory.room_id == '575757') & (QuizHistory.title == '输赢') & (QuizHistory.winner is not None)):
    t = info.begin_date
    # print(info.begin_date, info.winner)
    if info.winner == '赢':
        w[0].append(info.begin_date.date())
        w[1].append(t.hour + t.minute / 60.0)
    elif info.winner == '输':
        l[0].append(info.begin_date.date())
        l[1].append(t.hour + t.minute / 60.0)
draw_win_lose('虎神输赢', w, l)


# from model import Danmu
# from settings import RES_PATH
# from word_cloud_util import get_b64_pic
# jieba.load_userdict(RES_PATH + "/user_dict.txt")
# cur_time = datetime.datetime.strptime('2018-10-11 17:58:14', '%Y-%m-%d %H:%M:%S')
# danmu_list = Danmu.get_recent_danmu(room_id='371037', time=cur_time)
# print('danmu num: {}'.format(len(danmu_list)))
# danmus = ' '.join(danmu_list)
# get_b64_pic(danmus)[1].show()
