import time

from easypubsub.proxy import Proxy


def test_proxy():
    PUBLISHERS_ADDRESS = "tcp://127.0.0.1:5555"
    SUBSCRIBERS_ADDRESS = "tcp://127.0.0.1:5556"
    proxy = Proxy(
        PUBLISHERS_ADDRESS,
        SUBSCRIBERS_ADDRESS,
    )
    proxy.launch()
    time.sleep(0.5)
    proxy.stop()
