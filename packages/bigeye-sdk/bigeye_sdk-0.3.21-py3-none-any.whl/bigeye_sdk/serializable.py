from __future__ import annotations

import abc
import json
from dataclasses import asdict

import yaml
from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from pydantic.json import pydantic_encoder
from pydantic_yaml import YamlModel, YamlModelMixin

from bigeye_sdk.log import get_logger

log = get_logger(__file__)


class PydanticSubtypeSerializable(YamlModel):
    _subtypes_ = dict()

    def __init_subclass__(cls, type=None):
        cls._subtypes_[type or cls.__name__.lower()] = cls

    @classmethod
    def __get_validators__(cls):
        yield cls._convert_to_real_type_

    @classmethod
    def _convert_to_real_type_(cls, data):
        if isinstance(data, dict):
            data_type = data.get("type")
        elif data.type in cls._subtypes_:
            return data
        else:
            raise Exception(f'{type(data)} not supported.')

        if data_type is None:
            raise ValueError(f"Missing 'type' in {cls.__name__}'")

        sub = cls._subtypes_.get(data_type)

        if sub is None:
            raise TypeError(f"Unsupport sub-type: {data_type}")

        return sub(**data)

    @classmethod
    def parse_obj(cls, obj):
        return cls._convert_to_real_type_(obj)


class File(PydanticSubtypeSerializable, YamlModelMixin):
    type: str

    @classmethod
    def load(cls, file: str):
        with open(file, 'r') as fin:
            expected = yaml.safe_load(fin)

        return cls.parse_obj(expected)

    def save(self, file: str):
        with open(file, 'w') as fout:
            lines = self.yaml(exclude_unset=True)
            fout.writelines(lines)


@dataclass
class YamlSerializable(abc.ABC):
    @classmethod
    def load_from_file(cls, file: str):
        print(f'load_from_file class name: {cls.__name__}')
        with open(file, 'r') as fin:
            d = yaml.safe_load(fin)
            bsc = cls(**d)
            if bsc is None:
                raise Exception('Could not load from disk.')
            log.info(f'Loaded instance of {bsc.__class__.__name__} from disk: {file}')
            return bsc

    def to_dict(self, exclude_empty: bool = True):
        return asdict(self, dict_factory=lambda x: {k: v for (k, v) in x if v and exclude_empty})

    def save_to_file(self, file: str):
        j = json.dumps(self.to_dict(), indent=True, default=pydantic_encoder, sort_keys=False)
        d = json.loads(j)
        with open(file, 'w') as file:
            yaml.dump(d, file, sort_keys=False)
