from abc import ABCMeta
from datetime import datetime
from typing import Union, TypeVar, Dict
from dataclasses import dataclass
from typeguard import typechecked


PrimitiveU = Union[int, float, str, bool, dict, list]

PrimitiveT = TypeVar("PrimitiveT", int, float, str, bool, dict, list)

PriceTimeDict = Dict[datetime, float]

cls_key_name = "_DictSerializable_cls"


class DictSerializableMeta(ABCMeta):
    _siblings = {}

    def __init__(cls, name, bases, attrs):
        cls._siblings[cls.__name__] = cls

    @property
    def family(self):
        return self._siblings


class DictSerializable(metaclass=DictSerializableMeta):
    def to_dict(self) -> Dict:
        return {cls_key_name: self.__class__.__name__, **self.__dict__}

    @classmethod
    @typechecked
    def from_dict(cls, d: Dict) -> "DictSerializable":
        if not issubclass(cls, DictSerializable):
            raise ValueError("class is not a subclass")
        cls_name = d.pop(cls_key_name, None)
        if not cls:
            raise ValueError("class is not in dictionary")
        return cls.family[cls_name](**d)


def payload(cls):
    decorated = dataclass(cls, frozen=True)
    return type(decorated.__name__, (decorated, DictSerializable), {})
