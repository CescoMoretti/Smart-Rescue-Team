import json

class Msg_broker_telemetry(object):
    
    def __init__(self, start_cord, start_time, start_battery):
        #create data structure
        self.gps_cord = start_cord
        self.timestamp = start_time
        self.battery = start_battery
        self.data = {"gps" : start_cord, "timestamp" : start_time, "battery" : start_battery  }
    
    def get_json_from_var(self):
        self.data = {"gps" : self.gps_cord, "timestamp" : self.timestamp, "battery" : self.battery }
        json_data = json.dumps(self.data)

    def get_json_from_dict(self):        
        json_data = json.dumps(self.data)
