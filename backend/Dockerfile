# Use the official lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (required for some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create a writable cache directory for Hugging Face models
# Hugging Face Spaces requires this for downloading models
RUN mkdir -p /.cache/huggingface && chmod -R 777 /.cache

# Copy the rest of your backend code
COPY . .

# Hugging Face Spaces routes traffic to port 7860 by default
EXPOSE 7860

# Command to run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]