import datetime, glob, os, importlib, re
from typing import Dict, List

from sqlalchemy import MetaData

from . import flask_lib, io_lib

from ..models.main import AlphaException

"""
try:
    from core import core 
except:
    from .. import core
    
LOG = core.get_logger("database")"""


def convert_value(value):
    if type(value) == str and len(value) > 7 and value[4] == "/" and value[7] == "/":
        return datetime.datetime.strptime(value, "%Y/%m/%d")
    if value == "now()":
        return datetime.datetime.now()
    return value


def init_databases(
    core,
    tables: List[str] | Dict[str, str] = None,
    binds: List[str] = None,
    drop: bool = False,
    truncate: bool = False,
    sqlite: bool = True,
    force: bool = True,
):
    if core.configuration != "local" and not force:
        if core.log:
            core.log.error("Configuration must be <local>")
        return

    tables = (
        (
            {x.upper(): None for x in tables}
            if type(tables) == list
            else {x.upper(): y for x, y in tables.items()}
        )
        if tables is not None
        else None
    )

    core.prepare_api(core.configuration)
    core.load_models_sources()

    binds = (
        [bind.upper() for bind in binds]
        if binds is not None
        else list(flask_lib.TABLES.keys())
    )

    if binds is not None:
        for bind in binds:
            is_database_names_in_lib = any(
                [x for x in flask_lib.TABLES if x.upper() == bind]
            )
            if not is_database_names_in_lib:
                raise AlphaException(f"Cannot find {bind=}")

    tables_models, tables_binds = {}, {}
    if tables is not None:
        if binds is None:
            binds = list(flask_lib.TABLES.keys())
        for bind in binds:
            for c_table, m_table in flask_lib.TABLES[bind.upper()].items():
                for table_name, table_bind in tables.items():
                    if c_table.upper() == table_name.upper() and (
                        table_bind.upper() == bind.upper()
                        if table_bind is not None
                        else True
                    ):
                        tables_models[table_name.upper()] = m_table
                        tables_binds[table_name.upper()] = bind

        if len(tables_models) != len(tables):
            raise AlphaException(
                f"Cannot find tables {','.join(list(set(tables_models.keys()) - set(tables.keys())))}"
            )
        binds = list(tables_binds.values())

    init_databases_config = core.config.get("databases")
    if init_databases_config is None:
        raise AlphaException(
            "No initialisation configuration has been set in <databases> entry"
        )
    init_databases_config = {x.upper(): y for x, y in init_databases_config.items()}

    if tables is None or len(tables) == 0:
        core.database_create_all(binds, drop=drop, sqlite=sqlite)
    else:
        for table, table_model in tables_models.items():
            bind = tables_binds[table]
            engine = core.db.get_engine(bind=bind)
            if drop:
                try:
                    table_model.__table__.drop(engine)
                    if core.log:
                        core.log.info(f"Dropped {table=} on {bind=}")
                except Exception as ex:
                    if not "Table ou vue inexistante" in str(ex):
                        core.log.error(f"Cannot drop {table=} for {bind=}", ex=ex)
            if truncate:
                core.db.truncate(table_model)

            try:
                table_model.__table__.create(engine)
                if core.log:
                    core.log.info(f"Created {table=} on {bind=}")
            except Exception as ex:
                if core.log:
                    core.log.error(f"Cannot create {table=} for {bind=}", ex=ex)

    ini_types = {
        "json": {"key": "init_database_dir_json", "pattern": "*.json"},
        "py": {"key": "init_database_dir_py", "pattern": "*.py"},
        "sql": {"key": "init_database_dir_sql", "pattern": "*.sql"},
    }

    for bind in binds:
        if not bind in init_databases_config:
            core.log.warning(
                f"No initialisation configuration has been set in <databases> entry for {bind=}"
            )
            continue

        for ini_type, cf_ini in ini_types.items():
            bind_cf = init_databases_config[bind]
            if type(bind_cf) == str and bind_cf in init_databases_config:
                bind_cf = init_databases_config[bind_cf]
            if not cf_ini["key"] in bind_cf:
                continue

            ini_dir = bind_cf[cf_ini["key"]]
            files = glob.glob(ini_dir + os.sep + cf_ini["pattern"])

            for file_path in files:
                l_table_name = file_path.split(os.sep)[-1].split(".")[0].upper()
                if tables is not None and len(tables) != 0:
                    if not l_table_name in tables:
                        continue
                __process_databases_init(
                    core, core.db, bind, l_table_name, file_path, file_type=ini_type
                )


