from paho.mqtt import client as mqtt_client
import time


class Publisher_mqtt:
    def __init__(self, broker, port, topic, client_id):
        self.broker =broker
        self.port = port
        self.topic = topic
        self.client_id = client_id
        #self.user = user
        #self.psw = psw
        self.connection_status = False
        self.msg_count = 0
        self.timer_connection = time.time()
        self.client = mqtt_client.Client(self.client_id)


    def connect_mqtt(self):        
        # Set Connecting Client ID if not active
        if not self.connection_status:
            print("Connessione in corso...")            
            #client = mqtt_client.Client(self.client_id)
            #client.username_pw_set(self.user, self.psw)       
            self.client.connect("localhost", keepalive=15)
            self.connection_status = True
                   

    def publish(self, msg):
        self.connect_mqtt()
        self.msg_count += 1              
        result = self.client.publish(self.topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{self.topic}`")
        else:
            print(f"Failed to send message to topic {self.topic}")
            print(f"Lost connection after {self.timer_connection - time.time()}")
            self.connection_status = False
        

    
