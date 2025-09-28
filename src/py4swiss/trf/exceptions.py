class LineException(Exception):
    def __init__(self, message: str, column: int | None = None) -> None:
        self.message = message
        self.column = column
        super().__init__(message)


class ParsingException(Exception):
    def __init__(self, message: str, line: int | None = None, column: int | None = None) -> None:
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.__str__())

    def __str__(self) -> str:
        location = ""
        if self.line is not None:
            location += f"Line {self.line}"
        if self.column is not None:
            location += f", Column {self.column}" if location else f"Column {self.column}"
        return f"{self.message}" + (f" ({location})" if location else "")


class ConsistencyException(Exception):
    pass
