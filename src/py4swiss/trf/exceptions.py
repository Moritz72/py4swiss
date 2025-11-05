class LineException(Exception):
    """Parsing exception in a line of a TRF file."""

    def __init__(self, message: str, column: int | None = None) -> None:
        """Initialize the exception."""
        self.message = message
        self.column = column
        super().__init__(message)


class ParsingException(Exception):
    """Parsing exception in a TRF file."""

    def __init__(self, message: str, line: int | None = None, column: int | None = None) -> None:
        """Initialize the exception."""
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.__str__())

    def __str__(self) -> str:
        """Get the exact location of the cause of the exception."""
        location = ""
        if self.line is not None:
            location += f"Line {self.line}"
        if self.column is not None:
            location += f", Column {self.column}" if location else f"Column {self.column}"
        return f"{self.message}" + (f" ({location})" if location else "")


class ConsistencyException(Exception):
    """Exception due to inconsistent input in a TRF."""

    pass
