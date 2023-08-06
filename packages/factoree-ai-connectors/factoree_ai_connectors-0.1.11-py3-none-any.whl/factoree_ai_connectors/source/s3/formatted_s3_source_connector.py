from typing import TypeVar, Generic
from factoree_ai_connectors.files import S3FileCreatedEvent, S3File
from factoree_ai_connectors.source.s3.s3_source_connector import S3SourceConnector
from factoree_ai_connectors.text.text_parsers import TextParser

T = TypeVar('T', bound='S3File')


class FormattedS3SourceConnector(Generic[T]):
    def __init__(
        self,
        connector: S3SourceConnector,
        parser: TextParser
    ):
        super().__init__()
        self.connector = connector
        self.parser = parser

    def next_created_file_event(self) -> S3FileCreatedEvent[T] | None:
        event: S3FileCreatedEvent[T] | None = self.connector.next_created_file_event()
        if event:
            parsed_file = S3FileCreatedEvent[T](
                S3File[T](
                    event.file.filename,
                    self.parser.parse(event.file.data)
                ),
                event.sqs_msg_id
            )
            return parsed_file
        else:
            return None

    def mark_file_as_done(self, msg_id: str) -> bool:
        return self.connector.mark_file_as_done(msg_id)

    def purge_events(self):
        self.connector.purge_events()
