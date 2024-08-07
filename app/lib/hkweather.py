import os
import requests
from datetime import datetime

RSSURL = "http://rss.weather.gov.hk/rss/CurrentWeather.xml"
IMAGESEARCHPATTERN = "<img src=\""
TEMPERATURESEARCHPATTERN = "Air temperature : "
HUMIDITYSEARCHPATTERN = "Relative Humidity : "
THUNDERSTORMSEARCHPATTERN = "The Thunderstorm Warning has been issued."

lastUpdate = datetime(1970, 1, 1)
imageUrl = None
weatherIcon = None
temperature = None
humidity = None
warning = None

def updateWeather(WEATHERICONPATH):
    global lastUpdate, imageUrl, temperature, humidity, weatherIcon
    now = datetime.now()

    if (not lastUpdate) or ((now - lastUpdate).seconds > (59 * 60)):
        imageUrl = None
        weatherIcon = None
        temperature = None
        humidity = None
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
                        print("imageUrl: ",imageUrl)
                if not temperature:
                    startPos = line.find(TEMPERATURESEARCHPATTERN)
                    # print(startPos)
                    if startPos > 0:
                        startPos += len(TEMPERATURESEARCHPATTERN)
                        endPos = line.find(" ", startPos)
                        temperature = int(line[startPos:endPos])
                        print("temperature: ", temperature)
                if not humidity:
                    startPos = line.find(HUMIDITYSEARCHPATTERN)
                    # print(startPos)
                    if startPos > 0:
                        startPos += len(HUMIDITYSEARCHPATTERN)
                        endPos = line.find(" ", startPos)
                        humidity = int(line[startPos:endPos])
                        print("humidity: ", humidity)
                if not warning:
                    startPos = line.find(THUNDERSTORMSEARCHPATTERN)
                    # print(startPos)
                    if startPos > 0:
                        imageUrl = "https://rss.weather.gov.hk/img/ts.gif"
                        print(THUNDERSTORMSEARCHPATTERN)
        if imageUrl:
            startPos = imageUrl.rfind("/") + 1
            weatherIcon = imageUrl[startPos:]
            weatherIconFilename = os.path.join(WEATHERICONPATH, weatherIcon)
            if not os.path.exists(weatherIconFilename):
                r = requests.get(imageUrl, allow_redirects=True)
                open(weatherIconFilename, 'wb').write(r.content)

        lastUpdate = now

    return weatherIcon, temperature, humidity
