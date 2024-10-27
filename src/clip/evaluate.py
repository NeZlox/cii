# evaluate.py
import asyncio
from sklearn.metrics import accuracy_score, classification_report
import numpy as np
import torch
from torch.utils.data import DataLoader
from transformers import ViTForImageClassification
from src.vit.dataset import get_training_data, ArtDataset

# Оценка модели
async def evaluate_model(model, dataloader):
    model.eval()
    predictions, true_labels = [], []

    with torch.no_grad():
        for batch in dataloader:
            images, labels = batch
            outputs = model(images)
            logits = outputs.logits
            preds = (logits.cpu().numpy() > 0).astype(int)  # Превращаем логиты в бинарные предсказания
            predictions.extend(preds)
            true_labels.extend(labels.cpu().numpy())

    # Рассчитываем точность для многометочной классификации
    accuracy = accuracy_score(true_labels, predictions)  # Используем average='samples' для multi-label
    report = classification_report(true_labels, predictions, zero_division=0)

    print(f"Accuracy: {accuracy}")
    print(f"Classification Report:\n{report}")


# Асинхронная основная функция для оценки модели
async def main():
    # Извлечение данных
    data = await get_training_data()
    dataset = ArtDataset(data)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

    # Создаём модель заново для оценки
    model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224')

    # Оценка модели
    await evaluate_model(model, dataloader)

# Запуск асинхронной задачи
if __name__ == "__main__":
    asyncio.run(main())

