from threading import Thread
from typing import Optional

import zmq
from zmq.devices import ThreadProxy
from zmq.utils.win32 import allow_interrupt

from easypubsub.logging import getLogger

_logger = getLogger("EasyPubSub.Proxy")


class Proxy:
    """The EasyPubSub Proxy acts as an intermediary between Publishers and Subscribers.

    Args:
        subscribers_address: The address that subscribers will use to connect to the Proxy.
        publishers_address: The address that publisher will use to connect to the Proxy.

    Example:
        >>> from easypubsub.proxy import Proxy
        >>> proxy = Proxy("tcp://localhost:5555", "tcp://localhost:5556")
    """

    def __init__(self, subscribers_address: str, publishers_address: str) -> None:
        self.ctx = zmq.Context.instance()
        self.subcriber_address = subscribers_address
        self.publishers_address = publishers_address

        _logger.info("Creating socket for subscribers.")
        self.xpub_subscriber_socket = self.ctx.socket(zmq.XPUB)
        _logger.info(
            "Binding socket for subscribers to {}.".format(self.subcriber_address)
        )
        self.xpub_subscriber_socket.bind(self.subcriber_address)

        _logger.info("Creating socket for publishers.")
        self.xsub_publisher_socket = self.ctx.socket(zmq.XSUB)
        _logger.info(
            "Binding socket for publishers to {}.".format(self.publishers_address)
        )
        self.xsub_publisher_socket.bind(self.publishers_address)

        self._proxy_thread: Optional[Thread] = None

    def stop(self) -> None:
        """Fix CTRL-C on Windows."""

        # self.ctx.term()
        self.xpub_subscriber_socket.close()
        self.xsub_publisher_socket.close()

        if self._proxy_thread is not None and self._proxy_thread.is_alive():
            self._proxy_thread.join()

    def _launch(self) -> None:
        _logger.info("Launching proxy.")
        try:
            with allow_interrupt(self.stop):
                zmq.proxy(self.xpub_subscriber_socket, self.xsub_publisher_socket)
        except KeyboardInterrupt:
            _logger.info("Detected KeyboardInterrupt. Closing proxy and sockets.")
            self.xpub_subscriber_socket.close()
            self.xsub_publisher_socket.close()
        except zmq.error.ContextTerminated:
            _logger.info("Detected ContextTerminated. Closing proxy and sockets.")
            self.xpub_subscriber_socket.close()
            self.xsub_publisher_socket.close()
        except:
            _logger.exception("Unhandled exception. Closing proxy and sockets.")
            self.xpub_subscriber_socket.close()
            self.xsub_publisher_socket.close()

        _logger.info("Done.")

    def launch(self) -> None:
        """Launch the Proxy."""

        if self._proxy_thread is not None:
            _logger.warning("Proxy already launched.")
        else:
            self._proxy_thread = Thread(target=self._launch)
            self._proxy_thread.start()
