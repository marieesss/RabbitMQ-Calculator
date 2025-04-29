from flask import Flask, request, jsonify
import json
import pika
import threading
import time
import logging
import random



def checker():
    num1 = random.randint(0, 100)
    num2 = random.randint(0, 100)
    app.logger.info('Démarrage de la consommation RabbitMQ... %s and %s', num1, num2)

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
    x = threading.Thread(target=checker_thread)
    x.start()
    app.run(host='0.0.0.0', port=8000)