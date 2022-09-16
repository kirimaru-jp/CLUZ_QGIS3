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

from qgis.core import QgsVectorLayer, QgsSpatialIndex, QgsField
from qgis.PyQt.QtCore import QVariant

import os
import csv
import math
import time
import shutil
import statistics
import tempfile

from .cluz_messages import clearProgressBar, emptyPolgyonPUIDSetErrorMessage, makeProgressBar, warningMessage, criticalMessage
from .cluz_make_file_dicts import writeBoundDatFile


############################ Produce Marxan input files ############################

def createZonesFeatDatFile(setupObject):
    zonesFeatDatFile = setupObject.inputPath + os.sep + 'feat.dat'
    with open(zonesFeatDatFile,'w', newline='') as out_file:
        specDatWriter = csv.writer(out_file)
        specDatWriter.writerow(['id', 'name', 'target', 'spf'])

        targetDict = setupObject.targetDict
        featList = list(targetDict.keys())
        featList.sort()

        progressBar = makeProgressBar('Making a new feat.dat file')
        rowTotalCount = len(featList)
        rowCount = 1

        for aFeat in featList:
            progressBar.setValue((rowCount/rowTotalCount) * 100)
            rowCount += 1

            featList = targetDict[aFeat]
            rawFeatName = featList[0]
            changeBool, featName = convertFeatNameByChangingIncompatibleTextCharacters(rawFeatName)
            featTarget = featList[3]
            featSpf = featList[2]
            specDatWriter.writerow([aFeat, featName, featTarget, featSpf])
    clearProgressBar()
    # if changeBool:
    #     warningMessage('Conservation Feature names amended', 'Some of the conservation feature names have been modified in the spec.dat file to make them Marxan compatible.')


def convertFeatNameByChangingIncompatibleTextCharacters(rawFeatName):
    changeBool = False
    featName = rawFeatName.replace(' ', '_')
    featName = featName.replace('.', '')

    if rawFeatName != featName:
        changeBool = True

    return changeBool, featName


def createZonesTargetDatFile(setupObject):
    zonesFeatDatFile = setupObject.inputPath + os.sep + 'zonetarget.dat'
    with open(zonesFeatDatFile,'w', newline='') as out_file:
        zonesTargetDatWriter = csv.writer(out_file)
        zonesTargetDatWriter.writerow(['zoneid', 'featureid', 'target'])

        featList = list(setupObject.targetDict.keys())
        featList.sort()

        progressBar = makeProgressBar('Making a new feat.dat file')
        rowTotalCount = len(featList)
        rowCount = 1

        for zonesTargetTypeName in setupObject.zonesTargetDict:
            progressBar.setValue((rowCount/rowTotalCount) * 100)
            rowCount += 1

            zonesIDPrefix = zonesTargetTypeName.split('_')[0]
            zonesID = int(zonesIDPrefix[1:])
            zonesFeatTargetDict = setupObject.zonesTargetDict[zonesTargetTypeName]
            for featID in zonesFeatTargetDict:
                zonesTargetDatWriter.writerow([zonesID, featID, zonesFeatTargetDict[featID]])
    clearProgressBar()


def createZonesPropDatFile(setupObject):
    zonesPropDatFile = setupObject.inputPath + os.sep + 'zonecontrib.dat'
    with open(zonesPropDatFile,'w', newline='') as out_file:
        zonesPropDatWriter = csv.writer(out_file)
        zonesPropDatWriter.writerow(['zoneid', 'featureid', 'fraction'])

        featList = list(setupObject.targetDict.keys())
        featList.sort()

        progressBar = makeProgressBar('Making a new feat.dat file')
        rowTotalCount = len(featList)
        rowCount = 1

        for zonesPropTypeName in setupObject.zonesPropDict:
            progressBar.setValue((rowCount/rowTotalCount) * 100)
            rowCount += 1

            zonesIDPrefix = zonesPropTypeName.split('_')[0]
            zonesID = int(zonesIDPrefix[1:])
            zonesPropTargetDict = setupObject.zonesPropDict[zonesPropTypeName]
            for featID in zonesPropTargetDict:
                zonesPropDatWriter.writerow([zonesID, featID, zonesPropTargetDict[featID]])
    clearProgressBar()


def createZonesPuDatFile(setupObject):
    puZonesDatPathName = setupObject.inputPath + os.sep + 'pu.dat'

    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    puFeatures = puLayer.getFeatures()
    puIDField = puLayer.fields().indexFromName('Unit_ID')

    progressBar = makeProgressBar('Making a new pu.dat file')
    polyCount = 1
    polyTotalCount = puLayer.featureCount()

    with open(puZonesDatPathName,'w', newline='') as out_file:
        puDatWriter = csv.writer(out_file)
        zonesPuDatFileHeaderList = ['id'] + makeZonesHeaderList(setupObject, '_Cost')
        puDatWriter.writerow(zonesPuDatFileHeaderList)

        zonesPuCostFieldList = makeZonesFieldList(setupObject, puLayer, '_Cost')
        for puFeature in puFeatures:
            progressBar.setValue((polyCount/polyTotalCount) * 100)
            polyCount += 1
            puDatRowList = makePUDatRowList(setupObject, puFeature, puIDField, zonesPuCostFieldList)
            puDatWriter.writerow(puDatRowList)
    clearProgressBar()


