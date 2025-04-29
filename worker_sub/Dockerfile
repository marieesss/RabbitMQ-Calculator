FROM python:3.11-slim

WORKDIR /app

COPY worker_sub.py .

RUN pip install pika

CMD ["python", "worker_sub.py"]