import torch
from PIL import Image, UnidentifiedImageError
from transformers import AutoModelForImageClassification, ViTImageProcessor

MODEL_NAME = "Falconsai/nsfw_image_detection"
CACHE_DIR = "/models"

class NSFWImageDetector:
    """Class for detecting NSFW content based on image analysis."""
    def __init__(self):
        try:
            self.model = AutoModelForImageClassification.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
            self.processor = ViTImageProcessor.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
        except Exception as e:
            raise RuntimeError(f"Error loading model: {e}")

    def invoke(self, image_path: str) -> dict:
        try:
            img = Image.open(image_path)
        except FileNotFoundError:
            return {"success": False, "error": f"File not found: {image_path}"}
        except UnidentifiedImageError:
            return {"success": False, "error": f"Invalid image file: {image_path}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error opening image: {e}"}

        try:
            with torch.no_grad():
                inputs = self.processor(images=img, return_tensors="pt")
                outputs = self.model(**inputs)
                logits = outputs.logits

            predicted_label = logits.argmax(-1).item()
            return {
                "success": True,
                "label": self.model.config.id2label[predicted_label],
                "raw_logits": logits.tolist(),
            }
        except Exception as e:
            return {"success": False, "error": f"Prediction error: {e}"}
