# !/usr/bin/env python3
# -*- coding: utf-8 -*-


# @author: xincream

from python_blog.www.util import log
from python_blog.www.error import *

import asyncio
import os
import inspect
import functools
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


# RequestHandler目的就是从URL函数中分析其需要接收的参数，从request中获取必要的参数，
# URL函数不一定是一个coroutine，因此我们用RequestHandler()来封装一个URL处理函数。
# 调用URL函数，然后把结果转换为web.Response对象，这样，就完全符合aiohttp框架的要求：
class RequestHandler(object):
    """
    处理请求,统一标准化接口,构成标准的app.router.add_route第三个参数
    RequestHandler把任何参数都变成self._func(**kw)的形式(获取不同的函数的对应的参数)
    """
    def __init__(self, fn):
        self._func = asyncio.coroutine(fn)

    async def __call__(self, request):
        """
        定义__call__()方法，使得可以直接对实例进行调用
        :param request: 
        :return: 
        """
        log('RequestHandler.__call__ ...')
        args = inspect.signature(self._func).parameters  # 函数的参数表
        log('args: %s' % args)
        # 获取从GET或POST传进来的参数值，如果函数参数表有这参数名就加入
        kw = {arg: value for arg, value in request.__data__.items() if arg in args}
        # 获取match_info的参数值，例如@get('/blog/{id}')之类的参数值
        kw.update(request.match_info)
        # 如果有request参数的话也加入
        if 'request' in args:
            kw['request'] = request
            # 检查参数表中有没参数缺失
        for key, arg in args.items():
                # request参数不能为可变长参数
            if key == 'request' and arg.kind in (arg.VAR_POSITIONAL, arg.VAR_KEYWORD):
                return web.HTTPBadRequest(text='request parameter cannot be the var argument.')
                # 如果参数类型不是变长列表和变长字典，变长参数是可缺省的
            if arg.kind not in (arg.VAR_POSITIONAL, arg.VAR_KEYWORD):
                    # 如果还是没有默认值，而且还没有传值的话就报错
                if arg.default == arg.empty and arg.name not in kw:
                    return web.HTTPBadRequest(text='Missing argument: %s' % arg.name)

        log('call with args: %s' % kw)
        try:
            return await self._func(**kw)
        except APIError as e:
            return dict(error=e.error, data=e.data, message=e.message)


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


