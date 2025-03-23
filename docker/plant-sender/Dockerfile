FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY sender.py .
COPY data/ /app/data/

ENV PLANT_NAME=plant1

CMD ["python", "sender.py"]

