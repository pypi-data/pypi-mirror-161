import json
from abc import ABC, abstractmethod
from typing import TypeVar, Generic
import re

T = TypeVar('T')


class TextParser(ABC, Generic[T]):
    @abstractmethod
    def parse(self, text: str) -> T:
        pass


class CsvParser(TextParser[list[list[str]]]):
    def parse(self, text: str) -> list[list[str]]:
        grid = []
        for line in text.split("\n"):
            if line.strip():
                line_main_body = re.findall(r'(.*[^,]),*$', line.strip())[0]
                grid.append(line_main_body.split(","))

        for i in range(len(grid)):
            for j in range(len(grid[i])):
                grid[i][j] = CsvParser.__convert(grid[i][j])

        return grid

    @staticmethod
    def __convert(value: str) -> any:
        if value.isnumeric():
            return int(value)

        if re.match(r'^-\d+$', value) is not None:
            return int(value)

        if re.search(r'^-?\d+\.\d+$', value) is not None:
            return float(value)

        return value


class JsonParser(TextParser[dict]):
    def parse(self, text: str) -> dict:
        return json.loads(text)
