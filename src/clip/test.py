import asyncio

import torch
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, classification_report
from torch.utils.data import DataLoader
from PIL import Image
import matplotlib.pyplot as plt
from transformers import ViTForImageClassification

from src.database.cii_db.queries import TagsQuery
from src.vit.dataset import process_image, ArtDataset, get_training_data, get_all_tags
from src.vit.save_model import load_model


# Оценка модели на тестовых данных
async def evaluate_model(model, test_dataloader):
    model.eval()
    predictions, true_labels = [], []

    with torch.no_grad():
        for batch in test_dataloader:
            images, labels = batch
            outputs = model(images)
            logits = outputs.logits
            preds = (logits.cpu().numpy() > 0).astype(int)  # Превращаем логиты в бинарные предсказания
            predictions.extend(preds)
            true_labels.extend(labels.cpu().numpy())

    # Рассчитываем метрики
    accuracy = accuracy_score(true_labels, predictions)
    precision = precision_score(true_labels, predictions, average='samples')
    recall = recall_score(true_labels, predictions, average='samples')
    f1 = f1_score(true_labels, predictions, average='samples')
    report = classification_report(true_labels, predictions, zero_division=0)

    print(f"Accuracy: {accuracy}")
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"F1 Score: {f1}")
    print(f"Classification Report:\n{report}")


# Прогнозирование на новых изображениях
def predict_on_new_image(model, image_path, mlb):
    image = process_image(image_path)['pixel_values'].squeeze(0).unsqueeze(0)  # Преобразуем изображение
    model.eval()
    with torch.no_grad():
        output = model(image)
        logits = output.logits
        preds = (logits.cpu().numpy() > 0).astype(int)  # Превращаем логиты в бинарные предсказания

        # Декодируем бинарные предсказания обратно в теги
        decoded_tags = mlb.inverse_transform(preds)
        return decoded_tags  # Берем первый элемент, так как результат - это список списков


# Визуализация предсказаний на изображении
def show_image_with_tags(image_path, predicted_tags):
    image = Image.open(image_path)
    plt.imshow(image)

    # Преобразуем предсказанные теги в строки, чтобы их можно было отобразить
    predicted_tags_str = [str(tag) for tag in predicted_tags]

    plt.title(f"Predicted Tags: {', '.join(predicted_tags_str)}")  # Преобразуем список тегов в строку
    plt.axis('off')
    plt.show()

async def main():

    # Получение количества классов (тегов) из базы данных
    tags = await get_all_tags()
    num_tags = len(tags)

    # Загрузка сохраненной модели
    model = ViTForImageClassification.from_pretrained('vit-model', num_labels=num_tags)


    # Извлечение и подготовка данных для обучения
    data = await get_training_data(cnt=1000, start=0)
    dataset = ArtDataset(data, tag_names=tags)

    # Прогнозирование на новом изображении
    image_path = 'src/images/image_13013.jpg'
    prediction = predict_on_new_image(model, image_path, dataset.mlb)


    # Визуализация предсказаний
    show_image_with_tags(image_path, prediction[0])  # Берем первый элемент, так как это список


# Запуск асинхронной задачи
if __name__ == "__main__":
    asyncio.run(main())

"""
Запуск программы:
python -m src.vit.test
"""
