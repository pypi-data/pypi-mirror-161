import os
import pika

class Messenger:
    "VERSION 0.0.1"
    def __init__(self,connection,queue = None):
        self.connection = connection.connection
        self.channel = self.connection.channel()
        self.queue = queue

    def queue_declare(self, queue,*args,**kwargs):
        self.queue = queue
        declare = self.channel.queue_declare(queue,*args,**kwargs)
        if(queue == ''):
            self.queue = declare.method.queue

    def exchange(self, exchange = 'exchange', *args,**kwargs):
        kwargs['exchange'] = exchange
        self.channel.exchange_declare(*args,**kwargs)
        self._exchange = exchange

    def bind(self,binding_key):
        if(self.queue is None): raise Exception("Queue is not declared use .queue_declare to create a queue")
        self.channel.queue_bind(exchange=self._exchange, queue=self.queue, routing_key=binding_key)

    def send(self,routing_key,message,**kwargs):
        kwargs['routing_key'] = routing_key
        kwargs['body'] = message
        kwargs['exchange'] = self._exchange
        return self.channel.basic_publish(**kwargs)

    def reply(self,properties,message,**kwargs):
        kwargs['routing_key'] = properties.reply_to
        kwargs['body'] = message
        kwargs['exchange'] = ''
        kwargs['properties'] = pika.BasicProperties(correlation_id = properties.correlation_id)
        return self.channel.basic_publish(**kwargs)

    def basic_consume(self,*args,**kwargs):
        if(self.queue is not None): kwargs['queue'] = self.queue
        return self.channel.basic_consume(*args,**kwargs)

    def __call__(self,*args,**kwargs):
        if(self.queue is not None): kwargs['queue'] = self.queue
        self.iterator = self.channel.consume(*args,**kwargs)
        return self

    def __iter__(self):
        return iter(self.iterator)

    def _callback(self, ch,method, properties, message):
            if self.correlation_id == properties.correlation_id:
                self.response = message

    def request(self,routing_key,message, timeout = 10):
        self.response = None
        self.correlation_id = os.urandom(32).hex()
        self.send(routing_key,message,properties=pika.BasicProperties(
                        reply_to = self.queue,
                        correlation_id=self.correlation_id,
                    ))

        self.basic_consume(on_message_callback = self._callback, auto_ack = True)
        self.connection.process_data_events(time_limit=timeout)
        return self.response
