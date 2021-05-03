#https://towardsdatascience.com/object-detection-with-10-lines-of-code-d6cb4d86f606
#https://github.com/OlafenwaMoses/ImageAI

# build command
#docker build -t moononournation/imageai:2.1.6 .

#building Multi-Arch Images commands
#docker buildx ls
#docker buildx create --use
#docker buildx build --platform linux/amd64,linux/arm -t moononournation/imageai:2.1.6 .
#docker buildx build --platform linux/amd64,linux/arm -t moononournation/imageai:2.1.6 --push .

FROM tensorflow/tensorflow

EXPOSE 5000

WORKDIR /app

#install imageai
RUN apt-get update && apt-get install -y --no-install-recommends libgl1-mesa-glx
RUN /usr/bin/python3 -m pip install --upgrade pip
RUN pip install keras==2.4.3 numpy==1.19.3 pillow==7.0.0 scipy==1.4.1 h5py==2.10.0 matplotlib==3.3.2 opencv-python keras-resnet==0.2.0 imageai==2.1.6

#install HTTP server related
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get install -yq --no-install-recommends tzdata
RUN pip install flask paho-mqtt

CMD [ "python", "app.py" ]
