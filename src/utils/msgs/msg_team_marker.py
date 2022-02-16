import json
from os import device_encoding
import time
from utils.data_structures.data_coordinates import Data_coordinates
from utils.msgs.msg_abstact import Message_SRT


class Msg_team_marker(Message_SRT):

    def __init__(self, name, color, destination_cord):
        # create data structure
        if type(destination_cord) != Data_coordinates:
            raise Exception("Coordinates must be exepressed in Data_coordinates")
        self.name = name
        self.msg_type = "direction_marker"
        self.device_type = color
        self.gps_cord = destination_cord.get_dict()
        self.timestamp = time.time()
        self.data = {"name": name,
                     "msg_type": self.msg_type,
                     "device_type": self.device_type,
                     "gps": self.gps_cord,
                     "timestamp": self.timestamp}

    def get_json_from_var(self):
        json_data = json.dumps(self.data)
        return json_data

    def get_json_from_dict(self):
        json_data = json.dumps(self.data)
        return json_data
