import zmq

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

    def launch(self) -> None:
        """Launch the Proxy.

        This method will block until the Proxy is closed.
        """
        _logger.info("Launching proxy.")
        try:
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
