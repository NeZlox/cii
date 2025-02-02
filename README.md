## Настройка окружения

Создайте файл `.env` в корне проекта с следующим содержимым:

```sh
MODE=DEV
LOG_LEVEL=INFO

DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=0000
DB_NAME=cii

ELASTIC_HOST=localhost
ELASTIC_PORT=9200
ELASTIC_INDEX=tags_test
```



# Инструкция по запуску проекта

## 0. Выполнение миграций с помощью Alembic

Перед запуском приложения, выполните миграции с помощью команды:

```bash
alembic upgrade head
```

## 1. Запуск Elastic

Для запуска Elastic используйте Docker:

```bash
docker compose up -d
```

### Просмотр индекса в Elastic

Для проверки работы индекса, используйте следующий запрос:
http://localhost:5601/app/dev_tools
```http
GET /tags_test/_search
{
  "from": 0,
  "size": 10
}
```

## 2. Запуск парсера

Для запуска парсера, используйте следующую команду:

```bash
python -m src.parse.main
```

Не забудьте указать свой диапазон парсинга (строка 68 в файле `src/parse/main.py`), а также включенный Elastic и База данных для сохранения изображений.

## 3. Обучение моделей

### Обучение модели Vision Transformer (VIT)

Для обучения модели VIT, используйте следующую команду:

```bash
python -m src.vit.main
```

### Обучение модели CLIP

Для обучения модели CLIP, используйте команду:

```bash
python -m src.clip.main
```

## 4. Запуск API

Для запуска API, используйте следующую команду:

```bash
uvicorn src.main:app --host 127.0.0.3 --port 8002 --reload
```

## 5. Переобучение моделей после парсинга

После выполнения парсинга необходимо переобучить модели для поддержания актуальных классов тегов.
