FROM python:3.11-slim

WORKDIR /app

# Install dependencies once during build
RUN pip install --no-cache-dir paho-mqtt requests

# Copy application code
COPY bridge.py .

# Run the application
CMD ["python", "bridge.py"]