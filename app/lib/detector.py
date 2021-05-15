import json
import os
from imageai.Detection import ObjectDetection
from mtcnn.mtcnn import MTCNN
from matplotlib import pyplot
from PIL import Image, ImageDraw

DEBUG = os.getenv('DEBUG')


def draw_image_with_boxes(photoFilename, faces):
    with Image.open(photoFilename) as image:
        # Draw OSD
        draw = ImageDraw.Draw(image, "RGBA")

        for face in faces:
            x, y, w, h = face["box"]
            draw.rectangle([x, y, x + w, y + h], outline="red", width=2)

        image.save(photoFilename, "JPEG")


def detectPhoto(CWD, PHOTOPATH, PHOTOOUTPUTPATH, JSONOUTPUTPATH):
    objectDetection = ObjectDetection()
    faceDetection = MTCNN()

    objectDetection.setModelTypeAsRetinaNet()
    objectDetection.setModelPath(os.path.join(
        CWD, "model", "resnet50_coco_best_v2.1.0.h5"))
    objectDetection.loadModel()

    for filename in os.listdir(PHOTOPATH):
        photoFilename = os.path.join(PHOTOPATH, filename)
        photoOutputFilename = os.path.join(PHOTOOUTPUTPATH, filename)
        jsonOutputFilename = os.path.join(JSONOUTPUTPATH, filename + ".json")

        if DEBUG == 'Y':
            print(photoFilename)
        if (not os.path.exists(photoOutputFilename)) or (not os.path.exists(jsonOutputFilename)):
            detections = objectDetection.detectObjectsFromImage(
                input_image=photoFilename,
                output_image_path=photoOutputFilename
            )

            pixels = pyplot.imread(photoFilename)
            faces = faceDetection.detect_faces(pixels)
            for face in faces:
                x, y, w, h = face["box"]
                detections.append({"name": "face", "percentage_probability": (
                    face["confidence"] * 100), "box_points": [x, y, x + w, y + h]})

            draw_image_with_boxes(photoOutputFilename, faces)

            if DEBUG == 'Y':
                print(photoOutputFilename)
            with open(jsonOutputFilename, 'w') as outfile:
                json.dump(detections, outfile)
            if DEBUG == 'Y':
                print(jsonOutputFilename)
