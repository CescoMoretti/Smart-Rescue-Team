import json
from utils.data_structures.data_coordinates import Data_coordinates
import time

class Msg_dog_matchingAI(object):
    
    def __init__(self, start_cord, ack):
        #create data structure
        if type(start_cord) != Data_coordinates:
            raise Exception("Coordinates must be exepressed in Data_coordinates")
        self.gps_cord = start_cord.get_dict()
        self.timestamp = time.time()  
        self.ack = ack      #capire se mandare un immagine invece che un ack  
        self.data = {"gps" : self.gps_cord, "timestamp" : self.timestamp, "ack" : self.ack  }
    
    def get_json_from_var(self):
        self.data = {"gps" : self.gps_cord, "timestamp" : self.timestamp, "ack" : self.ack }
        json_data = json.dumps(self.data)
        return json_data

    def get_json_from_dict(self):        
        json_data = json.dumps(self.data)
        return json_data