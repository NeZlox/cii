# save_model.py
import json
from functools import lru_cache
from typing import List

from transformers import ViTForImageClassification

__all__ = ['save_model', 'load_model', 'load_classes']


# Сохранение модели
def save_model(model, tags: List[str], path='./vit-model'):
    model.save_pretrained(path)
    # Сохранение параметра num_labels в JSON-файл
    config_data = {"tags": tags}
    with open(f"{path}/classes.json", "w") as json_file:
        json.dump(config_data, json_file)


# Загрузка модели
@lru_cache(maxsize=1)
def load_model(path='./vit-model'):
    return ViTForImageClassification.from_pretrained(path)


def load_classes(path='./vit-model') -> List[str]:
    # Загрузка параметра num_labels из JSON-файла
    with open(f"{path}/classes.json", "r") as json_file:
        config_data = json.load(json_file)
    return config_data.get("tags")


if __name__ == "__main__":
    from train import model

    # Сохранение обученной модели
    save_model(model)

    # Пример загрузки модели
    loaded_model = load_model()
