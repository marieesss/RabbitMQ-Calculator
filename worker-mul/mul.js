const amqplib = require('amqplib');

const rabbitmq_url = 'amqp://admin:admin@rabbitmq:5672';
const exchange = 'calc_exchange'; 
const queueName = 'queue_mul';


const topic = 'operation.mul';

let channel;
let queue;

async function receive() {
    const connection = await amqplib.connect(rabbitmq_url);
    channel = await connection.createChannel();

    await channel.assertExchange(exchange, 'topic', { durable: true });

    queue = await channel.assertQueue(queueName, { exclusive: true });

    process.on('SIGINT', async () => {
        await channel.cancel(queue.queue);
        await channel.deleteQueue(queue.queue);
        process.exit(0);
    });

    await channel.bindQueue(queue.queue, exchange, topic);

    console.log(`[MUL] En attente de messages sur '${topic}'...`);

    channel.consume(queue.queue, consume, { noAck: false });
}

async function consume(message) {
    if (message !== null) {
        const data = JSON.parse(message.content.toString());
        const { n1, n2 } = data;

        console.log(`[MUL] Reçu : n1 = ${n1}, n2 = ${n2}`);

        const delay = Math.floor(Math.random() * 11000) + 5000;
        await new Promise(resolve => setTimeout(resolve, delay));

        const result = {
            n1,
            n2,
            op: 'mul',
            result: n1 * n2
        };

        const resultQueue = 'results';
        await channel.assertQueue(resultQueue, { durable: false });
        channel.sendToQueue(resultQueue, Buffer.from(JSON.stringify(result)));

        console.log(`[MUL] Résultat envoyé : ${result.result}`);

        channel.ack(message);
    }
}

receive();