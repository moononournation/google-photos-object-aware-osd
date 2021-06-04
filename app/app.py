from flask import Flask, request, make_response
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps
from datetime import datetime
import os
from lib import googlePhoto
from lib import detector
from lib import hkweather as weather
from lib import indoor
from lib import photoUtils

DEBUG = os.getenv('DEBUG')
GOOGLEPHOTOURL = os.getenv('GOOGLEPHOTO')
MQTTBROKER = os.getenv('MQTTBROKER')
CWD = os.getcwd()
CACHEFILEPATH = os.path.join(CWD, "cacheFile")
if (not os.path.exists(CACHEFILEPATH)):
    os.mkdir(CACHEFILEPATH)
PHOTOPATH = os.path.join(CACHEFILEPATH, "photo")
if (not os.path.exists(PHOTOPATH)):
    os.mkdir(PHOTOPATH)
DETECTEDPHOTOPATH = os.path.join(CACHEFILEPATH, "detectedPhoto")
if (not os.path.exists(DETECTEDPHOTOPATH)):
    os.mkdir(DETECTEDPHOTOPATH)
DETECTEDJSONPATH = os.path.join(CACHEFILEPATH, "detectedJson")
if (not os.path.exists(DETECTEDJSONPATH)):
    os.mkdir(DETECTEDJSONPATH)
WEATHERICONPATH = os.path.join(CACHEFILEPATH, "weatherIcon")
if (not os.path.exists(WEATHERICONPATH)):
    os.mkdir(WEATHERICONPATH)

if GOOGLEPHOTOURL and (GOOGLEPHOTOURL > ""):
    googlePhoto.updatePhoto(PHOTOPATH)

detector.detectPhoto(CWD, PHOTOPATH, DETECTEDPHOTOPATH, DETECTEDJSONPATH)

photoUtils.updatePhotoList(PHOTOPATH, DETECTEDJSONPATH)

# Initialize the Flask application
app = Flask(__name__)

# route http request to this method


@app.route("/", methods=["GET"])
def getIndexPage():
    return """
<html>
<head>
<style type="text/css">body{margin:0;}</style>
<script>
function p(){q=window.location.search;document.getElementById("photo").src="/OSDPhoto"+((q>"")?q+"&":"?")+"w="+window.innerWidth+"&h="+window.innerHeight+"&t="+Date.now();}
window.onload=function(){p();window.setTimeout(function(){p();setInterval(p,60000);},60000-(Date.now()%60000));};
</script>
</head>
<body><img id="photo"><body>
</html>
"""


@app.route("/OSDPhoto", methods=["GET"])
def getOSDPhoto():
    width = request.values.get("w")
    if width is None:
        width = 320
    else:
        width = int(width)
    height = request.values.get("h")
    if height is None:
        height = 240
    else:
        height = int(height)
    osdRatio = request.values.get("o")
    if osdRatio is None:
        osdRatio = 0.5
    else:
        osdRatio = float(osdRatio)

    filename, scale, crop_rect, image = photoUtils.getRandomPhoto(
        width, height, PHOTOPATH, DETECTEDPHOTOPATH, DETECTEDJSONPATH)

    osd_rect, osdSize = photoUtils.getDimension(
        filename, width, height, scale, crop_rect, osdRatio)

    colorEnhance = request.values.get("colorEnhance")
    if colorEnhance:
        converter = ImageEnhance.Color(image)
        image = converter.enhance(float(colorEnhance))

    if DEBUG == 'Y':
        print("crop_rect:", crop_rect, "osd_rect:", osd_rect,
              "osdSize:", osdSize)
    image = image.crop(crop_rect)
    image = image.resize((width, height))

    # Draw OSD
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle(osd_rect, fill=(0, 0, 0, 127))
    fontpath = os.path.join(CWD, "font", "FreeSansBold.ttf")
    now = datetime.now()

    # Draw time
    timeString = now.strftime("%H:%M")
    osdFont = ImageFont.truetype(fontpath, int(osdSize * 0.37))
    draw.text((osd_rect[0] + (osdSize * 0.04), osd_rect[1] +
               (osdSize * 0.02)), timeString, font=osdFont, fill=(255, 255, 255))

    # Draw date
    dateString = now.strftime("%b %d, %a")
    osdFont = ImageFont.truetype(fontpath, int(osdSize * 0.16))
    draw.text((osd_rect[0] + (osdSize * 0.04), osd_rect[1] + (osdSize * 0.40)),
              dateString, font=osdFont, fill=(255, 255, 255))

    # Update weather
    weatherIcon, temperature, humidity = weather.updateWeather(WEATHERICONPATH)
    if DEBUG == 'Y':
        print("weather:", weatherIcon, temperature, humidity)

    # Draw weather icon
    weatherIconFilename = os.path.join(WEATHERICONPATH, weatherIcon)
    icon = Image.open(weatherIconFilename, 'r')
    icon = icon.resize((int(osdSize * 0.36), int(osdSize * 0.36)))
    iconPos = (int(osd_rect[0] + (osdSize * 0.03)),
               int(osd_rect[1] + (osdSize * 0.62)))
    image.paste(icon, iconPos)

    # Draw indoor
    indoorData = indoor.getIndoorData()
    if indoorData:
        # Draw weather
        weatherString = str(temperature) + "°C " + str(humidity) + "%"
        osdFont = ImageFont.truetype(fontpath, int(osdSize * 0.12))
        draw.text((osd_rect[0] + (osdSize * 0.41), osd_rect[1] + (osdSize * 0.62)),
                  weatherString, font=osdFont, fill=(255, 255, 255))

        indoorTemperature = int(indoorData["temperature"])
        indoorHumidity = int(indoorData["humidity"])
        if DEBUG == 'Y':
            print("indoorData:", indoorTemperature, ",", indoorHumidity)
        indoorString = str(indoorTemperature) + "°C " + \
            str(indoorHumidity) + "%"
        draw.text((osd_rect[0] + (osdSize * 0.41), osd_rect[1] + (osdSize * 0.84)),
                  indoorString, font=osdFont, fill=(195, 195, 195))
        osdFont = ImageFont.truetype(fontpath, int(osdSize * 0.08))
        draw.text((osd_rect[0] + (osdSize * 0.41), osd_rect[1] + (osdSize * 0.77)),
                  "Indoor:", font=osdFont, fill=(195, 195, 195))
    else:
        # Draw weather
        temperatureString = str(temperature) + "°C"
        osdFont = ImageFont.truetype(fontpath, int(osdSize * 0.19))
        draw.text((osd_rect[0] + (osdSize * 0.42), osd_rect[1] + (osdSize * 0.61)),
                  temperatureString, font=osdFont, fill=(255, 255, 255))
        humidityString = str(humidity) + "%"
        osdFont = ImageFont.truetype(fontpath, int(osdSize * 0.19))
        draw.text((osd_rect[0] + (osdSize * 0.42), osd_rect[1] + (osdSize * 0.79)),
                  humidityString, font=osdFont, fill=(255, 255, 255))

    flip = request.values.get("flip")
    if flip == 'Y':
        image = ImageOps.flip(image)

    mirror = request.values.get("mirror")
    if mirror == 'Y':
        image = ImageOps.mirror(image)

    # return jpeg image
    response = make_response(image.tobytes("jpeg", "RGB"))
    response.headers["Content-Type"] = "image/jpeg"
    return response


# start flask app
app.run(host="0.0.0.0", port=5000)
