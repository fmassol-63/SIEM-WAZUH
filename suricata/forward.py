import os
import json
import time
import requests
import urllib3
from datetime import datetime

urllib3.disable_warnings()

OPENSEARCH_URL = "https://192.168.20.30:9200"
USER = "admin"
PASS = os.environ.get("OPENSEARCH_PASSWORD", "changeme")
LOG_FILE = "/var/log/suricata/eve.json"

def send_log(event):
    date = datetime.now().strftime("%Y.%m.%d")
    index = "suricata-" + date
    try:
        r = requests.post(
            OPENSEARCH_URL + "/" + index + "/_doc",
            json=event,
            auth=(USER, PASS),
            verify=False,
            timeout=5
        )
        return r.status_code == 201
    except Exception as e:
        print("Error: " + str(e))
        return False

def tail_file(filepath):
    with open(filepath, 'r') as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if line:
                try:
                    yield json.loads(line)
                except:
                    pass
            else:
                time.sleep(1)

print("Starting log forwarder...")
while True:
    try:
        for event in tail_file(LOG_FILE):
            if send_log(event):
                print("Sent: " + event.get("event_type", "unknown"))
    except Exception as e:
        print("Error: " + str(e))
        time.sleep(5)
