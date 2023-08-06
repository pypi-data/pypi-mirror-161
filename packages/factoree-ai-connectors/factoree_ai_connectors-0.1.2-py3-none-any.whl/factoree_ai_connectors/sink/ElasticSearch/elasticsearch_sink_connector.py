from dataclasses import dataclass, asdict
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk


@dataclass
class ElasticTimeSeries:
    _index: str
    _id: str
    time: str
    value: float | bool | str | int


class ElasticSearchSinkConnector:

    def __init__(self, es_url: str, es_api_key: str):
        super().__init__()
        self.es_url = es_url
        self.es_api_key = es_api_key

        self.client = Elasticsearch(
            self.es_url,
            api_key=self.es_api_key,
        )

    def put_documents(self, data: list[ElasticTimeSeries]) -> int:
        """
        writes a bulk of documents to elasticsearch
        :param data: a list of documents to put
        :return: number of successful uploaded documents
        """
        success_docs = 0
        for success, info in parallel_bulk(self.client, [asdict(doc) for doc in data]):
            if success:
                success_docs += 1
            else:
                print('A document failed:', info)
        return success_docs
