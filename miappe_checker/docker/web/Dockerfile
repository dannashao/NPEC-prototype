FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY docker/web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the web application files
COPY docker/web/app.py .
COPY docker/web/static ./static
COPY docker/web/templates ./templates
COPY docker/web/src ./src

ENV PYTHONPATH=/app

EXPOSE 80

# Use Gunicorn to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--access-logfile", "-", "--error-logfile", "-", "app:app"] 