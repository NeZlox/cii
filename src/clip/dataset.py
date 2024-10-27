# dataset.py
from typing import List
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from src.database.cii_db.queries import TagsQuery
from src.database.cii_db.queries.pictures import PicturesQuery
from pydantic import BaseModel
from PIL import Image
from torch.utils.data import Dataset
from transformers import CLIPProcessor

# Используем CLIPProcessor для подготовки изображений
processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')


class PicturesWithTagsSchema(BaseModel):
    id_picture: int
    path: str
    tags: List[str]

    class Config:
        orm_mode = True


def process_image(image_path):
    image = Image.open(image_path).convert("RGB")
    return processor(images=image, return_tensors="pt").pixel_values.squeeze(0)


# Асинхронная функция для извлечения данных из базы данных
async def get_training_data(cnt: int = 10, start: int = 0):
    data = await PicturesQuery.get_pictures_with_tags(cnt=cnt, start=start)
    pictures = {}
    for row in data:
        id_picture = row['id']
        path = row['path']
        tag = row['name']
        if id_picture not in pictures:
            pictures[id_picture] = {"path": path, "tags": []}
        pictures[id_picture]["tags"].append(tag)
    return [
        PicturesWithTagsSchema(id_picture=id_picture, path=data["path"], tags=data["tags"])
        for id_picture, data in pictures.items()
    ]


async def get_all_tags():
    tags = await TagsQuery.find_all()
    return list(set(tag.name for tag in tags))


class ArtDataset(Dataset):
    def __init__(self, data: List[PicturesWithTagsSchema], tag_names: List[str]):
        self.data = data
        self.mlb = MultiLabelBinarizer(classes=tag_names)
        all_tags = [picture.tags for picture in data]
        self.mlb.fit(all_tags)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        image_path = self.data[idx].path
        tags = self.data[idx].tags
        image = process_image(image_path)
        encoded_tags = self.mlb.transform([tags])[0].astype(np.float32)
        return image, encoded_tags
