# !/usr/bin/env python3
# -*- coding: utf-8 -*-


# @author: xincream

from python_blog.www.config import configs
from python_blog.www.model import User, Comment, Blog, next_id
from python_blog.www.error import APIPermissionError
from python_blog.www.util import log, exception
from python_blog.www.config import configs

import time
import hashlib


def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()


def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p


def user2cookie(user, max_age):
    """
    Generate cookie str by user.
    """
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, configs['COOKIE_KEY'])
    return '-'.join([user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()])


def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').
                replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)


async def cookie2user(cookie_str):
    """
    Parse cookie and load user if cookie is valid.
    """
    if not cookie_str:
        return None
    try:
        l = cookie_str.split('-')
        if len(l) != 3:
            return None
        uid, expires, sha1 = l
        if int(expires) < time.time():
            return None
        user = await User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, configs['COOKIE_KEY'])
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            log('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        exception(e)
        return None


def verify_password(password):
    """
    # 验证用户密码是否正确
    :param password: 
    :return: 
    """
    sha1 = hashlib.sha1()
    sha1.update(id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(password.encode('utf-8'))
    return password == sha1.hexdigest()



