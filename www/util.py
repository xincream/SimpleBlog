# !/usr/bin/env python3
# -*- coding: utf-8 -*-


# @author: xincream


import logging
import aiomysql


logging.basicConfig(level=logging.INFO)
pool = None

async def create_pool(loop_str, **kw):
    log('create database connection pool...')
    global pool
    pool = await aiomysql.create_pool(
        host=kw.get('host', 'localhost'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),  # 默认自动提交事务
        maxsize=kw.get('maxsize', 15),
        minsize=kw.get('minsize', 1),
        loop=loop_str  # 传递消息循环对象loop，用于异步执行
    )
    print(pool)


async def select(sql, args, size=None):
    """
    select
    :param sql: 
    :param args: 
    :param size: 
    :return: 
    """
    log('SQL: %s' % sql)
    async with pool.get() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql.replace('?', '%s'), args or ())
            if size:
                rs = await cur.fetchmany(size)
            else:
                rs = await cur.fetchall()
        log('rows returned %s' % len(rs))
        return rs


async def execute(sql, args, autocommit=True):
    """
    insert,update,delete
    :param sql: 
    :param args: 
    :param autocommit: 
    :return: 
    """
    log('SQL: %s' % sql)
    async with pool.get() as conn:
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                print(sql.replace('?', '%s'), tuple(args))
                await cur.execute(sql.replace('?', '%s'), args)
                affected = cur.rowcount
            if not autocommit:
                await conn.commit()
        except BaseException as e:
            if not autocommit:
                await conn.rollback()
            raise
        return affected


def log(strng):
    logging.info(strng)


def debug(strng):
    logging.debug(strng)


def warn(strng):
    logging.warning(strng)


def exception(strng):
    logging.exception(strng)


def create_args_string(num):
    l = ['?'] * num
    return ', '.join(l)