def makePUDatRowList(setupObject, puFeature, puIDField, zonesPuCostFieldList):
    decPrec = setupObject.decimalPlaces
    puAttributes = puFeature.attributes()
    puID = puAttributes[puIDField]

    puDatRowList = [puID]
    for costField in zonesPuCostFieldList:
        rawCostValue = puAttributes[costField]
        costValue = round(float(rawCostValue), decPrec)
        costValue = format(costValue, "." + str(decPrec) + "f")
        puDatRowList.append(costValue)

    return puDatRowList


def createZonesPUStatusDict(setupObject):
    zonesPUStatusDict = dict()
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    puFeatures = puLayer.getFeatures()
    puIDField = puLayer.fields().indexFromName('Unit_ID')
    zonesPuStatusFieldNameList = makeZonesHeaderList(setupObject, '_Status')

    for puFeature in puFeatures:
        puAttributes = puFeature.attributes()
        puID = puAttributes[puIDField]
        for statusFieldName in zonesPuStatusFieldNameList:
            zonesIDPrefix = statusFieldName.split('_')[0]
            zonesID = int(zonesIDPrefix[1:])
            statusField = puLayer.fields().indexFromName(statusFieldName)
            statusValue = puAttributes[statusField]
            try:
                zonesPUStatusList = zonesPUStatusDict[puID]
            except KeyError:
                zonesPUStatusList = ['blank'] * len(setupObject.zonesDict)
            zonesPUStatusList[zonesID - 1] = statusValue
            zonesPUStatusDict[puID] = zonesPUStatusList

    return zonesPUStatusDict


def createPuLockDatFile(setupObject, zonesPUStatusDict):
    puLockDatPathName = setupObject.inputPath + os.sep + 'pulock.dat'

    progressBar = makeProgressBar('Making a new pulock.dat file')
    lineCount = 1
    lineTotalCount = len(zonesPUStatusDict)

    with open(puLockDatPathName,'w', newline='') as out_file:
        puLockDatWriter = csv.writer(out_file)
        puLockDatWriter.writerow(['puID', 'zoneid'])
        puIDList = list(zonesPUStatusDict.keys())
        puIDList.sort()
        for puID in puIDList:
            progressBar.setValue((lineCount/lineTotalCount) * 100)
            lineCount += 1

            zonesPUStatusList = zonesPUStatusDict[puID]
            for aCol in range(0, len(zonesPUStatusList)):
                statusValue = zonesPUStatusList[aCol]
                zoneID = aCol + 1
                if statusValue == 'Locked':
                    puLockDatWriter.writerow([puID, zoneID])

    clearProgressBar()


def createPuZoneDatFile(setupObject, zonesPUStatusDict):
    puZonesDatPathName = setupObject.inputPath + os.sep + 'puzone.dat'

    progressBar = makeProgressBar('Making a new puzone.dat file')
    lineCount = 1
    lineTotalCount = len(zonesPUStatusDict)

    with open(puZonesDatPathName,'w', newline='') as out_file:
        puZonesDatWriter = csv.writer(out_file)
        puZonesDatWriter.writerow(['puID', 'zoneid'])
        puIDList = list(zonesPUStatusDict.keys())
        puIDList.sort()
        for puID in puIDList:
            progressBar.setValue((lineCount/lineTotalCount) * 100)
            lineCount += 1

            zonesPUStatusList = zonesPUStatusDict[puID]
            if 'Excluded' in zonesPUStatusList:
                restrictedToZoneList = makeRestrictedToZoneList(zonesPUStatusList)
                for zoneID in restrictedToZoneList:
                    puZonesDatWriter.writerow([puID, zoneID])

    clearProgressBar()


def makeRestrictedToZoneList(zonesPUStatusList):
    restrictedToZoneList = list()
    for aCol in range(0, len(zonesPUStatusList)):
        statusValue = zonesPUStatusList[aCol]
        zoneID = aCol + 1
        if statusValue != 'Excluded':
            restrictedToZoneList.append(zoneID)

    return restrictedToZoneList


def makeZonesHeaderList(setupObject, nameSuffix):
    zonesPuDatFileHeaderList = list()
    for zoneNum in range(1, len(setupObject.zonesDict) + 1):
        newZoneHeader = 'Z' + str(zoneNum) + nameSuffix
        zonesPuDatFileHeaderList.append(newZoneHeader)

    return zonesPuDatFileHeaderList


def makeZonesFieldList(setupObject, puLayer, nameSuffix):
    zonesPuCostFieldList = list()
    for zoneNum in range(1, len(setupObject.zonesDict) + 1):
        zonesCostFieldName = 'Z' + str(zoneNum) + nameSuffix
        zonesCostField = puLayer.fields().indexFromName(zonesCostFieldName)
        zonesPuCostFieldList.append(zonesCostField)

    return zonesPuCostFieldList


def createCostsDatFile(setupObject):
    costsDatPathName = setupObject.inputPath + os.sep + 'costs.dat'

    progressBar = makeProgressBar('Making a new costs.dat file')
    rowCount = 1
    totalRowCount = len(setupObject.zonesDict)

    with open(costsDatPathName,'w', newline='') as out_file:
        costsDatWriter = csv.writer(out_file)
        costsDatWriter.writerow(['costid', 'costname'])

        for zoneNum in range(1, len(setupObject.zonesDict) + 1):
            progressBar.setValue((rowCount/totalRowCount) * 100)
            rowCount += 1
            costsDatWriter.writerow([zoneNum, 'Z' + str(zoneNum) + '_Cost'])
    clearProgressBar()


