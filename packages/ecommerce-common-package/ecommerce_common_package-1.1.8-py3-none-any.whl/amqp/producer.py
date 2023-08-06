# # Questo file è necessario per l'invio del messaggio ai servizi correlati
# # Pika - Python Message Queue Asynchronous Library AMQP

import pika
import json
import collections

collections.Callable = collections.abc.Callable

class AMQPProducer:

    def __init__(self, username, password, exchange, queue, routing_key, hostname='rabbitmq', port=5672):
        self.username = username
        self.password = password
        self.exchange = exchange
        self.queue = queue
        self.routing_key = routing_key
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
    def __create_queue(self):
        self.channel.queue_declare(queue=self.queue, durable=True)
        self.channel.queue_bind(exchange=self.exchange, queue=self.queue, routing_key=self.routing_key)

    def publish(self, method, props, body):
        self.__create_connection()
        self.__create_channel()
        self.__create_queue()
    
        if self.connection.is_open and self.channel.is_open:
            print('Connection and channel are open')
            props = pika.BasicProperties(
                method, correlation_id=props.correlation_id,
            )
            
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=self.routing_key,
                body=body,
                properties=props
            )
            print('Message sent')
        else:
            print('Connection or channel not open, cannot send message')
            










