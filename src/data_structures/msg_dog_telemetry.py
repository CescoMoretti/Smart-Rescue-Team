import json
import time
from data_structures.data_coordinates import Data_coordinates

class Msg_dog_telemetry(object):
    
    def __init__(self, start_cord, start_battery):
        #create data structure
        if type(start_cord) != Data_coordinates:
            raise Exception("Coordinates must be exepressed in Data_coordinates")
        self.gps_cord = start_cord.get_dict()
        self.timestamp = time.time()
        self.battery = start_battery
        self.data = {"gps" : self.gps_cord, "timestamp" : self.timestamp, "battery" : start_battery  }
    
    def get_json_from_var(self):
        self.data = {"gps" : self.gps_cord, "timestamp" : self.timestamp, "battery" : self.battery }
        json_data = json.dumps(self.data)
        return json_data

    def get_json_from_dict(self):        
        json_data = json.dumps(self.data)
        return json_data

    
