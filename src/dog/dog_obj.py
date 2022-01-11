from pathlib import Path
import sys
path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
sys.path.insert(0, path)

from pubblisher_mqtt import Publisher_mqtt
from utils.msgs.msg_dog_telemetry import Msg_dog_telemetry
from utils.msgs.msg_dog_matchingAI import Msg_dog_matchingAI
from utils.data_structures.data_coordinates import Data_coordinates
from utils.models.thread_model import Thread_model

import time

#classe che implementa tutti i comportamenti dell'oggettio iot cane

class Dog:
    def __init__(self, broker, port,  client_id):
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.topic_tel = f'{self.client_id}/telemetry'  
        self.topic_ai = f'{self.client_id}/ai_result'       
        self.publisher_tel = Publisher_mqtt( broker, port, self.topic_tel, client_id)
        self.publisher_ai = Publisher_mqtt( broker, port, self.topic_ai, client_id)
        
        
    def  send_data_telemetry(self): 
        msg = Msg_dog_telemetry(self.read_coordinates(), self.read_battery())             
        self.publisher_tel.publish(msg.get_json_from_dict())
        time.sleep(2)

    def  send_data_ai(self):          
        msg = Msg_dog_matchingAI(self.read_coordinates())             
        self.publisher_ai.publish(msg.get_json_from_dict())
        time.sleep(2)
    
    def send_data(self):
        tele_thread = Thread_model('telemetry', self.send_data_telemetry)
        tele_thread.start()
        ai_thread = Thread_model('ai_data', self.send_data_ai)
        ai_thread.start()
        try:
            while True:
                time.sleep(2)
        except KeyboardInterrupt:
            tele_thread.join()
            ai_thread.join()
    
    def read_coordinates(self):
        telemetry = Data_coordinates(90,30)
        return telemetry
    def read_battery(self):
        return 50


