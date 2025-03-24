FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
# Clean install of dependencies with specific versions
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV MONGODB_URI=mongodb://mongodb-service:27017/plant_data
ENV GENOMIC_DATA_PATH=/app/data/genomic_data
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

CMD ["python", "app.py"]