# Alpha API system

## Introduction

The api system is completely based on Flask and compatible. You could use Flask inside Alpha system without any issue.

## Launch

To start the api execute the `api.py` file

```sh
python api.py
```

!!! note
    set `ALPHA_CONF` environment parameter is you want to set the environment.

Verify the deployment by navigating to your server address in your preferred browser:

```sh
127.0.0.1:<port>
```

## How to use

Your could import it using simply from the **utils**:

```python
from alphaz.utils.api import api
```

or from the **core** if you are using it

```python
from core import core, API
```

> **api** / **API** is the equivalent for **app** in **Flask** framework.


## Configuration

The api is automatically configured from the `api.jon` file. See [Configuration](configuration.md) for further details on how to use it.

### Main

- workers: In order to specify the numbers of workers

```json
"workers": 6
```

- routes_no_log: In order to specify the routes where log must be ignored

```json
"routes_no_log": ["//status", "//static", "//dashboard"],
```

- models: In order to specify the **Flask-SqlAlchemy** models definitions paths

```json
"models": ["models.databases"]
```

- routes: In order to specify the routes definitions paths

```json
"routes": ["apis.routes"]
```

- ssl: In order to activate ssl mode

```json
"ssl": false
```

- threaded: In order to activate the threaded mode

```json
"threaded": false
```

- config: In order to activate pass configuration to Flask **api** class

```json
"config": {
    "MYSQL_DATABASE_CHARSET": "utf8mb4",
    "SQLALCHEMY_TRACK_MODIFICATIONS": false,
    "SQLALCHEMY_POOL_RECYCLE": 299,
    "SQLALCHEMY_POOL_TIMEOUT": 30,
    "SQLALCHEMY_POOL_SIZE": 10,
    "JWT_SECRET_KEY": "a_secret_key",
    "JSON_SORT_KEYS": false
}
```

### Mails

In order to specify the mails configurations

```json
"mails": {
    "mail_server": {
        "host": "",
        "mail": "",
        "password": "",
        "port": 465,
        "server": "",
        "ssl": true,
        "tls": false
    }
}
```

### Auth

In order to specify the auth mode

```json
"auth": {
    "mode": "ldap",
    "ldap": {
        "server": "ldap://path_to_ldap",
        "baseDN": "ou=people,dc=a_name,dc=com",
        "users_filters": "(|(uid={uid})(mail={mail})(cn={cn}))",
        "user_filters": "(|(uid={username})(mail={username})(cn={username}))",
        "user_data": {
            "givenName": "name",
            "sn": "lastname",
            "c": "area",
            "st-locationdescription": "location",
            "st-seatnumber": "seat",
            "telephoneNumber": "phone-number"
        }
    },
    "users": {
        "a_user_name": {
            "user_roles": ["SUPER_USER"]
        }
    }
},
```

### Reloader type

