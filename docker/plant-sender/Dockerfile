FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
# Pin specific versions to avoid compatibility issues
RUN pip install --no-cache-dir numpy==1.23.5 && \
    pip install --no-cache-dir -r requirements.txt

COPY src/plant_sender ./plant_sender
COPY src/plant_sender/main.py .

ENV PLANT_NAME=plant1

CMD ["python", "main.py"]

