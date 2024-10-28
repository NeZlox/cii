import asyncio
import json
from functools import lru_cache
from typing import List

import torch
from transformers import CLIPModel

from src.clip.dataset import get_all_tags

__all__ = ['save_model', 'load_model', 'load_classes']


# Сохранение модели
def save_model(model, tags: List[str], path='./clip-model'):
    # Сохраняем всю модель вместе с дополнительными слоями
    torch.save(model.state_dict(), f"{path}/pytorch_model.bin")
    model.config.save_pretrained(path)

    config_data = {"tags": tags}
    with open(f"{path}/classes.json", "w") as json_file:
        json.dump(config_data, json_file)


# Загрузка модели
@lru_cache(maxsize=1)
async def load_model(path='./clip-model'):
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

    # Получаем все теги асинхронно для создания кастомного классификатора
    tags = await get_all_tags()
    num_tags = len(tags)

    # Задаем кастомный классификатор, соответствующий количеству тегов
    model.classifier = torch.nn.Linear(model.config.projection_dim, num_tags)

    # Загружаем веса модели
    model.load_state_dict(torch.load(f"{path}/pytorch_model.bin"))
    return model


def load_classes(path='./clip-model') -> List[str]:
    # Загрузка параметра num_labels из JSON-файла
    with open(f"{path}/classes.json", "r") as json_file:
        config_data = json.load(json_file)
    return config_data.get("tags")


if __name__ == "__main__":
    from train import model

    # Сохранение обученной модели
    save_model(model)

    # Пример загрузки модели
    loaded_model = asyncio.run(load_model())
