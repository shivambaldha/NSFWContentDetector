import requests
from pathlib import Path
from typing import Dict, Any


class OCRClient:
    """Client for sending OCR requests to a given API endpoint."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def invoke(self, image_path: str) -> Dict[str, Any]:
        """
        Send an OCR request with the given image file.
        """
        image_file = Path(image_path)
        if not image_file.exists():
            return {
                "status": False,
                "message": f"Image file not found: {image_path}",
                "response": None,
            }

        url = f"{self.base_url}/ocr"
        try:
            with open(image_file, "rb") as img:
                files = [("image", (image_file.name, img, "image/png"))]
                response = requests.post(url, files=files, timeout=30)

            response.raise_for_status()
            return {
                "status": True,
                "message": "Request successful",
                "response": response.json(),
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": False,
                "message": f"Error while sending OCR request: {e}",
                "response": None,
            }
