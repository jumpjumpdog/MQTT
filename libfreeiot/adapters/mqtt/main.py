"""
    MQTT Adapter Module
"""
import os
import json
import paho.mqtt.client as mqtt
from ..base import BaseAdapter
from .Parse import main as Parse

class MQTTAdapter(BaseAdapter):
    """ Base Adapter Class """
    client_id = os.environ.get("MQTT_CLIENTID") or "mqtt-adapter"
    server_address = os.environ.get("MQTT_HOST") or "localhost"
    server_port = int(os.environ.get("MQTT_PORT")) or 9001
    client = mqtt.Client("client",transport='websockets',clean_session=True)
    parse_driver = os.environ.get("MQTT_PARSE_DRIVER") or "json"

    def run(self):
        """ Main Entry for Adapter """
        # self.client = mqtt.Client("client",transport='websockets',clean_session=True)
        # self.client.on_connect = self.on_connect
        # self.client.on_message = self.on_message
        # self.client.on_publish = self.on_publish
        # self.client.on_subscribe = self.on_subscribe
        # self.client.connect(self.server_address, self.server_port) # 连接服务器（TCP）
        # # self.scope["mqt1tClient"] = self.client # 将 client 代入 Adapter 作用域
        # self.client.loop_start()
        # self.client.subscribe("temperature", qos=2)
        # print('Hello from MQTTAdapter')
        pass



    def on_connect(self, client, userdata, flags, rc):
        """ Callback while conntected """
        print("MQTT Broker connected with result code "+str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        # self.client.subscribe("humid")
        # self.client.publish("humid","hello")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        """ Callback while received messageA """
        # print(msg)
        Parse.main(client, msg.topic.split('/'), self.parse_driver_select(msg.payload.decode()))

    def on_subscribe(self,client, userdata, mid, granted_qos):
        print("subscribed with qos", granted_qos, "\n")

    def on_publish(client,userdata,mid):
        print("data published mid=", mid, "\n")


    def parse_driver_select(self, data):
        """ Select a driver to parse data """
        if self.parse_driver == 'msgpack':
            raise OSError("Parse driver 'msgpack' under development.")
        elif self.parse_driver == 'json':
            try:
                return json.loads(data)
            except json.JSONDecodeError as e:
                print("Parsing failed, reason: ", e)
        else:
            raise OSError("Parse driver '" + self.parse_driver + "' under development.")
