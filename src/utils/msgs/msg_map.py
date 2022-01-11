import json

class Msg_map(object):
    
    def __init__(self, start_cord, start_time, map):
        #create data structure
        self.map = map
        self.timestamp = start_time
        
        self.data = {"map" : map, "timestamp" : start_time }
    
    def get_json_from_var(self):
        self.data = {"map" : self.map, "timestamp" : self.timestamp }
        json_data = json.dumps(self.data)

    def get_json_from_dict(self):        
        json_data = json.dumps(self.data)