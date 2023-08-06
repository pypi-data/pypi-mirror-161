import time

from easypubsub.publisher import Publisher

PUBLISHERS_ADDRESS = "tcp://127.0.0.1:5556"

publisher = Publisher("test_publisher", PUBLISHERS_ADDRESS, default_topic="test_topic")
publisher.publish("This is a test message.")
publisher.publish("This is a debug test message.", topic="debug_test_topic")
publisher.publish("This is a test list".split(" "))
publisher.publish("This will throw a warning", topic="my_wrong_topic.")
time.sleep(2.0)
publisher.publish("This is a test message.")
publisher.publish("This is a debug test message.", topic="debug_test_topic")
publisher.publish("This is a test list".split(" "))
publisher.publish("This will throw a warning", topic="my_wrong_topic.")
