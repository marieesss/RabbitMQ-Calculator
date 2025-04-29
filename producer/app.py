from flask import Flask, request, jsonify
import json
import pika
import threading
import time
import logging
import random


connection = None
channel = None
operation="sum"

def init_rabbitmq():
    global connection, channel
    try:
        exchange_name = "topic_exchange"
        # Connection à RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', port=5672, credentials=pika.PlainCredentials("admin", "admin"),))
        channel = connection.channel()

        # New exchange
        channel.exchange_declare(exchange=exchange_name, exchange_type='topic')

        app.logger.info("RabbitMQ initialisé avec succès.")

    except Exception as e:
        app.logger.error(f"Erreur lors de l'initialisation de RabbitMQ : {str(e)}")
        connection, channel = None, None

def checker():
    # Random numbers
    num1 = random.randint(0, 100)
    num2 = random.randint(0, 100)
    app.logger.info('Démarrage de la consommation RabbitMQ... %s and %s', num1, num2)

    if channel is not None:

        message=json.dumps({"num1" : num1, "num2" : num2})
        channel.basic_publish(exchange="topic_exchange", routing_key=operation, body=message)
        app.logger.info('topic envoyé')

def checker_thread():
    while True:
        checker()
        time.sleep(5)

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

@app.route('/',  methods=['POST'])
def get_operations():
    data = request.get_json()
    operation = data['operation']

    return jsonify({"operation choosed": operation})


if __name__ == '__main__':
    init_rabbitmq()
    x = threading.Thread(target=checker_thread)
    x.start()
    app.run(host='0.0.0.0', port=8000)