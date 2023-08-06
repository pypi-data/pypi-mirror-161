from pytest import fixture
from shapely.geometry import Polygon, MultiPolygon, GeometryCollection
from geopandas import GeoDataFrame

from metagen.utils import Geometry
from metagen.utils.geometry import ShapeCollection


@fixture(autouse=True)
def polygon1():
    return Polygon([(0, 0), (1, 1), (1, 0)])


@fixture(autouse=True)
def polygon2():
    return Polygon([(0, 0), (-1, -1), (-1, 0)])


@fixture(autouse=True)
def polygon3():
    return Polygon([(0, 0), (-1, -1), (0, -1)])


@fixture(autouse=True)
def multipolygon(polygon1, polygon2, polygon3):
    return MultiPolygon([polygon1, polygon2, polygon3])


@fixture(autouse=True)
def geometry_collection(polygon1, polygon2, polygon3):
    return GeometryCollection([polygon1, polygon2, polygon3])


@fixture(autouse=True)
def geodataframe_poly(polygon1, polygon2, polygon3):
    return GeoDataFrame({'col1': ['name1', 'name2', 'name3'], 'geometry': [polygon1, polygon2, polygon3]}, crs="EPSG:4326")


# test Geometry
def test_geometry_has_geo_interface(polygon1):
    assert Geometry(data=polygon1)

    try:
        Geometry(data=1)
        assert False
    except AttributeError:
        assert True


def test_geometry_from_geopandas(geodataframe_poly, multipolygon):
    geom = Geometry(data=geodataframe_poly)
    assert geom.geometry() == multipolygon.convex_hull.__geo_interface__


def test_geometry_from_geometry_collection(geometry_collection, multipolygon):
    geom = Geometry(data=geometry_collection)
    assert geom.geometry() == multipolygon.convex_hull.__geo_interface__


def test_geometry_from_polygon(polygon1):
    geom = Geometry(data=polygon1)
    assert geom.geometry() == polygon1.convex_hull.__geo_interface__


def test_geometry_from_multipolygon(multipolygon):
    geom = Geometry(data=multipolygon)
    assert geom.geometry() == multipolygon.convex_hull.__geo_interface__

# test Colletion
def test_collection_poly(polygon1, polygon2, polygon3, multipolygon):
    collection = ShapeCollection([polygon1, polygon2, polygon3])
    assert collection.convex_hull == multipolygon.convex_hull
