FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs uploaded_images reports

# Set proper permissions for mounted data directories
RUN mkdir -p /app/data

# App environment variables will be provided at runtime
ENV IMGBB_API_KEY="" \
    SEARCHAPI_API_KEY="" \
    ANTHROPIC_API_KEY=""

# Set the working directory for Streamlit 
WORKDIR /app

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]