def createZonesDatFile(setupObject):
    zonesDatPathName = setupObject.inputPath + os.sep + 'zones.dat'

    progressBar = makeProgressBar('Making a new zones.dat file')
    rowCount = 1
    totalRowCount = len(setupObject.zonesDict)

    with open(zonesDatPathName,'w', newline='') as out_file:
        costsDatWriter = csv.writer(out_file)
        costsDatWriter.writerow(['zoneid', 'zonename'])

        for zoneID in setupObject.zonesDict:
            progressBar.setValue((rowCount/totalRowCount) * 100)
            costsDatWriter.writerow([zoneID, setupObject.zonesDict[zoneID]])
    clearProgressBar()


def createZonecostDatFile(setupObject):
    zonecostDatPathName = setupObject.inputPath + os.sep + 'zonecost.dat'

    progressBar = makeProgressBar('Making a new zonecost.dat file')
    rowCount = 1
    totalRowCount = len(setupObject.zonesDict)

    with open(zonecostDatPathName,'w', newline='') as out_file:
        zonecostDatWriter = csv.writer(out_file)
        zonecostDatWriter.writerow(['zoneid', 'costid', 'multiplier'])

        for zoneID in setupObject.zonesDict:
            progressBar.setValue((rowCount/totalRowCount) * 100)
            for costID in setupObject.zonesDict:
                if zoneID == costID:
                    zonecostDatWriter.writerow([zoneID, costID, 1])
                else:
                    zonecostDatWriter.writerow([zoneID, costID, 0])
    clearProgressBar()


# def makePUDatRowList(puFeature, puStatusDict, puIDField, puCostField, puStatusField, decPrec):
#     puAttributes = puFeature.attributes()
#     puID = puAttributes[puIDField]
#     puCost = puAttributes[puCostField]
#     puStatus = puAttributes[puStatusField]
#     puStatusCode = puStatusDict[puStatus]
#
#     puCentroid = puFeature.geometry().centroid()
#     rawXCoord = puCentroid.asPoint().x()
#     xCoord = round(float(rawXCoord), decPrec)
#     xCoord = format(xCoord, "." + str(decPrec) + "f")
#
#     rawYCoord = puCentroid.asPoint().y()
#     yCoord = round(float(rawYCoord), decPrec)
#     yCoord = format(yCoord, "." + str(decPrec) + "f")
#
#     puDatRowList = [puID, puCost, puStatusCode, xCoord, yCoord]
#
#     return puDatRowList


# def createZonesPuDatFile(setupObject):
#     decPrec = setupObject.decimalPlaces
#     puZonesDatPathName = setupObject.inputPath + os.sep + 'pu.dat'
#
#     puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
#     puFeatures = puLayer.getFeatures()
#     puIDField = puLayer.fields().indexFromName('Unit_ID')
#
#     progressBar = makeProgressBar('Making a new pu.dat file')
#     polyCount = 1
#     polyTotalCount = puLayer.featureCount()
#
#     with open(puZonesDatPathName,'w', newline='') as out_file:
#         puDatWriter = csv.writer(out_file)
#         puDatWriter.writerow(['id', 'cost', 'status', 'xloc', 'yloc'])
#         puStatusDict = {'Available': 0, 'Earmarked': 2, 'Conserved': 2, 'Excluded': 3}
#
#         for puFeature in puFeatures:
#             progressBar.setValue((polyCount/polyTotalCount) * 100)
#             polyCount += 1
#             puDatRowList = makePUDatRowList(puFeature, puStatusDict, puIDField, puCostField, puStatusField, decPrec)
#             puDatWriter.writerow(puDatRowList)
#     clearProgressBar()



