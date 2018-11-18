import rtree
import typing

from collections import namedtuple
from shapely import geometry


def _get_namedtuple_factory(geojson: dict) -> typing.Callable:
    """
    Create a factory which will create spatialdata named tuples for the user's input data.

    Args:
        fields: the fields in the user's data

    Returns:
        factory: a factory function which will create spatialdata from geojson objects.
    """

    fields = list(geojson.get('properties', {}).keys())

    spatial_data = namedtuple('spatialdata', field_names=set(fields + ['id', 'geom', 'bounds']))

    def with_id_factory(geojson: dict, idx: int):
        props = geojson.get('properties', {})
        geom = geometry.shape(geojson.get('geometry'))

        return spatial_data(id=geojson.get('id'), geom=geom, bounds=geom.bounds, **props)

    def without_id_factory(geojson: dict, idx: int):
        props = geojson.get('properties', {})
        geom = geometry.shape(geojson.get('geometry'))

        return spatial_data(id=idx, geom=geom, bounds=geom.bounds, **props)

    if 'id' in geojson:
        return with_id_factory

    return without_id_factory


def _check_bounds(query):
    if not hasattr(query, 'bounds'):
        raise AttributeError("Query argument to SpatialData methods must implement bounds property returning (xmin, ymin, xmax, ymax)")


def spatialdata_to_geojson(spatialdata):
    """
    Helper function to convert a spatial data object back into GeoJSON. Mostly provided in the situation where a user
    wishes to build up a new SpatialDataset with a subset of data from an existing one, or with processing added.

    Args:
        spatialdata: a `meridian` spatialdata namedtuple

    Returns:
        dict - GeoJSON representation of the spatialdata object

    """
    d = spatialdata._asdict()
    del d['bounds']
    return {
        'type': 'Feature',
        'id': d.pop('id'),
        'geometry': d.pop('geom').__geo_interface__,
        'properties': {**d}
    }


class SpatialDataset:
    """
    The SpatialDataset is the core piece of the library. It wraps spatial data and exposes methods to manage it.

    The properties kwarg allows the user to specify the properties of the underlying index, if they so choose.

    """

    def __init__(self, data: typing.Iterable, properties: rtree.index.Property=None):
        self.__data = dict()
        self.__rtree: rtree.Rtree = None

        self.__load(data, properties)

    def __len__(self):
        return len(self.__data)

    def __iter__(self):
        return iter(self.__data.values())

    @property
    def bounds(self):
        """
        The bounds of the SpatialDataset.

        Returns: 4-tuple (xmin, ymin, xmax, ymax
        """
        return self.__rtree.bounds

    def __load(self, data_stream, properties=None):
        factory = None
        for idx, geojson in enumerate(data_stream):
            if not factory:
                factory = _get_namedtuple_factory(geojson)

            record = factory(geojson, idx)
            self.__data[idx] = record

        if not properties:
            properties = rtree.index.Property()
            properties.dimension = 2
            properties.leaf_capacity = 1000
            properties.fill_factor = 0.9

        self.__rtree = rtree.Rtree(((idx, sd.bounds, None) for idx, sd in self.__data.items()), properties=properties)

    def intersects(self, query) -> bool:
        """
        Check if the SpatialDataset intersects with the query object.
        Args:
            query:

        Returns:
            bool

        """
        _check_bounds(query)
        return self.__rtree.count(query.bounds) != 0

    def intersection(self, query):
        """
        Find the intersection of the input geometry / spatial data and the SpatialDataset.

        Args:
            query: an object which exposes a `bounds` property of the (xmin, ymin, xmax, ymax) format.

        Returns:
            generator of intersecting objects
        """
        _check_bounds(query)
        return (self.__data[i] for i in self.__rtree.intersection(query.bounds))

    def count(self, query) -> int:
        """
        Count the number of objects in the SpatialDataset which intersect with the query object.

        Args:
            query: an object which exposes a `bounds` property of the (xmin, ymin, xmax, ymax) format.

        Returns:
            int
        """
        _check_bounds(query)
        return self.__rtree.count(query.bounds)

    def nearest(self, query, num_results=1):
        """
        Find the nearest n objects in the SpatialDataset to the query object.

        Args:
            query:
            num_results:

        Returns:

        """
        _check_bounds(query)
        return self.__rtree.nearest(query.bounds, num_results)
