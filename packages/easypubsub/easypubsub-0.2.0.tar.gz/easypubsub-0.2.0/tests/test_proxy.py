from easypubsub.proxy import Proxy

SUBSCRIBERS_ADDRESS = "tcp://127.0.0.1:5555"
PUBLISHERS_ADDRESS = "tcp://127.0.0.1:5556"
# Create a Proxy.
Proxy(SUBSCRIBERS_ADDRESS, PUBLISHERS_ADDRESS).launch()
