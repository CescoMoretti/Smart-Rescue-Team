import sys
sys.path.append(".")

from pubblisher_mqtt import Publisher_mqtt
from data_structures.msg_dog_telemetry import Msg_dog_telemetry
from data_structures.data_coordinates import Data_coordinates
import time

class Dog:
    def __init__(self, broker, port,  client_id):
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.topic_tel = f'{self.client_id}/telemetry'        
        self.publisher_tel = Publisher_mqtt( broker, port, self.topic_tel, client_id)
        
        
    def fun_prova(self):
        
        msg = Msg_dog_telemetry(self.read_telemetry(), self.read_battery)      
        while True:            
            self.publisher_tel.publish(msg)
            time.sleep(2)
    
    def read_telemetry():
        telemetry = Data_coordinates(90,30)
        return telemetry
    def read_battery():
        return 50


