"""Implementation of the h5py-like Bliss Data API with static HDF5 files"""

from typing import Any, Iterator, Tuple, Union
from numpy.typing import DTypeLike
import h5py
from silx.io import h5py_utils
from . import abstract

SEP = "/"


class Attributes(abstract.Attributes):
    """Node attributes."""

    def __init__(self, attrs: h5py.AttributeManager) -> None:
        self.__attrs = attrs
        super().__init__()

    def __getitem__(self, key: str) -> Any:
        return self.__attrs[key]

    def __iter__(self) -> Iterator[Any]:
        return iter(self.__attrs)

    def __len__(self) -> int:
        return len(self.__attrs)


class Node:
    """Node in the data tree."""

    def __init__(self, h5py_obj: Union[h5py.Group, h5py.Dataset]) -> None:
        self._h5py_obj = h5py_obj
        self.__attrs = None
        self.__parent = None
        self.__root = None
        super().__init__()

    @property
    def name(self) -> str:
        return self._h5py_obj.name

    @property
    def short_name(self) -> str:
        return self.name.split(SEP)[-1]

    @property
    def parent(self) -> "Group":
        if self.__parent is None:
            self.__parent = Group(self._h5py_obj.parent)
        return self.__parent

    @property
    def root(self) -> "Root":
        if self.__root is None:
            self.__root = Root(self._h5py_obj.file)
        return self.__root

    @property
    def attrs(self) -> Attributes:
        if self.__attrs is None:
            self.__attrs = Attributes(self._h5py_obj.attrs)
        return self.__attrs


class Group(Node, abstract.Group):
    """Node in the data tree which contains other nodes."""

    def __getitem__(self, key: str) -> Node:
        h5py_obj = self._h5py_obj[key]
        if isinstance(h5py_obj, h5py.Group):
            return Group(h5py_obj)
        else:
            return Dataset(h5py_obj)

    def __iter__(self) -> Iterator[Node]:
        return iter(self._h5py_obj)

    def __len__(self) -> int:
        return len(self._h5py_obj)


class Dataset(Node, abstract.Dataset):
    """Node in the data tree which contains data."""

    def __getitem__(self, idx: abstract.DataIndexType) -> abstract.DataType:
        return self._h5py_obj[idx]

    def __len__(self) -> int:
        return len(self._h5py_obj)

    @property
    def dtype(self) -> DTypeLike:
        return self._h5py_obj.dtype

    @property
    def shape(self) -> Tuple[int]:
        return self._h5py_obj.shape

    @property
    def size(self) -> int:
        return self._h5py_obj.size

    @property
    def ndim(self) -> int:
        return self._h5py_obj.ndim


class Root(Group, abstract.Root):
    """Root node in the data tree."""

    def __init__(self, file: str, **openargs) -> None:
        if isinstance(file, str):
            file = h5py_utils.File(file, **openargs)
        super().__init__(file)

    def close(self) -> None:
        self._h5py_obj.close()

    @property
    def parent(self) -> None:
        return None

    @property
    def root(self) -> "Root":
        return self

    @property
    def short_name(self) -> str:
        return self.name
