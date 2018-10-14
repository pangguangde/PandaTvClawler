# -*- coding: utf-8 -*-
# @Author  : pangguangde
# @File    : word_cloud_util.py
# @Time    : 2018/9/11 下午5:56
# @Desc    :
import base64
import datetime
import io
import re
import sys
from abc import ABC

import jieba
from wordcloud import WordCloud
from wordcloud.tokenization import unigrams_and_bigrams, process_tokens

from model import Danmu
from settings import RES_PATH
from utils.common_util import get_common_logger

logger = get_common_logger('word_cloud')
jieba.load_userdict(RES_PATH + "/user_dict.txt")


class MyWordCloud(WordCloud):

    def to_html(self):
        pass

    def process_text(self, text):
        """Splits a long text into words, eliminates the stopwords.

        Parameters
        ----------
        text : string
            The text to be processed.

        Returns
        -------
        words : dict (string, int)
            Word tokens with associated frequency.

        ..versionchanged:: 1.2.2
            Changed return type from list of tuples to dict.

        Notes
        -----
        There are better ways to do word tokenization, but I don't want to
        include all those things.
        """

        stopwords = set([i.lower() for i in self.stopwords])

        flags = (re.UNICODE if sys.version < '3' and type(text) is unicode  # noqa: F821
                 else 0)
        regexp = self.regexp if self.regexp is not None else r"\w[\w']+|\?+"

        words = re.findall(regexp, text, flags)
        # remove stopwords
        words = [word for word in words if word.lower() not in stopwords]
        # remove 's
        words = [word[:-2] if word.lower().endswith("'s") else word
                 for word in words]

        if self.collocations:
            word_counts = unigrams_and_bigrams(words, self.normalize_plurals)
        else:
            word_counts, _ = process_tokens(words, self.normalize_plurals)

        return word_counts


def get_b64_pic(text):
    text = text.replace('?', '荩').replace('？', '绛')
    logger.info('cutting words...')
    word_spilt_jieba = jieba.cut(text, cut_all=False)
    word_space = '|'.join(word_spilt_jieba)
    word_space = word_space.replace('荩', '?').replace('绛', '？')

    logger.info('generating word cloud...')
    wordcloud = MyWordCloud(
        background_color='white',
        max_words=200,
        max_font_size=220,
        random_state=100,
        width=1300,
        height=700,
        ranks_only=True,
        colormap='Dark2_r',
        font_path=RES_PATH + "/PingFang.ttc"
    ).generate(word_space)
    img = wordcloud.to_image()

    buffered = io.BytesIO()
    img.convert('RGB').save(buffered, format='PNG')
    logger.info('done')
    return base64.b64encode(buffered.getvalue())
    # img.save('/Users/pangguangde/Downloads/test1.jpg', quality=100)


if __name__ == '__main__':
    logger.info('querying danmu...')
    text_from_file = ' '.join(Danmu.get_recent_danmu(time=datetime.datetime(2018, 9, 10, 20)))
    get_b64_pic(text_from_file)
