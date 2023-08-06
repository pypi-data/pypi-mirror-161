import json
import re
from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from datetime import datetime

T = TypeVar('T')


class TextParser(ABC, Generic[T]):
    @abstractmethod
    def parse(self, text: str) -> T:
        pass


class CsvParser(TextParser[list[list[str]]]):
    def __init__(self, datetime_format: str | None = None, timestamp_column: int | None = None):
        if datetime_format is None or timestamp_column is None:
            self.timestamp_column = None
        else:
            self.timestamp_column = timestamp_column
            self.datetime_format = datetime_format

    def parse(self, text: str) -> list[list[str]]:
        grid = []
        for line in text.split("\n"):
            if line.strip():
                line_main_body = re.findall(r'(.*[^,]),*$', line.strip())[0]
                grid.append(line_main_body.split(","))

        for i in range(len(grid)):
            for j in range(len(grid[i])):
                grid[i][j] = self.__convert(grid[i][j], j)

        return grid

    def __convert(self, value: str, column: int) -> any:
        if value.isnumeric():
            return int(value)

        if re.match(r'^-\d+$', value) is not None:
            return int(value)

        if re.search(r'^-?\d+\.\d+$', value) is not None:
            return float(value)

        if re.search(r'^-?\d+[Ee][-+]?\d+$', value) is not None:
            return float(value)

        if re.search(r'^-?\d+\.\d+[Ee][-+]?\d+$', value) is not None:
            return float(value)

        if column == self.timestamp_column and value:
            try:
                return datetime.strptime(value, self.datetime_format)
            except ValueError as e:
                print(f'Failed to parsing date and time: [{value}]')
                raise e

        return value


class JsonParser(TextParser[dict]):
    def parse(self, text: str) -> dict:
        return json.loads(text)
