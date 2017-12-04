import zmq
import sys
import socket
import json

class Client:
    def __init__(self, name, host, filters, callback, control_port=5555, publish_port=5556):
        self.name = name
        self.control_url = "tcp://%s:%s" % (host, control_port)
        self.publish_url = "tcp://%s:%s" % (host, publish_port)
        self.filters = filters
        self.callback = callback
        self.context = zmq.Context()
        self.control = self.context.socket(zmq.REQ)
        self.publisher = self.context.socket(zmq.SUB)
        self.poller = zmq.Poller()
        self.poller.register(self.control, zmq.POLLIN)

    def connect(self):
        self.control.connect(self.control_url)
        self.publisher.connect(self.publish_url)
        
        for f in self.filters:
            self.publisher.setsockopt(zmq.SUBSCRIBE, f)
        
        print "[+] Registering node %s to listen for %s messages...." % (self.name, self.filter)
        self.control.send(b"CONNECT:%s:%s" % (self.name, ", ".join(self.filters)))

        data = self.__recv__()
        if data == "!!ERROR!!":
            raise socket.error("Could not connect to control server on: %s" % self.control_url)
        else:
            print data

    def __recv__(self, timeout=1000):
        socks = dict(self.poller.poll(timeout))
        if len(socks) == 0:
            return "!!ERROR!!"
        else:
            return self.control.recv()

    def cleanup(self):
        self.control.close()
        self.publisher.close()
        self.context.term()

    def run(self):
        while True:
            result = {}
            [address, content] = self.publisher.recv_multipart()
            print "[+] Recieved %s..." % content
            result["type"] = "result"
            result["data"] = self.callback(content)
            self.control.send(json.dumps(result))
            resp = self.control.recv()
            if resp == "!!ERROR!!":
                print "[!] Server has not acknowleged data sent..results may not have been processed "
            else:
                print "[+] %s" % resp
            
