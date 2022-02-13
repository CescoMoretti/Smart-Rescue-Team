import binascii, json

with open("C:/Users/Tobi/Documents/uni/progetto_iot/Smart-Rescue-Team/src/dog/camera_stream_simulator.jpg", "rb") as image_file:
    data = binascii.b2a_base64(image_file.read()).decode()
resp = {}
resp['image'] = data
print(json.dumps(resp))

#converting back to image using binascii.a2b_base64
with open("sample.jpg", "wb") as f2:
    f2.write(binascii.a2b_base64(data))