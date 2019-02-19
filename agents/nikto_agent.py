import dogclient
import socket
import sys
import subprocess
import requests

def is_http(host):
    urls = map(lambda x: "{}://{}".format(x, host), ["http", "https"])

    for u in urls:
        try:
            requests.get(u, timeout=1, verify=False)
            return True
        except:
            pass
    return False

def handle_data(event, emitter):
    data = event.data["host"] + ":" + event.data["port"]
    emitter.emit_event(dogclient.LogEvent("Staring Nikto scan for %s" % data))
    events = []

    try:
        if is_http(data):
            p = subprocess.Popen("nikto -ask no -h {}".format(data), stdout=subprocess.PIPE, shell=True)        
            out, err = p.communicate()
            print out
            events.append(dogclient.FileEvent("%s_nikto.txt" % data.replace(":", "_"), out))
        else:
            events.append(dogclient.LogEvent("{} is not a http server skipping".format(data)))
    except Exception as ex:
        events.append(dogclient.LogEvent("Error during nikto scan: %s" % ex))

    return events

c = dogclient.Client("Nikto Agent", sys.argv[1], ["SERVICE"], handle_data, risk_level=2)
try:
    c.connect()
    c.run()
except socket.error:
    print "[*] Error could not connect to server...."
except KeyboardInterrupt:
    print "[*] Shutdown signal recieved"
finally:
    c.cleanup()

