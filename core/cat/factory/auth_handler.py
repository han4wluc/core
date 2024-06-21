from os import getenv
from typing import Type
from pydantic import BaseModel, ConfigDict

from cat.mad_hatter.mad_hatter import MadHatter
from cat.factory.custom_auth_handler import (
    ApiKeyAuthHandler,
    BaseAuthHandler,
    CloseAuthHandler,
)


class AuthHandlerConfig(BaseModel):
    _pyclass: Type[BaseAuthHandler] = None

    @classmethod
    def get_auth_handler_from_config(cls, config):
        if cls._pyclass is None or issubclass(cls._pyclass.default, BaseAuthHandler) is False:
            raise Exception(
                "AuthHandler configuration class has self._pyclass==None. Should be a valid AuthHandler class"
            )
        return cls._pyclass.default(**config)


class CloseAuthConfig(AuthHandlerConfig):
    _pyclass: Type = CloseAuthHandler

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "Close Auth Handler",
            "description": "Deny all m2m connection.",
            "link": "",
        }
    )


class ApiKeyAuthConfig(AuthHandlerConfig):
    _pyclass: Type = ApiKeyAuthHandler

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "Api Key Auth Handler",
            "description": "Yeeeeah.",
            "link": "",
        }
    )


def get_allowed_auth_handler_strategies():
    list_auth_handler_default = [
        CloseAuthConfig,
        ApiKeyAuthConfig,
    ]

    mad_hatter_instance = MadHatter()
    list_auth_handler = mad_hatter_instance.execute_hook(
        "factory_allowed_auth_handlers", list_auth_handler_default, cat=None
    )

    return list_auth_handler

def get_auth_handlers_schemas():
    AUTH_HANDLER_SCHEMAS = {}
    for config_class in get_allowed_auth_handler_strategies():
        schema = config_class.model_json_schema()
        schema["auhrizatorName"] = schema["title"]
        AUTH_HANDLER_SCHEMAS[schema["title"]] = schema
    
    return AUTH_HANDLER_SCHEMAS

def get_auth_handler_from_name(name):
    list_auth_handler = get_allowed_auth_handler_strategies()
    for auth_handler in list_auth_handler:
        if auth_handler.__name__ == name:
            return auth_handler
    return None