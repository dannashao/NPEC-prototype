FROM python:3.9-slim

WORKDIR /app

# Install curl for debugging
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY docker/web/requirements.txt .
RUN pip install -r requirements.txt

# Copy the src directory
COPY src /app/src
# Copy the web app files
COPY docker/web .

# Add src to Python path
ENV PYTHONPATH=/app

EXPOSE 5001

CMD ["python", "app.py"] 