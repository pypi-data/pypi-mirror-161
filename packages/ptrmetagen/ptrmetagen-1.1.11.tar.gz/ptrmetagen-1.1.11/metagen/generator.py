from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, List, Type
import json

from metagen.base import LeafABC, UUIDEncoder, FactoryABC
from metagen.helpers import create_file, load_json
from metagen.pipes import path_check
from metagen.register import RegisterABC
from metagen.importer import ImporterABC


# serialization & deserialization
class SerializerABC(BaseModel, ABC):

    @abstractmethod
    def to_dict(self):
        pass

    @abstractmethod
    def to_json(self, path: Union[Path, str]) -> None:
        pass


class JSONSerializer(SerializerABC):
    reg: RegisterABC
    structure: dict = Field(default={})

    def to_dict(self) -> dict:
        for element in self.reg.get_elements():
            nodes = element.__nodes__().split('.')
            self.set_node(self.structure, nodes, element)
        return self.structure

    def set_node(self, structure: dict, nodes: list, element: Type[LeafABC]):
        node = nodes.pop(0)
        if len(nodes) > 0:
            if not structure.get(node):
                structure[node] = {}
            self.set_node(structure[node], nodes, element)
        else:
            if not structure.get(node):
                structure[node] = []
            structure[node].append(element.to_dict())

    def to_json(self, path: Union[Path, str]) -> None:
        structure = self.to_dict()

        path = path_check(path)

        if not path.parent:
            create_file(path.parent)

        with open(path, 'w', encoding='utf-8') as file:
            json.dump(structure, file, indent=6, cls=UUIDEncoder, ensure_ascii=False)


class DeSerializerABC(BaseModel, ABC):
    factory: FactoryABC

    @abstractmethod
    def load(self, path: Union[Path, str], **kwargs) -> None:
        pass


class JSONDeserializer(DeSerializerABC):

    def load(self, path: Union[Path, str], encoding='utf8') -> None:

        path = path_check(path)
        obj = load_json(path, encoding)
        for node, structure in obj.items():
            self._parse(node, structure)

    def _parse(self, nodes: str, obj: Union[dict, list]) -> None:

        if isinstance(obj, dict):
            for node, structure in obj.items():
                self._parse(f'{nodes}.{node}', structure)
        elif isinstance(obj, list):
            for data in obj:
                self.factory.create(nodes, data)


# generator
class GeneratorABC(BaseModel, ABC):
    serializer: SerializerABC
    deserializer: DeSerializerABC
    importer: ImporterABC
    reg: RegisterABC

    @abstractmethod
    def import_fixtures(self) -> dict:
        pass

    class Config:
        arbitrary_types_allowed = True


class _Generator(GeneratorABC):
    serializer: SerializerABC
    deserializer: DeSerializerABC
    importer: ImporterABC
    reg: RegisterABC

    def import_fixtures(self) -> dict:
        return self.importer.run(self.to_dict())

    def load_fixtures(self, path: Union[Path, str], encoding='utf8') -> None:
        """Load fixtures into the register"""
        self.deserializer.load(path, encoding=encoding)

    def to_dict(self) -> dict:
        """Generate dict representation of fixtures from register"""
        return self.serializer.to_dict()

    def to_json(self, path: Union[str, Path]) -> None:
        """Generate json representation of fixtures from register"""
        self.serializer.to_json(path)

    def get_element_by_nameInternal(self, name: str) -> Type[LeafABC]:
        """Return element of given nameInternal"""
        if self.reg.get_by_name(name):
            return self.reg.get_by_name(name)
        else:
            raise ValueError(f'Element with nameInternal {name} did not find')

    def get_element_by_uuid(self, uuid: str) -> Type[LeafABC]:
        """Return element of given uuid"""
        if self.reg.get_by_uuid(uuid):
            return self.reg.get_by_uuid(uuid)
        else:
            raise ValueError(f'Element with uuid {uuid} did not find')

    def get_elements_by_type(self, element: Type[LeafABC]) -> List[Type[LeafABC]]:
        """Return list of all elements of given element type"""
        return [v for k, v in self.reg.name.items() if isinstance(v, element.__wrapped__)]

    def get_elements_by_name(self, name: str) -> List[Type[LeafABC]]:
        """Return list of elements that internal name contains part of input string"""
        return [v for k, v in self.reg.name.items() if k.__contains__(name)]