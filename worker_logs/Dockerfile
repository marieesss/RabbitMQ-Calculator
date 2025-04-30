FROM python:3.11-slim

WORKDIR /app

COPY worker_logs.py .

RUN pip install pika

CMD ["python", "-u", "worker_logs.py"]
