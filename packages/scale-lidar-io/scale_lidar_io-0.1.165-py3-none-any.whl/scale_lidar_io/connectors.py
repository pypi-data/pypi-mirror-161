from abc import ABCMeta, abstractmethod

import numpy as np
import open3d as o3d
import pandas as pd
from laspy.file import File

_FIELDS = ["x", "y", "z", "i", "d"]


class Importer:
    """Points importer/helper"""

    class Base(metaclass=ABCMeta):
        """Abstract importer class to be inherited for data type specific implementation"""

        def __init__(self, fp: str) -> None:
            """Constructor to be called for preparing filepaths

            :param fp: Relative or absolute path to file to be loaded in explicit `load` method
            :type fp: str
            """
            self._filepath: str = fp
            self._data: pd.DataFrame = pd.DataFrame(columns=_FIELDS)

        def load(self, **kwargs) -> None:
            self._load(**kwargs)

        @property
        def data(self):
            return self._data.to_numpy()

        @abstractmethod
        def _load(self, **kwargs) -> None:
            ...

    class CSV(Base, metaclass=ABCMeta):
        """Metaclass for specific CSV Importer implementations.
        Due to non-standardized csv format, it is recommended to write more specific implementations on a case-by-case basis.
        """

        @abstractmethod
        def _load(self, **kwargs):
            ...

    class OrderedCSV(CSV):
        """Expects a csv file with or without header, but assumes correct order of columns / values as follows: `[x, y, z, i, d]`
        Cuts off any exceeding column count.
        """

        def _load(self, **kwargs):
            self._data = pd.read_csv(self._filepath, **kwargs)
            c_count = len(self._data.columns)
            if c_count > 5:  # Remove columns exceeding count of FIELDS
                self._data = self._data.drop(self._data.columns[5:], axis=1)
                c_count = 5

            self._data.columns = _FIELDS[:c_count]

    class NamedCSV(CSV):
        """Expects a csv file with header row and column names matching `x`, `y`, `z`, `i`, `d`
        Dismisses any columns not matching any of the expected names. Case-sensitive.
        """

        def _load(self, **kwargs):
            self._data = pd.read_csv(self._filepath, **kwargs)
            exists = []
            for c in _FIELDS:
                if c in self._data.columns:
                    exists.append(c)
            self._data = self._data[exists]

    class PCD(Base):
        """Uses open3d library to read pcd files, expects `[x, y, z]`, dismisses other columns."""

        def _load(self, **kwargs):
            self._data = pd.DataFrame(
                np.asarray(o3d.io.read_point_cloud(self._filepath).points)[:, :3],
                columns=_FIELDS[:3],
            )

    class LAS(Base):
        """Uses Laspy library to read .las file and expects properties `x`, `y`, `z`, `intensity` to be present."""

        def _load(self, **kwargs):
            las_file = File(self._filepath, mode="r")
            self._data = pd.DataFrame(
                np.column_stack(
                    [las_file.x, las_file.y, las_file.z, las_file.intensity]
                ),
                columns=["x", "y", "z", "i"],
            )
