import getpass
import logging
import os
import typing as T

import requests

from . import api_v4, config, types
from .config import MAPILLARY_CONFIG_PATH

LOG = logging.getLogger(__name__)


class HTTPError(requests.HTTPError):
    pass


def wrap_http_exception(ex: requests.HTTPError):
    resp = ex.response
    lines = [
        f"{ex.request.method} {resp.url}",
        f"> HTTP Status: {ex.response.status_code}",
        f"{ex.response.text}",
    ]
    return HTTPError("\n".join(lines))


def prompt_user_for_user_items(user_name: str) -> types.UserItem:
    print(f"Sign in for user {user_name}")
    user_email = input("Enter your Mapillary user email: ")
    user_password = getpass.getpass("Enter Mapillary user password: ")

    try:
        data = api_v4.get_upload_token(user_email, user_password)
    except requests.HTTPError as ex:
        if 400 <= ex.response.status_code < 500:
            resp = ex.response.json()
            subcode = resp.get("error", {}).get("error_subcode")
            if subcode in [1348028, 1348092, 3404005, 1348131]:
                title = resp.get("error", {}).get("error_user_title")
                message = resp.get("error", {}).get("error_user_msg")
                LOG.error(f"{title}: {message}")
                return prompt_user_for_user_items(user_name)
            else:
                raise wrap_http_exception(ex)
        else:
            raise wrap_http_exception(ex)

    upload_token = T.cast(str, data.get("access_token"))
    user_key = T.cast(str, data.get("user_id"))
    if not isinstance(upload_token, str) or not isinstance(user_key, (str, int)):
        raise RuntimeError(
            f"Error extracting user_key or token from the login response: {data}"
        )

    if isinstance(user_key, int):
        user_key = str(user_key)

    return {
        "MAPSettingsUsername": user_name,
        "MAPSettingsUserKey": user_key,
        "user_upload_token": upload_token,
    }


def list_all_users() -> T.List[types.UserItem]:
    if os.path.isfile(MAPILLARY_CONFIG_PATH):
        global_config_object = config.load_config(MAPILLARY_CONFIG_PATH)
        return [
            config.load_user(global_config_object, user_name)
            for user_name in global_config_object.sections()
        ]
    else:
        return []


def authenticate_user(user_name: str) -> types.UserItem:
    if os.path.isfile(MAPILLARY_CONFIG_PATH):
        global_config_object = config.load_config(MAPILLARY_CONFIG_PATH)
        if user_name in global_config_object.sections():
            return config.load_user(global_config_object, user_name)

    user_items = prompt_user_for_user_items(user_name)

    config.create_config(MAPILLARY_CONFIG_PATH)
    config.update_config(MAPILLARY_CONFIG_PATH, user_name, user_items)
    return user_items
