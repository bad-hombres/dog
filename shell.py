import zmq
import cmd
import sys
import json

class DogShell(cmd.Cmd):
    """Simple command processor example."""
   
    def __init__(self, host):
        cmd.Cmd.__init__(self)
        self.host = host
        self.do_chprj("default")
        self.context = zmq.Context()
        self.server = self.context.socket(zmq.REQ)
        self.server.connect("tcp://%s" % self.host)
        self.risk_level = "1"

    def do_chprj(self, line):
        self.project = line
        self.prompt = "%s@%s> " % (self.project, self.host)

    def do_add(self, line):
        data = line.split(" ")
        request = {"type": "result", "project": self.project, "risk_level": self.risk_level, "data": [
            {"type": "event", "event": data}
        ]}
        self.server.send(json.dumps(request))
        print self.server.recv()
    
    def do_lsapp(self, line):
        request = {"type": "lsapp", "project": self.project}
        self.server.send(json.dumps(request))
        print self.server.recv()
   
    def do_set_risk_level(self, line):
        self.risk_level = str(int(line))
        print "Current Risk Level: %s" % self.risk_level
    def do_quit(self, line):
        return True

if __name__ == '__main__':
    DogShell(sys.argv[1]).cmdloop()
