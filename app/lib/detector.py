import json
import os
from imageai.Detection import ObjectDetection

DEBUG = os.getenv('DEBUG')

def detectPhoto(CWD, PHOTOPATH, PHOTOOUTPUTPATH, JSONOUTPUTPATH):
    detector = ObjectDetection()
    detector.setModelTypeAsRetinaNet()
    detector.setModelPath(os.path.join(CWD, "model", "resnet50_coco_best_v2.1.0.h5"))
    detector.loadModel()

    for filename in os.listdir(PHOTOPATH):
        photoFilename = os.path.join(PHOTOPATH, filename)
        photoOutputFilename = os.path.join(PHOTOOUTPUTPATH, filename)
        jsonOutputFilename = os.path.join(JSONOUTPUTPATH, filename + ".json")
        if DEBUG == 'Y':
            print(photoFilename)
        if (not os.path.exists(photoOutputFilename)) or (not os.path.exists(jsonOutputFilename)):
            detections = detector.detectObjectsFromImage(
                input_image = photoFilename,
                output_image_path = photoOutputFilename
            )
            if DEBUG == 'Y':
                print(photoOutputFilename)
            with open(jsonOutputFilename, 'w') as outfile:
                json.dump(detections, outfile)
            if DEBUG == 'Y':
                print(jsonOutputFilename)
