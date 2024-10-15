# main.py
import asyncio

import torch

from src.vit.train import train_model
from src.vit.evaluate import evaluate_model
from src.vit.dataset import get_training_data, ArtDataset
from src.vit.save_model import save_model
from torch.utils.data import DataLoader
from transformers import ViTForImageClassification
from torch.optim import AdamW
from torch.nn import CrossEntropyLoss, BCEWithLogitsLoss
from src.database.cii_db.queries import TagsQuery


# Асинхронная функция, которая будет выполняться в главном потоке
async def main():
    # Получение количества классов (тегов) из базы данных
    num_tags = len(await TagsQuery.find_all())

    # Извлечение и подготовка данных для обучения
    data = await get_training_data(cnt=1000,start=0)
    dataset = ArtDataset(data, num_classes=num_tags)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

    # Создание модели, оптимизатора и функции потерь
    model = ViTForImageClassification.from_pretrained(
        'google/vit-base-patch16-224',
        num_labels=num_tags,
        ignore_mismatched_sizes=True  # Игнорируем несовпадения размеров слоёв
    )
    # Замена финального слоя (головы) классификации на новый, соответствующий числу меток (4500)
    model.classifier = torch.nn.Linear(model.config.hidden_size, num_tags)

    optimizer = AdamW(model.parameters(), lr=5e-5)
    loss_fn = BCEWithLogitsLoss()

    # Обучение модели
    await train_model(model, dataloader, optimizer, loss_fn, num_epochs=5)

    # Оценка модели
    await evaluate_model(model, dataloader)

    # Сохранение обученной модели
    save_model(model)


# Запуск асинхронной функции через цикл событий
if __name__ == "__main__":
    asyncio.run(main())
"""
pip install torch 
pip install transformers
pip install Pillow 
pip install scikit-learn 

python -m src.vit.main 
alembic upgrade head  
alembic downgrade -1 
alembic revision --autogenerate -m "initial_migration"   
"""
