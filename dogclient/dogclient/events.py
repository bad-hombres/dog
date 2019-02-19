# -*- coding: utf8 -*-
class DogEvent(object):
    def __init__(self, event_type, data):
        self.event_type = event_type
        self.data = data
        
    def get_event(self):
        tmp = ""
        if isinstance(self.data, dict):
            for k in self.data.keys():
                tmp += "{}={}~".format(k, str(self.data[k]).replace("~", "%7e"))
            tmp = tmp.rstrip("~")
        else:
            tmp = self.data.encode("ascii")

        return {"type": "event", "event": [self.event_type.encode("ascii"), tmp] }

    @classmethod
    def from_serialized(klass, event_type, data):
        tmp = {}

        for v in data.split("~"):
            vals = v.split("=")
            tmp[vals[0]] = vals[1]

        return DogEvent(event_type, tmp)

class HostEvent(DogEvent):
    def __init__(self, data):
        DogEvent.__init__(self, "HOST", {"value": data})

class IpRangeEvent(DogEvent):
    def __init__(self, data):
        DogEvent.__init__(self, "IPRANGE", {"value": data})

class ServiceEvent(DogEvent):
    def __init__(self, host, port):
        DogEvent.__init__(self, "SERVICE", {"host": host, "port": port})

class SoftwareEvent(DogEvent):
    def __init__(self, host, port, product, version, cpe):
        DogEvent.__init__(self, "SOFTWARE", {"host": host, "port": port, "product": product, "version": version, "cpe": cpe})

class LogEvent(DogEvent):
    def __init__(self, message):
        DogEvent.__init__(self, "LOG", message)

class CveEvent(DogEvent):
    def __init__(self, host, port, product, version, cve, details):
        DogEvent.__init__(self, "CVE", {"host": host, "port": port, "product": product, "version": version, "cve": cve, "details": details})

class ExploitEvent(DogEvent):
    def __init__(self, host, port, product, version, cve, url):
        DogEvent.__init__(self, "EXPLOIT", {"host": host, "port": port, "product": product, "version": version, "cve": cve, "url": url})

class FileEvent(DogEvent):
    def __init__(self, name, content):
        DogEvent.__init__(self, "FILE", {"name": name, "content": content})
