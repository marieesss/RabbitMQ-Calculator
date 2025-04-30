
from flask import Flask, request, jsonify, send_from_directory
import json
import pika
import logging
import os
import requests 

app = Flask(__name__, static_folder='front', static_url_path='')
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

connection = None
channel = None
routing_key = {"key": "add", "routing_key": "operation.add"}
exchange_name = "calc_exchange"
exchange_fanout_name = "fanout_exchange"

def init_rabbitmq():
    global connection, channel
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='rabbitmq', 
            port=5672, 
            credentials=pika.PlainCredentials("admin", "admin")
        ))
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange_name, exchange_type='topic', durable=True)
        channel.exchange_declare(exchange=exchange_fanout_name, exchange_type='fanout', durable=True)
        app.logger.info("RabbitMQ initialisé avec succès.")
    except Exception as e:
        app.logger.error(f"Erreur lors de l'initialisation de RabbitMQ : {str(e)}")
        connection, channel = None, None

@app.route('/', methods=['GET'])
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/', methods=['POST'])
def get_operations():
    global routing_key
    data = request.get_json()
    operation = data.get('operation')
    n1 = float(data.get('n1', 0))
    n2 = float(data.get('n2', 0))

    approuved_operations = [
        {"key": "add", "routing_key": "operation.add"},
        {"key": "sub", "routing_key": "operation.sub"},
        {"key": "div", "routing_key": "operation.div"},
        {"key": "mul", "routing_key": "operation.mul"},
        {"key": "all"}
    ]

    for op in approuved_operations:
        if op['key'] == operation:
            routing_key = op
            message = json.dumps({"n1": n1, "n2": n2})
            if operation == "all":
                channel.basic_publish(exchange=exchange_fanout_name, routing_key='', body=message)
            else:
                channel.basic_publish(exchange=exchange_name, routing_key=op['routing_key'], body=message)
            return jsonify({"message": f"{n1} {operation} {n2} envoyé"}), 200

    return jsonify({"message": f"Operation '{operation}' not found!"}), 400

@app.route('/logs')
def get_logs():
    try:
        response = requests.get('http://worker_logs:4000/logs')
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": f"Erreur de proxy: {str(e)}"}), 500

if __name__ == '__main__':
    init_rabbitmq()
    app.run(host='0.0.0.0', port=8000)
