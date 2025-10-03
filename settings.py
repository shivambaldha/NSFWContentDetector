import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ENV:
    def __init__(self):
        self.OCR_API_URL = os.getenv("OCR_API_URL")
        if not self.OCR_API_URL:
            raise ValueError("OCR_API_URL is not set in environment variables")