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
        if type(callback_fun) != types.FunctionType:
           raise Exception("Callback must be a method")
        self.callbak_fun = callback_fun

        self.client = mqtt_client.Client(self.client_id)               
        #client.username_pw_set(user, password=password)    
        self.client.on_connect= self.on_connect                 
        self.client.on_message= self.on_message
    def connect(self):
        self.client.connect(self.broker, port=self.port)  
        self.client.loop_start()
        while self.connection_status != True:    #Wait for connection
            time.sleep(0.1)
        self.client.subscribe(self.topic)

    def on_connect():
        print("Successful connection to the Broker!")
    def on_message(self):
        self.callback_fun()
'''
def prova():
    pass
test = Subscriber_mqtt("prova", "prova", "prova","prova", prova)'''