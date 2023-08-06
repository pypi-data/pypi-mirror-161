# Welcome to Alpha environment documention

Alpha is an **ecosystem** based on multiple **frameworks** and **libraries** for both **frontend** and **backend**.

## Purpose

The purpose of the **ecosystem** is to simplify any dev activity. 

??? note "Standard query"

    ```py
    from core import core
    DB = core.db 
    def get_logs(start_date=None, end_date=None, useLimit=False, pageForLimit=1):
        total = 0
        logs = []
        limit = 20
        start = (pageForLimit - 1) * limit

        query = "SELECT COUNT(*) AS count FROM logs"
        parameters = []
        if start_date is not None and end_date is not None:
            query += " AND CAST(date AS DATE) between %s and %s"
            parameters.append(start_date)
            parameters.append(end_date)       
        query+= " ORDER BY date DESC"

        rows = DB.get(query, parameters)
        for row in rows:
            total = row[0]

        query = "SELECT type, origin, message, stack, date FROM logs"
        parameters = []
        if start_date is not None and end_date is not None:
            query += " AND CAST(date AS DATE) between %s and %s"
            parameters.append(start_date)
            parameters.append(end_date)       
        query+= " ORDER BY date DESC"
        if useLimit:
            query+= " LIMIT %s OFFSET %s"
            parameters.append(limit)
            parameters.append(start)

        rows = db.get(query, parameters)        
        for row in rows:
            log = {}
            log["type"] = row[0]
            log["origin"] = row[1]
            log["message"] = row[2]
            log["stack"] = row[3]
            log["date"] = row[4]
            logs.append(log)

        return {'total' : total, 'logs' : logs}
    ```

??? note "Alpha Query"

    ```py
    from core import core
    DB = core.DB
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
    ```

## Backend: Alphaz

- Alphaz is a backend toolbox/framework based on a combination between Flask, SqlAlchemy and a multitude of other libraries.

    !!! note
        The overriding goal for Alphaz is to ease the backend development and easely link python backend to Angular frontend [Alphaa].

## Features

-   API Routing parameters management upgrade
-   Enhanced json files configuration

## Tech

Alphaz uses a number of open source projects to work properly:

-   [Flask](https://flask.palletsprojects.com/en/1.1.x/) - a micro web framework
-   [SqlAlchemy](https://www.sqlalchemy.org/) - a database toolkit
-   [Flask-SqlAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) - an extension for Flask that adds support for SQLAlchemy

## Project layout

- How to setup `Alpha`: [Alpha](alpha_setup.md)
## Frontend: Alphaa

- Alphaa is a frontend toolbox/framework

    !!! note
        The overriding goal for Alphaa is to ease the frontend development and easely link Angular frontend to python backend [Alphaz].
## Features

- Enhanced services
- Master class


## Project layout

- How to setup `Alpha`: [Alpha](alpha_setup.md)