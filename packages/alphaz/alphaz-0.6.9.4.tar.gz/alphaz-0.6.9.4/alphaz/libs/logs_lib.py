from datetime import datetime
from core import core
from ..models.database.main_definitions import Logs
from ..models.main import AlphaException

api = core.api
DB = core.db


def clear_logs():
    query = "TRUNCATE logs"
    return DB.execute(query)


def get_logs(
    start_date: datetime = None,
    end_date: datetime = None,
    limit: int = False,
    page: int = 0,
    per_page: int = 100,
):
    return DB.select(
        Logs,
        optional_filters=[
            {Logs.update_date: {">": start_date}},
            {Logs.update_date: {"<": end_date}},
        ],
        page=page,
        per_page=per_page,
        limit=limit,
        order_by=Logs.update_date.desc(),
    )


def log_a_message(
    logger: str,
    criticality: str,
    message: str,
    level: int,
    monitor: str = None,
    log_in_db: bool = False,
):
    log = core.get_logger(logger)
    if log is None:
        raise AlphaException(f"No {logger=} found")
    if hasattr(log, criticality):
        getattr(log, criticality)(
            message=message, monitor=monitor, level=level, log_in_db=log_in_db
        )
        return True
    return False
