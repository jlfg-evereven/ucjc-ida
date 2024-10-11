import pika
import os

# read rabbitmq connection url from environment variable
#amqp_url = 'amqp://localhost?connection_attempts=10&retry_delay=10'
amqp_url = os.environ['AMQP_URL']
url_params = pika.URLParameters(amqp_url)

# connect to rabbitmq
connection = pika.BlockingConnection(url_params)
chan = connection.channel()

# new queue
chan.queue_declare(queue='hello', durable=True)

# publish a 10 messages to the queue
for i in range(10):
    chan.basic_publish(exchange='', routing_key='hello',
                       body='Hello World', properties=pika.BasicProperties(delivery_mode=2))
    print("Produced the message")

chan.close()
connection.close()