#
#
# def createBoundDatFile(setupObject, extEdgeBool):
#     puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
#     puIDFieldIndex = puLayer.fields().indexFromName('Unit_ID')
#     puIDGeomDict = makePUIDGeomDict(puLayer, puIDFieldIndex)
#     vertexList, emptyPolgyonPUIDSet = makeVertexList(puIDGeomDict)
#     vertexList.sort()
#     boundResultsDict = makeBoundResultDict(vertexList)
#     if len(emptyPolgyonPUIDSet) > 0:
#         emptyPolgyonPUIDSetErrorMessage(emptyPolgyonPUIDSet)
#
#     writeBoundDatFile(setupObject, boundResultsDict, extEdgeBool)
#
#
# def makePUIDGeomDict(puLayer, puIDFieldIndex):
#     puIDGeomDict = dict()
#
#     progressBar = makeProgressBar('Processing planning unit shapefile spatial data')
#     polyCount = 1
#     polyTotalCount = puLayer.featureCount()
#
#     for aPolygon in puLayer.getFeatures():
#         progressBar.setValue((polyCount/polyTotalCount) * 100)
#         polyCount += 1
#         puIDGeomDict[aPolygon.attributes()[puIDFieldIndex]] = aPolygon.geometry()
#     clearProgressBar()
#
#     return puIDGeomDict
#
#
# def makeVertexList(puIDGeomDict):
#     vertexList = list()
#
#     progressBar = makeProgressBar('Extracting the vertex data from the planning unit shapefile')
#     progressCount = 1
#     numPUs = len(puIDGeomDict)
#
#     emptyPolgyonPUIDSet = set()
#     for puID in puIDGeomDict:
#         progressBar.setValue((progressCount/numPUs) * 100)
#         progressCount += 1
#
#         puGeom = puIDGeomDict[puID]
#         puVertexSet = makeNewPUVertexSet(puGeom)
#         if len(puVertexSet) == 0:
#             emptyPolgyonPUIDSet.add(puID)
#         else:
#             for aVertex in puVertexSet:
#                 vertexList.append((aVertex, puID))
#     clearProgressBar()
#
#     return vertexList, emptyPolgyonPUIDSet
#
#
# def makeBoundResultDict(vertexList):
#     boundResultsDict = dict()
#     rowNum = 0
#     listLength = len(vertexList) - 1
#
#     progressBar = makeProgressBar('Extracting the vertex data from the planning unit shapefile')
#     totRowNum = len(vertexList)
#
#     while rowNum < listLength:
#         progressBar.setValue((rowNum/totRowNum) * 100)
#
#         (vertexA, puIDA) = vertexList[rowNum]
#         (vertexB, puIDB) = vertexList[rowNum + 1]
#         if vertexA != vertexB:
#             rowNum += 1
#         else:
#             puDictKey = (puIDA, puIDB)
#             boundResultsDict[puDictKey] = returnRunningLengthValue(boundResultsDict, vertexA, puDictKey)
#             if puIDA == puIDB:
#                 rowNum += 1
#             else:
#                 rowNum += 2
#     clearProgressBar()
#
#     return boundResultsDict
#
#
# def returnRunningLengthValue(boundResultsDict, aVertex, puDictKey):
#     vertexLength = calcVertexLength(aVertex)
#     try:
#         runningLengthValue = boundResultsDict[puDictKey]
#         runningLengthValue += vertexLength
#     except KeyError:
#         runningLengthValue = vertexLength
#
#     return runningLengthValue
#
#
# def makeNewPUVertexSet(puGeom):
#     if puGeom.isMultipart():
#         polygonList = puGeom.asMultiPolygon()[0] #
#     else:
#         polygonList = list()
#         polygonList.append(puGeom.asPolygon())
#
#     aPolyPointList = list()
#     for aPolygon in polygonList:
#         polyXYList = list()
#         for aQgsPointXY in aPolygon:
#             polyXYList.append((aQgsPointXY.x(), aQgsPointXY.y()))
#         aPolyPointList.append(polyXYList)
#
#     puVertexSet = convertPolygonPointList2VertexSet(aPolyPointList)
#
#     return puVertexSet
#
#
# def calcVertexLength(aVertex):
#     (x1, y1, x2, y2) = aVertex
#     xLength = x2 - x1
#     yLength = y2 - y1
#     vertexLength = math.sqrt(xLength**2 + yLength**2)
#
#     return vertexLength
#
#
# def convertPolygonPointList2VertexSet(polyPointList): #This deals with multi polygon planning units
#     vertexSet = set()
#     for aPolygonPointList in polyPointList:
#         listLength = len(aPolygonPointList)
#         for aNumber in range(0, listLength - 1):
#             x1 = aPolygonPointList[aNumber][0]
#             y1 = aPolygonPointList[aNumber][1]
#             x2 = aPolygonPointList[aNumber + 1][0]
#             y2 = aPolygonPointList[aNumber + 1][1]
#             if x1 > x2:
#                 finalX1 = x2
#                 finalX2 = x1
#             else:
#                 finalX1 = x1
#                 finalX2 = x2
#             if y1 > y2:
#                 finalY1 = y2
#                 finalY2 = y1
#             else:
#                 finalY1 = y1
#                 finalY2 = y2
#             vecTuple = (finalX1, finalY1, finalX2, finalY2)
#             vertexSet.add(vecTuple)
#
#     return vertexSet
#
#
# ########################### Marxan dialog ###########################
#
def returnZonesOutputName(setupObject):
    oldOutputName = setupObject.outputName
    outputPath = setupObject.outputPath
    oldOutputBestName = outputPath + os.sep + oldOutputName + '_best.csv'

    oldOutputNameStem = ''
    numValueBool = True
    for aNum in range(len(oldOutputName), 0, -1):
        aChar = oldOutputName[aNum - 1]
        try:
            int(aChar)
        except ValueError:
            numValueBool = False
        if numValueBool is False:
            oldOutputNameStem = aChar + oldOutputNameStem

    if os.path.isfile(oldOutputBestName):
        nameSuffix = 1
        newName = outputPath + os.sep + oldOutputNameStem + str(nameSuffix) + '_best.csv'
        while os.path.isfile(newName):
            nameSuffix += 1
            newName = outputPath + os.sep + oldOutputNameStem + str(nameSuffix) + '_best.csv'

        outputName = oldOutputNameStem + str(nameSuffix)
    else:
        outputName = oldOutputName

    return outputName


