import dogclient
import socket

def handle_data(msg_typ, data, emitter):
    print data
    return [
            {"type": "event", "event": [b"HOST", b"10.11.1.1"]},
            {"type": "file", "name": "scan_results.txt", "content": "hello homies"}
    ]

c = dogclient.Client("Test App", "localhost", ["DOMAIN"], handle_data)
try:
    c.connect()
    c.run()
except socket.error:
    print "[*] Error could not connect to server...."
except KeyboardInterrupt:
    print "[*] Shutdown signal recieved"
finally:
    c.cleanup()

