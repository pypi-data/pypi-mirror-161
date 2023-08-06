from __future__ import annotations

import abc

import betterproto
from pydantic.dataclasses import dataclass
from typing import List, TypeVar, Union

from bigeye_sdk.log import get_logger

# create logger

log = get_logger(__file__)

DatawatchObject = TypeVar('DatawatchObject', bound=Union[betterproto.Message, List[betterproto.Message]])


@dataclass
class DatawatchFacade(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def from_datawatch_object(cls, obj: DatawatchObject) -> DatawatchFacade:
        pass

    @abc.abstractmethod
    def to_datawatch_object(self, **kwargs) -> DatawatchObject:
        pass