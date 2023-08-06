from threading import Thread
from typing import Optional

import zmq
from zmq.utils.win32 import allow_interrupt

from easypubsub.logging import getLogger

_logger = getLogger("EasyPubSub.Proxy")


class Proxy:
    """The EasyPubSub Proxy acts as an intermediary between Publishers and Subscribers.

    Attributes:
        publishers_address (str): The address that publisher will use to connect to the Proxy.
        subscribers_address (str): The address that subscribers will use to connect to the Proxy.

    Example:
        >>> from easypubsub.proxy import Proxy
        >>> proxy = Proxy("tcp://localhost:5555", "tcp://localhost:5556")
        >>> proxy.launch()
        ...
        >>> proxy.stop()
    """

    def __init__(
        self,
        publishers_address: str,
        subscribers_address: str,
    ) -> None:
        self.ctx = zmq.Context.instance()
        self.publishers_address = publishers_address
        self.subcriber_address = subscribers_address

        _logger.info("Creating socket for publishers.")
        self.xsub_publisher_socket = self.ctx.socket(zmq.XSUB)
        _logger.info(
            "Binding socket for publishers to {}.".format(self.publishers_address)
        )
        self.xsub_publisher_socket.bind(self.publishers_address)

        _logger.info("Creating socket for subscribers.")
        self.xpub_subscriber_socket = self.ctx.socket(zmq.XPUB)
        _logger.info(
            "Binding socket for subscribers to {}.".format(self.subcriber_address)
        )
        self.xpub_subscriber_socket.bind(self.subcriber_address)

        self._proxy_thread: Optional[Thread] = None

    def _launch(self) -> None:
        _logger.info("Launching proxy.")
        try:
            with allow_interrupt(self.stop):
                zmq.proxy(self.xpub_subscriber_socket, self.xsub_publisher_socket)
        except (KeyboardInterrupt, zmq.error.ContextTerminated, zmq.error.ZMQError):
            _logger.info("Closing proxy and sockets.")
            self.xpub_subscriber_socket.close()
            self.xsub_publisher_socket.close()

        _logger.info("Done.")

    def launch(self) -> None:
        """Launch the Proxy.

        This method will launch the Proxy in a separate thread, and return immediately.
        To stop the Proxy, call the :meth:`Proxy.stop` method."""

        if self._proxy_thread is not None:
            _logger.warning("Proxy already launched.")
        else:
            self._proxy_thread = Thread(target=self._launch)
            self._proxy_thread.start()

    def stop(self) -> None:
        """Stop the Proxy thread."""

        self.xpub_subscriber_socket.close()
        self.xsub_publisher_socket.close()

        if self._proxy_thread is not None and self._proxy_thread.is_alive():
            self._proxy_thread.join()
