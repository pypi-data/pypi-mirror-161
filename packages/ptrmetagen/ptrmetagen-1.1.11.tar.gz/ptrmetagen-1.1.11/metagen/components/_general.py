from typing import Union, Dict, Type
from uuid import UUID
from abc import ABC
from pydantic import BaseModel

from metagen.base import LeafABC, BaseModelWithDynamicKey, set_key_from_input
from metagen.helpers import make_hash


class Component(BaseModel, ABC):
    pass

    def __hash__(self) -> int:
        return make_hash(self.dict())


class Filter(BaseModelWithDynamicKey):
    __root__: Dict[str, UUID]

    @classmethod
    def set(cls, key_name: str, key: Union[str, UUID, Type[LeafABC]]):
        uuid = set_key_from_input(key)
        return cls(**{key_name: uuid})

