# test.py
import asyncio
import torch
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, classification_report
from torch.utils.data import DataLoader
from PIL import Image
import matplotlib.pyplot as plt
from transformers import CLIPProcessor, CLIPModel
from src.clip.dataset import process_image, ArtDataset, get_training_data, get_all_tags
from src.clip.save_model import load_model

# Инициализация CLIPProcessor
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Оценка модели
async def evaluate_model(model, test_dataloader):
    model.eval()
    predictions, true_labels = [], []

    with torch.no_grad():
        for batch in test_dataloader:
            images, labels = batch
            features = model.get_image_features(images)
            outputs = model.classifier(features)
            preds = (outputs.cpu().numpy() > 0).astype(int)
            predictions.append(preds)
            true_labels.append(labels.cpu().numpy())

    predictions = np.vstack(predictions)
    true_labels = np.vstack(true_labels)

    accuracy = accuracy_score(true_labels.ravel(), predictions.ravel())
    precision = precision_score(true_labels, predictions, average='samples')
    recall = recall_score(true_labels, predictions, average='samples')
    f1 = f1_score(true_labels, predictions, average='samples')
    report = classification_report(true_labels, predictions, zero_division=0)

    print(f"Accuracy: {accuracy}")
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"F1 Score: {f1}")
    print(f"Classification Report:\n{report}")

# Прогнозирование на новом изображении
def predict_on_new_image(model, image_path, mlb):
    image = process_image(image_path).unsqueeze(0)
    model.eval()
    with torch.no_grad():
        features = model.get_image_features(image)
        outputs = model.classifier(features)
        preds = (outputs.cpu().numpy() > 0).astype(int)
        decoded_tags = mlb.inverse_transform(preds)
        return decoded_tags

# Визуализация предсказаний на изображении
def show_image_with_tags(image_path, predicted_tags):
    image = Image.open(image_path)
    plt.imshow(image)
    predicted_tags_str = [str(tag) for tag in predicted_tags]
    plt.title(f"Predicted Tags: {', '.join(predicted_tags_str)}")
    plt.axis('off')
    plt.show()

async def main():
    tags = await get_all_tags()
    num_tags = len(tags)

    # Загрузка модели и добавление классификатора
    model = await load_model()
    model.classifier = torch.nn.Linear(512, num_tags).to(model.device)

    data = await get_training_data(cnt=1000, start=0)
    dataset = ArtDataset(data, tag_names=tags)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=False)

    await evaluate_model(model, dataloader)

    image_path = 'src/images/image_13013.jpg'
    prediction = predict_on_new_image(model, image_path, dataset.mlb)
    show_image_with_tags(image_path, prediction[0])

if __name__ == "__main__":
    asyncio.run(main())




"""
Запуск программы:
python -m src.clip.test
"""
