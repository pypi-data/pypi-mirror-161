import pickle
import time
from typing import Any, List, Tuple, Union

import zmq

from easypubsub.logging import getLogger


class Subscriber:
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

        self.connect()

    def __del__(self) -> None:
        self.poller.unregister(self.socket)

    def connect(self) -> None:
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
