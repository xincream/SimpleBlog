# !/usr/bin/env python3
# -*- coding: utf-8 -*-


# @author: xincream
from python_blog.www.util import log
from aiohttp import web
import json

async def logger_factory(app, handler):
    """
    middleware是一种拦截器，一个URL在被某个函数处理前，可以经过一系列的middleware的处理
    把通用的功能从每个URL处理函数中拿出来，集中放到一个地方
    :param app: 
    :param handler: 
    :return: 处理请求的函数
    """
    print('inside logger_factory')
    async def logger(request):
        # 记录日志
        log('Request: %s %s' % (request.method, request.path))
        # 继续处理请求
        return await handler(request)
    return logger


async def response_factory(app, handler):
    """
    把返回值转换为web.Response对象再返回
    :param app: 
    :param handler: 
    :return: 
    """
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
    """
    middleware是一种拦截器，一个URL在被某个函数处理前，可以经过一系列的middleware的处理
    :param app: 
    :param handler: 
    :return: 
    """
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