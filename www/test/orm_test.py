# !/usr/bin/env python3
# -*- coding: utf-8 -*-


# @author: xincream


from python_blog.www.util import log, create_pool
from python_blog.www.model import User, next_id
from python_blog.www.config import configs

import asyncio


async def test():
    await create_pool(loop, **configs['db_config'])

    # 测试find_count
    rows = await User.find_count('name')
    log('rows is: %s' % rows)

    # 测试save
    if rows < 5:
        for item in range(5):
            u = User(
                id=next_id(),
                email='test%s@126.com' % item,
                passwd='123456',
                name='test%s' % item,
                image='/static/img/user.png',
            )
            rows = await User.find_count('name', where=['email'], args=[u.email])
            print(rows)
            if rows == 0:
                await u.save()
                print('name %s was inserted...' % u.name)
            else:
                print('the email was already registered...')

    # 测试find_all
    users = await User.find_all(orderBy='created_at')
    for user in users:
        log('name: %s, password: %s' % (user.name, user.passwd))

    # 测试update
    user = users[1]
    user.email = 'test_update@126.com'
    user.name = 'test_update'
    await user.update()

    # 测试find
    test_user = await User.find(user.id)
    log('name: %s, email: %s' % (test_user.name, test_user.email))

    # 测试delete
    users = await User.find_all(orderBy='created_at', limit=(1, 2))
    for user in users:
        log('delete user: %s' % user.name)
        await user.remove()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())

