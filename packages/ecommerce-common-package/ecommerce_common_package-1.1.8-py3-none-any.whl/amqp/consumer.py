# # Questo file è necessario per l'invio del messaggio ai servizi correlati
# # Pika - Python Message Queue Asynchronous Library AMQP

from logging.config import listen
from pika.exceptions import AMQPConnectionError
import pika
import time
import collections

collections.Callable = collections.abc.Callable


class AMQPConsumer:

    # hostname --> HOST
    # port --> PORT
    # username --> USERNAME rabbitmq
    # password --> PASSWORD rabbitmq
    # exchange --> EXCHANGE (spazio di lavoro fra consumer e producer)
    # queue --> QUEUE (nome della coda dentro l'exchange)
    # routing_key --> ROUTING_KEY (identificatore percorso tra exchange e queue)
    
    def __init__(self, username, password, exchange, queues: list, routing_keys: list, callbacks: list, hostname='rabbitmq', port=5672):
        self.username = username
        self.password = password
        self.exchange = exchange
        
        self.queues = queues
        self.routing_keys = routing_keys
        self.callbacks = callbacks
        
        self.hostname = hostname
        self.port = port
        self.connection = None
        self.channel = None

    def __create_connection(self):
        print('Attempting to connect to ', self.hostname)
        param = pika.ConnectionParameters(
            host=self.hostname,
            port=self.port,
            credentials=pika.PlainCredentials(self.username, self.password),
            heartbeat=600,
            blocked_connection_timeout=300
        )
        self.connection = pika.BlockingConnection(param)

    # Setup canale
    def __create_channel(self):
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange, exchange_type='direct')

    # Setup queue
    def __create_queues(self):
        for i in range(len(self.queues)):
            self.channel.queue_declare(queue=self.queues[i], durable=True)
            self.channel.queue_bind(exchange=self.exchange, queue=self.queues[i], routing_key=self.routing_keys[i])
            self.channel.basic_consume(self.queues[i], self.callbacks[i], auto_ack=False) # Queue customers

    def start_connection(self):
        """
        Start connection to RabbitMQ
        """
        self.__create_connection()
        self.__create_channel()
        self.__create_queues()
        print('Connection and channel are open')
    
    def listen(self):
        try:
            self.start_connection()
            print('Listening for messages')
            self.channel.start_consuming()
        except AMQPConnectionError as e:
            self.channel.close()
            self.connection.close()
            print('Retrying to connect to', self.hostname)
            time.sleep(5)
            return self.listen()
            