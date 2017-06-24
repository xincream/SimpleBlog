# !/usr/bin/env python3
# -*- coding: utf-8 -*-


# @author: xincream


import asyncio


from python_blog.www.model import User
from python_blog.www.util import create_pool


async def test1(loop_str):
    db_str = {'user': 'root', 'password': '666666', 'db': 'blog'}
    await create_pool(loop_str, **db_str)  # 用asyncio event loop 来异步运行init()
    user = User(id=1, name='xincream')
    return await user.save()


async def test2(loop_str):
    await create_pool(loop_str, user='root', password='666666', db='blog')
    u = User(name='Test1', email='test1@example.com', passwd='1234567890', image='about:blank')
    print(u.get_value_or_default('id'))
    await u.save()
    await u.remove()


if __name__ == '__main__':
    print('test...')
    # 获取EventLoop:
    loop = asyncio.get_event_loop()
    # 执行coroutine
    loop.run_until_complete(test2(loop))
    loop.close()