def createZonesBLMFile(ZonesMarxanDialog, setupObject):
    zonesBLMValueDict = makeZonesBLMValueDictFromDialog(ZonesMarxanDialog)
    setupObject.zonesBLMDict = zonesBLMValueDict

    puZonesBLMDatPathName = setupObject.inputPath + os.sep + 'zoneboundcost.dat'

    progressBar = makeProgressBar('Making a new zoneboundcost.dat file')
    lineCount = 1
    lineTotalCount = len(zonesBLMValueDict)

    with open(puZonesBLMDatPathName,'w', newline='') as out_file:
        puZonesBoundCostDatWriter = csv.writer(out_file)
        puZonesBoundCostDatWriter.writerow(['zoneid1', 'zoneid2', 'cost'])
        puZonesLabelList = list(zonesBLMValueDict.keys())
        puZonesLabelList.sort()
        for aZoneLabel in puZonesLabelList:
            progressBar.setValue((lineCount/lineTotalCount) * 100)
            lineCount += 1
            zonesSplitLabel = aZoneLabel.split(' vs ')
            zoneID1 = zonesSplitLabel[0][5:]
            zoneID2 = zonesSplitLabel[1][5:]
            puZonesBoundCostDatWriter.writerow([zoneID1, zoneID2, zonesBLMValueDict[aZoneLabel]])
    clearProgressBar()

    return setupObject


def makeZonesBLMValueDictFromDialog(ZonesMarxanDialog):
    zonesBLMValueDict = dict()
    for aRow in range(0, ZonesMarxanDialog.blmTableWidget.rowCount()):
        labelValue = ZonesMarxanDialog.blmTableWidget.item(aRow, 0).text()
        blmValue = float(ZonesMarxanDialog.blmTableWidget.item(aRow, 1).text())
        zonesBLMValueDict[labelValue] = blmValue

    return zonesBLMValueDict

#
# def checkNumIterParaDict(numIter):
#     checkBool = True
#     try:
#         int(numIter)
#         if int(numIter) < 10000:
#             warningMessage('Input error', 'The number of iterations must be higher than 10000 because it must be be higher than the NUMTEMP value used in Marxan (see the Marxan manual for more details).')
#             checkBool = False
#     except ValueError:
#         warningMessage('Input error', 'The number of iterations must be an integer')
#         checkBool = False
#
#     return checkBool
#
#
# def checkNumRunsParaDict(numRun, checkBool):
#     try:
#         int(numRun)
#         if int(numRun) < 1:
#             warningMessage('Input error', 'The number of runs must be 1 or a larger whole number')
#             checkBool = False
#     except ValueError:
#         warningMessage('Input error', 'The number of runs must be an integer.')
#         checkBool = False
#
#     return checkBool
#
#
# def checkBlmValueParaDict(blmValue, checkBool):
#     try:
#         float(blmValue)
#         if float(blmValue) < 0:
#             warningMessage('Input error', 'The boundary length modifier must be a non-negative number.')
#             checkBool = False
#     except ValueError:
#         warningMessage('Input error', 'The boundary length modifier must be a non-negative number.')
#         checkBool = False
#
#     return checkBool
#
#
# def checkMissingPropValueParaDict(missingProp, checkBool):
#     try:
#         float(missingProp)
#         if float(missingProp) < 0 or float(missingProp) > 1:
#             checkBool = False
#             warningMessage('Input error', 'The species proportion value must be a number between 0 and 1.')
#     except ValueError:
#         checkBool = False
#         warningMessage('Input error', 'The species proportion value must be a number between 0 and 1.')
#
#     return checkBool
#
#
# def checkInitialPropValueParaDict(initialProp, checkBool):
#     try:
#         float(initialProp)
#         if float(initialProp) < 0 or float(initialProp) > 1:
#             checkBool = False
#             warningMessage('Input error', 'The proportion of planning units randomly included at the beginning of each run must be a number between 0 and 1.')
#     except ValueError:
#         checkBool = False
#         warningMessage('Input error', 'The proportion of planning units randomly included at the beginning of each run must be a number between 0 and 1.')
#
#     return checkBool
#
#
# def checkNumParallelAnalysesValueParaDict(numRunString, numParallelAnalyses, checkBool):
#     try:
#         if int(numRunString) < numParallelAnalyses:
#             checkBool = False
#             warningMessage('Input error', 'The number of parallel analyses must be less than the specified number of runs.')
#     except ValueError:
#         pass
#
#     return checkBool
#
#
# def checkPermissionToUseMarxanFolderParaDict(marxanParameterDict, marxanInputValuesBool):
#     marxanPathText = marxanParameterDict['marxanPath']
#     marxanFolder = os.path.dirname(marxanPathText)
#     marxanInputPath = marxanFolder + os.sep + 'input.dat'
#     try:
#         with open(marxanInputPath,'w', newline='') as marxanFile:
#             marxanWriter = csv.writer(marxanFile)
#     except PermissionError:
#         criticalMessage('Permission problem', 'You do not have permission to save files in the specified Marxan folder. CLUZ needs this to create input.dat and .bat files in the Marxan folder. Please move Marxan to a folder where you do have permission to save files.')
#         marxanInputValuesBool = False
#
#     return marxanInputValuesBool
#
#
def makeZonesMarxanInputFile(setupObject, marxanParameterDict):
    if marxanParameterDict['extraOutputsBool']:
        extraOutputValue = '3'
    else:
        extraOutputValue = '0'
    if os.path.isfile(marxanParameterDict['marxanPath']):
        writeZonesMarxanInputFile(setupObject, marxanParameterDict, extraOutputValue)


