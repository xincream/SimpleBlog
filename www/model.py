# !/usr/bin/env python3
# -*- coding: utf-8 -*-


# @author: xincream


from python_blog.www.orm import Model
from python_blog.www.field import StringField, IntegerField, BooleanField, FloatField, TextField
from python_blog.www.config import configs
from python_blog.www.util import log, exception

import time
import uuid
import re
import hashlib


def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


class User(Model):
    """
    用户
    """
    __table__ = 'users'

    id = StringField(primary_key=True, default=next_id(), ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    admin = BooleanField()
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(500)')
    created_at = FloatField(default=time.time())

    def to_json(self, **kw):
        json_user = self.copy()
        json_user['passwd'] = '******'
        if kw.get('encrypted'):
            json_user['email'] = re.sub('.@.+?\.', '***@xxx.', json_user['email'])
        return json_user

    async def save(self):
        self.id = next_id()
        sha1_pw = '%s:%s' % (self.id, self.passwd)
        self.passwd = hashlib.sha1(sha1_pw.encode('utf-8')).hexdigest()
        await super().save()

    # 用户登陆，返回一个已登陆的响应
    def signin(self, response, max_age=86400):
        expires = str(int(time.time() + max_age))
        s = '%s-%s-%s-%s' % (self.id, self.password, expires, configs['COOKIE_KEY'])
        cookie = '-'.join((self.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()))
        response.set_cookie(configs['COOKIE_NAME'], cookie, max_age=max_age, httponly=True)
        return response

    # 用户注销，返回一个已注销的响应
    @classmethod
    def signout(cls, response):
        response.set_cookie(configs['COOKIE_NAME'], '-deleted-', max_age=0, httponly=True)
        return response

    @classmethod
    async def find_by_cookie(cls, cookie_str):
        if not cookie_str:
            return None
        try:
            l = cookie_str.split('-')
            if len(l) != 3:
                return None
            uid, expires, sha1 = l
            if int(expires) < time.time():
                return None
            user = await cls.find(uid)
            if not user:
                return None
            s = '%s-%s-%s-%s' % (uid, user.get('password'), expires, configs['COOKIE_KEY'])
            if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
                log('invalid sha1')
                return None
            user.password = '******'
            return user
        except Exception as e:
            exception(e)
            return None


class Blog(Model):
    """
    博客
    """
    __table__ = 'blogs'

    id = StringField(primary_key=True, default=next_id(), ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    name = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time())


class Comment(Model):
    """
    评论
    """
    __table__ = 'comments'

    id = StringField(primary_key=True, default=next_id(), ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time())


if __name__ == '__main__':
    a = next_id()
    print(a)
    print(time.time())




