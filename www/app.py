# !/usr/bin/env python3
# -*- coding: utf-8 -*-


from python_blog.www.util import *
from python_blog.www.config import *
from python_blog.www.web import add_routes, add_static
from python_blog.www.factory import logger_factory, response_factory
from python_blog.www.filter import datetime_filter

import asyncio
import os
from aiohttp import web
from jinja2 import Environment, FileSystemLoader


# @author: xincream


def index(request):
    log(request)
    return web.Response(body=b'<h1>Start From Here</h1>', content_type='text/html')


# @asyncio.coroutine  # async 替代 @asyncio.coroutine装饰器,代表这个是要异步运行的函数
async def init(loop_str):
    await create_pool(loop_str, **configs['db_config'])
    app = web.Application(loop=loop_str, middlewares=[logger_factory, response_factory])
    init_jinja2(app, filters=dict(datetime=datetime_filter))
    app.router.add_route('GET', '/', index)
    add_routes(app, 'handlers')    # 把handlers模块的所有符合条件的函数注册了
    add_static(app)
    # srv = yield from loop_str.create_server(app.make_handler(), '127.0.0.1', 9000)
    # await 代替yield from ,表示要放入asyncio.get_event_loop中进行的异步操作
    srv = await loop_str.create_server(app.make_handler(), '127.0.0.1', 9000)
    log('server started at http://127.0.0.1:9000...')
    return srv


def init_jinja2(app, **kw):
    """
    Jinja2 内部使用 Unicode 
    :param app: 
    :param kw: 
    :return: 
    """
    log('init jinja2...')
    options = dict(
        autoescape=kw.get('autoescape', True),
        block_start_string=kw.get('block_start_string', '{%'),
        block_end_string=kw.get('block_end_string', '%}'),
        variable_start_string=kw.get('variable_start_string', '{{'),
        variable_end_string=kw.get('variable_end_string', '}}'),
        auto_reload=kw.get('auto_reload', True)
    )
    path = kw.get('path', None)
    if not path:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    log('set jinja2 template path: %s' % path)
    # 创建一个 Environment 对象，并用它加载模板
    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kw.get('filters', None)
    if filters:
        print('inside filters...',  filters.items())
        for k, v in filters.items():
            env.filters[k] = v    # 添加filter
    app['__templating__'] = env


if __name__ == '__main__':
    loop = asyncio.get_event_loop()  # 创建asyncio event loop
    loop.run_until_complete(init(loop))  # 用asyncio event loop 来异步运行init()
    loop.run_forever()
    # print(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
    # print(__file__)

