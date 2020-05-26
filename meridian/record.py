# Copyright (c) 2019 Tom Caruso & individual contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import os

from collections import OrderedDict
from operator import itemgetter
from typing import Iterable

import fiona

from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry


class Record(tuple):
    __slots__ = ()

    def __new__(cls, geom, *args, **kwargs):
        if cls.__annotations__:
            props = (
                kwargs.get(attr) or cls._defaults[attr]
                for attr, typ in cls.__annotations__.items()
            )
            return tuple.__new__(cls, (geom, *props))
        return tuple.__new__(cls, (geom,))

    def __init_subclass__(cls, **kwargs):
        if not getattr(cls, "__annotations__", None):
            cls.__annotations__ = OrderedDict()
        else:
            cls.__annotations__ = OrderedDict(cls.__annotations__)

        cls._defaults = {attr: getattr(cls, attr, None) for attr in cls.__annotations__}

        for idx, anno in enumerate(cls.__annotations__):
            setattr(cls, anno, property(itemgetter(idx + 1)))

    @classmethod
    def load_from(cls, path: str = None, geojson: Iterable[dict] = None) -> "Dataset":
        """
        Create a Dataset of the implemented model from a source, either
        a fiona-readable data file or iterable of geojson.

        Args:
            path: a path to a fiona-readable file.
            geojson: an iterable of geojson-like dictionaries

        Returns:
            A Dataset containing the items specified.
        """
        from meridian import Dataset

        if path and os.path.exists(path):
            with fiona.open(path) as src:
                return Dataset((cls.from_geojson(record) for record in src))
        elif geojson:
            return Dataset((cls.from_geojson(gj) for gj in geojson))
        else:
            raise Exception("One of path or geojson must be specified")

    @classmethod
    def from_geojson(cls, geojson):
        return cls.__new__(cls, shape(geojson["geometry"]), **geojson["properties"])

    @property
    def geom(self) -> BaseGeometry:
        return self[0]

    @property
    def _geom(self):
        """
        Adding _geom as a property allows a spatialdata to interact seamlessly
        with shapely geometries. All methods on geometries use the _geom
        property to access the underlying C geometry's pointer, so exposing
        it this way makes shapely think it's simply acting on another
        geometry object.
        """
        return self.geom._geom

    @property
    def __geo_interface__(self):
        return {
            "type": "Feature",
            "geometry": self.geom.__geo_interface__,
            "properties": OrderedDict(
                {anno: self[idx + 1] for idx, anno in enumerate(self.__annotations__)}
            ),
        }

    @property
    def bounds(self):
        return self.geom.bounds

    @property
    def geojson(self):
        return self.__geo_interface__

    def intersects(self, other):
        return self.geom.intersects(other)
