# main.py
import asyncio
import torch
from torch.optim import AdamW
from torch.nn import BCEWithLogitsLoss, Linear
from torch.utils.data import DataLoader
from transformers import CLIPModel, CLIPProcessor
from src.clip.dataset import get_training_data, ArtDataset, get_all_tags
from src.clip.train import train_model
from src.clip.evaluate import evaluate_model
from src.clip.save_model import save_model

# Инициализация CLIPProcessor для обработки изображений
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Асинхронная основная функция для обучения и оценки модели
async def main():
    # Получение всех тегов из базы данных
    tags = await get_all_tags()
    num_tags = len(tags)

    # Загрузка модели CLIP
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

    # Добавление классификатора с нужной размерностью
    model.classifier = Linear(512, num_tags).to(model.device)

    # Подготовка данных
    data = await get_training_data(cnt=1000, start=0)
    dataset = ArtDataset(data, tag_names=tags)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

    optimizer = AdamW(model.parameters(), lr=5e-5)
    loss_fn = BCEWithLogitsLoss()

    # Обучение модели
    await train_model(model, dataloader, optimizer, loss_fn, num_epochs=5)

    # Оценка модели
    await evaluate_model(model, dataloader)

    # Сохранение обученной модели
    save_model(model)

if __name__ == "__main__":
    asyncio.run(main())

"""
pip install torch 
pip install transformers
pip install Pillow 
pip install scikit-learn 

python -m src.clip.main 
alembic upgrade head  
alembic downgrade -1 
alembic revision --autogenerate -m "initial_migration"   
"""
