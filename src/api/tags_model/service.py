import torch
from PIL import Image
from sklearn.preprocessing import MultiLabelBinarizer
from transformers import CLIPProcessor, ViTFeatureExtractor

from src.clip import load_classes as load_clip_classes
from src.clip import load_model as load_clip_model
from src.logger import logger
from src.utils.singleton_meta import SingletonMeta
from src.vit import load_classes as load_vit_classes
from src.vit import load_model as load_vit_model


class TagsService(metaclass=SingletonMeta):
    _instance = None

    vit_model = None
    vit_processor = None
    vit_mlb = None

    clip_model = None
    clip_processor = None
    clip_mlb = None

    @classmethod
    async def init_service(cls):
        """Метод инициализации, вызываемый при первом использовании сервиса."""
        if cls._instance is None:
            cls._instance = TagsService()
            # logger.info("Initializing TagsService...")
            print("Initializing TagsService...")

            # Загрузка модели ViT и ее параметров
            cls.vit_model = load_vit_model('./vit-model')
            cls.vit_processor = ViTFeatureExtractor.from_pretrained("google/vit-base-patch16-224")
            vit_tags = load_vit_classes()
            cls.vit_mlb = MultiLabelBinarizer(classes=vit_tags)
            cls.vit_mlb.fit([vit_tags])
            # logger.info("ViT model initialized successfully.")
            print("TagsService ViT model initialized successfully.")

            # Загрузка модели CLIP и ее параметров
            cls.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            cls.clip_model = await load_clip_model('./clip-model')
            clip_tags = load_clip_classes()
            cls.clip_mlb = MultiLabelBinarizer(classes=clip_tags)
            cls.clip_mlb.fit([clip_tags])
            # logger.info("CLIP model initialized successfully.")
            print('TagsService CLIP model initialized successfully.')

    @classmethod
    async def predict_tags_vit(cls, image: Image.Image):
        """Предсказание тегов с помощью ViT."""
        if cls.vit_model is None:
            await cls.init_service()

        image_tensor = cls.vit_processor(images=image, return_tensors="pt").pixel_values.squeeze(0).unsqueeze(0)
        cls.vit_model.eval()
        with torch.no_grad():
            output = cls.vit_model(image_tensor)
            preds = (output.logits.cpu().numpy() > 0).astype(int)
            return cls.vit_mlb.inverse_transform(preds)

    @classmethod
    async def predict_tags_clip(cls, image: Image.Image):
        """Метод предсказания тегов, требующий инициализации сервиса."""
        if cls.clip_model is None:
            await cls.init_service()

        image_input = cls.clip_processor(images=image, return_tensors="pt").pixel_values
        with torch.no_grad():
            features = cls.clip_model.get_image_features(image_input)
            outputs = cls.clip_model.classifier(features)
            preds = (outputs.cpu().numpy() > 0).astype(int)
            return cls.clip_mlb.inverse_transform(preds)
