# !/usr/bin/env python3
# -*- coding: utf-8 -*-


# @author: xincream

from python_blog.www.util import log

import time
from datetime import datetime


def datetime_filter(t):
    """
    存储的格式是timestamp
    :param t: 
    :return: 
    """
    log('inside datetime filters...')
    delta = int(time.time() - t)
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta // 60)
    if delta < 86400:
        return u'%s小时前' % (delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)

