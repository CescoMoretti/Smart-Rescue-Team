import threading
import time 

#modello dei thread usati per gestire le comunicazioni

class Thread_model (threading.Thread):
    die = False
    def __init__(self, name, job):
        threading.Thread.__init__(self, daemon=True)
        self.name = name
        self.job = job

    def run (self):
        while not self.die:            
            self.job()

    def join(self):
        self.die = True
        super().join()