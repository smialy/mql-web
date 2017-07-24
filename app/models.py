import aiopg
from mql.mql import Mql
from mql.common import ast
from mql.common.traverse import NodeTransformer
from mql.parser.parser import expression
from mql.engines import psql


class AclTransformer(NodeTransformer):
    def visit_SelectStatement(self, node):
        acl = expression('s_owner = 1 AND s_unixperms = 256 OR s_group = 1 AND s_unixperms = 32 OR s_unixperms = 4')
        if node.where:
            node.where = ast.LogicExpression(
                'and',
                acl,
                node.where
            )
        else:
            node.where = acl
        return node


async def create_engine(dsn):
    pool = await aiopg.create_pool(dsn)
    engine = psql.create_engine(pool)
    # engine.add_transformer(AclTransformer())
    schema = await engine.load_schema()
    return Mql(engine, schema)
    # data = await mql.execute('SELECT name FROM test WHERE id = 1')
