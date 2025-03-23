FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY receiver.py .
COPY data/genomic_data.tab /app/data/

ENV MONGODB_URI=mongodb://mongodb-service:27017/
ENV GENOMIC_DATA_PATH=/app/data/genomic_data.tab

CMD ["python", "receiver.py"]