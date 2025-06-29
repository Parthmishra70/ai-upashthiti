FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV and face recognition
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgcc-s1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy API code
COPY api/ .

# Create necessary directories
RUN mkdir -p registered_faces test_images

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]