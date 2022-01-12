from pathlib import Path
import sys
path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
sys.path.insert(0, path)

from utils.models.subscriber_mqtt import Subscriber_mqtt
from utils.models.thread_model import Thread_model
from utils.data_structures.data_coordinates import Data_coordinates
import time

class Rescue_team_obj:
    def __init__(self, broker, port,  client_id):
        self.broker = broker
        self.port = port
        self.client_id = client_id        
        self.topic_tel = 'smart_rescue_team/+/telemetry'         
        self.subscriber_tel = Subscriber_mqtt(self.broker, self.port, self.topic_tel, self.client_id, self.callback_dog_tel)

    def start(self):
        self.send_data_telemetry
        self.subscriber_tel.connect()
        try:
            while True:
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("exiting")
            self.subscriber_tel.disconnect()
            #TODO join thread here if used for tele data

    
    def send_data_telemetry(self): 
        cords = self.read_coordinates()
        #TODO capire come mandare i dati (probabilmente staccare un thread)
        pass

    def callback_dog_tel(self):
        #TODO
        pass

    def read_coordinates(self):
        #TODO
        telemetry = Data_coordinates(90,30)
        return telemetry
  