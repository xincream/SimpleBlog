# !/usr/bin/env python3
# -*- coding: utf-8 -*-


# @author: xincream


from python_blog.www.util import log, create_pool
from python_blog.www.model import User
from python_blog.www.config import configs

import asyncio


async def test():
    await create_pool(loop, **configs['db_config'])

    # 测试count rows语句
    rows = await User.find_count('name')
    log('rows is: %s' % rows)

    # 测试insert into语句
    if rows < 2:
        for item in range(5):
            u = User(
                email='test%s@126.com' % item,
                passwd='123456',
                name='test%s' % item,
                image='/static/img/user.png',
            )
            rows = await User.find_count('name', where=['email'], args=[u.email])
            if rows == 0:
                await u.save()
            else:
                print('the email was already registered...')

    # 测试select语句
    users = await User.find_all(orderBy='created_at')
    for user in users:
        log('name: %s, password: %s' % (user.name, user.passwd))

    # 测试update语句
    user = users[1]
    user.email = 'test_update@126.com'
    user.name = 'test_update'
    await user.update()

    # 测试查找指定用户
    test_user = await User.find(user.id)
    log('name: %s, email: %s' % (test_user.name, test_user.email))

    # 测试delete语句
    users = await User.find_all(orderBy='created_at', limit=(1, 2))
    for user in users:
        log('delete user: %s' % user.name)
        await user.remove()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
