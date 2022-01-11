from pathlib import Path
import sys
path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
sys.path.insert(0, path)

from pubblisher_mqtt import Publisher_mqtt
from utils.msgs.msg_dog_telemetry import Msg_dog_telemetry
from utils.data_structures.data_coordinates import Data_coordinates

import time

class Dog:
    def __init__(self, broker, port,  client_id):
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.topic_tel = f'{self.client_id}/telemetry'        
        self.publisher_tel = Publisher_mqtt( broker, port, self.topic_tel, client_id)
        
        
    def  send_data(self):  
        while True:  
            msg = Msg_dog_telemetry(self.read_telemetry(), self.read_battery())             
            self.publisher_tel.publish(msg.get_json_from_dict())
            time.sleep(2)
    
    def read_telemetry(self):
        telemetry = Data_coordinates(90,30)
        return telemetry
    def read_battery(self):
        return 50


