import zmq
import sys
import socket
import json
from .events import LogEvent, DogEvent

class Emitter:
    def __init__(self, socket, project, risk_level):
        self.socket = socket
        self.project = project
        self.risk_level = risk_level

    def emit_event(self, event_object):
        event = [
           event_object
        ]

        return self.emit_result(event)

    def emit_result(self, data):
        result = {}
        result["type"] = "result"
        result["data"] = [x.get_event() for x in data]
        result["project"] = self.project
        result["risk_level"] = self.risk_level

        self.socket.send(json.dumps(result))
        return self.socket.recv()

class Client:
    def __init__(self, name, host, filters, callback, risk_level=3, control_port=5555, publish_port=5556):
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
        self.risk_level = risk_level

    def connect(self):
        self.control.connect(self.control_url)
        self.control.setsockopt(zmq.LINGER, 0)
        self.publisher.connect(self.publish_url)
        self.publisher.setsockopt(zmq.LINGER, 0)
        
        for f in self.filters:
            self.publisher.setsockopt(zmq.SUBSCRIBE, f)

        self.publisher.setsockopt(zmq.SUBSCRIBE, "SHUTDOWN")
        self.publisher.setsockopt(zmq.SUBSCRIBE, "PING")
        
        print "[+] Registering node %s to listen for %s messages...." % (self.name, self.filters)
        connect = {"type": "connect", "app": self.name + "@" + socket.gethostname(), "filters": self.filters}
        self.control.send(json.dumps(connect))

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
            [address, content, project, risk_level] = self.publisher.recv_multipart()
            risk_level = int(risk_level)
                
            if address == "SHUTDOWN":
                print "[!] Shutdown recieved..."
                break

            emitter = Emitter(self.control, project, risk_level)
            
            if address == "PING":
                print "[+] Recived PING message..."
                emitter.emit_event(LogEvent(self.name + "@" + socket.gethostname() + ", filters:" + str(self.filters)))
                continue

            print "[+] Recieved %s..." % content
            if self.risk_level <= risk_level:
                event = DogEvent.from_serialized(address, content)
                resp = emitter.emit_result(self.callback(event, emitter))

                if resp == "!!ERROR!!":
                    print "[!] Server has not acknowleged data sent..results may not have been processed "
                else:
                    print "[+] %s" % resp
            else:
                message = "Message recieved with risk_level: %s current risk_level: %s....message has been rejected" % (risk_level, self.risk_level)
                print "[!] " + message
                emitter.emit_event(LogEvent(message))
            
