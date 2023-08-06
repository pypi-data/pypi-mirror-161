import boto3


class S3Client:
    def __init__(
        self,
        s3_access_key: str,
        s3_secret_key: str,
        endpoint_url: str | None = None
    ):
        super().__init__()
        session = boto3.Session(
            aws_access_key_id=s3_access_key,
            aws_secret_access_key=s3_secret_key
        )
        self.s3 = session.resource('s3', endpoint_url=endpoint_url)

    def put(self, bucket_name: str, filename: str, document: str) -> bool:
        self.s3.Object(bucket_name, filename).put(Body=document)

        return True
