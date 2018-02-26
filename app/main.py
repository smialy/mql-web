from pathlib import Path

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_jinja2 import APP_KEY as JINJA2_APP_KEY

from .settings import Settings
from . import views
from .models import create_engine

THIS_DIR = Path(__file__).parent
BASE_DIR = THIS_DIR.parent


@jinja2.contextfilter
def reverse_url(context, name, **parts):
    """
      {{ 'the-view-name'|url }} might become "/path/to/view"
      {{ 'item-details'|url(id=123, query={'active': 'true'}) }} might become "/items/1?active=true
    """
    app = context['app']

    kwargs = {}
    if 'query' in parts:
        kwargs['query'] = parts.pop('query')
    if parts:
        kwargs['parts'] = parts
    return app.router[name].url(**kwargs)


@jinja2.contextfilter
def static_url(context, static_file_path):
    '''
      {{ 'styles.css'|static }} might become "http://mycdn.example.com/styles.css"

    '''
    app = context['app']
    try:
        static_url = app['static_root_url']
    except KeyError:
        raise RuntimeError('app does not define a static root url "static_root_url"')
    return '{}/{}'.format(static_url.rstrip('/'), static_file_path.lstrip('/'))




async def startup(app: web.Application):
    # app['pg_engine'] = await create_engine(pg_dsn(app['settings']), loop=app.loop)
    dsn = 'postgresql://cube:cube123@localhost/cube'
    app['mql'] = await create_engine(dsn)


async def cleanup(app: web.Application):
    pass
    # app['pg_engine'].close()
    # await app['pg_engine'].wait_closed()


def setup_routes(app):
    app.router.add_get('/', views.index, name='index')
    app.router.add_route('*', '/query', views.QueryView, name='query')


def create_app(loop):
    app = web.Application()
    settings = Settings()
    app.update(
        name='aio',
        settings=settings
    )

    jinja2_loader = jinja2.FileSystemLoader(str(THIS_DIR / 'templates'))
    aiohttp_jinja2.setup(app, loader=jinja2_loader, app_key=JINJA2_APP_KEY)
    app[JINJA2_APP_KEY].filters.update(
        url=reverse_url,
        static=static_url,
    )

    app.on_startup.append(startup)
    app.on_cleanup.append(cleanup)

    setup_routes(app)
    return app
