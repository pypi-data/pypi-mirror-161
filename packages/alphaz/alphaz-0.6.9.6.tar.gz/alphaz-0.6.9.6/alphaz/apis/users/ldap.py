from core import core

API, DB, LOG, CONFIG = core.api, core.db, core.log, core.config

import ldap3

LDAP_SERVER = API.conf.get("auth/ldap/server", required=True)
BASE_DN = API.conf.get("auth/ldap/baseDN", required=True)
LDAP_DATA = API.conf.get("auth/ldap/user_data", required=True)
LDAP_USERS_FILTERS = API.conf.get("auth/ldap/users_filters", default="uid={uid}")
LDAP_USER_FILTERS = API.conf.get("auth/ldap/user_filters", default="uid={username}")


def check_ldap_credentials(username, password):
    l = get_ldap_cnx()
    if l is None:
        return None

    try:
        ldap_result_id = l.search(
            BASE_DN,
            LDAP_USER_FILTERS.format(**{"username": username}),
            search_scope=ldap3.SUBTREE,
            attributes=ldap3.ALL_ATTRIBUTES,
        )
        if len(l.entries) == 0:
            LOG.error("Wrong username")
            l.unbind()
            return None
        result = l.entries[0]
        l.unbind()

        try:
            l = get_ldap_cnx(result.entry_dn, password)
            if l is None:
                return None
            if l.last_error is not None:
                LOG.error(l.last_error)
                return None
        except Exception as ex:
            l.unbind()
            LOG.error(ex=ex)
            return None
        l.unbind()

        return {
            x: y[0] if len(y) == 1 else y
            for x, y in result.entry_attributes_as_dict.items()
            if not x == "objectClass"
        }
    except Exception as ex:
        LOG.error(ex)
    return None


def get_ldap_cnx(dn=None, password=None):
    try:
        s = ldap3.Server(LDAP_SERVER)
        if dn is None and password is None:
            l = ldap3.Connection(s)
        else:
            l = ldap3.Connection(s, dn, password)
    except Exception as ex:
        LOG.error(ex)
        return None
    try:
        l.bind()
    except Exception as ex:
        LOG.error(ex=ex)
    return l


def get_ldap_users(filters: str):
    l = get_ldap_cnx()
    if l is None:
        return None

    l.search(
        BASE_DN, filters, search_scope=ldap3.SUBTREE, attributes=ldap3.ALL_ATTRIBUTES
    )
    entries = l.entries
    l.unbind()

    users = []
    for entry in entries:
        user = {}
        for key, value in entry.entry_attributes_as_dict.items():
            if type(value) == list:
                value = " ".join([str(x) for x in value])
            elif type(value) != str:
                value = str(value)
            user[key] = value
        users.append(user)
    return users