def writeZonesMarxanInputFile(setupObject, zonesMarxanParameterDict, extraOutputValue):
    with open(zonesMarxanParameterDict['marxanSetupPath'],'w', newline='') as marxanFile:
        marxanWriter = csv.writer(marxanFile)

        header1 = 'Input file for Marxan program, written by Ian Ball, Hugh Possingham and Matt Watts.'
        header2 = 'This file was generated using CLUZ, written by Bob Smith'
        marxanWriter.writerow([header1])
        marxanWriter.writerow([header2])
        marxanWriter.writerow([])

        marxanWriter.writerow(['General Parameters'])
        marxanWriter.writerow(['BLM ' + str(zonesMarxanParameterDict['blmValue'])])
        marxanWriter.writerow(['PROP  ' + str(zonesMarxanParameterDict['initialProp'])])
        marxanWriter.writerow(['RANDSEED -1'])
        marxanWriter.writerow(['NUMREPS ' + str(zonesMarxanParameterDict['numRun'])])
        marxanWriter.writerow(['AVAILABLEZONE  1']) # "The available zone is treated as an unprotected zone in Marxan Z."

        marxanWriter.writerow([])

        marxanWriter.writerow(['Annealing Parameters'])
        marxanWriter.writerow(['NUMITNS ' + str(zonesMarxanParameterDict['numIter'])])
        marxanWriter.writerow(['STARTTEMP -1'])
        marxanWriter.writerow(['COOLFAC  -1'])
        marxanWriter.writerow(['NUMTEMP 10000'])
        marxanWriter.writerow([])

        marxanWriter.writerow(['Cost Threshold'])
        marxanWriter.writerow(['COSTTHRESH  0'])
        marxanWriter.writerow(['THRESHPEN1  0'])
        marxanWriter.writerow(['THRESHPEN2  0'])
        marxanWriter.writerow([])

        marxanWriter.writerow(['Input Files'])
        marxanWriter.writerow(['INPUTDIR ' + setupObject.inputPath])
        marxanWriter.writerow(['PUNAME pu.dat'])
        marxanWriter.writerow(['FEATNAME feat.dat'])
        marxanWriter.writerow(['PUVSPRNAME puvspr2.dat'])
        marxanWriter.writerow(['ZONESNAME zones.dat'])
        marxanWriter.writerow(['COSTSNAME costs.dat'])
        marxanWriter.writerow(['ZONECOSTNAME zonecost.dat'])
        marxanWriter.writerow(['BOUNDNAME bound.dat'])
        if setupObject.zonesBoundFlag:
            marxanWriter.writerow(['ZONEBOUNDCOSTNAME zoneboundcost.dat'])
        marxanWriter.writerow(['PUZONENAME puzone.dat'])
        marxanWriter.writerow(['PULOCKNAME pulock.dat'])
        marxanWriter.writerow(['ZONETARGETNAME zonetarget.dat'])
        marxanWriter.writerow(['ZONECONTRIBNAME zonecontrib.dat'])

        marxanWriter.writerow([])

        marxanWriter.writerow(['Save Files'])
        marxanWriter.writerow(['SCENNAME ' + zonesMarxanParameterDict['outputName']])
        marxanWriter.writerow(['SAVERUN ' + extraOutputValue])
        marxanWriter.writerow(['SAVEBEST 3'])
        marxanWriter.writerow(['SAVESUMMARY 3'])
        marxanWriter.writerow(['SAVESCEN ' + extraOutputValue])
        marxanWriter.writerow(['SAVETARGMET 3'])
        marxanWriter.writerow(['SAVESUMSOLN 3'])

        marxanWriter.writerow(['SAVESOLUTIONSMATRIX 0'])
        marxanWriter.writerow(['SOLUTIONSMATRIXHEADERS 0'])
        marxanWriter.writerow(['SAVEPENALTY 0'])
        marxanWriter.writerow(['SAVELOG 3'])
        marxanWriter.writerow(['SAVEANNEALINGTRACE 0'])
        marxanWriter.writerow(['ANNEALINGTRACEROWS 0'])
        marxanWriter.writerow(['SAVEITIMPTRACE 0'])
        marxanWriter.writerow(['ITIMPTRACEROWS 0'])
        marxanWriter.writerow(['SAVEZONECONNECTIVITYSUM 0'])
        marxanWriter.writerow(['OUTPUTDIR ' + setupObject.outputPath])
        marxanWriter.writerow([])

        marxanWriter.writerow(['Program control.'])
        marxanWriter.writerow(['RUNMODE 1'])
        marxanWriter.writerow(['MISSLEVEL  ' + str(zonesMarxanParameterDict['missingProp'])])
        marxanWriter.writerow(['ITIMPTYPE 0'])
        marxanWriter.writerow(['VERBOSITY 3'])
        marxanWriter.writerow([])


def zonesMarxanUpdateSetupObject(ZonesMarxanDialog, setupObject, marxanParameterDict):
    setupObject.outputName = marxanParameterDict['outputName']
    setupObject.numIter = marxanParameterDict['numIter']
    setupObject.numRuns = marxanParameterDict['numRun']
    setupObject.blmValue = marxanParameterDict['blmValue']
    setupObject.boundFlag = ZonesMarxanDialog.boundCheckBox.isChecked()
    setupObject.extraOutputsFlag = ZonesMarxanDialog.extraCheckBox.isChecked()
    setupObject.zonesBoundFlag = ZonesMarxanDialog.boundZoneCheckBox.isChecked()
    setupObject.startProp = marxanParameterDict['initialProp']
    setupObject.targetProp = marxanParameterDict['missingProp']

    return setupObject


