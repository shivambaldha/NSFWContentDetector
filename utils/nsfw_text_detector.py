import joblib
import pandas as pd
import re
from typing import Dict, Any, List


# Constants
MODEL_PATH = "model_traning/model/production_pipeline.pkl"
TARGET_COLUMNS = [
    "toxic",
    "severe_toxic",
    "obscene",
    "threat",
    "insult",
    "identity_hate",
]


def load_model(path: str):
    """Load the ML model pipeline from a given path."""
    try:
        return joblib.load(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Model file not found at {path}")
    except Exception as e:
        raise RuntimeError(f"Error loading model: {e}")


class NSFWTextDetector:
    """Class for detecting NSFW or toxic text content."""

    def __init__(self, model_path: str = MODEL_PATH):
        try:
            self.model = load_model(model_path)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize NSFWTextDetector: {e}")

    @staticmethod
    def clean_text_basic(text: Any) -> str:
        """
        Perform basic text cleaning for ML model input.
        """
        if pd.isna(text):
            return ""

        text = str(text).lower()

        # Remove newlines, extra spaces, URLs, mentions, and unwanted chars
        text = re.sub(r"\n", " ", text)
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
        text = re.sub(r"@\w+", "", text)
        text = re.sub(r"[^a-zA-Z0-9\s.,!?]", " ", text)

        return text.strip()

    def predict_comment_toxicity(self, comment_text: str) -> Dict[str, float]:
        """
        Predict toxicity probabilities for a given comment.
        """
        try:
            predictions = self.model.predict_proba([comment_text])
            probabilities = [pred[0, 1] for pred in predictions]
        except Exception as e:
            raise RuntimeError(f"Error during prediction: {e}")

        return {col: prob for col, prob in zip(TARGET_COLUMNS, probabilities)}

    def analyze_comment(self, comment_text: str, results: Dict[str, float]) -> Dict[str, Any]:
        """
        Analyze toxicity results and provide decision/risk assessment.
        """
        max_prob = max(results.values())
        max_category = max(results, key=results.get)

        # Decision logic
        if max_prob > 0.9:
            decision, risk = "BLOCK IMMEDIATELY", "CRITICAL"
        elif max_prob > 0.7:
            decision, risk = "MANUAL REVIEW", "HIGH"
        elif max_prob > 0.3:
            decision, risk = "WARN USER", "MEDIUM"
        else:
            decision, risk = "ALLOW", "LOW"

        # Breakdown for risky comments
        breakdown = [
            f"{cat}:{results[cat]*100:.0f}%"
            for cat in TARGET_COLUMNS
            if results[cat] > 0.2
        ]

        # Detect toxic keywords
        toxic_words = [
            "stupid", "idiot", "hate", "kill", "die", "moron",
            "fool", "damn", "hell", "shit", "fuck", "garbage", "shut"
        ]
        found_words = [word for word in toxic_words if word in comment_text.lower()]

        if found_words:
            print(f"Detected words: {', '.join(found_words)}")

        return {
            "input_text": comment_text,
            "decision": decision,
            "risk": risk,
            "breakdown": breakdown,
            "category": max_category
        }

    def invoke(self, comment_text: str) -> Dict[str, Any]:
        """
        Full pipeline: clean text -> predict -> analyze.
        """
        cleaned_text = self.clean_text_basic(comment_text)
        results = self.predict_comment_toxicity(cleaned_text)
        return self.analyze_comment(cleaned_text, results)
