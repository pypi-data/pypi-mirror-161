import json
from abc import ABC
from pathlib import Path
from typing import Union, Any, Callable, List
import copy
from dataclasses import dataclass
from uuid import UUID


# helpe class to define and create pipileines
@dataclass
class Process(ABC):
    """Abstrac factory for processes"""

    @classmethod
    def __call__(self, *args, **kwargs):
        pass


class PipeMeta(type):
    def __new__(cls, clsname: str, superclasses: tuple, clsdict: dict):
        stac = [value for attr, value in clsdict.items() if (isinstance(value, (Process, Callable)))
                and (not attr.__contains__('__'))]
        clsdict.update(stac=stac)
        return super().__new__(cls, clsname, superclasses, clsdict)


class Pipe(metaclass=PipeMeta):

    def __call__(self, value) -> Any:
        current = value
        for method in self.stac:
            current = method(current)
        return current

# helper functions
def create_file(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def str2Path(path: Union[Path, str]) -> Path:
    if not isinstance(path, Path):
        return Path(path)
    return path


def is_exist(obj: Any) -> Any:
    if not hasattr(obj, 'exists'):
        raise AttributeError(f'Object {obj} has not "exist" method ')
    if not obj.parent.exists():
        raise ValueError(f'{obj} does not exist')
    return obj


def prepare_data_for_leaf(obj: dict) -> dict:
    new = obj.copy()
    data = new.pop('data')
    new.update(data)
    return new


def load_json(path: Union[str, Path], encoding='utf8'):
    with open(path, 'r', encoding=encoding) as file:
        return json.load(file)


def make_hash(obj):
    """ Makes a hash from a dictionary, list, tuple or set to any level, that contains
  only other hashable types (including any lists, tuples, sets, and
  dictionaries). """

    if isinstance(obj, (set, tuple, list)):
        return tuple([make_hash(e) for e in obj])

    elif not isinstance(obj, dict):

        return hash(obj)

    new_o = copy.deepcopy(obj)
    for k, v in new_o.items():
        new_o[k] = make_hash(v)

    return hash(tuple(frozenset(sorted(new_o.items()))))


def validate_list_uuid(values: Union[List[str], List[UUID]])-> List[UUID]:
    if not values:
        return values
    new = []
    for value in values:
        if isinstance(value, str):
            new.append(UUID(value))
        elif isinstance(value, UUID):
            new.append(value)
        else:
            raise ValueError(f'Validation error: {value} should be UUID or UUID string representation')
    return new


class Singleton(object):
    _instance = None
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance