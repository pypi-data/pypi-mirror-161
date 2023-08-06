from pydantic import BaseModel, Field, root_validator, validator, PrivateAttr
from typing import Optional, Union, List, Literal, Tuple, Type
from pathlib import Path
from inspect import signature
from uuid import UUID, uuid4

from metagen.base import LeafABC, FactoryABC
from metagen.helpers import prepare_data_for_leaf, make_hash, validate_list_uuid
from metagen.components import State
from metagen.main import exist_in_register


# base class
class Leaf(LeafABC):
    key: Optional[Union[UUID, str]] = Field(default_factory=uuid4)
    _input_pars: List[str] = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._input_pars = [k for k in data.keys()]

    def to_dict(self):
        include = {k for k, v in self.__dict__.items() if k in self._input_pars or v is not None}
        exlude = {k for k in self.__dict__.keys()} - include
        data = self.dict(by_alias=True, exclude=exlude, include=include)
        key = data.pop('key')
        return {"key": str(key), "data": data}

    @root_validator(pre=True, allow_reuse=True)
    def set_key(cls, values: dict) -> dict:
        return {k: (v.key if isinstance(v, Leaf) else v) for k, v in values.items()}

    @property
    def hash_attrs(self) -> tuple:
        return tuple()

    def __nodes__(self) -> str:
        pass

    def __hash__(self) -> int:
        # return hash(tuple([self.__dict__.get(attr) if not isinstance(self.__dict__.get(attr), list)
        #                            else tuple(self.__dict__.get(attr)) for attr in self.hash_attrs]))
        return make_hash({k: v for k, v in self.__dict__.items() if k in self.hash_attrs})

    def __setattr__(self, attrName, value):
        super(Leaf, self).__setattr__(attrName, value)

    __slots__ = ('__weakref__',)

    class Config:
        validate_assignment = True


# metadata
@exist_in_register
class Application(Leaf):

    name: str = Field(...)
    nameInternal: Optional[str]
    description: Optional[str]
    color: Optional[str]

    @root_validator()
    def set_application_key(cls, values):
        if values.get('name'):
            values['key'] = values['name']
            return values

    def __nodes__(self) -> str:
        return 'application.applications'

    @property
    def hash_attrs(self) -> tuple:
        return 'name', 'nameInternal'


@exist_in_register
class Configuration(Leaf):
    applicationKey: Optional[Union[str, Leaf]]
    nameInternal: Optional[str]
    data:  Optional[dict]

    def __nodes__(self) -> str:
        return 'application.configurations'

    @property
    def hash_attrs(self) -> tuple:
        return 'applicationKey', 'data', 'nameInternal'


@exist_in_register
class Scope(Leaf):
    applicationKey: Optional[Union[str, Leaf]]
    nameInternal: Optional[str]
    nameDisplay: Optional[str]
    description: Optional[str]
    tagKeys: Optional[Union[List[UUID], List[str]]]
    configuration: Optional[dict]

    _validate_tagKeys = validator('tagKeys', allow_reuse=True)(validate_list_uuid)

    def __nodes__(self) -> str:
        return 'metadata.scopes'

    # FIXME: add hashable configuration
    @property
    def hash_attrs(self) -> tuple:
        return 'applicationKey', 'nameDisplay', 'tagsKey', 'configuration', 'nameInternal'


@exist_in_register
class Place(Leaf):
    applicationKey: Optional[Union[str, Leaf]]
    scopeKey: Optional[UUID]
    nameInternal: Optional[str]
    nameDisplay: Optional[str]
    description: Optional[str]
    geometry: Optional[Union[dict, Path]]
    bbox: Optional[List[float]]

    def __nodes__(self) -> str:
        return 'metadata.places'

    @property
    def hash_attrs(self) -> tuple:
        return 'applicationKey', 'nameDisplay', 'scopeKey', 'nameInternal'


@exist_in_register
class LayerTemplate(Leaf):
    applicationKey: Optional[Union[str, Leaf]]
    nameInternal: Optional[str]
    nameDisplay: Optional[str]
    description: Optional[str]
    scopeKey: Optional[Union[UUID, Leaf]]
    tagKeys: Optional[Union[List[UUID], List[str]]]

    _validate_tagKeys = validator('tagKeys', allow_reuse=True)(validate_list_uuid)

    def __nodes__(self) -> str:
        return 'metadata.layerTemplates'

    @property
    def hash_attrs(self) -> tuple:
        return 'applicationKey', 'nameDisplay', 'nameInternal'


@exist_in_register
class Attribute(Leaf):
    applicationKey: Optional[Union[str, Leaf]]
    nameInternal: Optional[str]
    nameDisplay: Optional[str]
    description: Optional[str]
    type: Optional[Literal['number', 'text', 'bool']]
    unit: Optional[str]
    valueType: Optional[str]
    color: Optional[str]

    def __nodes__(self) -> str:
        return 'metadata.attributes'

    @property
    def hash_attrs(self) -> tuple:
        return 'applicationKey', 'nameDisplay', 'type', 'nameInternal'


