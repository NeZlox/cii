# train.py
import asyncio

import torch
from transformers import ViTForImageClassification
from torch.optim import AdamW
from torch.nn import CrossEntropyLoss, BCEWithLogitsLoss
from torch.utils.data import DataLoader

from src.database.cii_db.queries import TagsQuery
from src.vit.dataset import get_training_data, ArtDataset


# Функция для обучения модели
async def train_model(model, dataloader, optimizer, loss_fn, num_epochs=5):
    model.train()
    for epoch in range(num_epochs):
        running_loss = 0.0
        for batch in dataloader:
            images, labels = batch

            # Преобразуем метки в тип float32 для BCEWithLogitsLoss
            labels = labels.type(torch.float32)

            optimizer.zero_grad()
            outputs = model(images)
            loss = loss_fn(outputs.logits, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
        print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {running_loss / len(dataloader)}")


# Асинхронная основная функция для обучения модели
async def main():
    # Получение количества классов (тегов) из базы данных
    num_tags = len(await TagsQuery.find_all())

    # Извлечение данных
    data = await get_training_data()
    dataset = ArtDataset(data)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

    # Создаём модель, оптимизатор и функцию потерь
    model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224', num_labels=num_tags,
                                                      ignore_mismatched_sizes=True)
    optimizer = AdamW(model.parameters(), lr=5e-5)
    loss_fn = BCEWithLogitsLoss()

    # Обучение модели
    await train_model(model, dataloader, optimizer, loss_fn, num_epochs=5)


# Запуск асинхронной задачи
if __name__ == "__main__":
    asyncio.run(main())
