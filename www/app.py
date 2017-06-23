# !/usr/bin/env python3
# -*- coding: utf-8 -*-


from python_blog.www.util import *
from python_blog.www.config import *
from python_blog.www.web import add_routes

import asyncio
import os
import json
import time
from datetime import datetime
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
    # add_static(app)
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


def datetime_filter(t):
    """
    存储的格式是timestamp
    :param t: 
    :return: 
    """
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


async def logger_factory(app, handler):
    print('inside logger_factory')
    async def logger(request):
        # 记录日志
        log('Request: %s %s' % (request.method, request.path))
        # 继续处理请求
        return await handler(request)
    return logger


async def response_factory(app, handler):
    print('inside response_factory')
    async def response(request):
        result = await handler(request)
        if isinstance(result, web.StreamResponse):
            return result
        if isinstance(result, bytes):
            resp = web.Response(body=result)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(result, str):
            if result.startswith('redirect:'):
                return web.HTTPFound(result[9:])
            resp = web.Response(body=result.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(result, dict):
            template = result.get('__template__')
            if template is None:
                resp = web.Response(
                    body=json.dumps(result, ensure_ascii=False,
                                    default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                return resp
            else:
                resp = web.Response(body=app['__templating__'].
                                    get_template(template).render(**result).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
        if isinstance(result, int) and 100 <= result < 600:
            return web.Response(body=result)
        if isinstance(result, tuple) and len(result) == 2:
            t, m = result
            if isinstance(t, int) and 100 <= t < 600:
                return web.Response(t, str(m))  # ???
        # default:
        resp = web.Response(body=str(result).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'
        return resp
    return response


async def data_factory(app, handler):
    print('inside data_factory')
    async def parse_data(request):
        if request.method == 'POST':
            if request.content_type.startswith('application/json'):
                request.__data__ = await request.json()
                log('request json: %s' % str(request.__data__))
            elif request.content_type.startswith('application/x-www-form-urlencoded'):
                request.__data__ = await request.post()
                log('request form: %s' % str(request.__data__))
        return await handler(request)
    return parse_data


if __name__ == '__main__':
    loop = asyncio.get_event_loop()  # 创建asyncio event loop
    loop.run_until_complete(init(loop))  # 用asyncio event loop 来异步运行init()
    loop.run_forever()
    # print(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
    # print(__file__)

