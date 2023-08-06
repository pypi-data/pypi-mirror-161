import pickle
import time
from typing import Any, List, Tuple, Union

import zmq

from easypubsub.logging import getLogger


class Subscriber:
    """The EasyPubSub Subscriber provides an interface to subscribe to one or more topics.

    Attributes:
        name (str): The name of the subscriber. This is used for logging purposes.
        proxy_subscribers_address (str): The address that the subscriber will use to
            connect to the :obj:`~easypubsub.proxy.Proxy`.
        topics (str | List[str]): The topics to subscribe to. If not specified, the subscriber
            will subscribe to all topics. If specified, it can be a string or a list of strings.
        receive_timeout (float): The timeout for receiving messages in the :meth:`receive` method.

    Example:
        >>> from easypubsub.subscriber import Subscriber
        >>> subscriber = Subscriber("my_subscriber", "tcp://127.0.0.1:5556")
        >>> subscriber.receive()
        [("my_publisher", "Hello world!"), ("my_publisher.my_topic", "Hello again, world.")]
    """

    def __init__(
        self,
        name: str,
        proxy_subscribers_address: str,
        topics: Union[str, List[str]] = "",
        receive_timeout: float = 0.1,
    ) -> None:

        self.name = name
        self.subscribers_address = proxy_subscribers_address
        self.receive_timeout_ms = round(receive_timeout * 1000)

        if topics == "":
            self.topics = []
        elif isinstance(topics, str):
            self.topics = [topics.encode("utf-8")]
        else:
            self.topics = [topic.encode("utf-8") for topic in topics]

        self._logger = getLogger(f"EasyPubSub.Subscriber({name})")

        self._connect()

    def __del__(self) -> None:
        self.poller.unregister(self.socket)

    def _connect(self) -> None:
        self.ctx = zmq.Context.instance()
        self.socket = self.ctx.socket(zmq.SUB)
        self._logger.info(f"Connecting to {self.subscribers_address}.")
        self.socket.connect(self.subscribers_address)

        if len(self.topics) > 0:
            for topic in self.topics:
                self._logger.info(f"Subscribing to {topic.decode('utf-8')}.")
                self.socket.setsockopt(zmq.SUBSCRIBE, topic)
        else:
            self._logger.info("Subscribing to all topics.")
            self.socket.setsockopt(zmq.SUBSCRIBE, b"")

        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)

        time.sleep(1)

    def receive(self) -> List[Tuple[str, Any]]:
        """Receive one or more messages from the subscriptions.

        Returns:
            List[Tuple[str, Any]]: A list of tuples, each containing the topic and the message.

        Example:
            >>> subscriber.receive()
            [("my_publisher", "Hello world!"), ("my_publisher.my_topic", "Hello again, world.")]
        """
        messages: List[Any] = []
        messages_available = True
        while messages_available:
            sockets = dict(self.poller.poll(self.receive_timeout_ms))
            if self.socket in sockets:
                topic, message = self.socket.recv_multipart()
                messages.append((topic.decode("utf-8"), pickle.loads(message)))
            else:
                messages_available = False

        return messages
