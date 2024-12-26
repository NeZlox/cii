from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, AuthenticationException
from src.utils import SingletonMeta


class BaseElasticService(metaclass=SingletonMeta):
    _client: Elasticsearch = None

    @classmethod
    def connect(cls, host: str, username: str = None, password: str = None, verify_certs: bool = True):
        """Устанавливает соединение с Elasticsearch."""
        if cls._client is None:
            try:
                if username and password:
                    cls._client = Elasticsearch(
                        [host],
                        http_auth=(username, password),
                        verify_certs=verify_certs
                    )
                else:
                    cls._client = Elasticsearch([host], verify_certs=verify_certs)

                # Проверка соединения
                if not cls._client.ping():
                    raise ConnectionError("Elasticsearch cluster is not reachable.")

            except (ConnectionError, AuthenticationException) as e:
                print(f"Ошибка при подключении к Elasticsearch: {e}")

    @classmethod
    def get_client(cls):
        """Возвращает текущего клиента Elasticsearch."""
        if cls._client is None:
            raise ConnectionError("Elasticsearch client is not initialized. Call 'connect' first.")
        return cls._client

    @classmethod
    def close(cls):
        """Закрывает соединение с Elasticsearch."""
        if cls._client is not None:
            cls._client.transport.close()
            cls._client = None
