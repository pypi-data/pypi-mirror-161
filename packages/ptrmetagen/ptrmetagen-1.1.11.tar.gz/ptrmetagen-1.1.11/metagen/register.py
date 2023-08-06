from abc import ABC, abstractmethod
from uuid import UUID
from typing import Type, Any, List, Dict
from pydantic import BaseModel, Field

from metagen.base import LeafABC
from metagen.helpers import Singleton


class RegisterABC(BaseModel, ABC):

    @abstractmethod
    def get_elements(self) -> List[Type[LeafABC]]:
        pass

    @abstractmethod
    def add(self, element: Type[LeafABC]) -> None:
        pass

    @abstractmethod
    def update(self, attrName: str, value: Any)-> None:
        pass

    @abstractmethod
    def check_register(self, element: Type[LeafABC]) -> bool:
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Type[LeafABC]:
        pass

    @abstractmethod
    def get_by_hash(self, hash: int) -> Type[LeafABC]:
        pass

    @abstractmethod
    def get_by_uuid(self, uuid: UUID) -> Type[LeafABC]:
        pass

    class Config:
        arbitrary_types_allowed = True


# register
class DictRegister(RegisterABC, Singleton):
    hashs: dict = Field(default_factory=dict)
    uuid: dict = Field(default_factory=dict)
    name: dict = Field(default_factory=dict)

    def get_elements(self) -> List[Type[LeafABC]]:
        return [element for element in self.hashs.values()]

    def add(self, element: Type[LeafABC]) -> None:
        if not self.check_register(element):
            self.hashs.update({hash(element): element})
            self.uuid.update({str(element.key): element})
            self.name.update({element.nameInternal: element})
        else:
            raise ValueError(f'PTR element "{element.__class__.__name__}" with nameInternal: {element.nameInternal}, '
                             f'key: {element.key} and hash: {hash(element)} already exist')

    def update(self, attrName: str, value: Any)-> None:
        raise NotImplementedError()

    def check_register(self, element: Type[LeafABC]) -> bool:
        return all([self.hashs.get(hash(element)), self.name.get(element.nameInternal)])

    def get_by_name(self, name: str) -> Type[LeafABC]:
        return self.name.get(name)

    def get_by_hash(self, hash: int) -> Type[LeafABC]:
        return self.hashs.get(hash)

    def get_by_uuid(self, uuid: str) -> Type[LeafABC]:
        if UUID(uuid):
            return self.uuid.get(uuid)


class RegisterFactory(BaseModel):
    registers: Dict[str, Type[RegisterABC]] = Field(default_factory=dict)

    def add(self, registerName: str, registerType: Type[RegisterABC]) -> None:
        self.registers.update({registerName: registerType})

    def get(self, registerName: str, **ignore) -> Type[RegisterABC]:
        return self.registers[registerName]


register_factory = RegisterFactory()
register_factory.add(registerName='dict', registerType=DictRegister)
