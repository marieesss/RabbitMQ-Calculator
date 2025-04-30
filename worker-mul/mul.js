const amqplib = require('amqplib');

const rabbitmq_url = 'amqp://admin:admin@rabbitmq:5672';
const exchange = 'calc_exchange'; 
const result_exchange = 'result_exchange';
const queueName = 'queue_mul';
const fanout_exchange = 'fanout_exchange';

const topic = 'operation.mul';

let channel;

async function receive() {
    const connection = await amqplib.connect(rabbitmq_url);
    channel = await connection.createChannel();

    // Déclare les exchanges
    await channel.assertExchange(exchange, 'topic', { durable: true });
    await channel.assertExchange(fanout_exchange, 'fanout', { durable: true });

    // Déclare une queue PERSISTANTE (durable), non exclusive
    const { queue } = await channel.assertQueue(queueName, { durable: true });

    // Lie la queue aux exchanges
    await channel.bindQueue(queue, exchange, topic);
    await channel.bindQueue(queue, fanout_exchange, '');

    process.on('SIGINT', async () => {
        await channel.cancel(queue);
        await channel.deleteQueue(queue);
        process.exit(0);
    });

    console.log(`[MUL] En attente de messages sur '${topic}'...`);
    channel.consume(queue, consume, { noAck: false });
}

async function consume(message) {
    if (message !== null) {
        const data = JSON.parse(message.content.toString());
        const { n1, n2 } = data;

        console.log(`[MUL] Reçu : n1 = ${n1}, n2 = ${n2}`);

        // Simule une tâche avec délai aléatoire entre 5 et 16 sec
        const delay = Math.floor(Math.random() * 11000) + 5000;
        await new Promise(resolve => setTimeout(resolve, delay));

        const result = {
            n1,
            n2,
            op: 'mul',
            result: n1 * n2
        };

        // Publie le résultat dans l'exchange "result_exchange"
        channel.publish(result_exchange, 'operation.result', Buffer.from(JSON.stringify(result)));

        console.log(`[MUL] Résultat envoyé : ${result.result}`);

        channel.ack(message);
    }
}

receive();