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
import collections
import operator
import pathlib

from typing import Tuple, Dict, Any

import fiona

from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry


class Record(Tuple[Any]):
    __slots__ = ()

    def __new__(cls, geom: BaseGeometry, *args: Any, **kwargs: Any):
        """
        Create a new Record. keyword arguments should be supplied which match the user-defined
        annotation on the class.

        Args:
            geom: A shapely geometry object
            *args:
            **kwargs: keyword arguments with names matching the user-defined annotations.
        """
        if cls.__annotations__:
            props = (
                kwargs.get(attr) or cls._defaults[attr]
                for attr, typ in cls.__annotations__.items()
            )
            return tuple.__new__(cls, (*props, geom))
        return tuple.__new__(cls, (geom,))

    def __init_subclass__(cls, **kwargs: Any) -> None:
        if not getattr(cls, "__annotations__", None):
            cls.__annotations__ = collections.OrderedDict()
        else:
            cls.__annotations__ = collections.OrderedDict(cls.__annotations__)

        cls._defaults = {attr: getattr(cls, attr, None) for attr in cls.__annotations__}

        for idx, anno in enumerate(cls.__annotations__):
            setattr(cls, anno, property(operator.itemgetter(idx)))

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(f'{k}={v!r}' for k, v in self.items())})"

    @classmethod
    def load_from(cls, src: Any, **kwargs: Any) -> "Dataset":
        """
        Create a Dataset of the implemented model from a source, either
        a fiona-readable data file or iterable of geojson.

        Args:
            src: a path to a fiona-readable file or an
                 iterable of geojson-like dictionaries
            kwargs:
                passed directly to kwargs of fiona.open()

        Returns:
            A Dataset containing the items specified.
        """
        from meridian import Dataset

        if isinstance(src, list) or hasattr(src, "__next__"):
            return Dataset((cls.from_geojson(gj) for gj in src))
        elif isinstance(src, (str, pathlib.Path)) and pathlib.Path(src).exists():
            with fiona.open(src, **kwargs) as collection:

                return Dataset(
                    (
                        cls.from_geojson(record)
                        for record in collection
                        if record["geometry"]
                    )
                )
        else:
            raise Exception("One of path or geojson must be specified")

    @classmethod
    def from_geojson(cls, geojson: Dict[str, Any]) -> "Record":
        """
        Create a new Record from a geojson-like dict.

        Args:
            geojson:

        Returns:
            A new instance of the Record subclass.
        """
        return cls.__new__(cls, shape(geojson["geometry"]), **geojson["properties"])

    @property
    def geom(self) -> BaseGeometry:
        """The geometry of the Record."""
        return self[-1]

    @property
    def _geom(self) -> Any:
        """
        Adding _geom as a property allows a Record to interact seamlessly
        with shapely geometries. All methods on geometries use the _geom
        property to access the underlying C geometry's pointer, so exposing
        it this way makes shapely think it's simply acting on another
        geometry object.
        """
        return self.geom._geom

    @property
    def __geo_interface__(self) -> Dict[str, Any]:
        """
        https://gist.github.com/sgillies/2217756
        """
        return {
            "type": "Feature",
            "geometry": self.geom.__geo_interface__,
            "properties": collections.OrderedDict(
                {anno: self[idx] for idx, anno in enumerate(self.__annotations__)}
            ),
        }

    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        """
        The bounds of the Record's geometry, as a tuple like
        (xmin, ymin, xmax, ymax)

        Returns:
            4-tuple of float
        """
        return self.geom.bounds

    @property
    def geojson(self) -> Dict[str, Any]:
        """
        Get the record as geojson

        Returns:

        """
        return self.__geo_interface__

    def items(self):
        for idx, fieldname in enumerate(self.__annotations__):
            yield fieldname, self[idx]

        yield "geom", self.geom
