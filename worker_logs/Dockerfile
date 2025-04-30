FROM python:3.11-slim

WORKDIR /app

COPY worker_logs.py .

RUN pip install flask pika flask-cors

RUN pip install requests

EXPOSE 4000

CMD ["python", "-u", "worker_logs.py"]