from flask import Flask, jsonify
import pika
import json
import threading
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
log_history = []

credentials = pika.PlainCredentials('admin', 'admin')
parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

queue_name = 'result_queue'
exchange_name = 'result_exchange'
routing_key = 'operation.result'

channel.exchange_declare(exchange=exchange_name, exchange_type='direct', durable=True)
channel.queue_declare(queue=queue_name)
channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)

def on_request(ch, method, properties, body):
    try:
        # Récupération des variables
        message = json.loads(body)
        n1 = message['n1']
        n2 = message['n2']
        operation = message['op']
        result = message['result']
        log_entry = f"{n1} {operation} {n2} = {result}"
        print(f"[Worker LOGS] {log_entry}")
        log_history.append(log_entry)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"[Worker LOGS] Erreur : {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consuming():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=on_request)
    channel.start_consuming()

@app.route('/logs')
def get_logs():
    return jsonify(log_history[-10:])  # ✅ Retourne les logs stockés

if __name__ == '__main__':
    threading.Thread(target=start_consuming, daemon=True).start()
    app.run(host='0.0.0.0', port=4000)