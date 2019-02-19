import dogclient
import socket
import sys
import json
import requests

def cvefor(cpe):
    r = requests.get("https://cve.circl.lu/api/cvefor/{}".format(cpe))
    return r.json()

def handle_data(event, emitter):
    events = []
    try:
        host = event.data["host"]
        port = event.data["port"]
        product = event.data["product"]
        version = event.data["version"]
        cpe = event.data["cpe"]

        emitter.emit_event(dogclient.LogEvent("Staring CVE Search for %s" % cpe))
        if len(cpe.strip()) > 0:
            results = cvefor(cpe)
            events = []

            for result in results:
                cve = result["id"]
                summary = result["summary"]
                refs = ""

                if "references" in result.keys():
                    summary += "\n" + "\n".join(result["references"])

                events.append(dogclient.CveEvent(host, port, product, version, cve, summary))

                if "exploit-db" in result.keys():
                    exploits = map(lambda x: "https://www.exploit-db.com/exploits/%s/" % x['id'].replace("EDB-ID:", ""), result['exploit-db'])
                    for e in exploits:
                        events.append(dogclient.ExploitEvent(host, port, product, version, cve, e))

    except Exception as ex:
        print ex
        events.append(dogclient.LogEvent("Error during CVE search: %s" % ex))

    return events

c = dogclient.Client("CVE-Search", sys.argv[1], ["SOFTWARE"], handle_data, risk_level=1)
try:
    c.connect()
    c.run()
except socket.error:
    print "[*] Error could not connect to server...."
except KeyboardInterrupt:
    print "[*] Shutdown signal recieved"
finally:
    c.cleanup()

