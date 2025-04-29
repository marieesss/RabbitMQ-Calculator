from flask import Flask, request, jsonify
import json
import pika
import threading
import time
import logging
import random


connection = None
channel = None
routing_key={"key" : "addition", "routing_key": "operation.add"}
exchange_name = "calc_exchange"
exchange_fanout_name = "fanout_exchange"


def init_rabbitmq():
    global connection, channel
    try:
        # Connection à RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', port=5672, credentials=pika.PlainCredentials("admin", "admin"),))
        channel = connection.channel()

        app.logger.info("RabbitMQ initialisé avec succès.")

        app.logger.info(exchange_name)

        # New exchange
        channel.exchange_declare(exchange=exchange_name, exchange_type='topic', durable=True)
        channel.exchange_declare(exchange=exchange_fanout_name, exchange_type='fanout', durable=True)


        app.logger.info("RabbitMQ initialisé avec succès.")

    except Exception as e:
        app.logger.error(f"Erreur lors de l'initialisation de RabbitMQ : {str(e)}")
        connection, channel = None, None

def send_numbers():
    # Random numbers
    num1 = random.randint(0, 100)
    num2 = random.randint(0, 100)
    app.logger.info('Démarrage de la consommation RabbitMQ... %s ', routing_key)

    # If channel exists, send number to routing key choosen
    if channel is not None:
        message=json.dumps({"n1" : num1, "n2" : num2})
        if routing_key.get('key') == "all" :
            channel.basic_publish(exchange=exchange_fanout_name, routing_key='', body=message)
        else:
            channel.basic_publish(exchange=exchange_name,routing_key=routing_key.get('routing_key'), body=message)
def checker_thread():
    while True:
        send_numbers()
        time.sleep(5)

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

@app.route('/',  methods=['POST'])
def get_operations():
    global routing_key
    data = request.get_json()
    operation = data['operation']

    approuved_operations = [
        {"key" : "addition", "routing_key": "operation.add"}, 
        {"key" : "soustraction", "routing_key": "operation.sub"}, 
        {"key" : "division", "routing_key": "operation.div"}, 
        {"key" : "multiplication", "routing_key": "operation.mul"},
        {"key" : "all"}
        ]

    # Chercher l'opération dans la liste
    operation_found = None
    for op in approuved_operations:
        if op['key'] == operation:
            # Change global routine key
            routing_key = op
            operation_found = op
            break 

    if operation_found:
        return jsonify({"message": f"Operation '{operation}' found!"})
    else:
        return jsonify({"message": f"Operation '{operation}' not found!"}), 404


if __name__ == '__main__':
    init_rabbitmq()
    x = threading.Thread(target=checker_thread)
    x.start()
    app.run(host='0.0.0.0', port=8000)