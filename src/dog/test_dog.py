from dog_obj import Dog
import random
import threading
from utils.models.thread_main import Thread_main

def main():
    broker = 'localhost'
    port = 1883
    client_id = f'dog-{random.randint(0, 1000)}'
    #user = 'emqx'
    #psw = 'public'
    
    cane1 = Dog(broker, port, client_id)
    cane1.activate_dog()

if __name__ == "__main__":
    main()