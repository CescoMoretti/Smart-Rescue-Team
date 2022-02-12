from paho.mqtt import client as mqtt_client
import time
import types


class Subscriber_mqtt():

    def __init__(self, broker, port, topic, client_id, callback_fun):
        self.broker =broker
        self.port = port
        self.topic = topic
        self.client_id = client_id
        self.connection_status = False        
        self.callbak_fun = callback_fun

        self.client = mqtt_client.Client(self.client_id)               
        #client.username_pw_set(user, password=password)    
        self.client.on_connect= self.on_connect                 
        self.client.on_message= self.on_message
    def connect(self):
        self.client.connect(self.broker, port=self.port)  
        self.client.loop_start()
        time.sleep(2)
        self.client.subscribe(self.topic)

    def disconnect(self):
        self.client.disconnect()
        self.client.loop_stop()

 
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        
        #self.client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        print(str(msg.payload.decode()))
        self.callbak_fun(str(msg.payload.decode()))
