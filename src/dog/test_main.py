from dog_obj import Dog
import random


if __name__ == '__main__':
    broker = 'test.mosquitto.org'
    port = 1883
    client_id = f'dog-{random.randint(0, 1000)}'
    #user = 'emqx'
    #psw = 'public'

    cane1 = Dog(broker, port, client_id)
    cane1.fun_prova()