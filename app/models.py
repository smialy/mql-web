import aiopg
from mql.mql import Mql
from mql.common import ast
from mql.common.traverse import NodeTransformer
from mql.parser.parser import expression
from mql.engines import psql


class AclTransformer(NodeTransformer):
    def visit_SelectStatement(self, node):
        acl = expression('s_owner = 1 AND s_unixperms = 256 OR s_group = 1 AND s_unixperms = 32 OR s_unixperms & 4 = 4')
        if node.where:
            node.where.condition = ast.LogicExpression(
                'and',
                acl,
                node.where.condition
            )
        else:
            node.where = ast.SelectWhere(acl)

        if node.results[0].is_wildcard():
            node.results = [ast.SelectIdentifier("")]
        else:
            node.results = [item for item in node.results if not item.name.startswith('_')]

        return node


class LimitTransformer(NodeTransformer):
    def visit_SelectStatement(self, node):
        if not node.limit:
            node.limit = ast.SelectLimit(100)
        return node


async def create_engine(dsn):
    pool = await aiopg.create_pool(dsn)
    engine = psql.create_engine(pool)

    engine.add_transformer(AclTransformer())
    engine.add_transformer(LimitTransformer())

    schema = await engine.load_schema()
    return Mql(engine, schema)
    # data = await mql.execute('SELECT name FROM test WHERE id = 1')
