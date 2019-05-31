"""
    MQTT Adapter Module
"""
import os
import json
import paho.mqtt.client as paho
from Base.base import BaseAdapter
from tool import  equipmentQuery, getEqpByID, online
from pymongo import MongoClient
import time
import json
import random

mongo = MongoClient( "localhost",  27017)
mongo.db = mongo["freeiot"]
temperature_col = mongo.db["temperature"]
temperature_topic = "temperature"

online_eqps = []
eqps_t = {}
def init_online_eqps():
    eqps = equipmentQuery()
    for eqp in eqps:
        online_eqps.append(eqp['id'])
        max_t = int(eqp['max_t'])
        min_t = int(eqp['min_t'])
        eqps_t[eqp['id']] = [max_t,min_t,(max_t+min_t)/2]
init_online_eqps()
def create_data(init_data,max_const,min_const):
    flag = random.randint(-1,1)*0.2
    init_data = init_data + flag if (init_data + flag > max_const or init_data +flag<min_const) else init_data - flag
    max_data = init_data +random.randint(0,10)*0.1
    min_data = init_data -random.randint(0,10)*0.1
    return (max_data,min_data,init_data)
def timer(n,client):
    while True:
        int_msg_time = int(time.time()*1000)
        for eqp_id in online_eqps:
            (max_t,min_t,temperature) = create_data(eqps_t[eqp_id][2],eqps_t[eqp_id][0],eqps_t[eqp_id][1])
            eqps_t[eqp_id][2] = temperature
            client.publish(eqp_id+'/'+temperature_topic,payload=json.dumps({'id':'no id','create_time':int_msg_time,"temperature":{"min_t":min_t,"max_t":max_t,"t":temperature}}),qos=2)
            temperature_col.insert_one({"eqp_id": eqp_id, "create_time": int_msg_time,
                                    "temperature": {"min_t": min_t, "max_t": max_t, "t": temperature}})
        # print((max_t, min_t, temperature))
        # print(temperature_topic)
        time.sleep(n)

class MQTTAdapter(BaseAdapter):
    """ Base Adapter Class """

    def __init__(self):
        self.client_id = "mqtt-adapter"
        self.server_address = "localhost"
        self.server_port = 9001
        self.client = paho.Client("client", transport='websockets', clean_session=True)
        self.parse_driver = os.environ.get("MQTT_PARSE_DRIVER") or "json"


    def subscribeAllEquipment(self,client):
        eqpList = equipmentQuery()
        for eqp in eqpList:
            client.subscribe(eqp['id']+'/temperature')

    def run(self):
        """ Main Entry for Adapter """
        self.client = paho.Client("client",transport='websockets',clean_session=True)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.client.on_subscribe = self.on_subscribe
        self.client.connect(self.server_address, self.server_port) # 连接服务器（TCP）
        # self.scope["mqt1tClient"] = self.client # 将 client 代入 Adapter 作用域
        # self.client.subscribe("temperature")
        self.client.subscribe("SYS/online")
        self.client.subscribe("SYS/will")
        self.subscribeAllEquipment(self.client)
        self.client.loop_start()
        print('Hello from MQTTAdapter')
        timer(2,self.client)
        # self.client.loop_forever()

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
        topic = msg.topic.split('/')
        payload = json.loads(msg.payload.decode())
        if topic[0]=='SYS':
            if topic[1] == 'online':
                if payload['id'] not in online_eqps:
                    online(payload['id'])
                    online_eqps.append(payload['id'])
        elif topic[1] == 'temperature':
            temperature = getEqpByID(topic[0])
            if (not (payload['temperature']['t']>temperature.min_t and payload['temperature']['t']<temperature.max_t)):
                print("发送了")
                client.publish("exceptionsLength",1)
        # Parse.main(client, msg.topic.split('/'), self.parse_driver_select(msg.payload.decode()))

    def on_subscribe(self,client, userdata, mid, granted_qos):
        print("subscribed with qos", granted_qos, "\n")

    def on_publish(client,userdata,mid):
        print("data published mid=", mid, "\n")

    def subscribe(self, topic):
        self.client.subscribe(topic=topic)

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

if __name__ == '__main__':
    mqtt = MQTTAdapter()
    mqtt.run()


