from datetime import datetime
import boto3
import json
from factoree_ai_connectors.files import S3TextFile, S3FileCreatedEvent


class S3SourceConnector:
    event_list: [S3FileCreatedEvent[S3TextFile]] = []
    current_file = None

    def __init__(
            self,
            bucket: str,
            region_name: str,
            sqs_url: str,
            aws_access_key: str,
            aws_secret_key: str
    ):
        self.bucket = bucket
        self.sqs_url = sqs_url
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key

        self.sqs_client = boto3.client(
            'sqs',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=region_name
        )
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=region_name
        )

    def next_created_file_event(self) -> S3FileCreatedEvent[S3TextFile] | None:
        if not self.event_list:
            self.__next_created_file_events()
        # check if there are files to read
        if not self.event_list:
            return None
        file: S3FileCreatedEvent[S3TextFile] = self.event_list.pop()
        self.current_file = file
        return self.current_file

    def purge_events(self):
        self.sqs_client.purge_queue(QueueUrl=self.sqs_url)

    def __next_created_file_events(self) -> list[S3FileCreatedEvent[S3TextFile]]:
        # TODO: error handling
        print(f'Getting events from {self.sqs_url}')
        response = self.sqs_client.receive_message(
            QueueUrl=self.sqs_url,
            MaxNumberOfMessages=10,
        )

        filenames = []
        files: list[S3FileCreatedEvent[S3TextFile]] = []
        for message in response.get('Messages', []):
            handler = message.get('ReceiptHandle', '')
            try:
                body_str = message.get('Body')
                body_json = json.loads(body_str)
                for record in body_json.get('Records', []):
                    filename = record.get('s3', {}).get('object', {}).get('key')
                    filenames.append(record.get('s3', {}).get('object', {}).get('key'))
                    data: str = self.__read_file_content_from_s3(filename)
                    files.append(S3FileCreatedEvent(S3TextFile(filename, data), handler))
            except IndexError or TypeError as e:
                print(e)
            print(f'{datetime.now().strftime("%H:%M:%S")} - received files: {filenames}')
        print(f'{datetime.now().strftime("%H:%M:%S")} - received {len(filenames)} new files')
        self.event_list.extend(files)
        return files

    def __read_file_content_from_s3(self, s3_path: str) -> str:
        data = self.s3_client.get_object(Bucket=self.bucket, Key=s3_path)
        return data['Body'].read().decode('UTF-8')

    def mark_file_as_done(self, file_id: str) -> bool:
        # TODO: error handling
        print(f'{datetime.now().strftime("%H:%M:%S")} - deleting message {file_id} from queue')
        self.sqs_client.delete_message(
            QueueUrl=self.sqs_url,
            ReceiptHandle=file_id
        )
        return True
