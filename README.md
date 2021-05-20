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

### Jetson Nano 2G
#### Preparation
```
sudo apt-get update
sudo apt-get install -y --no-install-recommends libhdf5-serial-dev hdf5-tools libhdf5-dev zlib1g-dev zip libjpeg8-dev liblapack-dev libblas-dev gfortran libgl1-mesa-glx libglib2.0-0 python3-pip

python3 -m pip install -U pip
pip install -U testresources setuptools==49.6.0 numpy==1.19.4 future==0.18.2 mock==3.0.5 h5py==2.10.0 keras_preprocessing==1.1.1 keras_applications==1.0.8 gast==0.2.2 futures protobuf pybind11

pip install --pre --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v45 tensorflow

pip install mtcnn==0.1.0 keras==2.4.3 pillow==7.0.0 scipy==1.4.1 matplotlib==3.3.2 opencv-python keras-resnet==0.2.0 imageai==2.1.6
pip install flask paho-mqtt
```
#### Run
```
git clone https://github.com/moononournation/google-photos-object-aware-osd.git
cd google-photos-object-aware-osd/app
python3 app.py
```