@exist_in_register
class Period(Leaf):
    applicationKey: Optional[Union[str, Leaf]]
    scopeKey: Optional[UUID]
    nameInternal: Optional[str]
    nameDisplay: Optional[str]
    description: Optional[str]
    start: Optional[str]
    end: Optional[str]
    period: Optional[str]

    @root_validator(pre=True)
    def handle_prtData_input(cls, values):
        if all([key not in values for key in ['period', 'start', 'end']]):
            raise ValueError('Period has to have period or start and end parameters')
        elif 'period' not in values and any([key not in values for key in ['start', 'end']]):
            raise ValueError('Period has to have defined start and end parameters')
        else:
            return values

    def __nodes__(self) -> str:
        return 'metadata.periods'

    @property
    def hash_attrs(self) -> tuple:
        return 'applicationKey', 'nameDisplay', 'period', 'start', 'end', 'nameInternal'


@exist_in_register
class Case(Leaf):
    applicationKey: Optional[Union[str, Leaf]]
    nameInternal: Optional[str]
    nameDisplay: Optional[str]
    description: Optional[str]
    tagKeys: Optional[Union[List[UUID], List[str]]]

    _validate_tagKeys = validator('tagKeys', allow_reuse=True)(validate_list_uuid)

    def __nodes__(self) -> str:
        return 'metadata.cases'

    @property
    def hash_attrs(self) -> tuple:
        return 'applicationKey', 'nameDisplay', 'nameInternal', 'tagKeys'


@exist_in_register
class Style(Leaf):
    nameDisplay: Optional[str]
    nameInternal: Optional[str]
    description: Optional[str]
    source: Optional[str]
    nameGeoserver: Optional[str]
    definition: Optional[dict]
    applicationKey: Optional[Union[str, Leaf]]
    tagKeys: Optional[UUID]

    def __nodes__(self) -> str:
        return 'metadata.styles'

    @property
    def hash_attrs(self) -> tuple:
        return 'nameDisplay', 'description', 'source', 'nameGeoserver', 'applicationKey', 'tagKeys', 'definition', \
               'nameInternal'


@exist_in_register
class Tag(Leaf):
    nameInternal: Optional[str]
    nameDisplay: Optional[str]
    description: Optional[str]
    color: Optional[str]
    tagKeys: Optional[Union[List[UUID], List[str]]]

    _validate_tagKeys = validator('tagKeys', allow_reuse=True)(validate_list_uuid)

    def __nodes__(self) -> str:
        return 'metadata.tags'

    @property
    def hash_attrs(self) -> tuple:
        return 'nameDisplay', 'tagKeys', 'nameInternal'


# datasource


@exist_in_register
class SpatialVector(Leaf):
    nameInternal: Optional[str]
    layerName: Optional[str]
    tableName: Optional[str]
    fidColumnName: Optional[str] = Field(default='ogc_fid')
    geometryColumnName: Optional[str] = Field(default='geom')
    type: Literal['vector'] = Field(default='vector')

    def __nodes__(self) -> str:
        return 'dataSources.spatial'

    @property
    def hash_attrs(self) -> tuple:
        return 'type', 'layerName', 'tableName', 'fidColumnName', 'geometryColumnName', 'nameInternal'


@exist_in_register
class SpatialWMS(Leaf):
    nameInternal: Optional[str]
    url: Optional[str]
    layers: Optional[str]
    styles: Optional[str]
    configuration: Optional[dict]
    params: Optional[dict]
    attribution: Optional[str]
    type: Literal['wms'] = Field(default='wms')

    def __nodes__(self) -> str:
        return 'dataSources.spatial'

    @property
    def hash_attrs(self) -> tuple:
        return 'url', 'layers', 'styles', 'params', 'configuration', 'type', 'attribution', 'nameInternal'


@exist_in_register
class SpatialWMTS(Leaf):
    nameInternal: Optional[str]
    urls: Optional[List[str]]
    type: Literal['wmts'] = Field(default='wmts')

    def __nodes__(self) -> str:
        return 'dataSources.spatial'

    @property
    def hash_attrs(self) -> tuple:
        return 'urls', 'type'


@exist_in_register
class SpatialCOG(Leaf):
    nameInternal: Optional[str]
    url: Optional[str]
    type: Literal['cog'] = Field(default='cog')

    def __nodes__(self) -> str:
        return 'dataSources.spatial'

    @property
    def hash_attrs(self) -> tuple:
        return 'url', 'type', 'nameInternal'


@exist_in_register
class SpatialAttribute(Leaf):
    """
    Spatial attribute is used to create link on data stored in PostgreSQL Database.
    Element attribute:
     - nameInternal: Optional[str] : internal name of element, unique
     - attribution: Optional[str] : '''todo: add description'''
     - tableName: Optional[str] : PostgreSQL table name
     - columnName: Optional[str] : PostgreSQL column name
     - fidColumnName: Optional[str] : PostgreSQL fid column name
    """
    nameInternal: Optional[str]
    attribution: Optional[str]
    tableName: Optional[str]
    columnName: Optional[str]
    fidColumnName: Optional[str] = Field(default='ogc_fid')

    def __nodes__(self) -> str:
        return 'dataSources.attribute'

    @property
    def hash_attrs(self) -> tuple:
        return 'attribution', 'tableName', 'columnName', 'fidColumnName', 'nameInternal'


