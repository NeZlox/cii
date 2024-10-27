import asyncio

import torch
from transformers import CLIPModel

from src.clip.dataset import get_all_tags


# Сохранение модели
def save_model(model, path='./clip-model'):
    # Сохраняем всю модель вместе с дополнительными слоями
    torch.save(model.state_dict(), f"{path}/pytorch_model.bin")
    model.config.save_pretrained(path)


# Загрузка модели
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


if __name__ == "__main__":
    from train import model

    # Сохранение обученной модели
    save_model(model)

    # Пример загрузки модели
    loaded_model = asyncio.run(load_model())
