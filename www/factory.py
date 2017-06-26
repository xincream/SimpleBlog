# !/usr/bin/env python3
# -*- coding: utf-8 -*-


# @author: xincream
from python_blog.www.util import log
from python_blog.www.model import User
from python_blog.www.config import configs

from aiohttp import web
import json
from urllib import parse


async def logger_factory(app, handler):
    """
    middleware是一种拦截器，一个URL在被某个函数处理前，可以经过一系列的middleware的处理
    把通用的功能从每个URL处理函数中拿出来，集中放到一个地方
    :param app: 
    :param handler: 
    :return: 处理请求的函数
    """
    async def logger(request):
        """
        响应之前打印日志
        :param request: 
        :return: 
        """
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
    async def response(request):
        log('inside response_factory..., request: %s' % request)
        result = await handler(request)
        print(result)
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
                # result['__user__'] = request.__user__
                resp = web.Response(body=app['__templating__'].
                                    get_template(template).render(**result).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
        if isinstance(result, int) and 100 <= result < 600:
            return web.Response(body=result)
        if isinstance(result, tuple) and len(result) == 2:
            t, m = result
            if isinstance(t, int) and 100 <= t < 600:
                return web.Response(status=t, text=str(m))
        # default:
        resp = web.Response(body=str(result).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'
        return resp
    return response


async def data_factory(app, handler):
    """
    middleware是一种拦截器，一个URL在被某个函数处理前，可以经过一系列的middleware的处理
    将参数绑定在request.__data__
    :param app: 
    :param handler: 
    :return: 
    """
    async def parse_data(request):
        log('inside data_factory..., request: %s' % request)
        if request.method in ('POST', 'PUT'):
            if not request.content_type:
                return web.HTTPBadRequest(text='Missing Content-Type.')
            content_type = request.content_type.lower()
            if content_type.startswith('application/json'):
                request.__data__ = await request.json()
                if not isinstance(request.__data__, dict):
                    return web.HTTPBadRequest(text='JSON body must be object.')
                log('request json: %s' % str(request.__data__))
            elif content_type.startswith(('application/x-www-form-urlencoded', 'multipart/form-data')):
                params = await request.post()
                request.__data__ = dict(**params)
                log('request form: %s' % str(request.__data__))
            else:
                return web.HTTPBadRequest(text='Unsupported Content-Type: %s' % content_type)
        elif request.method == 'GET':
            qs = request.query_string
            request.__data__ = {k: v[0] for k, v in parse.parse_qs(qs, True).items()}
            log('request query: %s' % request.__data__)
        else:
            request.__data__ = dict()
        return await handler(request)
    return parse_data


async def auth_factory(app, handler):
    """
    通过cookie找到当前用户信息，把用户绑定在request.__user__
    :param app: 
    :param handler: 
    :return: 
    """
    async def auth(request):
        log('check user: %s %s' % (request.method, request.path))
        cookie = request.cookies.get(configs['COOKIE_NAME'])
        request.__user__ = await User.find_by_cookie(cookie)
        if request.__user__ is not None:
            log('set current user: %s' % request.__user__.email)
        return await handler(request)
    return auth
