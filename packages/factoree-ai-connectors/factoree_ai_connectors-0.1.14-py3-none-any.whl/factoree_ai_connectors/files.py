from abc import ABC
from dataclasses import dataclass
from typing import TypeVar, Generic

T = TypeVar('T')
F = TypeVar('F', bound='S3File')


@dataclass
class S3File(ABC, Generic[T]):
    filename: str
    data: T


@dataclass
class S3TextFile(S3File[str]):
    pass


@dataclass
class S3CsvFile(S3File[list[list]]):
    pass


@dataclass
class S3JsonFile(S3File[dict]):
    pass


@dataclass
class S3FileCreatedEvent(Generic[F]):
    file: F
    sqs_msg_id: str
