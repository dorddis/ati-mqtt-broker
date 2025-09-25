FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies once during build
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY publisher.py .

# Run the application
CMD ["python", "publisher.py"]