import zmq
import time

context = zmq.Context()
control = context.socket(zmq.REP)
publisher = context.socket(zmq.PUB)

control.bind("tcp://*:5555")
publisher.bind("tcp://*:5556")

poller = zmq.Poller()
poller.register(control, zmq.POLLIN)

i = 0
while True:
    socks = dict(poller.poll(10))
    if control in socks and socks[control] == zmq.POLLIN:
        print control.recv()
        control.send("OK")

    if i % 5 == 0:
        publisher.send_multipart([b"DOMAIN", b"%s" % i])
    else:
        publisher.send_multipart([b"POOP", b"poop"])

    i = i + 1
