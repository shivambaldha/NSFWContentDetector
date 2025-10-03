# Use an official Python runtime as a parent image
FROM python:3.12

# Set environment variables
# ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Set Hugging Face cache directory inside the image
ENV HF_HOME=/models

# Pre-download model during build
RUN python -c "from transformers import AutoModelForImageClassification, ViTImageProcessor; \
AutoModelForImageClassification.from_pretrained('Falconsai/nsfw_image_detection', cache_dir='/models'); \
ViTImageProcessor.from_pretrained('Falconsai/nsfw_image_detection', cache_dir='/models')"

# Copy the current directory contents into the container at /app/
COPY . /app/

ENV PYTHONPATH="${PYTHONPATH}:/app"
RUN echo $PYTHONPATH