# relations
@exist_in_register
class RelationSpatial(Leaf):
    nameInternal: Optional[str]
    scopeKey: Optional[Union[UUID, Leaf]]
    periodKey: Optional[Union[UUID, Leaf]]
    placeKey: Optional[Union[UUID, Leaf]]
    spatialDataSourceKey: Optional[Union[UUID, Leaf]]
    layerTemplateKey: Optional[Union[UUID, Leaf]]
    applicationKey: Optional[Union[str, Leaf]]
    caseKey: Optional[Union[UUID, Leaf]]
    scenarioKey: Optional[Union[UUID, Leaf]]

    def __nodes__(self) -> str:
        return 'relations.spatial'

    @property
    def hash_attrs(self) -> tuple:
        return 'scopeKey:', 'periodKey', 'placeKey', 'spatialDataSourceKey', 'layerTemplateKey', 'applicationKey', \
               'caseKey', 'scenarioKey', 'nameInternal'


@exist_in_register
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

    def __nodes__(self) -> str:
        return 'relations.attribute'

    @property
    def hash_attrs(self) -> tuple:
        return 'scopeKey:', 'periodKey', 'placeKey', 'attributeDataSourceKey', 'layerTemplateKey', 'scenarioKey', \
               'caseKey', 'attributeSetKey', 'attributeKey', 'areaTreeLevelKey', 'applicationKey', 'nameInternal'

# views


@exist_in_register
class View(Leaf):
    nameInternal: Optional[str]
    applicationKey: Optional[Union[str, Leaf]]
    nameDisplay: Optional[str]
    description: Optional[str]
    state: Optional[State]
    tagKeys: Optional[List[Union[UUID, str, Leaf]]]

    def __nodes__(self) -> str:
        return 'views.views'

    @property
    def hash_attrs(self) -> tuple:
        return 'applicationKey', 'nameDisplay', 'state', 'tagKeys', 'nameInternal'

    @validator('tagKeys', pre=True)
    def set_tagKey(cls, values):
        return [value.key if isinstance(value, Leaf) else value for value in values]


class ElementSignature(BaseModel):
    parameters: Tuple[str, ...]
    type: Optional[str]

    @root_validator(pre=True)
    def get_pars_from_signature(cls, values)-> tuple:
        element = values.get('parameters')
        try:
            values['parameters'] = tuple([pars for pars in signature(element).parameters])
        except TypeError:
            values['parameters'] = tuple([pars for pars in signature(element.__wrapped__).parameters])

        try:
            values['type'] = element.__fields__.get('type').default
        except AttributeError:
            pass

        return values

    def check_signature(self, input_parameters: List[str]) -> bool:
        if self.type:
            if self.type != input_parameters.get('type'):
                return False

        return all([True if k in self.parameters else False for k in input_parameters.keys()])

    def __hash__(self):
        return hash(self.parameters)


class ElementFactory(FactoryABC, BaseModel):
    elements_register: dict = Field(default_factory=dict)


    def add(self, element: Type[Leaf]) -> None:
        element_signature = ElementSignature(parameters=element)

        if not self.elements_register.get(element.__nodes__(self)):
            self.elements_register.update({element.__nodes__(self): {}})

        self.elements_register[element.__nodes__(self)].update({element_signature: element})

    def _get_element_types(self, nodes: str) -> dict:
        try:
            return self.elements_register[nodes]
        except KeyError:
            raise NotImplementedError(f'No elements for node {nodes}')

    @staticmethod
    def _find_element_by_signature(element_types: dict, init_data: dict)-> Optional[LeafABC]:
        for signature, element in element_types.items():
            if signature.check_signature(init_data):
                return element
        return None

    def create(self, nodes: str, data: dict) -> LeafABC:
        element_types = self._get_element_types(nodes)
        init_data = prepare_data_for_leaf(data)
        element = self._find_element_by_signature(element_types, init_data)
        if element:
            return element(**init_data)
        else:
            raise ValueError(f'No element signature match input element parameters '
                             f'{", ".join([par for par in init_data])} and nodes: {nodes} ')








element_factory = ElementFactory()
element_factory.add(Application)
element_factory.add(Configuration)
element_factory.add(Scope)
element_factory.add(Place)
element_factory.add(LayerTemplate)
element_factory.add(Attribute)
element_factory.add(Period)
element_factory.add(Case)
element_factory.add(Style)
element_factory.add(SpatialVector)
element_factory.add(SpatialWMS)
element_factory.add(SpatialWMTS)
element_factory.add(SpatialAttribute)
element_factory.add(RelationSpatial)
element_factory.add(RelationAttribute)
element_factory.add(View)
element_factory.add(Tag)
element_factory.add(SpatialCOG)
