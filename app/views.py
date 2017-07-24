from aiohttp.hdrs import METH_POST
from aiohttp.web import json_response
from aiohttp.web_exceptions import HTTPFound
from aiohttp_jinja2 import template



@template('index.jinja')
async def index(request):
    return {
        'title': request.app['name'],
        'intro': "Success! you've setup a basic aiohttp app.",
    }


async def query(request):
    mql = request.app['mql']
    data = await mql.execute('SELECT id, name FROM test')
    return json_response(data)
