import json
import os
import random

DEBUG = os.getenv('DEBUG')
photoList = []
random.seed()


def updatePhotoList(PHOTOPATH, DETECTEDJSONPATH):
    global photoPath, jsonOutputPath, photoList
    photoPath = PHOTOPATH
    jsonOutputPath = DETECTEDJSONPATH
    photoList.clear()
    for filename in os.listdir(photoPath):
        jsonFilename = os.path.join(jsonOutputPath, filename + ".json")
        if filename.endswith(".jpg") and os.path.exists(jsonFilename):
            photoList.append(filename)
        else:
            continue


def getRandomPhoto():
    randomIdx = random.randint(0, len(photoList) - 1)
    return photoList[randomIdx]


def getDimension(filename, image, width, height, OSDRATIO):
    iW = image.width
    iH = image.height
    wScale = width / iW
    hScale = height / iH
    scale = 0
    cW = 0
    cH = 0
    if wScale < hScale:
        scale = hScale
        cW = width / scale
        cH = iH
        cropA = (0, 0, cW - 1, cH - 1)
        cropB = ((iW - cW) / 2, 0, ((iW + cW) / 2) - 1, cH - 1)
        cropC = (iW - cW, 0, iW - 1, cH - 1)
    else:
        scale = wScale
        cW = iW
        cH = height / scale
        cropA = (0, 0, cW - 1, cH - 1)
        cropB = (0, (iH - cH) / 2, cW - 1, ((iH + cH) / 2) - 1)
        cropC = (0, iH - cH, cW - 1, iH - 1)

    osdSize = min(width, height) * OSDRATIO
    margin = osdSize * 0.05

    osdNW = (margin, margin,
             margin + osdSize, margin + osdSize)
    osdNE = (width - margin - osdSize, margin,
             width - margin, margin + osdSize)
    osdCT = ((width - osdSize) / 2, (height - osdSize) / 2,
             (width + osdSize) / 2, (height + osdSize) / 2)
    osdSW = (margin, height - margin - osdSize,
             margin + osdSize, height - margin)
    osdSE = (width - margin - osdSize, height - margin - osdSize,
             width - margin, height - margin)

    jsonFilename = os.path.join(jsonOutputPath, filename + ".json")
    with open(jsonFilename) as jsonFile:
        items = json.load(jsonFile)

        # determine CROP area
        overlapA = 0
        overlapB = 0
        overlapC = 0

        osdSize = min(width, height) * OSDRATIO
        margin = osdSize * 0.05

        for item in items:
            iBp = item["box_points"]
            weight = item["percentage_probability"] * \
                ((iBp[2] - iBp[0] + 1) / width) * \
                ((iBp[3] - iBp[1] + 1) / height)
            if item["name"] == 'person':
                weight *= 10
            overlapA += overlap(iBp, cropA) * weight
            overlapB += overlap(iBp, cropB) * weight
            overlapC += overlap(iBp, cropC) * weight
            if DEBUG == 'Y':
                print(item["name"], "|", str(item["percentage_probability"]),
                      "|", iBp, "|", weight)

        # Crop select most details area
        max_overlap = max(overlapA, overlapB, overlapC)
        if DEBUG == 'Y':
            print("Crop overlap:", overlapA, "|", overlapB,
                  "|", overlapC, "|", max_overlap)

        # prefer centre if same value
        if overlapB == max_overlap:
            crop_rect = cropB
        elif overlapA == max_overlap:
            crop_rect = cropA
        elif overlapC == max_overlap:
            crop_rect = cropC

        # determine OSD position
        overlapNW = 0
        overlapNE = 0
        overlapCT = 0
        overlapSW = 0
        overlapSE = 0

        scaledOsdNW = ((osdNW[0] / scale) + crop_rect[0], (osdNW[1] / scale) + crop_rect[1],
                       (osdNW[2] / scale) + crop_rect[0], (osdNW[3] / scale) + crop_rect[1])
        scaledOsdNE = ((osdNE[0] / scale) + crop_rect[0], (osdNE[1] / scale) + crop_rect[1],
                       (osdNE[2] / scale) + crop_rect[0], (osdNE[3] / scale) + crop_rect[1])
        scaledOsdCT = ((osdCT[0] / scale) + crop_rect[0], (osdCT[1] / scale) + crop_rect[1],
                       (osdCT[2] / scale) + crop_rect[0], (osdCT[3] / scale) + crop_rect[1])
        scaledOsdSW = ((osdSW[0] / scale) + crop_rect[0], (osdSW[1] / scale) + crop_rect[1],
                       (osdSW[2] / scale) + crop_rect[0], (osdSW[3] / scale) + crop_rect[1])
        scaledOsdSE = ((osdSE[0] / scale) + crop_rect[0], (osdSE[1] / scale) + crop_rect[1],
                       (osdSE[2] / scale) + crop_rect[0], (osdSE[3] / scale) + crop_rect[1])
        for item in items:
            iBp = item["box_points"]
            weight = item["percentage_probability"] * \
                (iBp[2] - iBp[0] + 1) * \
                (iBp[3] - iBp[1] + 1) / width / height
            if item["name"] == 'person':
                weight *= 10
            overlapNW += overlap(iBp, scaledOsdNW) * weight
            overlapNE += overlap(iBp, scaledOsdNE) * weight
            overlapCT += overlap(iBp, scaledOsdCT) * weight
            overlapSW += overlap(iBp, scaledOsdSW) * weight
            overlapSE += overlap(iBp, scaledOsdSE) * weight

        # OSD select least cover details area
        min_overlap = min(overlapNW, overlapNE,
                          overlapCT, overlapSW, overlapSE)
        if DEBUG == 'Y':
            print("OSD overlap:", overlapNW, "|", overlapNE, "|", overlapCT,
                  "|", overlapSW, "|", overlapSE, "|", min_overlap)

        if overlapNW == min_overlap:
            osd_rect = osdNW
        elif overlapNE == min_overlap:
            osd_rect = osdNE
        elif overlapCT == min_overlap:
            osd_rect = osdCT
        elif overlapSW == min_overlap:
            osd_rect = osdSW
        elif overlapSE == min_overlap:
            osd_rect = osdSE

    return crop_rect, osd_rect, osdSize


def overlap(rectA, rectB):
    left = max(rectA[0], rectB[0])
    top = max(rectA[1], rectB[1])
    right = min(rectA[2], rectB[2])
    bottom = min(rectA[3], rectB[3])

    if ((right >= left) and (bottom >= top)):
        return (right - left + 1) * (bottom - top + 1)
    else:
        return 0
