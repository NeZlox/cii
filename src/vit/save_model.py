# save_model.py
from transformers import ViTForImageClassification

# Сохранение модели
def save_model(model, path='./vit-model'):
    model.save_pretrained(path)

# Загрузка модели
def load_model(path='./vit-model'):
    return ViTForImageClassification.from_pretrained(path)

if __name__ == "__main__":
    from train import model

    # Сохранение обученной модели
    save_model(model)

    # Пример загрузки модели
    loaded_model = load_model()
