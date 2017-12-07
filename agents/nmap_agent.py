import dogclient
import socket
import sys
import nmap

def handle_data(msg_type, data, emitter):
    emitter.emit_event("LOG", "Staring NMAP scan for %s" % data)
    nm = nmap.PortScanner()
    events = []

    try:
        if msg_type == "IPRANGE":
            nm.scan(hosts=data, arguments='-n -sP')
            hosts_list = [x for x in nm.all_hosts() if nm[x]['status']['state'] == "up"]
            events = map(lambda x: {"type": "event", "event": ["HOST", x ]}, hosts_list)

        if msg_type == "HOST":
            nm.scan(data, arguments="-sV --top-ports 100")

            if 'tcp' in nm[data].keys():
                for k in nm[data]['tcp'].keys():
                    product = nm[data]["tcp"][k]['product']
                    version = nm[data]["tcp"][k]['version']
                    cpe = nm[data]["tcp"][k]['cpe']

                    events.append({"type": "event", "event": ["SERVICE", "%s:%s" % (data, k)] })
                    if not product == "":
                        events.append({"type": "event", "event": ["SOFTWARE", "%s:%s~%s~%s~%s" % (data, k,product, version, cpe)] })

            events.append({"type": "file", "name": "%s_nmap.csv" % data, "content": nm.csv() })
    except Exception as ex:
        events.append({"type": "event", "event": ["LOG", "Error during nmap scan: %s" % ex] })

    return events

c = dogclient.Client("Nmap Service", sys.argv[1], ["HOST", "IPRANGE"], handle_data, risk_level=3)
try:
    c.connect()
    c.run()
except socket.error:
    print "[*] Error could not connect to server...."
except KeyboardInterrupt:
    print "[*] Shutdown signal recieved"
finally:
    c.cleanup()

