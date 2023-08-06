import typing as t
from abc import abstractmethod

import numpy as np


class Geometry:
    points: np.ndarray
    row_ptr: t.Optional[np.ndarray]
    type: str
    csr: bool = True

    def __init__(self, points, row_ptr=None):
        self.points = np.asarray(points)
        self.row_ptr = np.asarray(row_ptr) if row_ptr is not None else None

        self._verify()

    def __len__(self):
        if not self.csr:
            return self.points.shape[0]
        return self.row_ptr.size - 1

    @abstractmethod
    def _verify(self):
        raise NotImplementedError

    def as_c_input(self) -> t.Tuple[np.ndarray, np.ndarray, str]:
        row_ptr = self.row_ptr if self.csr else np.array([0], dtype=np.uint32)
        return self.points, row_ptr, self.type


class PointGeometry(Geometry):
    type = "point"
    csr = False

    def _verify(self):
        if self.row_ptr is not None:
            raise ValueError("PointGeometry can't have row_ptr")


class LinestringGeometry(Geometry):
    type = "linestring"

    def _verify(self):
        if self.row_ptr is None:
            raise ValueError("LinestringGeometry needs row_ptr")


class OpenPolygonGeometry(Geometry):
    type = "open_polygon"

    def _verify(self):
        if self.row_ptr is None:
            raise ValueError("OpenPolygonGeometry needs row_ptr")


class ClosedPolygonGeometry(Geometry):
    type = "closed_polygon"

    def _verify(self):
        if self.row_ptr is None:
            raise ValueError("ClosedPolygonGeometry needs row_ptr")
