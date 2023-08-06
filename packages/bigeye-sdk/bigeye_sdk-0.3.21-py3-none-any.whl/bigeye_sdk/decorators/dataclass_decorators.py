import inspect
from dataclasses import is_dataclass

import yaml

from bigeye_sdk.functions.casing import snake_case
from bigeye_sdk.log import get_logger

log = get_logger(__file__)


def add_from_dict(cls):
    def from_dict(env):
        return cls(**{
            k: v for k, v in env.items()
            if k in inspect.signature(cls).parameters
        })

    cls.from_dict = from_dict
    return cls
