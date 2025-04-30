import pika
import json
import random
import time

# Connexion à RabbitMQ
credentials = pika.PlainCredentials('admin', 'admin')
parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Déclarer l'exchange direct pour toutes les opérations
exchange_name = 'calc_exchange'
result_exchange_name="result_exchange"
exchange_fanout = "fanout_exchange"

channel.exchange_declare(exchange=exchange_name, exchange_type='topic', durable=True)
channel.exchange_declare(exchange=exchange_fanout, exchange_type='fanout', durable=True)


# Définir la queue sub_queue et la binder correctement
queue_name = 'sub_queue'
routing_key = 'operation.sub'

channel.queue_declare(queue=queue_name)
channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
channel.queue_bind(exchange=exchange_fanout, queue=queue_name, routing_key='')


# Callback pour traiter les messages
def on_request(ch, method, properties, body):
    try:
        message = json.loads(body)
        n1 = message['n1']
        n2 = message['n2']

        print(f"[Worker SUB] Reçu : {n1} - {n2}")

        # Simulation d'un calcul complexe
        time.sleep(random.randint(5, 15))

        result = n1 - n2

        response = {
            "n1": n1,
            "n2": n2,
            "op": "sub",
            "result": result
        }

        # Publier le résultat
        channel.basic_publish(
            exchange=result_exchange_name,
            routing_key='operation.result',
            body=json.dumps(response)
        )

        # Accuser réception
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"[Worker SUB] Calcul terminé : {n1} - {n2} = {result}")

    except Exception as e:
        print(f"[Worker SUB] Erreur de traitement : {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

# Ne traiter qu'un seul message à la fois
channel.basic_qos(prefetch_count=1)

# Consommer les messages
channel.basic_consume(queue=queue_name, on_message_callback=on_request)

print("[Worker SUB] En attente de messages... CTRL+C pour quitter")
channel.start_consuming()
