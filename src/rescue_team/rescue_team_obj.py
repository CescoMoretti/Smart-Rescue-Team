import binascii
from doctest import DONT_ACCEPT_BLANKLINE
from pathlib import Path
import sys
path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
sys.path.insert(0, path)
from utils.msgs.msg_team_telemetry import Msg_team_telemetry
from utils.msgs.msg_dog_matchingAI import Msg_dog_matchingAI
from utils.models.subscriber_mqtt import Subscriber_mqtt
from utils.models.thread_model import Thread_model
from utils.data_structures.data_coordinates import Data_coordinates
import time
import requests
import json, os

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
        


    def start(self):
        tele_thread = Thread_model('telemetry', self.send_data_telemetry)
        tele_thread.start()
        self.subscriber_tel.connect()
        self.subscriber_ai.connect()
        try:
            while True:
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("exiting")
            tele_thread.join()
            self.subscriber_tel.disconnect()
            self.subscriber_ai.disconnect()
            

    
    def send_data_telemetry(self): 
        msg = Msg_team_telemetry(self.client_id, self.read_coordinates())             
        #r = requests.post("http://127.0.0.1:5000/data/add/"+ msg.get_json_from_dict())
        #print("data team position sended to server: " + str(r.status_code), r.reason)
        time.sleep(2)


    def callback_dog_tel(self, data):        
        r = requests.post("http://127.0.0.1:5000/data/add/"+ data)
        print("data receved sended to server: " + str(r.status_code), r.reason)

    def callback_dog_ai(self, data):
        #r = requests.post("http://127.0.0.1:5000/data/add/"+ data)
        #print("data receved sended to server: " + str(r.status_code), r.reason)
        data_json = json.loads(data)
        #msg = Msg_dog_matchingAI(data_json["name"],
                                #data_json["gps"],
                                #data_json["img"],
                                #data_json["imgname"],
                                #data_json["ack"])
        
        if data_json['ack'] == True:
            self.progressive_imgId += 1
            with open(this_path+'/src/rescue_team/received_positive_imgs/'+str(self.progressive_imgId)+'.jpg', 'wb') as fw:
                fw.write(binascii.a2b_base64(data_json['img']))

            print('Detected People by dog '+str(data_json['name'])+'!\nAt time '+str(data_json['timestamp']))
            


    def read_coordinates(self):
        #TODO
        telemetry = Data_coordinates(90,30)
        return telemetry
  