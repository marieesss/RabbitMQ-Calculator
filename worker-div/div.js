const amqplib = require('amqplib');

const rabbitmq_url = 'amqp://admin:admin@rabbitmq:5672';
const exchange = 'calc_exchange';
const topic = 'operation.div';
const queueName = 'queue_div';

let channel;

async function receive() {
    const connection = await amqplib.connect(rabbitmq_url);
    channel = await connection.createChannel();

    await channel.assertExchange(exchange, 'topic', { durable: true });
    await channel.assertQueue(queueName, { durable: true });
    await channel.bindQueue(queueName, exchange, topic);

    console.log(`[DIV] En attente de messages sur '${topic}'...`);

    channel.consume(queueName, consume, { noAck: false });

    process.on('SIGINT', async () => {
        console.log("[DIV] Arrêt demandé. Fermeture propre...");
        await channel.close();
        await connection.close();
        process.exit(0);
    });
}

async function consume(message) {
    if (message !== null) {
        const data = JSON.parse(message.content.toString());
        const { n1, n2 } = data;

        console.log(`[DIV] Reçu : n1 = ${n1}, n2 = ${n2}`);

        const delay = Math.floor(Math.random() * 11000) + 5000;
        await new Promise(resolve => setTimeout(resolve, delay));

        let resultValue;
        if (n2 !== 0) {
            resultValue = n1 / n2;
        } else {
            resultValue = null;
        }

        const result = {
            n1,
            n2,
            op: 'div',
            result: resultValue
        };

        channel.publish(exchange, 'operation.result', Buffer.from(JSON.stringify(result)));

        console.log(`[DIV] Résultat envoyé : ${result.result}`);
        channel.ack(message);
    }
}

receive();