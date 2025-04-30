import pika
import json
import random
import time

# Connexion à RabbitMQ
credentials = pika.PlainCredentials('admin', 'admin')
parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()


print("aqui")

# Définir la queue résultats
queue_name = 'result_queue'
routing_key = 'operation.result'
exchange_name = 'result_exchange'
channel.exchange_declare(exchange=exchange_name, exchange_type='direct', durable=True)

channel.queue_declare(queue=queue_name)
channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)

# Callback pour traiter les messages
def on_request(ch, method, properties, body):
    try:
        print("here")
        # Récupération des variables
        message = json.loads(body)
        n1 = message['n1']
        n2 = message['n2']
        operation = message['op']
        result = message['result']

        print(f"[Worker LOGS] Nouveau Résultat: {n1} {operation} {n2} est égale à {result}")

        # Accuser réception
        ch.basic_ack(delivery_tag=method.delivery_tag)


    except Exception as e:
        print(f"[Worker SUB] Erreur de traitement : {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

# Ne traiter qu'un seul message à la fois
channel.basic_qos(prefetch_count=1)

# Consommer les messages
channel.basic_consume(queue=queue_name, on_message_callback=on_request)

print("[Worker SUB] En attente de messages... CTRL+C pour quitter")
channel.start_consuming()
