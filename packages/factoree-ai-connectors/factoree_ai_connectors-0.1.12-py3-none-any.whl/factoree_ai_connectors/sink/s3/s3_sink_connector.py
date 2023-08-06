import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from factoree_ai_connectors.sink.s3_client import S3Client


def grid_to_csv(data: list[list]):
    comma_separated_rows = []
    for row_idx in range(len(data)):
        new_row = []
        for value in data[row_idx]:
            new_row.append(str(value))
        comma_separated_rows.append(",".join(new_row))
    return "\n".join(comma_separated_rows)


class S3SinkConnector:
    def __init__(
        self,
        s3_client: S3Client
    ):
        super().__init__()
        self.s3_client = s3_client

    def write_csv_file(self, bucket_name: str, filename: str, data: list[list]) -> bool:
        return self.s3_client.put(bucket_name, filename, grid_to_csv(data))

    def write_json_file(self, bucket_name: str, filename: str, json_data: dict) -> bool:
        print(f'{datetime.now().strftime("%H:%M:%S")} - write_json_file({filename})')
        return self.s3_client.put(bucket_name, filename, json.dumps(json_data))

    def write_json_files(self, bucket_name: str, filenames: list[str],
                         json_data: list[dict]) -> bool:
        result = True
        max_workers = max(30, len(filenames))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i in range(len(filenames)):
                filename = filenames[i]
                executor.submit(write_json_file, self, bucket_name, filename, json_data[i])

        return result


def write_json_file(connector: S3SinkConnector, bucket_name: str, filename: str, json_data: dict) -> bool:
    return connector.write_json_file(bucket_name, filename, json_data)
