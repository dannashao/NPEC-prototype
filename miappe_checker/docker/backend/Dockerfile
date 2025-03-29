FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY docker/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the src directory
COPY src /app/src

# Copy backend files
COPY docker/backend .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 