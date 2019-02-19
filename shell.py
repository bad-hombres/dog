import zmq
import cmd
import sys
import json
import os

class DogShell(cmd.Cmd):
    """Simple command processor example."""
   
    def __init__(self, host):
        cmd.Cmd.__init__(self)
        self.host = host
        self.risk_level = "1"
        self.do_chprj("default")
        self.context = zmq.Context()
        self.server = self.context.socket(zmq.REQ)
        self.server.connect("tcp://%s" % self.host)

    def emptyline(self):
        pass

    def __update_prompt(self):
        self.prompt = "%s@%s:(risk level: %s)> " % (self.project, self.host, self.risk_level)

    def complete_chprj(self, text, line, i, e):
        dirs = os.listdir("$HOME/.dog")
        return filter(lambda x: x.startswith(text), dirs)

    def do_chprj(self, line):
        self.project = line
        self.__update_prompt()

    def do_add(self, line):
        data = line.split(" ")
        request = {"type": "result", "project": self.project, "risk_level": self.risk_level, "data": [
            {"type": "event", "event": data}
        ]}
        self.server.send(json.dumps(request))
        print self.server.recv()
   
    def do_lsprj(self, line):
        request = {"type": "lsprj", "project": self.project}
        self.server.send(json.dumps(request))
        print self.server.recv()

    def do_lsapp(self, line):
        request = {"type": "lsapp", "project": self.project}
        self.server.send(json.dumps(request))
        print self.server.recv()
   
    def do_set_risk_level(self, line):
        self.risk_level = str(int(line))
        self.__update_prompt()
    
    def __send_client_command(self, command):
        data = [command, "1"]
        request = {"type": "result", "project": self.project, "risk_level": self.risk_level, "data": [
            {"type": "event", "event": data}
        ]}
        self.server.send(json.dumps(request))
        print self.server.recv()

    def do_shutdown(self, line):
        self.__send_client_command("SHUTDOWN")
        sys.exit(0)

    def do_ping(self, line):
        self.__send_client_command("PING")

    def do_quit(self, line):
        return True

if __name__ == '__main__':
    DogShell(sys.argv[1]).cmdloop()