def makeZonesMarxanBatFile(setupObject):
    zonesMarxanFullName = setupObject.marxanPath
    zonesMarxanBatFileName = zonesMarxanFullName.replace('.exe', '.bat')
    with open(zonesMarxanBatFileName,'w', newline='') as batFile:
        batWriter = csv.writer(batFile)
        batWriter.writerow(['cd ' + os.path.dirname(zonesMarxanFullName)])
        batWriter.writerow(['\"' +zonesMarxanFullName + '\"'])

    return zonesMarxanBatFileName


def waitingForZonesMarxan(setupObject, outputName):
    marxanPathName = setupObject.outputPath + os.sep + outputName + '_best.csv'
    try:
        while os.path.isfile(marxanPathName) is False:
            time.sleep(2)
    except KeyboardInterrupt:
         pass


def addBestZonesMarxanOutputToPUShapefile(setupObject, bestZonesOutputFilePath, bestZonesFieldName):
    bestZonesDict = makeBestZonesDict(bestZonesOutputFilePath)
    puLayer = QgsVectorLayer(setupObject.puPath, "Planning units", "ogr")
    idFieldIndex = puLayer.fields().indexFromName("Unit_ID")

    bestZonesFieldIndex = puLayer.fields().indexFromName(bestZonesFieldName)
    provider = puLayer.dataProvider()
    if bestZonesFieldIndex == -1:
        provider.addAttributes([QgsField(bestZonesFieldName, QVariant.Int)])
        puLayer.updateFields()
    bestZonesFieldIndex = provider.fieldNameIndex(bestZonesFieldName)

    progressBar = makeProgressBar('Loading best output results')
    polyTotalCount = puLayer.featureCount()
    polyCount = 1

    puFeatures = puLayer.getFeatures()
    puLayer.startEditing()
    for puFeature in puFeatures:
        progressBar.setValue((polyCount/polyTotalCount) * 100)
        polyCount += 1

        puRow = puFeature.id()
        puAttributes = puFeature.attributes()
        puID = puAttributes[idFieldIndex]
        bestZone = bestZonesDict[puID]
        puLayer.changeAttributeValue(puRow, bestZonesFieldIndex, bestZone)
    puLayer.commitChanges()
    clearProgressBar()


def makeBestZonesDict(bestOutputFilePath):
    bestZonesDict = dict()
    with open(bestOutputFilePath, 'rt') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip the headers
        for row in reader:
            puID = int(float(row[0]))
            bestZone = int(float(row[1]))
            bestZonesDict[puID] = bestZone

    return bestZonesDict


def addSummedZonesMarxanOutputToPUShapefile(setupObject, summedOutputFilePath):
    summedScoreDict = makeZonesSummedScoresDict(summedOutputFilePath)

    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    provider = puLayer.dataProvider()
    idFieldIndex = provider.fieldNameIndex('Unit_ID')

    for zoneID in list(setupObject.zonesDict):
        zonesSummedFieldName = 'Z' + str(zoneID) + '_' + 'SFreq'
        summedFieldIndex = provider.fieldNameIndex(zonesSummedFieldName)
        if summedFieldIndex == -1:
            provider.addAttributes([QgsField(zonesSummedFieldName, QVariant.Int)])
            puLayer.updateFields()

    progressBar = makeProgressBar('Loading summed solution output results')
    polyTotalCount = puLayer.featureCount()
    polyCount = 1

    puFeatures = puLayer.getFeatures()
    puLayer.startEditing()
    for puFeature in puFeatures:
        progressBar.setValue((polyCount/polyTotalCount) * 100)
        polyCount += 1

        puRow = puFeature.id()
        puAttributes = puFeature.attributes()
        puID = puAttributes[idFieldIndex]
        for zoneID in list(setupObject.zonesDict):
            zonesSummedFieldName = 'Z' + str(zoneID) + '_' + 'SFreq'
            zoneSFScoreFieldIndex = provider.fieldNameIndex(zonesSummedFieldName)
            zoneNameText = setupObject.zonesDict[zoneID]
            sfScore = summedScoreDict[zoneNameText][puID]

            puLayer.changeAttributeValue(puRow, zoneSFScoreFieldIndex, sfScore)

    puLayer.commitChanges()
    clearProgressBar()


def makeZonesSummedScoresDict(summedOutputFile):
    zonesSummedScoreDict = dict()
    with open(summedOutputFile, 'rt') as f:
        zonesSFFileReader = csv.reader(f)
        zonesSFFileHeader = next(zonesSFFileReader)
        zonesSFFileZoneNameList = zonesSFFileHeader[2:]
        for row in zonesSFFileReader:
            puID = int(row[0])
            zonesSFFileZoneSFScoreList = row[2:]
            for aCol in range(0, len(zonesSFFileZoneNameList)):
                headerName = zonesSFFileZoneNameList[aCol]
                sfScore = int(zonesSFFileZoneSFScoreList[aCol])

                try:
                    aZoneSummedScoreDict = zonesSummedScoreDict[headerName]
                except KeyError:
                    aZoneSummedScoreDict = dict()
                aZoneSummedScoreDict[puID] = sfScore
                zonesSummedScoreDict[headerName] = aZoneSummedScoreDict

    return zonesSummedScoreDict

