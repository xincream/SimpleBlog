# !/usr/bin/env python3
# -*- coding: utf-8 -*-


# @author: xincream


import asyncio
import os
import inspect
import functools
from python_blog.www.util import log
from aiohttp import web


# 生成GET、POST等请求方法的装饰器
def request(path, *, method):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = method
        wrapper.__route__ = path
        return wrapper
    return decorator

get = functools.partial(request, method='GET')
post = functools.partial(request, method='POST')
put = functools.partial(request, method='PUT')
delete = functools.partial(request, method='DELETE')


def get_required_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY and \
                        param.default == inspect.Parameter.empty:
            args.append(name)
        return tuple(args)


def get_named_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)


def has_named_kw_args(fn):
    params = inspect.signature(fn).parameters
    for param in params.values():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True


def has_var_kw_args(fn):
    params = inspect.signature(fn).parameters
    for param in params.values():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True


def has_request_arg(fn):
    sig = inspect.signature(fn)
    pass


# RequestHandler目的就是从URL函数中分析其需要接收的参数，从request中获取必要的参数，
# URL函数不一定是一个coroutine，因此我们用RequestHandler()来封装一个URL处理函数。
# 调用URL函数，然后把结果转换为web.Response对象，这样，就完全符合aiohttp框架的要求：
class RequestHandler(object):
    """
    处理请求
    """
    def __init__(self, fn):
        self._func = asyncio.async(fn)

    async def __call__(self, request):
        kw = {}  # 获得参数
        r = await self._func(**kw)
        return r


def add_static(app):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.router.add_static('/static/', path)
    log('add static %s => %s' % ('/static/', path))


def add_routes(app, module_name):
    """
    自动把模块的所有符合条件的函数注册了:
    :param app: 
    :param module_name: 
    :return: 
    """
    try:
        mod = __import__(module_name, fromlist=['get_submodule'])
    except ImportError as e:
        raise e
    # 遍历mod的方法和属性,主要是找处理方法
    # 定义的处理方法，被@get或@post修饰过，所以方法里会有'__method__'和'__route__'属性
    for attr in dir(mod):
        print(attr)
        if attr.startswith('_'):  # 定义的处理方法不是以'_'开头的
            continue
        fn = getattr(mod, attr)
        if callable(fn) and hasattr(fn, '__method__') and hasattr(fn, '__route__'):
            args = ', '.join(inspect.signature(fn).parameters.keys())
            log('add route %s %s => %s(%s)' % (fn.__method__, fn.__route__, fn.__name__, args))
            app.router.add_route(fn.__method__, fn.__route__, RequestHandler(fn))


@get('/test/{id}')
def get_test(id):
    print('test')


if __name__ == '__main__':
    app_test = web.Application()
    add_routes(app_test, 'web')

