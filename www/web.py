# !/usr/bin/env python3
# -*- coding: utf-8 -*-


# @author: xincream


import asyncio
import os
import inspect
import functools
from python_blog.www.util import log
from urllib import parse
from aiohttp import web


def get(path):
    """
    decorator @get('/path')
    :param path: 
    :return: 
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper
    return decorator


def post(path):
    """
    decorator @post('/path')
    :param path: 
    :return: 
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper
    return decorator


class RequestHandler(object):
    """
    处理请求
    """
    def __init__(self, app, fn):
        self._app = app
        self._func = fn

    async def __call__(self, request):
        kw = {}  # 获得参数
        r = await self._func(**kw)
        return r


def add_static(app):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.router.add_static('/static/', path)
    log('add static %s => %s' % ('/static/', path))


def add_route(app, fn):
    """
    注册一个url处理函数
    :param app: 
    :param fn: 
    :return: 
    """
    method = getattr(fn, '__method__', None)  # get or post
    path = getattr(fn, '__route__', None)
    print(method, path)
    if not (method and path):
        raise ValueError('@get or @post not defined in %s.' % str(fn))
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine(fn)
    log('add route %s %s => %s(%s)' % (method, path, fn.__name__,
                                       ', '.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method, path, RequestHandler(app, fn))


def add_routes(app, module_name):
    """
    自动把模块的所有符合条件的函数注册了:
    :param app: 
    :param module_name: 
    :return: 
    """
    n = module_name.rfind('.')
    print(n)
    if n == -1:
        mod = __import__(module_name, globals(), locals())
        print(mod)
    else:
        name = module_name[n+1:]
        mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)
    for attr in dir(mod):
        print(attr)
        if attr.startswith('_'):
            continue
        fn = getattr(mod, attr)

        if callable(fn):
            method = getattr(fn, '__method__', None)
            path = getattr(fn, '__route__', None)
            print(method)
            if method and path:
                # add_route(app, fn)
                print(fn.__name__)




@get('/test/{id}')
def get_test(id):
    print('test')


if __name__ == '__main__':
    app_test = web.Application()
    add_route(app_test, get_test)

