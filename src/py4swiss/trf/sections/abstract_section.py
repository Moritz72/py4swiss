from abc import ABC
from enum import Enum
from typing import ClassVar, TypeVar, cast

from pydantic import BaseModel

from py4swiss.trf.exceptions import LineError

T = TypeVar("T", bound=Enum)


class Date(BaseModel):
    """
    Representation of a date in a TRF.

    Attributes:
        year (int): The year of the date
        month (int): The month of the date
        day (int): The day of the date

    """

    YEAR_LENGTH: ClassVar[int] = 4
    YEAR_LENGTH_SHORT: ClassVar[int] = 2
    MONTH_LENGTH: ClassVar[int] = 2
    DAY_LENGTH: ClassVar[int] = 2
    LENGTH: ClassVar[int] = 10
    LENGTH_SHORT: ClassVar[int] = 8

    year: int
    month: int
    day: int


class AbstractSection(BaseModel, ABC):
    """Abstract representation of a parsed section of a TRF."""

    @staticmethod
    def _serialize_string(string: str | None, padding: int = 0) -> str:
        """Return a string representation of the given string with optional padding."""
        if string is None:
            return padding * ""

        return string.ljust(padding)

    @staticmethod
    def _serialize_integer(integer: int | None, padding: int = 0) -> str:
        """Return a string representation of the given integer with optional padding."""
        if integer is None:
            return padding * ""

        return str(integer).rjust(padding)

    @staticmethod
    def _serialize_integers(integers: list[int], padding: int = 0) -> str:
        """Return a string representation of the given integer list with optional padding."""
        parts = [AbstractSection._serialize_integer(integer, padding) for integer in integers]
        return " ".join([part for part in parts if part is not None])

    @staticmethod
    def _serialize_decimal(decimal: int | None, padding: int = 0, decimal_places: int = 1) -> str:
        """Return a string representation of the given decimal with optional padding."""
        mod = pow(10, decimal_places)
        return f"{decimal // mod}.{decimal % mod}".rjust(padding)

    @staticmethod
    def _serialize_decimals(decimals: list[int], padding: int = 0, decimal_places: int = 1) -> str:
        """Return a string representation of the given decimal list with optional padding."""
        parts = [AbstractSection._serialize_decimal(decimal, padding, decimal_places) for decimal in decimals]
        return " ".join([part for part in parts if part is not None])

    @staticmethod
    def _serialize_date(date: Date | None, short: bool = False) -> str:
        """Return a string representation of the given date."""
        if date is None:
            return Date.LENGTH * ""

        if short:
            year_string = str(date.year).zfill(Date.YEAR_LENGTH_SHORT)
        else:
            year_string = str(date.year).zfill(Date.YEAR_LENGTH)

        month_string = str(date.month).zfill(Date.MONTH_LENGTH)
        day_string = str(date.day).zfill(Date.DAY_LENGTH)

        return f"{year_string}/{month_string}/{day_string}"

    @staticmethod
    def _serialize_enum(enum: Enum | None) -> str:
        """Return a string representation of the given enum."""
        if enum is None:
            return ""

        return str(enum.value)

    @staticmethod
    def _deserialize_string(string: str) -> str | None:
        """Convert the given string to a string (or None in case of an empty string)."""
        if not bool(string.strip()):
            return None

        return string.strip()

    @staticmethod
    def _deserialize_integer(string: str, index: int = 0) -> int | None:
        """Convert the given string to an integer (or None in case of an empty string)."""
        if not bool(string.strip()):
            return None

        try:
            return int(string.lstrip())
        except ValueError as e:
            error_message = f"Invalid integer '{string}'"
            raise LineError(error_message, column=index + 1) from e

    @staticmethod
    def _deserialize_integers(string: str, index: int = 0) -> list[int]:
        """Convert the given string to a list of integers."""
        integers = []

        for part in string.split(" "):
            integer = AbstractSection._deserialize_integer(part, index)

            if integer is not None:
                integers.append(integer)

            index += len(part) + 1

        return integers

    @staticmethod
    def _deserialize_decimal(string: str, index: int = 0, decimal_places: int = 1) -> int | None:
        """Convert the given string to a decimal (or None in case of an empty string)."""
        if not bool(string.strip()):
            return None

        try:
            dot_index = -decimal_places - 1
            if string[dot_index] != ".":
                raise ValueError

            integer_part = int(string[:dot_index].lstrip() or "0")
            decimal_part = int(string[dot_index + 1 :])
            return cast("int", integer_part * pow(10, decimal_places) + decimal_part)
        except ValueError as e:
            error_message = f"Invalid decimal '{string}'"
            raise LineError(error_message, column=index + 1) from e

    @staticmethod
    def _deserialize_decimals(string: str, index: int = 0, decimal_places: int = 1) -> list[int]:
        """Convert the given string to a list of decimals."""
        decimals = []

        for part in string.split(" "):
            integer = AbstractSection._deserialize_decimal(part, index, decimal_places)

            if integer is not None:
                decimals.append(integer)

            index += len(part) + 1

        return decimals

    @staticmethod
    def _deserialize_date(string: str, index: int = 0, short: bool = False) -> Date | None:
        """Convert the given string to a date (or None in case of an empty string)."""
        if not bool(string.strip()):
            return None

        try:
            if short:
                year = int(string[: Date.YEAR_LENGTH_SHORT].strip() or 0)
                string = string[Date.YEAR_LENGTH_SHORT + 1 :]
            else:
                year = int(string[: Date.YEAR_LENGTH].strip() or 0)
                string = string[Date.YEAR_LENGTH + 1 :]

            month = int(string[: Date.MONTH_LENGTH].strip() or 0)
            string = string[Date.MONTH_LENGTH + 1 :]

            day = int(string[: Date.DAY_LENGTH].strip() or 0)
            string = string[Date.DAY_LENGTH + 1 :]

            return Date(year=year, month=month, day=day)
        except ValueError as e:
            error_message = f"Invalid date '{string}'"
            raise LineError(error_message, column=index + 1) from e

    @staticmethod
    def _deserialize_enum(string: str, enum_cls: type[T], index: int = 0) -> T | None:
        """Convert the given string to an instance of the given enum class (or None in case of an empty string)."""
        if not bool(string.strip()):
            return None

        try:
            return enum_cls(string.strip())
        except ValueError as e:
            error_message = f"Invalid {enum_cls.__name__} '{string}'"
            raise LineError(error_message, column=index + 1) from e