def __process_databases_init(core, db, bind, table_name, file_path, file_type="py"):
    if file_type == "py":
        current_path = os.getcwd()
        module_path = (
            file_path.replace(current_path, "")
            .replace("/", ".")
            .replace("\\", ".")
            .replace(".py", "")
        )

        if module_path[0] == ".":
            module_path = module_path[1:]

        module = importlib.import_module(module_path)

        if hasattr(module, "ini"):
            ini = module.__dict__["ini"]
            if type(ini) != dict:
                raise AlphaException(
                    "In file {file_path} <ini> configuration must be of type <dict>"
                    % (file_path)
                )

            __get_entries(core, db, bind, table_name, file_path, ini)
    elif file_type == "json":
        try:
            ini = io_lib.read_json(file_path)
        except Exception as ex:
            raise AlphaException("Cannot read file %s: %s" % (file_path, ex))

        __get_entries(core, db, bind, table_name, file_path, ini)
    elif file_type == "sql":
        with open(file_path, "r") as f:
            sql = f.read()
            matchs = re.findall(r"to_date\('[^']+','[^']+'\)", sql)
            for match in matchs:
                date = match.replace("to_date(", "").split(",")[0]
                format = match.split(",")[1].replace(")", "")
                sql = sql.replace(match, f"strftime({format}, {date})")
            statements = sql.split(";")
            for statement in statements:
                try:
                    db.execute(statement, bind=bind.upper())
                except Exception as ex:
                    db.log.error(ex=ex)


def __get_entries(core, db, bind, table_name, file_path, configuration):
    # models_sources = [importlib.import_module(x) if type(x) == str else x for x in models_sources]
    # TODO: fix
    """if not bind in flask_lib.TABLES:
        raise AlphaException(
            f"In file {file_path} configuration {bind=} is not recognized"
        )"""

    if type(configuration) != dict:
        core.log.error(
            f"In file {file_path} configuration of {bind=} must be of type <dict>"
        )
        return

    found = False
    for schema, tables in flask_lib.TABLES.items():
        if table_name in tables:  # TODO: modify
            found = True
            table = tables[table_name]

    if not found:
        core.log.error(
            f"In file {file_path} configuration of {bind=} the {table_name=} is not found"
        )
        return

    if "objects" in configuration:
        entries = configuration["objects"]
        db.process_entries(bind, table, values=entries)

    data_type = "alpha"
    if "headers" in configuration and "values" in configuration:
        values = configuration["values"]
        headers = configuration["headers"]
    elif (
        "results" in configuration
        and "columns" in configuration["results"][0]
        and "items" in configuration["results"][0]
    ):
        values = configuration["results"][0]["items"]
        headers = list(configuration["results"][0]["items"][0].keys())
        data_type = "sql"
    else:
        core.log.error(
            f"Ini configuration in file {file_path} does not have a valid structure"
        )
        return

    if type(values) != list:
        core.log.error(
            f'In file {file_path} "values" key from {table_name=} and {bind=} must be of type <list>'
        )
        return

    if type(headers) != list:
        core.log.error(
            f'In file {file_path} "headers" key from {table_name=} and {bind=} must be of type <list>'
        )
        return

    entries = []
    for entry in values:
        if type(entry) != list and data_type == "alpha":
            core.log.error(
                f"In file {file_path} from {table_name=} and {bind=} entries must be of type <list>"
            )
            continue
        elif type(entry) != dict and data_type == "sql":
            core.log.error(
                f"In file {file_path} from {table_name=} and {bind=} entries must be of type <dict>"
            )
            continue
        entries.append(entry if data_type == "alpha" else list(entry.values()))

        """if LOG:
            LOG.info(
                "Adding %s entries from <list> for {table_name=} in {bind=} from file %s"
                % (len(entries), table_name, database, file_path)
            )"""
    db.process_entries(bind, table, headers=headers, values=entries)
    core.log.info(f"{table_name=} and {bind=} initiated with file {file_path}")


def get_databases_tables_dict(core) -> Dict[str, str]:
    return {}  # TODO: update
    return {x: list(y.metadata.tables.keys()) for x, y in core.databases.items()}


def __get_table_model(schema: str, tablename: str):
    # TODO: add alphaz
    module = importlib.import_module(f"models.databases.{schema}")
    model = None
    for el in module.__dict__.values():
        if hasattr(el, "__tablename__") and el.__tablename__ == tablename:
            model = el
    if model is None:
        raise AlphaException(f"Cannot find {tablename=} in {schema=}")
    return model


def get_table_columns(schema: str, tablename: str):
    model = __get_table_model(schema, tablename)
    return model.get_columns()


def get_table_model(schema: str, tablename: str):
    model = __get_table_model(schema, tablename)
    return model.get_model()


def get_table_content(
    schema: str,
    tablename: str,
    order_by: str,
    direction: str,
    page_index: int,
    page_size: int,
    limit: int = None,
):
    from core import core

    model = __get_table_model(schema, tablename)
    return core.db.select(
        model,
        page=page_index,
        per_page=page_size,
        order_by=order_by,
        order_by_direction=direction,
        limit=limit,
    )
