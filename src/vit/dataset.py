# dataset.py
from typing import List

import numpy as np
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer

from src.database.cii_db.queries.pictures import PicturesQuery
from pydantic import BaseModel
from PIL import Image
from torch.utils.data import Dataset
from transformers import ViTFeatureExtractor

# Используем ViTFeatureExtractor для подготовки изображений
feature_extractor = ViTFeatureExtractor.from_pretrained('google/vit-base-patch16-224')


# Схема для хранения изображений с тегами
class PicturesWithTagsSchema(BaseModel):
    id_picture: int
    path: str
    tags: List[str]

    class Config:
        orm_mode = True


def process_image(image_path):
    image = Image.open(image_path)

    # Преобразуем изображение в RGB (ViT ожидает изображения в формате RGB)
    image = image.convert("RGB")

    # Изменение размера изображения до 224x224
    image = image.resize((224, 224))

    # Преобразование изображения с помощью feature_extractor
    return feature_extractor(images=image, return_tensors="pt")


# Асинхронная функция для извлечения данных из базы данных
async def get_training_data(cnt: int = 10, start: int = 0):
    # Извлекаем данные из базы данных
    data = await PicturesQuery.get_pictures_with_tags(cnt=cnt, start=start)
    pictures = {}

    # Обработка данных, группировка по id_picture
    for row in data:
        id_picture = row['id']
        path = row['path']
        tag = row['name']

        if id_picture not in pictures:
            pictures[id_picture] = {"path": path, "tags": []}
        pictures[id_picture]["tags"].append(tag)

    # Преобразуем данные в формат Pydantic
    return [
        PicturesWithTagsSchema(id_picture=id_picture, path=data["path"], tags=data["tags"])
        for id_picture, data in pictures.items()
    ]


# Класс Dataset для загрузки изображений и тегов
class ArtDataset(Dataset):
    def __init__(self, data: List[PicturesWithTagsSchema], num_classes):
        self.data = data
        self.num_classes = num_classes

        # Инициализация MultiLabelBinarizer для многометочных данных
        self.mlb = MultiLabelBinarizer(classes=range(num_classes))
        all_tags = [picture.tags for picture in data]

        self.mlb.fit(all_tags)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        image_path = self.data[idx].path
        tags = self.data[idx].tags

        # Преобразование изображения
        image = process_image(image_path)['pixel_values'].squeeze(0)

        # Преобразование тегов в бинарные метки (0 или 1 для каждого класса)
        encoded_tags = self.mlb.transform([tags])[0].astype(np.float32)

        return image, encoded_tags
