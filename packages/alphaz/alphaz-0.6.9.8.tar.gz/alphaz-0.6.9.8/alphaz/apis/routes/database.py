from ...utils.api import route, Parameter

from ...libs import logs_lib, flask_lib, database_lib

from ...models.main import AlphaException

from typing import List

from core import core

api = core.api
db = core.db
log = core.get_logger("api")


@route("/database/tables", admin=True)
def liste_tables():
    return database_lib.get_databases_tables_dict(core)


@route(
    "/database/create",
    admin=True,
    parameters=[
        Parameter("schema", required=True),
        Parameter("table", required=True),
        Parameter("drop", ptype=bool),
    ],
)
def create_table():
    return core.create_table(**api.get_parameters())


@route(
    "/database/drop",
    admin=True,
    parameters=[Parameter("schema", required=True), Parameter("table", required=True)],
)
def drop_table():
    dropped = core.drop_table(api.get("schema"), api.get("table"))
    if dropped:
        return "table %s dropped" % api.get("table")


@route(
    "/database/init",
    admin=True,
    parameters=[
        Parameter("binds", ptype=List[str]),
        Parameter("tables", ptype=List[str]),
        Parameter("drop", ptype=bool, default=False),
        Parameter("truncate", ptype=bool, default=False),
        Parameter("force", ptype=bool, default=False),
    ],
)
def init_all_database():
    database_lib.init_databases(core, **api.get_parameters())


@route("database/blocking", admin=True)
def get_blocking_queries():
    return core.db.get_blocked_queries()


@route(
    "/table",
    parameters=[
        Parameter("schema", ptype=str, default="ALPHA"),
        Parameter("tablename", ptype=str, required=True),
        Parameter("order_by", ptype=str),
        Parameter("direction", ptype=str),
        Parameter("page_index", ptype=int),
        Parameter("page_size", ptype=int),
        Parameter("limit", ptype=int),
    ],
    logged=True,
)
def get_transactions_history():
    return database_lib.get_table_content(**api.get_parameters())


@route(
    "/table/columns",
    parameters=[
        Parameter("schema", ptype=str, default="ALPHA"),
        Parameter("tablename", ptype=str, required=True),
    ],
)
def get_table_columns():
    return database_lib.get_table_columns(**api.get_parameters())


@route(
    "/table/model",
    parameters=[
        Parameter("schema", ptype=str, default="ALPHA"),
        Parameter("tablename", ptype=str, required=True),
    ],
)
def get_table_model():
    return database_lib.get_table_model(**api.get_parameters())
