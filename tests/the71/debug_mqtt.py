#!/usr/bin/env python3
"""
Debug MQTT messages to see what data is being sent
"""

import json
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("factory/+/+/+")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print(f"Topic: {msg.topic}")
        print(f"Value: {data.get('value')} (type: {type(data.get('value'))})")
        print(f"Data: {data}")
        print("-" * 50)
    except Exception as e:
        print(f"Error: {e}")

client = mqtt.Client()
client.username_pw_set('iot', 'iotpass')
client.on_connect = on_connect
client.on_message = on_message

client.connect('localhost', 1883, 60)
client.loop_forever()
