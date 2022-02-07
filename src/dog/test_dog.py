from dog_obj import Dog
import random, cv2


def main():
    broker = 'localhost'
    port = 1883
    client_id = f'dog-{random.randint(0, 1000)}'
    #user = 'emqx'
    #psw = 'public'

    cane1 = Dog(broker, port, client_id)
    imgpath = 'imgs/IMG_6047.JPG'
    img =  cv2.imread('imgs/IMG_6047.JPG')
    cane1.send_data(img)

if __name__ == "__main__":
    main()