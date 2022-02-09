from pathlib import Path
import sys
path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
sys.path.insert(0, path)

from utils.models.pubblisher_mqtt import Publisher_mqtt
from utils.msgs.msg_dog_telemetry import Msg_dog_telemetry
from utils.msgs.msg_dog_matchingAI import Msg_dog_matchingAI
from utils.data_structures.data_coordinates import Data_coordinates
from utils.models.thread_model import Thread_model
from dog.ai_detection import Detector

import time

#classe che implementa tutti i comportamenti dell'oggettio iot cane

class Dog:
    def __init__(self, broker, port, client_id):
        self.broker = broker
        self.port = port
        self.client_id = client_id        
        self.topic_tel = f'smart_rescue_team/{client_id}/telemetry'  
        self.topic_ai = f'smart_rescue_team/{client_id}/ai_result'       
        self.publisher_tel = Publisher_mqtt( broker, port, self.topic_tel, f'{self.client_id}_publisher_tel')
        self.publisher_ai = Publisher_mqtt( broker, port, self.topic_ai, f'{self.client_id}_publisher_ai')
        self.detector = Detector('.\YOLOv3\yolov3-tiny.weights', '.\YOLOv3\yolov3-tiny.cfg', '.\YOLOv3\coco.names')
        
    def  send_data_telemetry(self): 
        msg = Msg_dog_telemetry(self.client_id, self.read_coordinates(), self.read_battery())             
        self.publisher_tel.publish(msg.get_json_from_dict())
        time.sleep(2)

    def  send_data_ai(self):          
        msg = Msg_dog_matchingAI(self.client_id, self.read_coordinates(),self.get_result_ai())             
        self.publisher_ai.publish(msg.get_json_from_dict())
        time.sleep(2)
    

    def send_data(self, img):
        tele_thread = Thread_model('telemetry', self.send_data_telemetry)
        tele_thread.start()
        ai_thread = Thread_model('ai_data', self.detector.detectMissingPeople(img))
        ai_thread.start()
        try:
            while True:
                time.sleep(2)
        except KeyboardInterrupt:
            tele_thread.join()
            ai_thread.join()
    
    def read_coordinates(self):
        #TODO
        telemetry = Data_coordinates(90,30)
        return telemetry
    def read_battery(self):
        #TODO
        return 50
    def get_result_ai(self):
        return "ack"