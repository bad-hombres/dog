import dogclient
import socket
import sys
import nmap

# Configured to work with new ELK
def handle_data(event, emitter):
    emitter.emit_event(dogclient.LogEvent("Staring NMAP scan for %s" % event.data["value"]))
    nm = nmap.PortScanner()
    events = []
    data = event.data["value"]

    try:
        if event.event_type == "IPRANGE":
            nm.scan(hosts=data, arguments='-n -sP')
            hosts_list = [x for x in nm.all_hosts() if nm[x]['status']['state'] == "up"]
            events = map(lambda x: dogclient.HostEvent(x), hosts_list)

        if event.event_type == "HOST":
            nm.scan(data, arguments="-sV --top-ports 100")

            if 'tcp' in nm[data].keys():
                for k in nm[data]['tcp'].keys():
                    product = nm[data]["tcp"][k]['product']
                    version = nm[data]["tcp"][k]['version']
                    cpe = nm[data]["tcp"][k]['cpe']

                    events.append(dogclient.ServiceEvent(data, k))
                    if not product == "":
                        events.append(dogclient.SoftwareEvent(data, k, product, version, cpe))

            events.append(dogclient.FileEvent("%s_nmap.csv" % data, nm.csv()))
    except Exception as ex:
        events.append(dogclient.LogEvent("Error during nmap scan: %s" % ex))

    return events

c = dogclient.Client("Nmap Service", sys.argv[1], ["HOST", "IPRANGE"], handle_data, risk_level=1)
try:
    c.connect()
    c.run()
except socket.error:
    print "[*] Error could not connect to server...."
except KeyboardInterrupt:
    print "[*] Shutdown signal recieved"
finally:
    c.cleanup()

