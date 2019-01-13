"""
/***************************************************************************
                                 A QGIS plugin
 CLUZ for QGIS
                             -------------------
        begin                : 2019-01-08
        copyright            : (C) 2019 by Bob Smith, DICE
        email                : r.j.smith@kent.ac.uk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import math
import csv

from .cluz_messages import runYesCancelWarningDialogBox, clearProgressBar, makeProgressBar, warningMessage
from .cluz_mpfunctions import puStatusDoesNotEqualExcluded
from .cluz_mpoutputs import printMPPatchListDict


def makeMinpatchDataDict(setupObject, minpatchObject):
    minpatchDataDict = dict()
    inputPath = setupObject.inputPath
    setupOKBool = True

    puDict, xyLocDictionary = makeMPPUDicts(inputPath + os.sep + 'pu.dat')
    minpatchDataDict['initialUnitDictionary'] = puDict
    minpatchDataDict['xyLocDictionary'] = xyLocDictionary

    targetDict = makeMPTargetDict(inputPath + os.sep + 'spec.dat')
    minpatchDataDict['targetDictionary'] = makeMPTargetDict(inputPath + os.sep + 'spec.dat')

    abundanceMatrixDictionary = makeMPAbundMatrixDict(inputPath + os.sep + 'puvspr2.dat', targetDict, puDict)
    minpatchDataDict['abundanceMatrixDictionary'] = abundanceMatrixDictionary

    boundMatrixDict = makeBoundMatrixDict(inputPath + os.sep + 'bound.dat', puDict)
    minpatchDataDict['boundaryMatrixDictionary'] = boundMatrixDict

    areaDictionary, zoneDict, zoneTypeDict = makeMPDicts(inputPath + os.sep + 'minpatch.dat')
    minpatchDataDict['areaDictionary'] = areaDictionary
    minpatchDataDict['zoneDictionary'] = zoneDict
    minpatchDataDict['zoneTypeDictionary'] = zoneTypeDict
    if len(zoneTypeDict) > 1:
        minpatchObject.zonestatsBool = True
    else:
        minpatchObject.zonestatsBool = False

    setupOKBool = checkMPPUIDValuesMatch(puDict, zoneDict, setupOKBool)
    filesToBeCreatedList = makeMPFilesToBeCreatedList(setupObject, minpatchObject, zoneTypeDict)
    setupOKBool = checkMPOverwriteExistingFiles(filesToBeCreatedList, setupOKBool)
    setupOKBool = checkMPFilesCanBeSaved(filesToBeCreatedList, setupOKBool)
    setupOKBool = checkMPPatchPUIDFile(setupObject, minpatchDataDict, setupOKBool)
    if setupOKBool:
        addPatchPUIDDict = makeMPPatchPUIDDict(setupObject, minpatchDataDict)
        minpatchDataDict['addPatchPUIDDictionary'] = addPatchPUIDDict
        minpatchDataDict = updateMinpatchDataDictWithParameters(minpatchObject, minpatchDataDict)

    return minpatchDataDict, setupOKBool


def checkMPPUIDValuesMatch(puDict, zoneDict, setupOKBool):
    if setupOKBool:
        if zoneDict.keys() != puDict.keys():
            warningMessage('Input files error: ', 'the planning unit ID values in the unit.dat and MinPatch details file do not match, so MinPatch has been terminated.')
            setupOKBool = False
        
    return setupOKBool


def checkMPOverwriteExistingFiles(filesToBeCreatedList, setupOKBool):
    if setupOKBool:
        outputFilesAlreadyExistBool = False
        for filePath in filesToBeCreatedList:
            if os.path.isfile(filePath):
                outputFilesAlreadyExistBool = True
        if outputFilesAlreadyExistBool:
            warningValue = runYesCancelWarningDialogBox('Overwrite files?', 'This will overwrite the existing files from a previous MinPatch analysis of the same Marxan files. Do you want to continue?')
            if warningValue is False:
                setupOKBool = False

    return setupOKBool


def checkMPFilesCanBeSaved(filesToBeCreatedList, setupOKBool):
    if setupOKBool:
        outputFilesCannotBeSavedBool = False
        try:
            for filePath in filesToBeCreatedList:
                with open(filePath, 'wb') as f:
                    csv.reader(f)
        except IOError:
            outputFilesCannotBeSavedBool = True

        if outputFilesCannotBeSavedBool:
            warningMessage('Output files error: ', 'at least one of the required output files cannot be created. Please check that you have permission to write files in the specified output folder and that a file with the same name is not already open.')
            setupOKBool = False

    return setupOKBool


def checkMPPatchPUIDFile(setupObject, minpatchDataDict, setupOKBool):
    if setupOKBool:
        makeNewPatchPUIDFilesBool = checkPatchPUIDFile(setupObject, minpatchDataDict)
        if makeNewPatchPUIDFilesBool:
            if radiusValuesVeryHigh(minpatchDataDict):
                responseValue = runYesCancelWarningDialogBox('Radius values very high', 'At least one of the radius values specified in the MinPatch details file is more than 25% of the approximate height and/or width of the planning region. This could produce very large patches and make MinPatch run very slowly. Is that OK?')
                if responseValue is False:
                    setupOKBool = False
            if setupOKBool:
                createPatchPUIDTextFile(setupObject, minpatchDataDict)

    return setupOKBool


def updateMinpatchDataDictWithParameters(minpatchObject, minpatchDataDict):
    minpatchDataDict['bound_cost'] = minpatchObject.blm
    minpatchDataDict['rem_small_patch'] = minpatchObject.removeBool
    minpatchDataDict['add_patches'] = minpatchObject.addBool
    minpatchDataDict['whittle_polish'] = minpatchObject.whittleBool
    minpatchDataDict['patch_stats'] = True
    minpatchDataDict['zone_stats'] = minpatchObject.zonestatsBool

    return minpatchDataDict


def makeMPFilesToBeCreatedList(setupObject, minpatchObject, zoneTypeDict):
    patchStatsFilePath = setupObject.outputPath + os.sep + 'mp_' + minpatchObject.marxanFileName + '_patchstats.csv'
    bestFilePath = setupObject.outputPath + os.sep + 'mp_' + minpatchObject.marxanFileName + '_best.txt'
    summedFilePath = setupObject.outputPath + os.sep + 'mp_' + minpatchObject.marxanFileName + '_summed.txt'
    filesToBeCreatedList = [patchStatsFilePath, bestFilePath, summedFilePath]

    marxanNameString = minpatchObject.marxanFileName + '_r'
    finalNameString = 'mp_' + marxanNameString
    marxanSolFileList = makeMPMarxanFileList(setupObject, marxanNameString)

    for marxanSolFilePath in marxanSolFileList:
        runOutputFilePath = marxanSolFilePath.replace(marxanNameString, finalNameString)
        filesToBeCreatedList.append(runOutputFilePath)

    if minpatchObject.zonestatsBool:
        zoneStatsBaseFileName = setupObject.outputPath + os.sep + 'mp_' + minpatchObject.marxanFileName
        zoneStatsFilePath = zoneStatsBaseFileName + '_zonestats.csv'
        filesToBeCreatedList.append(zoneStatsFilePath)
        for zoneID in zoneTypeDict.keys():
            zoneFeatStatsFilePath = zoneStatsBaseFileName + '_zonefeaturestat' + str(zoneID) + '.csv'
            filesToBeCreatedList.append(zoneFeatStatsFilePath)

    return filesToBeCreatedList


def makeMPMarxanFileList(setupObject, marxanNameString):
    marxanFileList = list()
    rawList = os.listdir(setupObject.outputPath)
    for aString in rawList:
        if aString.startswith(marxanNameString):
            bString = setupObject.outputPath + os.sep + aString
            cString = os.path.normpath(bString)
            marxanFileList.append(cString)

    return marxanFileList


def makeMPPUDicts(puLocString):
    unitDict = dict()
    xyLocDictionary = dict()

    with open(puLocString, 'rt') as f:
        puReader = csv.reader(f)
        next(puReader)
        for aRow in puReader:
            puID = int(aRow[0])
            puCost = float(aRow[1])
            puStatus = int(aRow[2])
            xLoc = float(aRow[3])
            yLoc = float(aRow[4])

            unitDict[puID] = [puCost, puStatus]
            xyLocDictionary[puID] = [puStatus, xLoc, yLoc]

    return unitDict, xyLocDictionary


def makeMPTargetDict(targetLocString):
    targetDict = dict()

    with open(targetLocString, 'rt') as f:
        targetReader = csv.reader(f)
        next(targetReader)
        for aRow in targetReader:
            featID = int(aRow[0])
            featName = aRow[1]
            featTarget = float(aRow[2])
            featSpf = float(aRow[3])
            featType = int(aRow[4])

            if featTarget > 0:
                targetDict[featID] = [featName, featTarget, featSpf, featType]

    return targetDict


def makeMPDicts(detailsDatPath):
    areaDictionary = dict()
    zoneDict = dict()
    zoneTypeDict = dict()

    with open(detailsDatPath, 'rt') as f:
        zoneReader = csv.reader(f)
        next(zoneReader)
        for aRow in zoneReader:
            puID = int(aRow[0])
            areaValue = float(aRow[1])
            zoneID = int(aRow[2])
            zonePatchAreaValue = float(aRow[3])
            zoneRadiusValue = float(aRow[4])

            areaDictionary[puID] = areaValue
            zoneDict[puID] = [zoneID, zonePatchAreaValue, zoneRadiusValue]
            zoneTypeDict[zoneID] = [zonePatchAreaValue, zoneRadiusValue]

    return areaDictionary, zoneDict, zoneTypeDict


def checkPatchPUIDFile(setupObject, minpatchDataDict):
    zoneTypeDict = minpatchDataDict['zoneTypeDictionary']
    zoneTypeRadiusDict = dict()
    for zoneID in zoneTypeDict:
        zoneRadius = zoneTypeDict[zoneID][1]
        zoneTypeRadiusDict[zoneID] = zoneRadius

    makeNewPatchPUIDFilesBool = False
    patchPUIDFilePath = setupObject.inputPath + os.sep + 'patchPUID.dat'
    try:
        patchPUIDZoneRadiusDict = makePatchPUIDZoneRadiusDict(patchPUIDFilePath)
    except IOError:
        makeNewPatchPUIDFilesBool = True
        patchPUIDZoneRadiusDict = dict()

    if zoneTypeRadiusDict != patchPUIDZoneRadiusDict:
        makeNewPatchPUIDFilesBool = True

    return makeNewPatchPUIDFilesBool


def makePatchPUIDZoneRadiusDict(patchPUIDFilePath):
    patchPUIDZoneRadiusDict = dict()
    with open(patchPUIDFilePath, 'rt') as f:
        patchReader = csv.reader(f)
        for aRow in patchReader:
            firstTextBlock = aRow[0]
            if '***' in firstTextBlock:
                if '*** Patch search distance for Zone' in firstTextBlock:
                    rawZoneTextList = firstTextBlock.split('=')
                    zoneID = int(rawZoneTextList[0].replace('*** Patch search distance for Zone ', ''))
                    zoneRadiusValue = float(rawZoneTextList[1])
                    patchPUIDZoneRadiusDict[zoneID] = zoneRadiusValue
            else:
                break

    return patchPUIDZoneRadiusDict


def makeMPPatchPUIDDict(setupObject, minpatchDataDict):
    patchPUIDPathName = setupObject.inputPath + os.sep + 'patchPUID.dat'
    areaDictionary = minpatchDataDict['areaDictionary']
    zoneDict = minpatchDataDict['zoneDictionary']

    patchPUIDDict = dict()

    with open(patchPUIDPathName, 'rt') as f:
        patchReader = csv.reader(f)
        for aRow in patchReader:
            if '***' not in aRow[0]:
                puID, patchIDList = makePatchIDDetailsFromFileRow(aRow)
                if IsPatchBiggerThanMinimumSize(puID, patchIDList, areaDictionary, zoneDict):
                    patchPUIDDict[puID] = patchIDList
                else:
                    patchPUIDDict[puID] = []

    return patchPUIDDict


def makePatchIDDetailsFromFileRow(aRow):
    rawFirstTwoValuesList = aRow.pop(0).split(':[')
    puID = int(rawFirstTwoValuesList[0])
    firstPatchValue = rawFirstTwoValuesList[1]
    if isPatchPUIDListEmpty(firstPatchValue):
        patchIDList = list()
    else:
        aRow.insert(0, firstPatchValue)
        endRawString = aRow.pop(len(aRow) - 1)
        endString = endRawString.replace(']','')
        aRow.append(endString)
        patchIDList = [int(aString) for aString in aRow]

    return puID, patchIDList


def isPatchPUIDListEmpty(firstPatchValue):
    patchPUIDListIsEmpty = False
    if firstPatchValue == ']':
        patchPUIDListIsEmpty = True

    return patchPUIDListIsEmpty


def IsPatchBiggerThanMinimumSize(puID, patchIDList, areaDictionary, zoneDict):
    patchIsBiggerThanMinimum = False
    minPatchSize = zoneDict[puID][1]
    runningPatchSize = areaDictionary[puID]
    for patchPUID in patchIDList:
        patchPUSize = areaDictionary[patchPUID]
        runningPatchSize += patchPUSize

    if runningPatchSize >= minPatchSize:
        patchIsBiggerThanMinimum = True

    return patchIsBiggerThanMinimum


def makeBoundMatrixDict(boundaryLocationString, unitDictionary):
    boundMatrixDict = dict()
    puList = list(unitDictionary.keys())
    for aNum in puList:
        boundMatrixDict[aNum] = dict()

    with open(boundaryLocationString, 'rt') as f:
        boundReader = csv.reader(f)
        next(boundReader)
        for aRow in boundReader:
            id1Value = int(aRow[0])
            id2Value = int(aRow[1])
            boundValue = float(aRow[2])

            boundDict1 = boundMatrixDict[id1Value]
            boundDict1[id2Value] = boundValue
            boundDict2 = boundMatrixDict[id2Value]
            boundDict2[id1Value] = boundValue

    return boundMatrixDict


def makeMPAbundMatrixDict(abundanceLocationString, targetDictionary, unitDictionary):
    abundMatrixDict = dict()
    puList = unitDictionary.keys()
    featSet = set(targetDictionary.keys())
    for aNum in puList:
        abundMatrixDict[aNum] = dict()

    with open(abundanceLocationString, 'rt') as f:
        abundReader = csv.reader(f)
        next(abundReader)
        for aRow in abundReader:
            featID = int(aRow[0])
            if featID in featSet:
                puID = int(aRow[1])
                featAmount = float(aRow[2])

                puAbundDict = abundMatrixDict[puID]
                puAbundDict[featID] = featAmount

    return abundMatrixDict


def createPatchPUIDTextFile(setupObject, minpatchDataDict):
    xyLocDictionary = minpatchDataDict['xyLocDictionary']
    zoneDict = minpatchDataDict['zoneDictionary']
    zoneTypeDict = minpatchDataDict['zoneTypeDictionary']
    unitDict = minpatchDataDict['initialUnitDictionary']
    boundMatrixDict = minpatchDataDict['boundaryMatrixDictionary']
    patchListDict = dict()

    progressBar = makeProgressBar('Making patchPUID.dat file in input folder')
    rowTotalCount = len(unitDict)
    rowCount = 1

    for puID in unitDict:
        progressBar.setValue((rowCount/rowTotalCount) * 100)
        rowCount += 1

        puStatus, puXvalue, puYvalue = xyLocDictionary[puID]
        zoneID, zonePatchAreaValue, zonePatchRadiusValue = zoneDict[puID]
        puIDPatchSet = set()
        if puStatusDoesNotEqualExcluded(unitDict, puID):
            candidatePUIDPatchSet = set(boundMatrixDict[puID].keys())
            alreadyTestedPUIDPatchSet = set()
            alreadyTestedPUIDPatchSet.add(puID)
            while len(candidatePUIDPatchSet) > 0:
                testCandidatePUID = candidatePUIDPatchSet.pop()
                testCandidatePUStatus, testCandidatePUXvalue, testCandidatePUYvalue = xyLocDictionary[testCandidatePUID]
                if puStatusDoesNotEqualExcluded(unitDict, testCandidatePUID):
                    if isPUCentroidWithinPatchRadius(puXvalue, puYvalue, testCandidatePUXvalue, testCandidatePUYvalue, zonePatchRadiusValue):
                        puIDPatchSet.add(testCandidatePUID)
                        testCandidatePUIDPatchSet = set(boundMatrixDict[testCandidatePUID].keys())
                        newCandidatePUIDPatchSet = testCandidatePUIDPatchSet.difference(alreadyTestedPUIDPatchSet)
                        candidatePUIDPatchSet = candidatePUIDPatchSet.union(newCandidatePUIDPatchSet)
                    alreadyTestedPUIDPatchSet.add(testCandidatePUID)

            puIDPatchList = list(puIDPatchSet)
            puIDPatchList.sort()
            patchListDict[puID] = puIDPatchList

    clearProgressBar()
    printMPPatchListDict(patchListDict, zoneTypeDict, setupObject.inputPath + os.sep + 'patchPUID.dat')


def isPUCentroidWithinPatchRadius(aXValue, aYValue, bXValue, bYValue, patchRadiusValue):
    centroidWithinPatchRadius = False
    xDiff = aXValue - bXValue
    yDiff = aYValue - bYValue
    xDiffSquare = pow(xDiff,2)
    yDiffSquare = pow(yDiff,2)
    centrDist = math.sqrt(xDiffSquare + yDiffSquare)
    if centrDist <= patchRadiusValue:
        centroidWithinPatchRadius = True

    return centroidWithinPatchRadius


def radiusValuesVeryHigh(minpatchDataDict):
    checkBool = False
    minX, maxX, minY, maxY = returnMinMaxXYList(minpatchDataDict)
    xExtent = maxX - minX
    yExtent = maxY - minY
    highestRadiusValue = returnHighestRadiusValue(minpatchDataDict)
    if highestRadiusValue / xExtent > 0.25 or highestRadiusValue / yExtent > 0.25:
        checkBool = True

    return checkBool


def returnMinMaxXYList(minpatchDataDict):
    xyLocDictionary = minpatchDataDict['xyLocDictionary']
    minX, maxX, minY, maxY = ['blank', 'blank', 'blank', 'blank']
    for puID in xyLocDictionary:
        puStatus, xLocString, yLocString = xyLocDictionary[puID]
        xLoc = float(xLocString)
        yLoc = float(yLocString)
        if minX == 'blank' or xLoc < minX:
            minX = xLoc
        if maxX == 'blank' or xLoc > maxX:
            maxX = xLoc
        if minY == 'blank' or yLoc < minY:
            minY = yLoc
        if maxY == 'blank' or yLoc > maxY:
            maxY = yLoc

    minMaxXYList = [minX, maxX, minY, maxY]

    return minMaxXYList


def returnHighestRadiusValue(minpatchDataDict):
    zoneTypeDict = minpatchDataDict['zoneTypeDictionary']
    highestRadiusValue = -1
    for zoneID in zoneTypeDict:
        zoneRadiusValue = zoneTypeDict[zoneID][1]
        if zoneRadiusValue > highestRadiusValue:
            highestRadiusValue = zoneRadiusValue

    return highestRadiusValue

