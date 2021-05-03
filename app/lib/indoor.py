import json
import os
from paho.mqtt import client as mqtt_client

DEBUG = os.getenv('DEBUG')
MQTTBROKER = os.getenv('MQTTBROKER')
MQTTTOPIC = os.getenv('MQTTTOPIC')
port = 1883
# generate client ID with pub prefix randomly
client_id = "google-photo-object-aware-osd"
indoorData = None

if MQTTBROKER and (MQTTBROKER > ""):
    def on_connect(client, userdata, flags, rc):
        if DEBUG == 'Y':
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(MQTTBROKER, port)
    client.loop_start()

    def on_message(client, userdata, msg):
        global indoorData
        # print(msg)
        indoorData = json.loads(msg.payload.decode())

    client.subscribe(MQTTTOPIC)
    client.on_message = on_message


def getIndoorData():
    return indoorData
