class Data_coordinates:
    def __init__(self, lat, long):
        self.lat = lat
        self.long = long
    
    def get_dict(self):
        dict = { "lat" : self.lat, "long" : self.long}
        return dict
