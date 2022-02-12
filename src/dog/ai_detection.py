from charset_normalizer import detect
import numpy as np
import matplotlib.pyplot as plt
import cv2, os


class Detector():

    def __init__(self, weights_path, cfg_path, l_names_path):
        self.this_path = os.getcwd()
        self.weights_path = weights_path
        self.cfg_path = cfg_path
        self.l_names_path = l_names_path
        self.yolo_net = cv2.dnn.readNetFromDarknet(cfg_path, weights_path)
        self.layerNames = self.yolo_net.getLayerNames()
        self.layerNames = [self.layerNames[i - 1] for i in self.yolo_net.getUnconnectedOutLayers()]

        with open(self.l_names_path, 'r') as f:
            self.classes = f.read().splitlines()
        self.progressiveId = 0


    def detectMissingPeople(self, imgpath):
        self.progressiveId += 1
        detected = False
        COLORS = np.random.randint(0, 255, size=(len(self.classes), 3), dtype="uint8")
        frame =  cv2.imread(imgpath)

        (H, W) = frame.shape[:2]

        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        self.yolo_net.setInput(blob)

        layerOutputs = self.yolo_net.forward(self.layerNames)

        bounding_boxes = []
        confidences = []
        class_ids = []

        for output in layerOutputs:
            for detection in output:
                score = detection[5:]
                class_id = np.argmax(score)
                confidence = score[class_id]

                if confidence > 0.65 and class_id == 0:
                    box = detection[0:4] * np.array([W, H, W, H])
                    (centerX, centerY, width, height) = box.astype("int")

                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))

                    bounding_boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(bounding_boxes, confidences, 0.65, 0.4)

        if len(indexes) > 0:
            detected = not detected
            # loop over the indexes we are keeping
            for i in indexes.flatten():
                # extract the bounding box coordinates
                (x, y) = (int(bounding_boxes[i][0]), int(bounding_boxes[i][1]))
                (w, h) = (int(bounding_boxes[i][2]), int(bounding_boxes[i][3]))

                # draw a bounding box rectangle and label on the image
                color = [int(c) for c in COLORS[class_ids[i]]]
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                text = "{}: {:.4f}".format(self.classes[class_ids[i]], confidences[i])
                cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

        cv2.imwrite(self.this_path+'/src/dog/predicted_imgs/' + str(self.progressiveId) + '.jpg', frame)
        return self.progressiveId, self.this_path+'/src/dog/predicted_imgs/' + str(self.progressiveId) + '.jpg', detected
