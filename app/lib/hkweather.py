import os
import requests
from datetime import datetime

RSSURL = "http://rss.weather.gov.hk/rss/CurrentWeather.xml"
IMAGESEARCHPATTERN = "<img src=\""
TEMPERATURESEARCHPATTERN = "Air temperature : "
HUMIDITYSEARCHPATTERN = "Relative Humidity : "

lastUpdate = datetime(1970, 1, 1)
imageUrl = None
weatherIcon = None
temperature = None
humidity = None

def updateWeather(WEATHERICONPATH):
    global lastUpdate, imageUrl, temperature, humidity, weatherIcon
    now = datetime.now()

    if (not lastUpdate) or ((lastUpdate - now).seconds > (30 * 60)):
        r = requests.get(RSSURL, allow_redirects=True)

        for iterLine in r.iter_lines():
            if iterLine:
                line = iterLine.decode('utf-8')
                # print(line)
                if not imageUrl:
                    startPos = line.find(IMAGESEARCHPATTERN)
                    # print(startPos)
                    if startPos > 0:
                        startPos += len(IMAGESEARCHPATTERN)
                        endPos = line.find("\"", startPos)
                        imageUrl = line[startPos:endPos]
                if not temperature:
                    startPos = line.find(TEMPERATURESEARCHPATTERN)
                    # print(startPos)
                    if startPos > 0:
                        startPos += len(TEMPERATURESEARCHPATTERN)
                        endPos = line.find(" ", startPos)
                        temperature = int(line[startPos:endPos])
                if not humidity:
                    startPos = line.find(HUMIDITYSEARCHPATTERN)
                    # print(startPos)
                    if startPos > 0:
                        startPos += len(HUMIDITYSEARCHPATTERN)
                        endPos = line.find(" ", startPos)
                        humidity = int(line[startPos:endPos])

        if imageUrl:
            startPos = imageUrl.rfind("/") + 1
            weatherIcon = imageUrl[startPos:]
            weatherIconFilename = os.path.join(WEATHERICONPATH, weatherIcon)
            if not os.path.exists(weatherIconFilename):
                r = requests.get(imageUrl, allow_redirects=True)
                open(weatherIconFilename, 'wb').write(r.content)

        lastUpdate = now

    return weatherIcon, temperature, humidity
