from typing import List

from src.utils.elastic_service import BaseElasticService
from elasticsearch import Elasticsearch, helpers
from keybert import KeyBERT
from flair.embeddings import TransformerDocumentEmbeddings
import warnings
from elasticsearch import ElasticsearchWarning

warnings.filterwarnings("ignore", category=ElasticsearchWarning)

"""
GET /tags_test/_search
{
  "from": 10,
  "size": 10
}

"""
class ElasticService(BaseElasticService):
    roberta = TransformerDocumentEmbeddings('roberta-base')
    kw_model = KeyBERT(model=roberta)

    @classmethod
    async def search(cls, search_string: str, index_name: str, limit: int = 10):

        keyword = cls.kw_model.extract_keywords(search_string, keyphrase_ngram_range=(1, 2), top_n=10)
        tags = []

        for group in keyword:
            tags.append(group[0])

        query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "tags": {
                                    "query": " ".join(tags),
                                    "operator": "or",
                                    "fuzziness": "AUTO"  # Позволяет учитывать неточные совпадения и падежи
                                }
                            }
                        }
                    ]
                }
            },
            "sort": [
                {"_score": {"order": "desc"}}  # Ранжирование по релевантности
            ],
            "size": limit  # Установка лимита на количество записей
        }

        try:
            # Выполняем поиск
            response = cls._client.search(index=index_name, body=query)

            # Извлекаем id элементов из PostgreSQL из результатов поиска
            results = [
                hit["_source"]["postgresql_id"]
                for hit in response["hits"]["hits"]
            ]

            return results

        except Exception as e:
            print(f"Ошибка при выполнении поиска: {e}")
            return []

    @classmethod
    async def add_data(cls, index_name: str, id_image: int, tags_image: List[str]):
        test_data = [
            {
                "_index": index_name,
                "_id": id_image,
                "_source": {
                    "tags": tags_image,
                    "postgresql_id": id_image
                }
            }
        ]

        try:
            # Используем bulk для массовой загрузки данных
            helpers.bulk(cls._client, test_data)

            print("Тестовые данные успешно добавлены.")
        except Exception as e:
            print(f"Ошибка при добавлении данных: {e}")
