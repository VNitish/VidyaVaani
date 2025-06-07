# Use Python 3.10 as base
FROM python:3.10-slim-buster

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 10000

# Start Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:create_app()"]