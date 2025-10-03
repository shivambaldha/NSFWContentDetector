# NSFW Content Detector

This repository provides a complete pipeline for detecting NSFW (Not Safe For Work) content in both **images** and **text**, with integrated OCR capabilities. The project supports model training, inference, and deployment using Docker.

---

## 📂 Project Structure

```
NSFWContentDetector
├── model_training/             # Model training assets
│   ├── Data/                   # Training and test datasets
│   │   ├── test_labels.csv.zip
│   │   ├── test.csv.zip
│   │   └── train.csv.zip
│   ├── model/                  # Saved ML models
│   │   └── production_pipeline.pkl
│   └── model_training.ipynb    # Jupyter notebook for model training
│
├── ocr/                        # OCR-related utilities
│   ├── ocr-api.ipynb           # Notebook for OCR experimentation
│   └── README.md
│
├── utils/                      # Utility scripts
│   ├── nsfw_image_detector.py  # Image-based NSFW detection
│   ├── nsfw_text_detector.py   # Text-based NSFW detection
│   ├── ocr.py                  # OCR text extraction helper
│   └── utils.py                # Shared helper functions
│
├── .env                        # Environment variables
├── app.py                      # Main application entry point
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker setup
├── requirements.txt            # Python dependencies
└── settings.py                 # Application configuration
```

---

## 🚀 Features

* **Image NSFW Detection** – Detect inappropriate content in images.
* **Text NSFW Detection** – Identify explicit or unsafe language.
* **OCR Integration** – Extract text from images for analysis.
* **Model Training Support** – Retrain or fine-tune detection models.
* **Containerized Deployment** – Easily run with Docker/Docker Compose.

---
## 🛠 Tech Stack

* **Python 3.12**
* **Scikit-learn / Hugging Face / Pandas / Torch**
* **Flask (for API, configurable in `app.py`)**
* **Docker & Docker Compose**

---

## ⚙️ Setup Instructions

Before setting up this repository, you need to configure the OCR-API.
Go to the `./ocr` directory and follow the instructions in the `README.md` file to set up the API.

Once configured, you will get an API endpoint that allows communication between this system and the OCR service.

### 1. Clone the Repository

```bash
git clone https://github.com/shivambaldha/NSFWContentDetector.git
cd NSFWContentDetector
```

or

Copy the `./NSFWContentDetector` directory.

### 2. Configure `.env`

Create a `.env` file in the root directory and define environment variables, for example:

```
OCR_API_URL=your-api
```

Replace `your-api` with the OCR API endpoint you obtained after setup.

### 3. Run with Docker

Build and start the containerized application using Docker Compose:

```bash
docker-compose up --build
```

The application will be available at:

```
http://localhost:8080
```

---

## 🌐 API Endpoints

There are two main endpoints available:

### 1. Health Check Endpoint

**Method:** GET
**URL:** [http://localhost:8080/](http://localhost:8080/)

Response:

```json
{
  "message": "Welcome to NSFW Content Detector API!",
  "status": "healthy",
  "timestamp": "2025-10-03T06:13:25Z"
}
```

---

### 2. Predict Endpoint

**Method:** POST
**URL:** [http://localhost:8080/v1/predict](http://localhost:8080/v1/predict)

**Body (Form-Data):**

* Key: `image`
* Type: File
* Value: Select an image file (e.g., `img_7.png`)

Response:

```json
{
  "category": "toxic",
  "input_text": "the graphic description of the crime scene made me feel sick.",
  "nsfw": {
    "is_nsfw": false,
    "method": "text based model"
  },
  "risk": "LOW",
  "success": true,
  "timestamp": "2025-10-03T06:30:51Z"
}
```

---

## 📌 Notes

* Datasets (`.csv.zip`) are compressed for storage efficiency.
* The trained pipeline is saved as `production_pipeline.pkl`.
* You can retrain models via `model_training.ipynb`.

---

## 📜 License

This project is licensed under the MIT License.
