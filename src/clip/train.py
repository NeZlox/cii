# train.py
import asyncio
import torch
from torch.optim import AdamW
from torch.nn import BCEWithLogitsLoss
from torch.utils.data import DataLoader
from transformers import CLIPModel
from src.clip.dataset import get_training_data, ArtDataset, get_all_tags


async def train_model(model, dataloader, optimizer, loss_fn, num_epochs=5):
    model.train()
    for epoch in range(num_epochs):
        running_loss = 0.0
        for batch in dataloader:
            images, labels = batch
            labels = labels.type(torch.float32).to(model.device)

            optimizer.zero_grad()

            # Получаем особенности изображения
            features = model.get_image_features(images)

            # Подаем их в классификатор
            outputs = model.classifier(features)

            loss = loss_fn(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
        print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {running_loss / len(dataloader)}")


async def main():
    tags = await get_all_tags()
    num_tags = len(tags)
    data = await get_training_data(cnt=1000, start=0)
    dataset = ArtDataset(data, tag_names=tags)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
    model = CLIPModel.from_pretrained('openai/clip-vit-base-patch32')
    model.visual_projection = torch.nn.Linear(model.config.hidden_size, num_tags)
    optimizer = AdamW(model.parameters(), lr=5e-5)
    loss_fn = BCEWithLogitsLoss()
    await train_model(model, dataloader, optimizer, loss_fn, num_epochs=5)


if __name__ == "__main__":
    asyncio.run(main())
