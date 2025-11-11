class LineError(Exception):
    """Parsing error in a line of a TRF file."""

    def __init__(self, message: str, column: int | None = None) -> None:
        """Initialize a new error."""
        self.message = message
        self.column = column
        super().__init__(message)


class ParsingError(Exception):
    """Parsing error in a TRF file."""

    def __init__(self, message: str, row: int | None = None, column: int | None = None) -> None:
        """Initialize a new error."""
        self.message = message
        self.row = row
        self.column = column
        super().__init__(self.__str__())

    def __str__(self) -> str:
        """Return the exact location of the cause of the exception."""
        location = ""
        if self.row is not None:
            location += f"Row {self.row}"
        if self.column is not None:
            location += f", Column {self.column}" if location else f"Column {self.column}"
        return f"{self.message}" + (f" ({location})" if location else "")


class ConsistencyError(Exception):
    """Error due to inconsistent input in a TRF."""

    pass
