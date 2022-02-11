import numpy as np
import matplotlib.pyplot as plt
import cv2


class Detector():
    def __init__(self, weights_path, cfg_path, l_names):
        self.weights_path = weights_path
        self.cfg_path = cfg_path
        self.l_names = l_names
        self.yolo_net = cv2.dnn.readNet(self.weights_path, self.cfg_path)
        with open(self.l_names, 'r') as f:
            self.classes = f.read().splitlines()
        self.progressiveId = 0


    def detectMissingPeople(self, imgpath):

        self.progressiveId += 1
        detected = False
        img =  cv2.imread(imgpath)
        blob = cv2.dnn.blobFromImage(img, 1/255, (320,320), (0,0,0), swapRB=True, crop=False)

        print(blob.shape)

        self.yolo_net.setInput(blob)
        output_layers_name = self.yolo_net.getUnconnectedOutLayersNames()
        output_layer = self.yolo_net.forward(output_layers_name)

        bounding = []
        confidences = []
        class_ids = []

        print(output_layer)

        for output in output_layer:
            for detection in output:
                score = detection[5:]
                class_id = np.argmax(score)
                confidence = score[class_id]
                width = img.shape[1]
                height = img.shape[0]
                if confidence > 0.7 and class_id == 0:
                    center_x = int(detection[0]*width)
                    center_y = int(detection[0]*height)
                    w = int(detection[0]*width)
                    h = int(detection[0]*height)

                    x = int(center_x - w/2)
                    y = int(center_y - h/2)

                    bounding.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(bounding, confidences, 0.5, 0.4)

        font = cv2.FONT_HERSHEY_COMPLEX
        colors = np.random.uniform(0, 255, size=(len(bounding), 3))

        if len(indexes) > 0:
            detected = not detected
            for i in indexes.flatten():
                x, y, w, h = bounding[i]
                label = str(self.classes[class_ids[i]])
                confid = str(round(confidences[i], 2))
                color = colors[i]

                cv2.rectangle(img, (x, y), (x+w, y+h), color, 3)
                cv2.putText(img, label + ' ' + confid, (x, y+20), font, 2, (255, 255, 255), 3)

        cv2.imwrite('Smart-Rescue-Team/src/dog/predicted_imgs/' + str(self.progressiveId) + '.jpg', img)
        return self.progressiveId, 'Smart-Rescue-Team/src/dog/predicted_imgs/' + str(self.progressiveId) + '.jpg', detected