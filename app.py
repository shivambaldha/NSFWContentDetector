from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from utils.ocr import OCRClient
from utils.nsfw_text_detector import NSFWTextDetector
from utils.nsfw_image_detector import NSFWImageDetector
from utils.utils import is_nsfw

import os
import traceback
from datetime import datetime, timezone

from settings import ENV

env = ENV()

OCR_API_URL = env.OCR_API_URL
app = Flask(__name__)

# Allowed image extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# -----------------------------
# Global error handler
# -----------------------------
@app.errorhandler(Exception)
def handle_unexpected_error(error):
    app.logger.error(f"Unhandled exception: {traceback.format_exc()}")
    return (
        jsonify(
            {
                "success": False,
                "error": "Internal server error",
                "timestamp": get_timestamp(),
            }
        ),
        500,
    )


# -----------------------------
# Health Check Route
# -----------------------------
@app.route("/")
def health_check():
    return (
        jsonify(
            {
                "message": "Welcome to NSFW Content Detector API!",
                "status": "healthy",
                "timestamp": get_timestamp(),
            }
        ),
        200,
    )


# -----------------------------
# NSFW Content Prediction
# -----------------------------
@app.route("/v1/predict", methods=["POST"])
def nsfw_content_prediction() -> dict:
    try:
        if "image" not in request.files:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "No image uploaded",
                        "timestamp": get_timestamp(),
                    }
                ),
                400,
            )

        image_file = request.files["image"]

        if image_file.filename == "":
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Empty filename",
                        "timestamp": get_timestamp(),
                    }
                ),
                400,
            )

        if not allowed_file(image_file.filename):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Invalid file type. Allowed types: png, jpg, jpeg",
                        "timestamp": get_timestamp(),
                    }
                ),
                400,
            )

        filename = secure_filename(image_file.filename)
        os.makedirs("uploads", exist_ok=True)
        image_path = os.path.join("uploads", filename)
        image_file.save(image_path)

        # Initialize clients
        ocr_client = OCRClient(OCR_API_URL)
        text_detector = NSFWTextDetector()
        image_detector = NSFWImageDetector()

        ###################################
        # Step 1: Image-based NSFW detection
        ###################################
        image_result = image_detector.invoke(image_path)

        if not image_result.get("success", True):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": image_result.get("error", "Image detection failed"),
                        "timestamp": get_timestamp(),
                    }
                ),
                500,
            )

        if image_result.get("label") == "nsfw":
            return (
                jsonify(
                    {
                        "success": True,
                        "nsfw": {
                            "is_nsfw": True,
                            "method": "image based model",
                            "reason": "We found unsafe content in the image",
                        },
                        "timestamp": get_timestamp(),
                    }
                ),
                200,
            )

        ###################################
        # Step 2: OCR to extract text
        ###################################
        ocr_result = ocr_client.invoke(image_path)

        if not ocr_result.get("status", False):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": ocr_result.get("message", "OCR failed"),
                        "timestamp": get_timestamp(),
                    }
                ),
                500,
            )

        extracted_text = ocr_result.get("response", {}).get("extracted_text", "")
        if not extracted_text.strip():
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "No text extracted from image",
                        "timestamp": get_timestamp(),
                    }
                ),
                400,
            )

        ###################################
        # Step 3: Text-based NSFW detection
        ###################################
        text_result = text_detector.invoke(extracted_text)
        text_result = is_nsfw(text_result)

        # Always add timestamp
        text_result["timestamp"] = get_timestamp()

        return jsonify(text_result), 200

    except Exception as e:
        app.logger.error(f"Prediction error: {traceback.format_exc()}")
        return (
            jsonify({"success": False, "error": str(e), "timestamp": get_timestamp()}),
            500,
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
