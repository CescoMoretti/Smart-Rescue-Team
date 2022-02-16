import binascii
from doctest import DONT_ACCEPT_BLANKLINE
from pathlib import Path
import sys
path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
sys.path.insert(0, path)
from utils.msgs.msg_team_telemetry import Msg_team_telemetry
from utils.msgs.msg_team_marker import Msg_team_marker
from utils.msgs.msg_dog_matchingAI import Msg_dog_matchingAI
from utils.models.subscriber_mqtt import Subscriber_mqtt
from utils.models.thread_model import Thread_model
from utils.data_structures.data_coordinates import Data_coordinates
import time
import requests
import json, os
import numpy as np

this_path = os.getcwd()

class Rescue_team_obj:
    def __init__(self, broker, port,  client_id):
        self.broker = broker
        self.port = port
        self.client_id = client_id        
        self.topic_tel = 'smart_rescue_team/+/telemetry'    
        self.topic_ai = 'smart_rescue_team/+/ai_result'       
        self.subscriber_tel = Subscriber_mqtt(self.broker, self.port, self.topic_tel, self.client_id + "-tel", self.callback_dog_tel)
        self.subscriber_ai = Subscriber_mqtt(self.broker, self.port, self.topic_ai, self.client_id + "-ai", self.callback_dog_ai)
        self.progressive_imgId = 0
        self.movement_param = {"direction": [0, 0], "step_lenght": 0}
        self.current_cord = Data_coordinates(44.8596,10.7643) #Only for simulation purposes
        


    def start(self):
        tele_thread = Thread_model('telemetry', self.send_data_telemetry)
        tele_thread.start()
        update_direction_thread = Thread_model('telemetry', self.update_direction)
        update_direction_thread.start()
        self.subscriber_tel.connect()
        self.subscriber_ai.connect()
        try:
            while True:                
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("exiting")
            tele_thread.join()
            update_direction_thread.join()
            self.subscriber_tel.disconnect()
            self.subscriber_ai.disconnect()
            

  
    def send_data_telemetry(self): 
        msg = Msg_team_telemetry(self.client_id, self.read_coordinates())             
        r = requests.post("http://127.0.0.1:5000/data/add/"+ msg.get_json_from_dict())
        print("data team position sended to server: " + str(r.status_code), r.reason)
        time.sleep(2)

    def callback_dog_tel(self, data):        
        r = requests.post("http://127.0.0.1:5000/data/add/"+ data)
        print("data receved sended to server: " + str(r.status_code), r.reason)

    def callback_dog_ai(self, data):
        r = requests.post("http://127.0.0.1:5000/data/add/"+ data)
        print("data receved sended to server: " + str(r.status_code), r.reason)
        #le immagini vanno decodificate direttamente nel server non ha senso farlo qui
        #data_json = json.loads(data)
        #msg = Msg_dog_matchingAI(data_json["name"],
                                #data_json["gps"],
                                #data_json["img"],
                                #data_json["imgname"],
                                #data_json["ack"])
        
        #if data_json['ack'] == True:
        #    self.progressive_imgId += 1
        #    with open(this_path+'/src/rescue_team/received_positive_imgs/'+str(self.progressive_imgId)+'.jpg', 'wb') as fw:
        #        fw.write(binascii.a2b_base64(data_json['img']))
        #
        #    print('Detected People by dog '+str(data_json['name'])+'!\nAt time '+str(data_json['timestamp']))
            
    def update_direction(self):        
        obtained_direction = requests.get("http://127.0.0.1:5000/get_direction/<"+ self.client_id+ ">")
        print("receved direction: " + str(obtained_direction.json()))
        self.movement_param["direction"]= obtained_direction.json()["direction"]
        self.movement_param["step_lenght"] = obtained_direction.json()["step_lenght"]
        msg = Msg_team_marker(self.client_id, obtained_direction.json()["color"], obtained_direction.json()["direction"])
        r = requests.post("http://127.0.0.1:5000/data/add/" + msg.get_json_from_dict())
        print("data team marker sended to server: " + str(r.status_code), r.reason)
        #r = requests.post("http://127.0.0.1:5000/data/add/{name:" + self.client_id + ",msg_type: new_direction, device_type:"+obtained_direction.json()["color"]+"gps:{lat:" + self.movement_param["direction"][0] + ", long:" + self.movement_param["direction"][1]+"}},")
        time.sleep(5)
        

    def read_coordinates(self):
        norm_direction = np.linalg.norm(self.movement_param["direction"])
        
        if norm_direction != 0:
            self.current_cord.lat += self.movement_param["step_lenght"] * self.movement_param["direction"][0] / norm_direction
            self.current_cord.long += self.movement_param["step_lenght"] * self.movement_param["direction"][1] / norm_direction
            print("now coordinates: " + str(self.current_cord.get_dict()))
        return self.current_cord
        
  