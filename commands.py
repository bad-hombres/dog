import projects

class CommandHandler:
    def __init__(self, client_registry):
        self.registry = client_registry
        self.handlers = {
            "connect": self.handle_connect,
            "result": self.handle_result
        }

    def handle_result(self, command):
        if not command["data"] is None:
            project = projects.Project(command["project"])
            events = []
            for d in command["data"]:
                if d["type"] == "event":
                    event = map(lambda x: x.encode('ascii'), d["event"])
                    event.append(project.name.encode('ascii'))
                    events.append(event)
                    project.save_data(d["event"])

                if d["type"] == "file":
                    project.save_file(d["name"], d["content"])

        return "OK", events

    def handle_connect(self, command):
        self.registry[command["app"]] = command["filters"]
        return "OK", [[b"DOMAIN", "www.google.com", "default"]]

    def handle(self, command):
        return self.handlers[command["type"]](command)

