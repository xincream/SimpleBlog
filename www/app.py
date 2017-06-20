import logging
import asyncio, os, json, time
from datetime import datetime
from aiohttp import web


logging.basicConfig(level=logging.INFO)


def index(request):
    return web.Response(body=b'<h1>Start From Here</h1>', content_type='text/html')


# @asyncio.coroutine  # async 替代 @asyncio.coroutine装饰器,代表这个是要异步运行的函数
async def init(loop_str):
    app = web.Application(loop=loop_str)
    app.router.add_route('GET', '/', index)
    # srv = yield from loop_str.create_server(app.make_handler(), '127.0.0.1', 9000)
    # await 代替yield from ,表示要放入asyncio.get_event_loop中进行的异步操作
    srv = await loop_str.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return srv


if __name__ == '__main__':
    loop = asyncio.get_event_loop()  # 创建asyncio event loop
    loop.run_until_complete(init(loop))  # 用asyncio event loop 来异步运行init()
    loop.run_forever()
