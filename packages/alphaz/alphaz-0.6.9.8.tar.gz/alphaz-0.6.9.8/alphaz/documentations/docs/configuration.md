# Dynamic json alpha configuration syntax

## Parameters

### Main

- project_name: in order to specify the project name


### Directories

You must at least specify the **root** and **home** directories:

```json
"root": "/application/{{user}}",
"home": "/home/{{user}}",
```

Other main directories could be defined in a sub **directories** path:

```json
"directories": {
    "data": "{{root}}/data",
    "logs": "{{root}}/logs",
    "cache": "{{root}}/cache",
    "database_models": ["models.databases"]
}
```

### System environments variables

In order to set operating system environment variables

```json
"envs": {
    "ORACLE_HOME": "/application/software/oracle/12.1.0.2"
}
```

### Environments configurations

In order to specify the envs configurations:

```json
"configuration": "local",
"configurations": {
    "local": {
        "debug": true,
        "host_public": "",
        "host_web": "",
        "port": 5006,
        "ssl_cert": "",
        "ssl_key": "",
        "admin": true,
        "admin_databases": true
    },
    "dev": {
        "debug": true,
        "host_public": "",
        "host_web": "",
        "port": 5000,
        "ssl_cert": "",
        "ssl_key": "",
        "admin": true,
        "admin_databases": true
    }
}
```

**configuration** parameter is the default one.

### Users

Configuration could be modified dynamically depending on the user

```json
"users": {
    "user_dev": {
        "debug": false,
        "mode": "wsgi",
        "configuration": "dev"
    },
    "user_int": {
        "debug": false,
        "mode": "wsgi",
        "configuration": "int"
    },
    "user_acc": {
        "debug": false,
        "mode": "wsgi",
        "configuration": "acc"
    },
    "user_prod": {
        "debug": false,
        "mode": "wsgi",
        "configuration": "prod"
    }
}
```

### Platforms

Configuration could be modified dynamically depending on the operating system

```json
"platforms": {
    "windows": {
        "root": "/alpha/{{user}}",
        "home": "/alpha/{{user}}",
        "host": "0.0.0.0"
    }
},
```

### Loggers

In order the specify the loggers configurations:

```json
"loggers": {
    "main": {
        "level": "debug"
    },
    "database": {
        "level": "debug"
    }
}
```

### Tests

In order to specify the directories that contains tests:

```json
"tests" : {
    "auto_directory": "tests/auto",
    "auto_import": "alphaz.tests.auto",
    "save_directory": "{{save_root}}/tests"
},
```

### Menu

```json
"menus": {
    "save_directory": "{{save_root}}/menus"
},
```