In order to specify the [Werkzeug](https://werkzeug.palletsprojects.com/en/2.1.x/) reloader type

```json
"reloader_type": "stat"
```

### Admin

In order to specify the admins configurations

```json
"admins": {"ips":["127.0.0.1"], "password":"a_password"},
```


### Dashboard

In order to configure the [Flask-Monitoring Dashboard](https://flask-monitoringdashboard.readthedocs.io/)

```json
"dashboard": {
    "dashboard": {
        "APP_VERSION": 1.0,
        "SAMPLING_PERIOD": 20,
        "ENABLE_LOGGING": true,
        "active": false
    },
    "authentication": {
        "USERNAME": "username",
        "PASSWORD": "",
        "GUEST_USERNAME": "guest",
        "GUEST_PASSWORD": ["guest1", "guest2"],
        "SECURITY_TOKEN": "a_security_token"
    },
    "database": {
        "DATABASE": "sqlite:///{{root}}/dashboard.db"
    }
}
```
## Routes

### Basic

To specify an api route, juste use the `route` flag:

```python
from alphaz.utils.api import route, api, Parameter

@route("route_name")
def method_name():
    return "hello"
```

Method automatically convert the output to the right format. Default format is `json`

### Description

A description could be specified:

```python
@route("route_name", description="This route say hello")
def method_name():
    return "hello"
```

### Category

The routes are organized by `category`, by default the route category is defined by it **file name**, but it could be specified using the `cat` parameter:

```python
@route("route_name", category="politeness")
def method_name():
    return "hello"
```

## Parameters

### Simple

You could simply define parameters by listing all parameters in `parameters` list:

```python
from alphaz.utils.api import route, api, Parameter

@route("books", parameters=["name"])
def method_name():
    return "Book name is %s or %s"%(api["name"], api.get("name",default=""))
```

Parameter value is accessed by `api` instance, using `get` method, they could also be accessed using `get_parameters` method from `api` instance.

### Object

Or you could use the `Parameter` class to specify properties such as:

- **ptype**: value type int, str, bool, `SqlAlchemy model`
  - parameter is `automatically converted` to the specified type
  - if conversion failed an `exception` is raised
- **required**: the parameter is required or not
- **default**: default parameter value
- **options**: authorized values
- **mode**: input mode
- **cacheable**: parameter is taken into acount in the caching system or not
- **private**: parameter is hiden from documentation or not

```python
@route("/logs",
    parameters = [
        Parameter('page',required=True,ptype=int),
        Parameter('startDate',required=True),
        Parameter('endDate',default=None),
        Parameter('error', options=["Y","N"])
    ])
def admin_logs():
    return get_logs(**api.get_parameters())
```

> Promote this method as it allows a better control on parameters

### Default parameters

Some parameter are always available:
- **no_log** (bool): disable logs for this route
- **reset_cache** (bool): reset cache before calling this route
- **requester** (str): requester to this route
- **format** (str): output format
    - json: 
    - xml:
- **admin** (str): admin password
- **admin_user_id** (int): id of the user to connect has an admin 

## SqlAlchemy model

If you specify a `SqlAlchemy model` as a type it will be automatically converted to the specified model.

```python
from core import core
db = core.db

class Logs(db.Model, AlphaTable):
    __tablename__ = 'LOGS'

    id                       = AlphaColumn(Integer,nullable=False,primary_key=True)
    name                     = AlphaColumn(String,nullable=False)

@route("logs",
    parameters = [
        Parameter('log',ptype=Logs)
    ])
def admin_logs():
    db.add(api['log'])
```

## Methods

Methods are specified the same way as in `Flask`, using `methods` parameter:

```python
@route('logs', methods=["GET"])
def get_logs():
    return db.select(Logs)

@route('logs', methods=["POST"])
def set_logs():
    return db.add(Logs)
```

Methods can be managed using `different routes` or within `a single route`:

```python
@route('logs', methods=["GET", "POST", "DELETE"])
def get_logs():
    if api.is_get():
        return db.select(Logs)
    elif api.is_post():
        return db.add(Logs)
    elif api.is_delete():
        return db.delete(Logs)
```

## Authorizations

Route can be protected using the login system or admin rights.

### Login system

To protect a route using the login system you must specify: `logged=True`

```python
@route('protected', logged=True)
def protected_route():
    user = api.get_logged_user()
    return user
```

User information can be accessed using *get_logged_user* method.

## Cache

A cache system is implemented, in order to use it you must specify the

## Admin

Admin could auto log to any user account on local mode

### Condition

To be an admin a user must have at least one condition:

- a **role** > 9
- specify the magic password has **admin** API parameter
- connect using an admin ip. The ips admin list must be defined in the **api.json** configuration files under the **key**=**admins_ips**

### How to use

If you met one of the admin condition you do not need any password in order to log has any of the user in the database.

You could be logged for specific routes using the **single route mode** or to any route using the **login/logout** system.
#### Single route mode

- You could specifiy either admin_user_id={user_id} or admin_user_name={username} directly into any request in order to login with this user for this specific route.

!!! note "Exemple"
    /anyroute?admin_user_id=1000

#### Login to the api

Use the route **/auth/su** in order to set an admin session that is valid until the end of the api runtime.

- You must specifiy either admin_user_id={user_id} or admin_user_name={username}

!!! note "Exemple"
    /auth/su?admin_user_id=1000

#### Logout from the api

Use the route **/logout/su** in order to logout.




## Issues

> In progress

### Database alias

> In progress

