# google-photos-object-aware-osd

Google Photos photo frame with ImageAI object aware OSD

## Get started

### Download trained models

You can download latest trained models at ImageAI release page:
https://github.com/OlafenwaMoses/ImageAI/releases/tag/1.0

And copy the download model, e.g. resnet50_coco_best_v2.1.0.h5, to app/model folder.

### Run docker
Replace with your own shared Google Photos album and Timezone:
```
docker run -it -p 5000:5000 -v `pwd`/app:/app -eDEBUG=Y -eGOOGLEPHOTO=https://photos.app.goo.gl/j9kVKWsfWq9N1jD88 -e TZ=Asia/Hong_Kong moononournation/imageai:2.1.6
```

### Run docker with MQTT indoor monitor
Replace with your own shared Google Photos album, timezone and MQTT broker:
```
docker run -it -p 5000:5000 -v `pwd`/app:/app -eDEBUG=Y -eGOOGLEPHOTO=https://photos.app.goo.gl/j9kVKWsfWq9N1jD88 -eMQTTBROKER=192.168.1.176 -eMQTTTOPIC=MSC/1F/8005 -e TZ=Asia/Hong_Kong moononournation/imageai:2.1.6
```