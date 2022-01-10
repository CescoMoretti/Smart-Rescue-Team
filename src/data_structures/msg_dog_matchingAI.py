import json
from data_coordinates import Data_coordinates
class Msg_dog_matchingAI(object):
    
    def __init__(self, start_cord, start_time):
        #create data structure
        self.gps_cord = start_cord
        self.timestamp = start_time  
        self.ack = "ack"    #capire se mandare un immagine invece che un ack  
        self.data = {"gps" : start_cord, "timestamp" : start_time, "ack" : "ack"  }
    
    def get_json_from_var(self):
        self.data = {"gps" : self.gps_cord, "timestamp" : self.timestamp, "ack" : self.ack }
        json_data = json.dumps(self.data)

    def get_json_from_dict(self):        
        json_data = json.dumps(self.data)