# !/usr/bin/env python3
# -*- coding: utf-8 -*-


# @author: xincream


# url handlers


from python_blog.www.web import get


# 测试
@get('/about')
async def about():
    return {
        '__template__': 'about.html'
    }

