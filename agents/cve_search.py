import dogclient
import socket
import sys
import json
from ares import CVESearch

def handle_data(msg_type, data, emitter):
    emitter.emit_event("LOG", "Staring CVE Search for %s" % data)
    api = CVESearch()
    events = []

    try:
        service, name, version, cpe = data.split("~")

        if len(cpe.strip()) > 0:
            contents = api.cvefor(cpe)
            results = json.loads(contents)
            events = []

            for result in results:
                refs = map(lambda x: "<a target='_blank' href='%s'>%s</a>" % (x, x), result['references'])
                if "references" in result.keys():
                    event_info = """<p>
                        <h4>%s - %s - %s (%s)</h4>

                        <p>%s</p>
                        <p>%s</p>
                    </p>""" % (name, version, result["id"], service, result["summary"], "<br/>".join(refs))
                    events.append({"type": "event", "event": ["CVE", event_info]})

                if "exploit-db" in result.keys():
                    exploits = map(lambda x: "<a target='_blank' href='https://www.exploit-db.com/exploits/%s/'>%s</a>" % (x['id'], x['description']), result['exploit-db'])
                    for e in exploits:
                        events.append({"type": "event", "event": ["EXPLOIT", e ]})

    except Exception as ex:
        events.append({"type": "event", "event": ["LOG", "Error during CVE search: %s" % ex] })

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

