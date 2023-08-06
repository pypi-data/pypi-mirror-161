import datetime, jwt, itertools
import enum
from enum import Enum

from ...libs import user_lib, secure_lib, json_lib

from ...models.database.users_definitions import User, UserSession

from ...models.main import AlphaException, EnumStr
from ...models.api import AlphaRequest

from core import core, API, DB

from flask import request


class LoginModes(EnumStr):
    LDAP = enum.auto()
    NO_CONFIRMATION = enum.auto()


LOG = core.get_logger("users")
LOGIN_MODE = core.api.conf.get("auth/mode")
LOGIN_MODE = None if LOGIN_MODE is None else LOGIN_MODE.upper()

DATA_TO_JWT = {"id": "id", "username": "sub", "time": "iat", "user_roles": "roles"}

# Serve for registration
def try_register_user(
    mail, username, password, password_confirmation, validation=True, infos=""
):
    userByMail = user_lib.get_user_data_by_mail(mail)
    userByUsername = user_lib.get_user_data_by_username(username)

    if (
        validation
        and (userByMail is not None and "id" in userByMail)
        or (userByUsername is not None and "id" in userByUsername)
    ):
        if (
            LOGIN_MODE != LoginModes.NO_CONFIRMATION.value
            and (
                "id" in userByMail
                and userByMail["role"] is not None
                and userByMail["role"] < 0
            )
            or ("id" in userByUsername and userByUsername["role"] < 0)
        ):
            raise AlphaException("account_not_validated")
        raise AlphaException("account_duplicated")

    if password != password_confirmation:
        raise AlphaException("password_missmatch")

    '''mail_valid = validate_email(mail)
    if not mail_valid:
        return "mail_format"'''

    '''if not password_check_format(password):
        return "password_format"'''

    password_hashed = secure_lib.secure_password(password)

    # ADD CHECKS FOR LENGHT OF USERNAME/MAIL!!

    # Generate token
    token = secure_lib.get_token()

    parameters = {"token": token, "name": username, "mail": mail}

    if validation and not API.send_mail(
        mail_config="registration", parameters_list=[parameters], db=DB
    ):
        raise AlphaException("sending")
    DB.add(
        User(
            username=username,
            mail=mail,
            password=password_hashed,
            role=-1 if validation else 1,
            date_registred=datetime.datetime.now(),
            last_activity=datetime.datetime.now(),
            registration_token=token,
            infos=json_lib.jsonify_data(infos, string_output=True),
        )
    )


def update_infos(user_data, infos) -> bool:
    if type(infos) != str:
        infos = json_lib.jsonify_data(infos, string_output=True)

    infos_user = (
        json_lib.jsonify_data(user_data["infos"])
        if type(user_data["infos"]) != str
        else user_data["infos"]
    )
    if infos == infos_user:
        return True
    user_id = user_data["id"]
    return DB.update(User, values={"infos": infos}, filters=[User.id == user_id])


def ask_password_reset(username_or_mail):
    user_by_mail = user_lib.get_user_data_by_mail(username_or_mail)
    user_by_username = user_lib.get_user_data_by_username(username_or_mail)

    if len(user_by_mail.keys()) == 0 and len(user_by_username.keys()) == 0:
        raise AlphaException("unknown_inputs")

    if "id" not in user_by_mail and "id" not in user_by_username:
        raise AlphaException("unknown_inputs")

    user_data = user_by_mail if "id" in user_by_mail else user_by_username

    # Generate token
    token = secure_lib.get_token()

    query = "UPDATE user SET password_reset_token = %s, password_reset_token_expire = UTC_TIMESTAMP() + INTERVAL 20 MINUTE WHERE id = %s;"
    values = (
        token,
        user_data["id"],
    )

    if not DB.execute_query(query, values):
        raise AlphaException("sql_error")

    # MAIL
    parameters = {}
    parameters["mail"] = user_data["mail"]
    parameters["token"] = token
    parameters["username"] = user_data["username"]
    parameters["name"] = user_data["username"]

    mail_sent = API.send_mail(
        mail_config="password_reset", parameters_list=[parameters], db=DB
    )


def confirm_user_registration(token):
    if "consumed" in token:
        raise AlphaException("invalid_token")
    user_data = user_lib.get_user_data_by_registration_token(DB, token)

    if len(user_data) == 0:
        AlphaException("not_found")

    if "id" in user_data:
        # Set Role to 0 and revoke token
        user = DB.select(User, filters={"id": user_data["id"]}, first=True, json=False)
        if user is None:
            raise AlphaException("error")
        user.role = 0
        user.registration_token = "consumed"
        DB.commit()

        valid = True
        if not valid:
            raise AlphaException("error")


def infos_dict_from_ldap(ldap_structure: dict, ldap_data: dict) -> dict:
    added_infos = {}
    if ldap_structure is not None:
        for ldap_name, name in ldap_structure.items():
            added_infos[name] = ldap_data[ldap_name] if ldap_name in ldap_data else ""
            if type(added_infos[name]) == list:
                added_infos[name] = " ".join(
                    [
                        x.decode("utf-8") if hasattr(x, "decode") else x
                        for x in added_infos[name]
                    ]
                )
    return added_infos


def get_expire_datetime():
    defaults_validity = {
        "days": 7,
        "seconds": 0,
        "microseconds": 0,
        "milliseconds": 0,
        "minutes": 0,
        "hours": 0,
        "weeks": 0,
    }
    validity_config = API.conf.get("token/login/validity")
    validity_config = {
        x: y
        if (validity_config is None or not x in validity_config)
        else validity_config[x]
        for x, y in defaults_validity.items()
    }
    expire = datetime.datetime.now() + datetime.timedelta(**validity_config)
    return expire


