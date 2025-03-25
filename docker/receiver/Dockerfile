FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
# Clean install of dependencies with specific versions
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY validation.py .
COPY app.py .

# Create directory for logs
RUN mkdir -p /app/logs && \
    chmod 755 /app/logs

# Environment variables
ENV MONGODB_URI="mongodb://mongodb-service:27017/plant_data"
ENV GENOMIC_DATA_PATH="/app/data/genomic_data"
ENV FLASK_APP="app.py"
ENV FLASK_ENV="production"
ENV PYTHONUNBUFFERED="1"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application
CMD ["python", "app.py"]