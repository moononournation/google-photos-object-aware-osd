from PIL import Image, ImageEnhance
import json
import os
import random

DEBUG = os.getenv('DEBUG')
photoList = []
random.seed()
overlapWeightRatioThresholdDict = {}


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


def getWeight(item, iBp, width, height):
    weight = item["percentage_probability"]
    # if item["name"] == 'person':
    #     weight *= 2
    if item["name"] == 'face':
        weight *= 1.5  # percentage > 66.7 become > 1
        weight *= weight # amplifer weight of face
    return weight * (iBp[2] - iBp[0] + 1) * \
        (iBp[3] - iBp[1] + 1) / width / height


def overlap(rectA, rectB):
    left = max(rectA[0], rectB[0])
    top = max(rectA[1], rectB[1])
    right = min(rectA[2], rectB[2])
    bottom = min(rectA[3], rectB[3])

    if ((right >= left) and (bottom >= top)):
        return (right - left + 1) * (bottom - top + 1)
    else:
        return 0


def getRandomPhoto(width, height, PHOTOPATH, DETECTEDPHOTOPATH, DETECTEDJSONPATH):
    global overlapWeightRatioThreshold

    scale = 0
    crop_rect = (0, 0, 0, 0)
    overlapWeightRatio = -1
    aspectRatioStr = '{0:.2f}'.format(width / height)
    if (aspectRatioStr in overlapWeightRatioThresholdDict):
        overlapWeightRatioThreshold = overlapWeightRatioThresholdDict[aspectRatioStr]
    else:
        overlapWeightRatioThreshold = 0
    while overlapWeightRatio < overlapWeightRatioThreshold:
        randomIdx = random.randint(0, len(photoList) - 1)

        filename = photoList[randomIdx]

        if DEBUG == 'Y':
            photoFilename = os.path.join(DETECTEDPHOTOPATH, filename)
        else:
            photoFilename = os.path.join(PHOTOPATH, filename)

        image = Image.open(photoFilename)
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
            step = (iW - cW) / 4
            offset = 0
            cropA = (offset, 0, offset + cW - 1, cH - 1)
            offset += step
            cropB = (offset, 0, offset + cW - 1, cH - 1)
            offset += step
            cropC = (offset, 0, offset + cW - 1, cH - 1)
            offset += step
            cropD = (offset, 0, offset + cW - 1, cH - 1)
            cropE = (iW - cW, 0, iW - 1, cH - 1)
        else:
            scale = wScale
            cW = iW
            cH = height / scale
            step = (iH - cH) / 4
            offset = 0
            cropA = (0, offset, cW - 1, offset + cH - 1)
            offset += step
            cropB = (0, offset, cW - 1, offset + cH - 1)
            offset += step
            cropC = (0, offset, cW - 1, offset + cH - 1)
            offset += step
            cropD = (0, offset, cW - 1, offset + cH - 1)
            cropE = (0, iH - cH, cW - 1, iH - 1)

        jsonFilename = os.path.join(DETECTEDJSONPATH, filename + ".json")
        with open(jsonFilename) as jsonFile:
            items = json.load(jsonFile)

            # determine CROP area
            fullWeight = 0
            overlapA = 0
            overlapB = 0
            overlapC = 0
            overlapD = 0
            overlapE = 0

            for item in items:
                iBp = item["box_points"]
                weight = getWeight(item, iBp, width, height)
                fullWeight += (iBp[2] - iBp[0] + 1) * \
                    (iBp[3] - iBp[1] + 1) * weight
                overlapA += overlap(iBp, cropA) * weight
                overlapB += overlap(iBp, cropB) * weight
                overlapC += overlap(iBp, cropC) * weight
                overlapD += overlap(iBp, cropD) * weight
                overlapE += overlap(iBp, cropE) * weight
                if DEBUG == 'Y':
                    print(item["name"], "|", str(item["percentage_probability"]),
                          "|", iBp, "|", weight)

            # Crop select most details area
            max_overlap = max(overlapA, overlapB,
                              overlapC, overlapD, overlapE)
            if fullWeight == 0:
                overlapWeightRatio = 1
            else:
                overlapWeightRatio = max_overlap / fullWeight
            if DEBUG == 'Y':
                print("Crop overlap:", overlapA, "|", overlapB, "|",
                      overlapC, "|", overlapD, "|", overlapE, "|", max_overlap)

            print("Overlap Weight Ratio:", overlapWeightRatio)

            # prefer centre if same value
            if overlapC == max_overlap:
                crop_rect = cropC
            if overlapB == max_overlap:
                crop_rect = cropB
            if overlapD == max_overlap:
                crop_rect = cropD
            elif overlapA == max_overlap:
                crop_rect = cropA
            elif overlapE == max_overlap:
                crop_rect = cropE

    overlapWeightRatio = round(overlapWeightRatio - 0.051, 1) # truncate value after 1 decimal place
    if (overlapWeightRatioThreshold < overlapWeightRatio):
        overlapWeightRatioThresholdDict[aspectRatioStr] = overlapWeightRatio
        print("Adjust Overlap Weight Ratio Threshold to:", overlapWeightRatio)

    return filename, scale, crop_rect, image


def getDimension(filename, width, height, scale, crop_rect, osdRatio):
    osdSize = min(width, height) * osdRatio
    margin = osdSize * 0.04

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
            weight = getWeight(item, iBp, width, height)
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

    return osd_rect, osdSize