def get_encoded_jwt_from_user_data(user_data):
    extra_tokens = API.conf.get(
        f"auth/users/{user_data['username']}/user_roles", default=[]
    )
    if not "user_roles" in user_data:
        user_data["user_roles"] = []
    if type(extra_tokens) == list:
        user_data["user_roles"].extend(extra_tokens)
    user_data["user_roles"] = list(set(user_data["user_roles"]))

    # Generate token
    user_data["time"] = int(datetime.datetime.now().timestamp())
    user_data_to_encode = {y: user_data[x] for x, y in DATA_TO_JWT.items()}
    user_data_to_encode["exp"] = int(get_expire_datetime().timestamp())
    user_data_to_encode["app"] = API.conf.get("name")
    user_data_to_encode["env"] = core.configuration

    encoded_jwt = jwt.encode(
        user_data_to_encode, API.config["JWT_SECRET_KEY"], algorithm="HS256",
    )
    try:  # TODO: remove
        encoded_jwt = encoded_jwt.decode("ascii")
    except Exception as ex:
        pass
    return encoded_jwt


def try_login(username: str, password: str, su: bool = False):
    user_data = API.get_logged_user()

    # if logged_user is not None:
    # raise AlphaException("user_already_logged")
    if not su and (
        user_data is None or len(user_data) == 0 or user_data["username"] != username
    ):
        if LOGIN_MODE == LoginModes.LDAP.value:
            from .ldap import check_ldap_credentials, LDAP_DATA

            valid_ldap = check_ldap_credentials(username, password)
            if valid_ldap is None:
                raise AlphaException("Wrong user or password")

            added_infos = infos_dict_from_ldap(LDAP_DATA, valid_ldap)

            user_data = user_lib.get_user_data_from_login(
                username, password, no_password_check=True
            )
            if user_data is None:
                try_register_user(
                    mail=valid_ldap["mail"] if "mail" in valid_ldap else "",
                    username=username,
                    password=password,
                    password_confirmation=password,
                    validation=False,
                    infos=added_infos,
                )
                user_data = user_lib.get_user_data_from_login(
                    username, password, no_password_check=True
                )
            else:
                update_infos(user_data, added_infos)
        else:
            user_data = user_lib.get_user_data_from_login(username, password)
            if user_data is None:
                raise AlphaException("unknown_user")

        if user_data["role"] == 0:
            raise AlphaException("account_not_validated")
        if not "JWT_SECRET_KEY" in API.config:
            raise AlphaException("Missing <JWT_SECRET_KEY> api parameter")
    elif su and user_data is None:
        user_data = API.get_su_user(username, username)

    if user_data is None or len(user_data) == 0:
        raise AlphaException("unknown_user")

    expire = get_expire_datetime()
    token = get_encoded_jwt_from_user_data(user_data)

    # Add new token session related to user
    if not DB.add_or_update(
        UserSession(
            user_id=user_data["id"], token=token, ip=request.remote_addr, expire=expire,
        )
    ):
        raise AlphaException("Cannot update user session")

    return {
        **{
            x: y
            for x, y in user_data.items()
            if not x in DATA_TO_JWT or x == "username"
        },
        "token": token,
        "valid_until": expire,
    }


def try_su_login(admin_user_id: str = None, admin_user_name: str = None):
    output = try_login(
        admin_user_name if admin_user_name is not None else admin_user_id, None, su=True
    )
    API.admin_token = output["token"]
    return output


def confirm_user_password_reset(tmp_token, password, password_confirmation):
    if "consumed" in tmp_token:
        raise AlphaException("consumed_token")

    user_data = user_lib.get_user_data_by_password_reset_token(DB, tmp_token)
    if not "id" in user_data:
        raise AlphaException("invalid_token")

    try_reset_password(user_data, password, password_confirmation)


def try_reset_password(password, password_confirmation):
    if password != password_confirmation:
        raise AlphaException("password_missmatch")
    user_data = API.get_logged_user()

    '''if not password_check_format(password):
        return "password_format"'''
    # Set New password and revoke token
    password_hashed = secure_lib.secure_password(password)

    # Reset password
    query = "UPDATE user SET password = %s, password_reset_token = 'consumed' WHERE id = %s;"
    values = (
        password_hashed,
        user_data["id"],
    )
    valid = DB.execute_query(query, values)
    if not valid:
        raise AlphaException("reset_error")

    # Reset all sessions as password changed
    query = "DELETE FROM user_session WHERE user_id = %s;"
    values = (user_data["id"],)
    valid = DB.execute_query(query, values)
    if not valid:
        raise AlphaException("clean_error")


def logout():
    token = AlphaRequest.get_token()
    if token is None:
        raise AlphaException("token_not_specified")
    if not DB.delete(UserSession, filters={"token": token}):
        raise AlphaException("fail")


def logout_su():
    API.admin_token = None


def get_user_session_from_id(id: int) -> UserSession:
    return DB.select(UserSession, filters=[UserSession.user_id == id], first=True)


def try_subscribe_user(mail, nb_days, target_role):
    userByMail = user_lib.get_user_data_by_mail(mail)
    user_data = None
    if "id" in userByMail:
        if "id" in userByMail:
            user_data = userByMail
    expired_date = datetime.datetime.now() + datetime.timedelta(days=nb_days)
    if user_data is not None:
        # Reset password
        query = "UPDATE user SET role = %s, expire = %s WHERE id = %s;"
        values = (
            target_role,
            expired_date,
            user_data["id"],
        )
        valid = DB.execute_query(query, values)
        if not valid:
            AlphaException("update_error")
    AlphaException("unknow_user")
