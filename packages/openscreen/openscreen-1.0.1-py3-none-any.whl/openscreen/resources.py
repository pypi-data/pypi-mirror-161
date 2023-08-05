from dataclasses import dataclass, is_dataclass
from typing import Any
from .session import Session


class Resource:
    _session: Session
    path_parameters: Any = {}

    def __init__(self, session, path_parameters=None):
        if path_parameters is None:
            path_parameters = {}
        self.session = session
        self.path_parameters = path_parameters

    def getSession(self) -> Session:
        return self.session


class Resources:
    session: Session
    path_parameters: Any = {}

    def __init__(self, session, path_parameters=None):
        if path_parameters is None:
            path_parameters = {}
        self.session = session
        self.path_parameters = path_parameters

    def getSession(self) -> Session:
        return self.session


def nested_dataclass(*args, **kwargs):
    def wrapper(cls):
        cls = dataclass(cls, **kwargs)
        original_init = cls.__init__
        def __init__(self, *args, **kwargs):
            for name, value in kwargs.items():
                field_type = cls.__annotations__.get(name, None)
                if is_dataclass(field_type) and isinstance(value, dict):
                     new_obj = field_type(**value)
                     kwargs[name] = new_obj
                elif isinstance(value, list) and is_dataclass(field_type.__args__[0]):
                    kwargs[name] = [field_type.__args__[0](**v) for v in value]
            try:
                original_init(self, *args, **kwargs)
            except TypeError:
                # failed because of wrong attribute then we remove that attribute
                original_init(self, *args, **{
                    k: v for k, v in kwargs.items()
                    if k in cls.__annotations__
                })

        cls.__init__ = __init__
        return cls
    return wrapper(args[0]) if args else wrapper