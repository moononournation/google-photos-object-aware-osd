import os
import requests

DEBUG = os.getenv('DEBUG')
GOOGLEPHOTOURL = os.getenv('GOOGLEPHOTO')
GOOGLEPHOTOURLPREFIX = "https://lh3.googleusercontent.com/"
GOOGLEPHOTOSEEKPATTERN = "id=\"_ij\""
GOOGLEPHOTOSEARCHPATTERN = "\",[\"" + GOOGLEPHOTOURLPREFIX

def updatePhoto(PHOTOPATH):
    r = requests.get(GOOGLEPHOTOURL, allow_redirects=True)
    seekPatternFound = False

    for iterLine in r.iter_lines():
        if iterLine:
            line = iterLine.decode('utf-8')
            if not seekPatternFound:
                pos = line.find(GOOGLEPHOTOSEEKPATTERN)
                if pos > 0: seekPatternFound = True
            else:
                GOOGLEPHOTOSEARCHPATTERN
                pos1 = line.find(GOOGLEPHOTOSEARCHPATTERN)
                if pos1 > 0:
                    pos1 += len(GOOGLEPHOTOSEARCHPATTERN)
                    pos2 = line.find("\"", pos1)
                    if pos2 > 0:
                        photoId = line[pos1:pos2]
                        photoFilename = os.path.join(PHOTOPATH, "p" + photoId[1:20] + ".jpg")
                        if DEBUG == 'Y':
                            print(photoFilename)
                        if not os.path.exists(photoFilename):
                            photoUrl = GOOGLEPHOTOURLPREFIX + photoId + "=w1920"
                            photoRequest = requests.get(photoUrl, allow_redirects=True)
                            open(photoFilename, 'wb').write(photoRequest.content)
                            photoRequest.close()
