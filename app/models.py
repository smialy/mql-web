import aiopg
import asyncpg

from mql.mql import Mql
from mql.common import ast
from mql.common.traverse import NodeTransformer
from mql.common.source import Source
from mql.execution import psql


class LimitTransformer(NodeTransformer):
    def visit_SelectStatement(self, node):
        if not node.limit:
            node.limit = ast.SelectLimit(100)
        return node


async def create_engine(dsn, db_name='cube'):
    pool = await aiopg.create_pool(dsn)
    connection = psql.AiopgConnection(pool)

    # import json
    # pool = await asyncpg.create_pool(dsn)
    # async with pool.acquire() as connection:
    #     await connection.set_type_codec(
    #             'json',
    #             encoder=json.dumps,
    #             decoder=json.loads,
    #             schema='pg_catalog'
    #         )
    # connection = psql.AsyncpgConnection(pool)

    engine = psql.PgsqlEngine(connection)
    schema = await engine.load_schema(db_name)
    # source = None
    # print(schema.serialize())
    source = Source(db_name, engine, schema)
    # executor = Executor(db_name, engine)
    mql = Mql(
        default_source=db_name,
        sources=[source]
    )

    mql.add_transformer(LimitTransformer())
    return mql


