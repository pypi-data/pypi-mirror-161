from dataclasses import dataclass
from typing import List, Callable

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties


@dataclass
class RabbitChannel:
    Chat: str
    Queue: str
    RoutingKey: str
    Callback: Callable[[BlockingChannel, Basic.Deliver, BasicProperties, bytes], None]


@dataclass
class RabbitOption:
    AmpqUrl: str
    RabbitChannel: List[RabbitChannel]


class RabbitMQ_Client:
    def __init__(self, option: RabbitOption):
        self.__rmq_url_connection_str = option.AmpqUrl
        self.__params = pika.URLParameters(self.__rmq_url_connection_str)
        self.__connection = pika.BlockingConnection(self.__params)
        self.__channel = self.__connection.channel()

        # durable=True - https://www.rabbitmq.com/tutorials/tutorial-two-python.html

        for item in option.RabbitChannel:
            self.__channel.exchange_declare(item.Chat, durable=True, exchange_type="topic")
            # Attaching consumer callback functions to respective queues that we wrote above
            # https://www.rabbitmq.com/tutorials/tutorial-three-python.html
            # exclusive=True  - once the consumer connection is closed, the queue should be deleted.
            self.__channel.queue_bind(exchange=item.Chat, queue=item.Queue,
                                      routing_key=item.RoutingKey)
            self.__channel.basic_consume(queue=item.Queue, on_message_callback=item.Callback, auto_ack=True)

        self.__channel.start_consuming()
