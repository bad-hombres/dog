import zmq
import time
import json
import commands

context = zmq.Context()
control = context.socket(zmq.REP)
publisher = context.socket(zmq.PUB)

control.bind("tcp://*:5555")
publisher.bind("tcp://*:5556")

poller = zmq.Poller()
poller.register(control, zmq.POLLIN)
clients = {}
handler = commands.CommandHandler(clients)

while True:
    socks = dict(poller.poll(10))
    if control in socks and socks[control] == zmq.POLLIN:
        command = json.loads(control.recv())
        response, events = handler.handle(command)
        control.send(response)
        for event in events:
            publisher.send_multipart(event)
