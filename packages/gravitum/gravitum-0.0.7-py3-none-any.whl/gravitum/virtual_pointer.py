from typing import List, Union

from .exceptions import InvalidOperationError
from .types import ByteOrder, Integer, IntType, IntVar, UInt8
from .utils import get_type


class VirtualPointer:
    """Provide pointer operation on bytearray."""

    def __init__(
        self,
        source: bytearray,
        data_type: Union[IntType, str],
        byteorder: ByteOrder = "little",
        offset: int = 0,
    ):
        self._data_type = None

        self.source = source
        self.byteorder = byteorder
        self.offset = offset
        self.data_type = data_type

    def __add__(self, other):
        """Support addition."""
        return self.add(other)

    def __sub__(self, other):
        """Support subtraction."""
        return self.sub(other)

    @property
    def data_type(self):
        """Get data type."""
        return self._data_type

    @data_type.setter
    def data_type(self, type_or_name: Union[IntType, str]):
        """Set data type."""
        if isinstance(type_or_name, str):
            try:
                self._data_type = get_type(type_name=type_or_name)

            except ValueError as e:
                raise InvalidOperationError("Unsupported type") from e

        elif issubclass(type_or_name, Integer):
            self._data_type = type_or_name

        else:
            raise TypeError()

    def copy(self) -> "VirtualPointer":
        """Copy this object."""
        return self.__class__(
            source=self.source,
            data_type=self.data_type,
            byteorder=self.byteorder,
            offset=self.offset,
        )

    def add(self, num: int) -> "VirtualPointer":
        """Offset this pointer position."""
        obj = self.copy()
        obj.offset += num * self.data_type.get_size()
        return obj

    def sub(self, num: int) -> "VirtualPointer":
        """Reverse offset this pointer position."""
        return self.add(-num)

    def cast(self, data_type: Union[IntType, str]) -> "VirtualPointer":
        """Cast to the specified type."""
        obj = self.copy()
        obj.data_type = data_type
        return obj

    def read_bytes(self, size: int) -> bytes:
        """Read bytes from source bytearray."""
        if self.offset + size > len(self.source):
            raise InvalidOperationError("Read out of range")

        return bytes(self.source[self.offset : self.offset + size])

    def write_bytes(self, data: Union[bytes, bytearray, List[int]]):
        """Write bytes into source bytearray."""
        try:
            for i, v in enumerate(data):
                self.source[self.offset + i] = v

        except IndexError as e:
            raise InvalidOperationError("Write out of range") from e

    def read(self) -> IntVar:
        """Read an integer from source bytearray."""
        data = self.read_bytes(self.data_type.get_size())
        return self.data_type.from_bytes(data, byteorder=self.byteorder)

    def write(self, value: Union[IntVar, int]):
        """Write an integer into source bytearray."""
        data = self.data_type(value).to_bytes(byteorder=self.byteorder)
        self.write_bytes(data)


def vptr(
    source: bytearray,
    data_type: Union[IntType, str] = UInt8,
    byteorder: ByteOrder = "little",
) -> VirtualPointer:
    """Shorthand of `VirtualPointer(source, data_type)`."""
    return VirtualPointer(source=source, data_type=data_type, byteorder=byteorder)
