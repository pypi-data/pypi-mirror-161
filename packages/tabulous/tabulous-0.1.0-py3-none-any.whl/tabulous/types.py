from __future__ import annotations
from typing import (
    Any,
    Callable,
    Iterable,
    NewType,
    Sequence,
    Tuple,
    List,
    TypeVar,
    Union,
    TYPE_CHECKING,
    NamedTuple,
    SupportsIndex,
)
from typing_extensions import Annotated
from enum import Enum
import weakref

import numpy as np
from numpy.typing import ArrayLike

if TYPE_CHECKING:
    import pandas as pd
    from .widgets import TableBase

    _TableLike = Union[pd.DataFrame, dict, Iterable, ArrayLike]
else:
    _TableLike = Any


__all__ = [
    "TableData",
    "TableColumn",
    "TableDataTuple",
    "TableInfo",
    "TablePosition",
    "ItemInfo",
    "HeaderInfo",
    "SelectionRanges",
    "SelectionType",
]

if TYPE_CHECKING:
    TableData = NewType("TableData", pd.DataFrame)
    TableColumn = NewType("TableColumn", pd.Series)
else:
    TableData = NewType("TableData", Any)
    TableColumn = NewType("TableColumn", Any)

TableDataTuple = NewType("TableDataTuple", tuple)


class TableInfoAlias(type):
    def __getitem__(cls, names: str | tuple[str, ...]):
        if isinstance(names, str):
            names = (names,)
        else:
            for name in names:
                if not isinstance(name, str):
                    raise ValueError(
                        f"Cannot subscribe type {type(name)} to TableInfo."
                    )

        return Annotated[TableInfoInstance, {"column_choice_names": names}]


class TableInfo(metaclass=TableInfoAlias):
    """
    A generic type to describe a DataFrame and its column names.

    ``TableInfo["x", "y"]`` is equivalent to ``tuple[pd.DataFrame, str, str]``
    with additional information for magicgui construction.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(f"Type {cls.__name__} cannot be instantiated.")


class TableInfoInstance(Tuple["pd.DataFrame", List[str]]):
    def __new__(cls, *args, **kwargs):
        raise TypeError(f"Type {cls.__name__} cannot be instantiated.")


def _check_tuple_of_slices(value: Any) -> tuple[slice, slice]:
    v0, v1 = value
    if isinstance(v0, slice) and isinstance(v1, slice):
        if v0.step and v0.step != 1:
            raise ValueError("Cannot set slice with step.")
        if v1.step and v1.step != 1:
            raise ValueError("Cannot set slice with step.")
        return tuple(value)
    else:
        raise TypeError(f"Invalid input: ({type(v0)}, {type(v1)}).")


class SelectionRanges(Sequence[tuple[slice, slice]]):
    """A table data specific selection range list."""

    def __init__(self, data: TableBase, ranges: Iterable[tuple[slice, slice]] = ()):
        self._ranges = list(ranges)
        self._data_ref = weakref.ref(data)

    def __repr__(self) -> str:
        rng_str: list[str] = []
        for rng in self:
            r, c = rng
            rng_str.append(f"[{r.start}:{r.stop}, {c.start}:{c.stop}]")
        return f"{self.__class__.__name__}({', '.join(rng_str)})"

    def __getitem__(self, index: int) -> tuple[slice, slice]:
        """The selected range at the given index."""
        return self._ranges[index]

    def __len__(self) -> int:
        """Number of selections."""
        return len(self._ranges)

    def __iter__(self):
        """Iterate over the selection ranges."""
        return iter(self._ranges)

    @property
    def values(self) -> SelectedData[TableBase]:
        return SelectedData(self)


_T = TypeVar("_T", bound="TableBase")


class SelectedData(Sequence[_T]):
    """Interface with the selected data."""

    def __init__(self, obj: SelectionRanges):
        self._obj = obj

    def __getitem__(self, index: int) -> _T:
        """Get the selected data at the given index of selection."""
        data = self._obj._data_ref().data
        sl = self._obj[index]
        return data.iloc[sl]

    def __len__(self) -> int:
        """Number of selections."""
        return len(self._obj)

    def __iter__(self) -> Iterable[_T]:
        return (self[i] for i in range(len(self)))


FilterType = Union[Callable[["pd.DataFrame"], np.ndarray], np.ndarray]


class TabPosition(Enum):
    """Enum for tab position."""

    top = "top"
    left = "left"
    bottom = "bottom"
    right = "right"


class ItemInfo(NamedTuple):
    """A named tuple for item update."""

    row: int | slice
    column: int | slice
    value: Any
    old_value: Any


class HeaderInfo(NamedTuple):
    """A named tuple for header update."""

    index: int
    value: Any
    old_value: Any


_Sliceable = Union[SupportsIndex, slice]
_SingleSelection = Tuple[_Sliceable, _Sliceable]
SelectionType = List[_SingleSelection]
