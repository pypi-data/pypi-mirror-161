import time
from easypubsub.proxy import Proxy

def test_proxy():
    SUBSCRIBERS_ADDRESS = "tcp://127.0.0.1:5555"
    PUBLISHERS_ADDRESS = "tcp://127.0.0.1:5556"
    proxy = Proxy(SUBSCRIBERS_ADDRESS, PUBLISHERS_ADDRESS)
    proxy.launch()
    time.sleep(0.5)
    proxy.stop()
