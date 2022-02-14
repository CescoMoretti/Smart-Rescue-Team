from abc import ABC, abstractmethod

class Message_SRT(ABC):
 
    @abstractmethod
    def get_json_from_dict(self):
        pass
 