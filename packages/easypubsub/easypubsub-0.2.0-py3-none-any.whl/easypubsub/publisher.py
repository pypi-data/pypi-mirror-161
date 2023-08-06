import pickle
import time
from typing import Any, Optional

import zmq

from easypubsub.logging import getLogger


class Publisher:
    def __init__(
        self, name: str, proxy_publishers_address: str, default_topic: str = ""
    ) -> None:
        self.publishers_address = proxy_publishers_address
        self.default_topic = default_topic
        self.name = name

        self._logger = getLogger(f"EasyPubSub.Publisher({name})")
        self.connect()

    def connect(self) -> None:
        self.ctx = zmq.Context.instance()
        self.socket = self.ctx.socket(zmq.PUB)
        self._logger.info(f"Connecting to {self.publishers_address}.")
        self.socket.connect(self.publishers_address)

        time.sleep(1)

    def publish(self, message: Any, topic: Optional[str] = None) -> None:
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
