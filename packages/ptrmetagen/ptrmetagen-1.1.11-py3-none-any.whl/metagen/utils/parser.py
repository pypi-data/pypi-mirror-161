from pathlib import Path
from typing import Optional, Union, List, Literal, Callable
from uuid import UUID, uuid4

from pydantic import Field, PrivateAttr, BaseModel, root_validator

from metagen.components import State
import pydantic.main


class Leaf(BaseModel):
    key: Optional[Union[UUID, str]] = Field(default_factory=uuid4)

    class Config:
        validate_assignment = True
        allow_mutation = True

    def __setattr__(self, key, value):
        return object.__setattr__(self, key, value)

    def dict(self, **ignore):
        attr_dict = self.__dict__.copy()
        key = attr_dict.pop('key')
        return {'key': str(key), 'data': {k: v for k,v in attr_dict.items() if v is not None}}

    @root_validator(pre=True)
    def prepare_date(cls, values: dict):
        if values is not None:
            data = values.pop('data')
            values.update({k: v for k, v in data.items()})
            return values
        else:
            return values


class Node(BaseModel):

    @root_validator(pre=True)
    def prepare_date(cls, values: dict):
        if values is not None:
            return values


class Application(Leaf):
    name: Optional[str]
    nameInternal: Optional[str]
    description: Optional[str]
    color: Optional[str]


class Configuration(Leaf):
    applicationKey: Optional[Union[str, Leaf]]
    nameInternal: Optional[str]
    data:  Optional[dict]


class Applications(Node):
    applications: Optional[List[Application]]
    configurations: Optional[List[Configuration]]


class Scope(Leaf):
    applicationKey: Optional[Union[str, Leaf]]
    nameInternal: Optional[str]
    nameDisplay: Optional[str]
    description: Optional[str]


class Place(Leaf):
    applicationKey: Optional[Union[str, Leaf]]
    scopeKey: Optional[UUID]
    nameInternal: Optional[str]
    nameDisplay: Optional[str]
    description: Optional[str]
    geometry: Optional[Union[dict, Path]]
    bbox: Optional[List[float]]


class LayerTemplate(Leaf):
    applicationKey: Optional[Union[str, Leaf]]
    nameInternal: Optional[str]
    nameDisplay: Optional[str]
    description: Optional[str]


class Attribute(Leaf):
    applicationKey: Optional[Union[str, Leaf]]
    nameInternal: Optional[str]
    nameDisplay: Optional[str]
    description: Optional[str]
    type: Optional[Literal['numeric', 'text', 'bool']]
    unit: Optional[str]
    valueType: Optional[str]
    color: Optional[str]


class Period(Leaf):
    applicationKey: Optional[Union[str, Leaf]]
    scopeKey: Optional[UUID]
    nameInternal: Optional[str]
    nameDisplay: Optional[str]
    description: Optional[str]
    start: Optional[str]
    end: Optional[str]
    period: Optional[str]


class Case(Leaf):
    applicationKey: Optional[Union[str, Leaf]]
    nameInternal: Optional[str]
    nameDisplay: Optional[str]
    description: Optional[str]


class Style(Leaf):
    nameDisplay: Optional[str]
    nameInternal: Optional[str]
    description: Optional[str]
    source: Optional[str]
    nameGeoserver: Optional[str]
    definition: Optional[dict]
    applicationKey: Optional[Union[str, Leaf]]
    tagKeys: Optional[UUID]


class Tag(Leaf):
    nameInternal: Optional[str]
    nameDisplay: Optional[str]
    description: Optional[str]
    color: Optional[str]
    tagKeys: Optional[List[UUID]]


class Metadata(Node):
    scopes: Optional[List[Scope]]
    places: Optional[List[Place]]
    layerTemplates: Optional[List[LayerTemplate]]
    attributes: Optional[List[Attribute]]
    periods: Optional[List[Period]]
    styles: Optional[List[Style]]
    tags: Optional[List[Tag]]
    cases: Optional[List[Case]]


# datasource
class SpatialVector(Leaf):
    nameInternal: Optional[str]
    layerName: Optional[str]
    tableName: Optional[str]
    fidColumnName: Optional[str] = Field(default='ogc_fid')
    geometryColumnName: Optional[str] = Field(default='geom')
    type: Literal['vector'] = Field(default='vector')


class SpatialWMS(Leaf):
    nameInternal: Optional[str]
    url: Optional[str]
    layers: Optional[str]
    styles: Optional[str]
    configuration: Optional[dict]
    params: Optional[dict]
    type: Literal['wms'] = Field(default='wms')


