import time

from easypubsub.subscriber import Subscriber

SUBSCRIBERS_ADDRESS = "tcp://127.0.0.1:5555"

subscriber = Subscriber(
    "test_subscriber", SUBSCRIBERS_ADDRESS, topics="test_publisher.test_topic"
)

try:
    while True:
        result = subscriber.receive()
        if len(result) > 0:
            print("Received:")
            for topic, message in result:
                print(f"{topic}: {message}")
        else:
            time.sleep(1.0)
            # print("No message received.")
except KeyboardInterrupt:
    pass
