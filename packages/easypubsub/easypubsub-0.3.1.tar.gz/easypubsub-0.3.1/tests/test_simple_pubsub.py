import time

from easypubsub.proxy import Proxy
from easypubsub.publisher import Publisher
from easypubsub.subscriber import Subscriber


def test_simple_pubsub():
    """
    Test the simple Publish/Subscribe functionality.
    """

    PUBLISHERS_ADDRESS = "tcp://127.0.0.1:5555"
    SUBSCRIBERS_ADDRESS = "tcp://127.0.0.1:5556"

    # Create a Proxy.
    proxy = Proxy(PUBLISHERS_ADDRESS, SUBSCRIBERS_ADDRESS)
    proxy.launch()
    time.sleep(1.0)

    # Create a Publisher.
    publisher = Publisher(
        "test_publisher", PUBLISHERS_ADDRESS, default_topic="test_topic"
    )
    publisher.publish("This is a first test message.")

    # Create a Subscriber.
    subscriber = Subscriber(
        "test_subscriber", SUBSCRIBERS_ADDRESS, topics="test_publisher.test_topic"
    )

    # Wait for connection to establish.
    time.sleep(1.0)
    publisher.publish("This is a second test message.")
    messages = subscriber.receive()
    assert len(messages) == 1

    # Stop the Proxy.
    proxy.stop()