#
# def makeParameterValueList(calibrateRawParameterDict, exponentialBool):
#     parameterValueList = []
#     numAnalyses = float(calibrateRawParameterDict['numAnalysesText'])
#     origMinAnalyses = float(calibrateRawParameterDict['minAnalysesText'])
#     origMaxAnalyses = float(calibrateRawParameterDict['maxAnalysesText'])
#
#     if exponentialBool:
#         if origMinAnalyses == 0:
#             minAnalyses = 0.00000000000000000000000000000001
#         else:
#             minAnalyses = math.log(origMinAnalyses)
#         maxAnalyses = math.log(origMaxAnalyses)
#     else:
#         minAnalyses = origMinAnalyses
#         maxAnalyses = origMaxAnalyses
#
#     valIncrease = (maxAnalyses - minAnalyses) / (numAnalyses - 1)
#
#     for aValue in range(0, int(numAnalyses)):
#         parameterValue = float(minAnalyses) + (valIncrease * aValue)
#         if exponentialBool:
#             if origMinAnalyses == 0 and aValue == 0:
#                 parameterValue = 0
#             else:
#                 parameterValue = math.exp(parameterValue)
#         parameterValueList.append(parameterValue)
#
#     return parameterValueList
#
#
# def makeAnalysisResultsDict(setupObject, marxanParameterDict):
#     analysisDict = dict()
#     scoreList = list()
#     costList = list()
#     puCountList = list()
#     connectivityCostList = list()
#     penaltyList = list()
#     mpmList = list()
#
#     summaryTextPath = setupObject.outputPath + os.sep + marxanParameterDict['outputName'] + '_sum.txt'
#     if os.path.isfile(summaryTextPath):
#         with open(summaryTextPath, 'rt') as f:
#             summaryReader = csv.reader(f)
#             headerList = next(summaryReader)
#             for aRow in summaryReader:
#                 scoreValue = float(aRow[headerList.index('Score')])
#                 costValue = float(aRow[headerList.index('Cost')])
#                 puCountValue = int(aRow[headerList.index('Planning_Units')])
#                 connectivityCostValue = float(aRow[headerList.index('Connectivity')])
#                 penaltyValue = float(aRow[headerList.index('Penalty')])
#                 mpmValue = float(aRow[headerList.index('MPM')])
#
#                 scoreList.append(scoreValue)
#                 costList.append(costValue)
#                 puCountList.append(puCountValue)
#                 connectivityCostList.append(connectivityCostValue)
#                 penaltyList.append(penaltyValue)
#                 mpmList.append(mpmValue)
#
#         medianScore = statistics.median(scoreList)
#         medianCost = statistics.median(costList)
#         medianpuCount = statistics.median(puCountList)
#         medianConnectivity = statistics.median(connectivityCostList)
#         medianPenalty = statistics.median(penaltyList)
#         medianMPM = statistics.median(mpmList)
#
#         analysisDict['numIter'] = marxanParameterDict['numIter']
#         analysisDict['numRun'] = marxanParameterDict['numRun']
#         analysisDict['blmValue'] = marxanParameterDict['blmValue']
#         analysisDict['outputName'] = str(marxanParameterDict['outputName'])
#
#         analysisDict['medianScore'] = medianScore
#         analysisDict['medianCost'] = medianCost
#         analysisDict['medianpuCount'] = medianpuCount
#         analysisDict['medianConnectivity'] = medianConnectivity
#         analysisDict['medianPenalty'] = medianPenalty
#         analysisDict['medianMPM'] = medianMPM
#
#     else:
#         warningMessage('No files found', 'The Marxan summary file was not found and so this process will terminate.')
#
#     return analysisDict
#
#
# def makeCalibrateOutputFile(resultPath, calibrateResultsDict):
#     with open(resultPath,'w', newline='') as writerFile:
#         calibrateWriter = csv.writer(writerFile)
#         header1 = ['Analysis', 'Name', 'Iterations', 'Runs', 'BLM']
#         header2 = ['Med Portfolio Cost', 'Med Planning Unit cost', 'Med Boundary length', 'Med Feature Penalty cost', 'Med MPM', 'Med PU Count']
#         finalHeaderRow = header1 + header2
#         calibrateWriter.writerow(finalHeaderRow)
#
#         analysisNumberList = list(calibrateResultsDict.keys())
#         analysisNumberList.sort()
#         for aNumber in analysisNumberList:
#             analysisDict = calibrateResultsDict[aNumber]
#
#             numIter = analysisDict['numIter']
#             numRun = analysisDict['numRun']
#             blmValue = analysisDict['blmValue']
#             outputName = analysisDict['outputName']
#
#             medianScore = analysisDict['medianScore']
#             medianCost = analysisDict['medianCost']
#             medianpuCount = analysisDict['medianpuCount']
#             medianConnectivity = analysisDict['medianConnectivity']
#             medianPenalty = analysisDict['medianPenalty']
#             medianMPM = analysisDict['medianMPM']
#
#             rowList1 = [str(aNumber + 1), outputName, str(numIter), str(numRun), str(blmValue)]
#             rowList2 = [str(medianScore), str(medianCost), str(medianConnectivity), str(medianPenalty), str(medianMPM), str(medianpuCount)]
#             finalRowList = rowList1 + rowList2
#
#             calibrateWriter.writerow(finalRowList)