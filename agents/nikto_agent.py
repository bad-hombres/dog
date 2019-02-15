import dogclient
import socket
import sys
import subprocess

def handle_data(msg_type, data, emitter):
    emitter.emit_event("LOG", "Staring Nikto scan for %s" % data)
    events = []

    try:
        p = subprocess.Popen("nikto -h {}".format(data), stdout=subprocess.PIPE, shell=True)        
        out, err = p.communicate()
        print out
        events.append({"type": "file", "name": "%s_nikto.txt" % data.replace(":", "_"), "content": out})
    except Exception as ex:
        events.append({"type": "event", "event": ["LOG", "Error during nikto scan: %s" % ex] })

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

