# evaluate.py
import asyncio

import torch
from sklearn.metrics import accuracy_score, classification_report
from torch.utils.data import DataLoader
from transformers import CLIPModel

from src.clip.dataset import ArtDataset, get_all_tags, get_training_data


async def evaluate_model(model, dataloader):
    model.eval()
    predictions, true_labels = [], []
    with torch.no_grad():
        for batch in dataloader:
            images, labels = batch
            features = model.get_image_features(images)
            outputs = model.classifier(features)
            preds = (outputs.cpu().numpy() > 0).astype(int)
            predictions.extend(preds)
            true_labels.extend(labels.cpu().numpy())
    accuracy = accuracy_score(true_labels, predictions)
    report = classification_report(true_labels, predictions, zero_division=0)
    print(f"Accuracy: {accuracy}")
    print(f"Classification Report:\n{report}")


async def main():
    tags = await get_all_tags()
    data = await get_training_data()
    dataset = ArtDataset(data, tag_names=tags)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
    model = CLIPModel.from_pretrained('openai/clip-vit-base-patch32')
    await evaluate_model(model, dataloader)


if __name__ == "__main__":
    asyncio.run(main())
