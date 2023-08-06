import pytest

from metagen.metadata import Application, LayerTemplate
from .fixtures.elements import layer_template_1a, layer_template_1b, application_1a, configuration_1a, scope_1a, \
    scope_1b, place_1a, period_1a, attribute_1a, spatial_wms_1a, case_1a, relation_spatial_1a, spatial_attribute_1a, \
    spatial_wmts_1a, spatial_vector_1a, style_1a, tag_1a, relation_attribute_1a


def test_element_duplicity(layer_template_1a, layer_template_1b):
    assert layer_template_1a.key == layer_template_1b.key


def test_hashbility(layer_template_1a, application_1a, configuration_1a, scope_1a, place_1a, period_1a, attribute_1a,
                    spatial_wms_1a, case_1a, relation_spatial_1a, spatial_attribute_1a, spatial_wmts_1a,
                    spatial_vector_1a, style_1a, tag_1a, relation_attribute_1a):
    assert hash(layer_template_1a)
    assert hash(application_1a)
    assert hash(configuration_1a)
    assert hash(scope_1a)
    assert hash(place_1a)
    assert hash(period_1a)
    assert hash(attribute_1a)
    assert hash(spatial_wms_1a)
    assert hash(case_1a)
    assert hash(relation_spatial_1a)
    assert hash(spatial_attribute_1a)
    assert hash(spatial_wmts_1a)
    assert hash(spatial_vector_1a)
    assert hash(style_1a)
    assert hash(tag_1a)
    assert hash(relation_attribute_1a)


def test_hash_independence_on_order_of_tagKeys(scope_1a,scope_1b):
    assert hash(scope_1a) == hash(scope_1b)


def test_stac_attribute_in_leaf():
    app = Application(name='test', nameInternal='test')
    assert hasattr(app, '_input_pars')
    assert app._input_pars == ['name', 'nameInternal']


def test_exlude_stac_attribute_from_leaf():
    app = Application(name='test', nameInternal='test')
    dict = app.dict()
    assert dict.get('_input_pars') is None


def test_to_dict():
    """testing of exluding atributes with none values except those specified as none during the inicialization"""
    lt = LayerTemplate(applicationKey=None, nameInternal='test')
    lt_dict = lt.to_dict()
    data = lt_dict.get('data')
    assert all([k in ['applicationKey', 'nameInternal'] for k in data.keys()])
    assert data.get('applicationKey') is None


# def test_refresh_hash():
#     lt1 = LayerTemplate(applicationKey='app_test', nameInternal=f'lt', nameDisplay='lt')
#     lt2 = LayerTemplate(applicationKey='app', nameInternal=f'lt', nameDisplay='lt')
#     lt2.nameDisplay= 'app_test'
#     assert hash(lt1) == hash(lt2)
