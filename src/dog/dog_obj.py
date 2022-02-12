import base64
import binascii
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
import glob
import random
import shutil
import os
import time


#classe che implementa tutti i comportamenti dell'oggetto iot cane
this_path = os.getcwd()
imgpath = this_path+'/src/dog/camera_stream_simulator.jpg'
imgs = glob.glob(this_path+'/src/dog/imgs/*.jpg')


class Dog:
    def __init__(self, broker, port, client_id):
        self.broker = broker
        self.port = port
        self.client_id = client_id        
        self.topic_tel = f'smart_rescue_team/{client_id}/telemetry'  
        self.topic_ai = f'smart_rescue_team/{client_id}/ai_result'       
        self.publisher_tel = Publisher_mqtt( broker, port, self.topic_tel, f'{self.client_id}_publisher_tel')
        self.publisher_ai = Publisher_mqtt( broker, port, self.topic_ai, f'{self.client_id}_publisher_ai')
        print(this_path)
        #self.detector = Detector('YOLOv3/yolov3.weights',
        #                this_path+'/dog/YOLOv3/yolov3.cfg',
        #                'Smart-Rescue-Team/src/dog/YOLOv3/coco.names')
        self.detector = Detector(this_path+'/src/dog/YOLOv3/yolov3.weights',
                        this_path+'/src/dog/YOLOv3/yolov3.cfg',
                        this_path+'/src/dog/YOLOv3/coco.names')
                        
        

    def send_data_telemetry(self): 
        msg = Msg_dog_telemetry(self.client_id, self.read_coordinates(), self.read_battery())             
        self.publisher_tel.publish(msg.get_json_from_dict())
        time.sleep(2)

    def send_data_ai(self):
        imgname, imgpath_pred, ack = self.detector.detectMissingPeople(imgpath)
        with open(imgpath_pred, 'rb') as imgfile:
            encoded_img = base64.b64encode(imgfile.read())     
            encoded_img = binascii.b2a_base64(imgfile.read()).decode()
            print(encoded_img)

        msg = Msg_dog_matchingAI(self.client_id, self.read_coordinates(), encoded_img, imgname, ack)             
        self.publisher_ai.publish(msg.get_json_from_dict())
        time.sleep(3)

    def simulate_camera(self):
        a = imgs[random.randint(0, (len(imgs) - 1))]
        shutil.copyfile(a, this_path+'/src/dog/camera_stream_simulator.jpg')
        time.sleep(2)
    

    def activate_dog(self):
        tele_thread = Thread_model('telemetry', self.send_data_telemetry)
        tele_thread.start()
        time.sleep(1)
        ai_thread = Thread_model('ai_data', self.send_data_ai)
        ai_thread.start()
        cam_thread = Thread_model('cam_simulation', self.simulate_camera)
        cam_thread.start()
        try:
            while True:
                time.sleep(2)
        except KeyboardInterrupt:
            tele_thread.join()
            ai_thread.join()
            cam_thread.join()
        
    
    def read_coordinates(self):
        #TODO
        telemetry = Data_coordinates(90,30)
        return telemetry

    def read_battery(self):
        #TODO
        return 50