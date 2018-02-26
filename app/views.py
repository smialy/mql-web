import json
from aiohttp.hdrs import METH_POST
from aiohttp.web import json_response, Response, View
from aiohttp.web_exceptions import HTTPFound, HTTPBadRequest
from aiohttp_jinja2 import template

from mql.common.errors import format_error as mql_format_error


async def index(request):
    return HTTPFound('/query')


class QueryView(View):

    @template('index.jinja')
    async def get(self):
        pass

    async def post(self):
        mql = self.request.app['mql']
        data = await parse_body(self.request)
        if not data:
            raise HTTPBadRequest()

        query = data['query']
        params = data['params']
        result = await mql.execute(query, params)
        return encode_result(result)


async def parse_body(request):
    content_type = request.content_type
    if content_type == 'application/json':
        return await request.json()
    elif content_type in ('application/x-www-form-urlencoded', 'multipart/form-data'):
        return await request.multipart()


def format_error(error):
    formatted_error = {
        'message': mql_format_error(error, short=False),
    }
    if hasattr(error, 'position') and error.position is not None:
        formatted_error['position'] = error.position

    return formatted_error


def format_result(result):
    response = {}
    if result.errors:
        response['errors'] = [format_error(e) for e in result.errors]
    else:
        if result.encoded:
            return True, '{{"data":{}}}'.format(result.data)
        response['data'] = result.data
    return False, response


def encode_result(result, encode=json_response):
    encoded, response = format_result(result)
    if encoded:
        return Response(text=response, content_type='application/json')
    return encode(response)