class SpatialWMTS(Leaf):
    nameInternal: Optional[str]
    urls: Optional[List[str]]
    type: Optional[Literal['wmts']] = Field(default='wmts')


class SpatialCOG(Leaf):
    nameInternal: Optional[str]
    url: Optional[str]
    type: Optional[Literal['cog']] = Field(default='cog')


class SpatialAttribute(Leaf):
    nameInternal: Optional[str]
    attribution: Optional[str]
    tableName: Optional[str]
    columnName: Optional[str]
    fidColumnName: Optional[str] = Field(default='ogc_fid')


class DataSources(Node):
    spatial: Optional[List[Union[SpatialWMS,SpatialWMTS,SpatialCOG,SpatialVector]]]
    attribute: Optional[List[SpatialAttribute]]


class RelationSpatial(Leaf):
    nameInternal: Optional[str]
    scopeKey: Optional[Union[UUID, Leaf]]
    periodKey: Optional[Union[UUID, Leaf]]
    placeKey: Optional[Union[UUID, Leaf]]
    spatialDataSourceKey: Optional[Union[UUID, Leaf]]
    layerTemplateKey: Optional[Union[UUID, Leaf]]
    applicationKey: Optional[Union[str, Leaf]]
    caseKey: Optional[Union[UUID, Leaf]]


class RelationAttribute(Leaf):
    nameInternal: Optional[str]
    scopeKey: Optional[Union[UUID, Leaf]]
    periodKey: Optional[Union[UUID, Leaf]]
    placeKey: Optional[Union[UUID, Leaf]]
    attributeDataSourceKey: Optional[Union[UUID, Leaf]]
    layerTemplateKey: Optional[Union[UUID, Leaf]]
    scenarioKey: Optional[Union[UUID, Leaf]]
    caseKey: Optional[Union[UUID, Leaf]]
    attributeSetKey: Optional[Union[UUID, Leaf]]
    attributeKey: Optional[Union[UUID, Leaf]]
    areaTreeLevelKey: Optional[Union[UUID, Leaf]]
    applicationKey: Optional[Union[str, Leaf]]


class Relations(Node):
    spatial: Optional[List[RelationSpatial]]
    attribute: Optional[List[RelationAttribute]]


class View(Leaf):
    nameInternal: Optional[str]
    applicationKey: Optional[Union[str, Leaf]]
    nameDisplay: Optional[str]
    description: Optional[str]
    state: Optional[dict]
    tagKeys: Optional[List[Union[UUID, str, Leaf]]]



class Views(Node):
    views: Optional[List[View]]


class Structure(Node):
    application: Optional[Applications]
    metadata: Optional[Metadata]
    dataSources: Optional[DataSources]
    relations: Optional[Relations]
    views: Optional[Views]


if __name__ == '__main__':
    from pathlib import Path
    from metagen.helpers import load_json
    import re
    file = Path('C:\\Users\micha\PycharmProjects\\app-esaWorldWater\\fixtures.json')
    fixtures = load_json(file)
    fix = Structure(**fixtures)

    def get_keys(array: List[Leaf], keys: dict):
        for item in array:
            keys.update({item.key: item})

    def get_relationKeys(array: List[Leaf], keys: dict):
        for item in array:
            for k, v in item.__dict__.items():
                if k.__contains__('Key'):
                    keys.update({v: item})

    def loop_structure2get(structure: Structure, keys: dict, func: Callable):
        for k, v in structure.__dict__.items():
            if v is not None:
                if isinstance(v, list):
                    func(v, keys)
                else:
                    loop_structure2get(v, keys, func)
        return keys

    def find_in(structure: list, attr, match):
        for s in structure:
            if getattr(s, attr) == match:
                return s


    key_list = loop_structure2get(fix, keys={}, func=get_keys)
    relkey_list = loop_structure2get(fix, keys={}, func=get_relationKeys)
    missed = set([v for v in relkey_list]).difference(set([v for v in key_list]))
    for mis in missed:
        print(mis)
    print(f'total: {len(missed)}')

    print('oprava:')
    for mis in missed:
        print(mis)
        element = relkey_list[mis]
        if element.nameInternal.__contains__('attributerelation'):
            matches = re.findall('([\d]{4}_[\d]{2}_[\d]{2})', element.nameInternal)

            period_str = '-'.join(matches[0].split('_'))
            periodElement =find_in(fix.metadata.periods, 'period', period_str)
            element.periodKey = periodElement.key

    new_fix = fix.dict(exclude_none=True)

    import json
    from metagen.base import UUIDEncoder

    with open(file.parent / 'new_fixtures.json', 'w') as jfile:
        json.dump(new_fix, jfile, indent=6, cls=UUIDEncoder)



