const amqplib = require('amqplib');

const rabbitmq_url = 'amqp://admin:admin@rabbitmq:5672';
const exchange = 'calc_exchange';
const topic = 'operation.add';
const queueName = 'queue_add';

let channel;

async function receive() {
    const connection = await amqplib.connect(rabbitmq_url);
    channel = await connection.createChannel();

    await channel.assertExchange(exchange, 'topic', { durable: true });
    await channel.assertQueue(queueName, { durable: true });
    await channel.bindQueue(queueName, exchange, topic);

    console.log(`[ADD] En attente de messages sur '${topic}'...`);

    channel.consume(queueName, consume, { noAck: false });

    process.on('SIGINT', async () => {
        console.log("[ADD] Arrêt demandé. Fermeture propre...");
        await channel.close();
        await connection.close();
        process.exit(0);
    });
}

async function consume(message) {
    if (message !== null) {
        const data = JSON.parse(message.content.toString());
        const { n1, n2 } = data;

        console.log(`[ADD] Reçu : n1 = ${n1}, n2 = ${n2}`);

        const delay = Math.floor(Math.random() * 11000) + 5000;
        await new Promise(resolve => setTimeout(resolve, delay));

        const result = {
            n1,
            n2,
            op: 'add',
            result: n1 + n2
        };

        const resultQueue = 'results';
        await channel.assertQueue(resultQueue, { durable: false });
        channel.sendToQueue(resultQueue, Buffer.from(JSON.stringify(result)));

        console.log(`[ADD] Résultat envoyé : ${result.result}`);
        channel.ack(message);
    }
}

receive();