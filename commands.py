import projects

class CommandHandler:
    def __init__(self, client_registry, logger):
        self.logger = logger
        self.registry = client_registry
        self.handlers = {
            "connect": self.handle_connect,
            "result": self.handle_result,
            "lsapp": self.handle_lsapp
        }

    def handle_result(self, command):
        if not command["data"] is None:
            project = projects.Project(command["project"], self.logger)
            events = []
            for d in command["data"]:
                if d["type"] == "event":
                    event = map(lambda x: x.encode('ascii'), d["event"])
                    event.append(project.name.encode('ascii'))
                    events.append(event)
                    self.logger.info("Data %s recieved for project %s" % (event, project.name))
                    project.save_data(d["event"])

                if d["type"] == "file":
                    self.logger.info("File: %s recieved for project %s" % (d["name"], project.name))
                    project.save_file(d["name"], d["content"])

        return "OK", events

    def handle_lsapp(self, command):
        results = ""
        for r in self.registry.keys():
            results += "%s: %s\n" % (r, self.registry[r])

        return results, []

    def handle_connect(self, command):
        self.logger.info("App: %s connected and is listening for %s" % (command["app"], command["filters"]))

        self.registry[command["app"]] = command["filters"]
        return "OK", [[b"DOMAIN", "www.google.com", "default"]]

    def handle(self, command):
        return self.handlers[command["type"]](command)

