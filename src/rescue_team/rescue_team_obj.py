from utils.models.pubblisher_mqtt import Publisher_mqtt
class Rescue_team_obj:
    def __init__(self, broker, port,  client_id):
        self.broker = broker
        self.port = port
        self.client_id = client_id        
        self.topic_tel = f'{client_id}/telemetry'
        self.publisher_tel = Publisher_mqtt( broker, port, self.topic_tel, f'{self.client_id}_publisher_tel')     

    def start(self):
        pass 
    
    def publish_tel():
        pass