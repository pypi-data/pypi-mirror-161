import pickle
import time
from typing import Any, Optional

import zmq

from easypubsub.logging import getLogger


class Publisher:
    """The EasyPubSub Publisher provides an interface to publish messages to a topic.

    Attributes:
        name (str): The name of the publisher. This will be used as a prefix to
            all topics used by this publisher.
        proxy_publishers_address (str): The address that the publisher will use to
            connect to the :obj:`~easypubsub.proxy.Proxy`.
        default_topic (str): The default topic to use when publishing messages.
            By default, it uses "" (empty string), which means that the messages will be
            published using :attr:`name` as the topic .

    Example:
        >>> from easypubsub.publisher import Publisher
        >>> publisher = Publisher("my_publisher", "tcp://127.0.0.1:5555")
        >>> publisher.publish("Hello world!")
        This messsage will be published to the topic "my_publisher"
        >>> publisher.publish("Hello again, world.", "my_topic")
        This message will be published to the topic "my_publisher.my_topic"
    """

    def __init__(
        self, name: str, proxy_publishers_address: str, default_topic: str = ""
    ) -> None:
        self.publishers_address = proxy_publishers_address
        self.default_topic = default_topic
        self.name = name

        self._logger = getLogger(f"EasyPubSub.Publisher({name})")
        self._connect()

    def _connect(self) -> None:
        """Connect to the proxy."""
        self.ctx = zmq.Context.instance()
        self.socket = self.ctx.socket(zmq.PUB)
        self._logger.info(f"Connecting to {self.publishers_address}.")
        self.socket.connect(self.publishers_address)

        time.sleep(1)

    def publish(self, message: Any, topic: Optional[str] = None) -> None:
        """Publish a message to a topic.

        Args:
            message (Any): The message to publish. This can be any type of data that can be pickled.
            topic (Optional[str]): The topic to publish the message to. If not specified, the
                :attr:`default_topic` will be used.
        """
        if topic is None:
            topic = self.default_topic
        if topic.endswith("."):
            self._logger.warning(
                f'Topic "{topic}" ends with a dot, I will remove the final dot before publishing.'
            )
        topic = f"{self.name}.{topic}".strip(".")
        try:
            pickled_message = pickle.dumps(message)
            self.socket.send_multipart([topic.encode("utf-8"), pickled_message])
        except:
            self._logger.exception("Could not publish message. See traceback.")
