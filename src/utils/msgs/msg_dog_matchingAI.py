import json
from utils.data_structures.data_coordinates import Data_coordinates
import time

class Msg_dog_matchingAI(object):
    
    def __init__(self, name, start_cord, img, imgname, ack):
        #create data structure
        if type(start_cord) != Data_coordinates:
            raise Exception("Coordinates must be exepressed in Data_coordinates")
        self.name = name
        self.msg_type = "ai_matching"
        self.device_type = "dog"
        self.gps_cord = start_cord.get_dict()
        self.timestamp = time.time()  
        self.img = img
        self.imgname = imgname
        self.ack = ack      #capire se mandare un immagine invece che un ack  
        self.data = {"name" : name, 
                     "msg_type" : self.msg_type, 
                     "device_type" : self.device_type ,
                     "gps" : self.gps_cord, 
                     "timestamp" : self.timestamp,
                     "img" : self.img,
                     "imgname" : self.imgname, 
                     "ack" : self.ack}

    def get_json_from_dict(self):        
        json_data = json.dumps(self.data)
        return json_data