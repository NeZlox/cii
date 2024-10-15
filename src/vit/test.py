import asyncio

import torch
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, classification_report
from torch.utils.data import DataLoader
from PIL import Image
import matplotlib.pyplot as plt
from transformers import ViTForImageClassification

from src.database.cii_db.queries import TagsQuery
from src.vit.dataset import process_image, ArtDataset, get_training_data
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
    print(f"Classification Report:\\n{report}")


# Прогнозирование на новых изображениях
def predict_on_new_image(model, image_path):
    image = process_image(image_path)['pixel_values'].squeeze(0).unsqueeze(0)  # Преобразуем для подачи в модель
    model.eval()
    with torch.no_grad():
        output = model(image)
        logits = output.logits
        preds = (logits.cpu().numpy() > 0).astype(int)  # Превращаем логиты в бинарные предсказания
        return preds


# Визуализация предсказаний на изображении
def show_image_with_tags(image_path, predicted_tags, mlb):
    image = Image.open(image_path)
    plt.imshow(image)

    # Преобразуем предсказания в NumPy массив
    predicted_tags = np.array(predicted_tags).reshape(1, -1)  # Обеспечиваем правильную форму для `inverse_transform`

    # Декодируем предсказанные теги обратно в их текстовые значения
    decoded_tags = mlb.inverse_transform(predicted_tags)

    plt.title(f"Predicted Tags: {decoded_tags}")
    plt.axis('off')
    plt.show()


async def main():
    # Загрузка сохраненной модели
    model = ViTForImageClassification.from_pretrained('vit-model', num_labels=4519)

    # Прогнозирование на новом изображении
    image_path = 'src/images/image_13013.jpg'
    prediction = predict_on_new_image(model, image_path)
    print(f"Predicted tags: {prediction}")

    # Получение количества классов (тегов) из базы данных
    num_tags = len(await TagsQuery.find_all())

    # Извлечение и подготовка данных для обучения
    data = await get_training_data()
    dataset = ArtDataset(data, num_classes=num_tags)
    # Визуализация предсказаний
    dataset = ArtDataset(data, num_classes=num_tags)
    # dataset = ArtDataset([], 4519)  # Создаем пустой датасет только для использования mlb


    show_image_with_tags(image_path, prediction[0], dataset.mlb)


# Запуск асинхронной задачи
if __name__ == "__main__":
    asyncio.run(main())

"""
python -m src.vit.test
"""
