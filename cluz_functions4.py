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

from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsFields, QgsVectorLayer, QgsVectorLayer, QgsVectorFileWriter, QgsWkbTypes, QgsFeature, QgsField, QgsSpatialIndex

import os
import statistics

from .cluz_functions5 import makeNewPUVertexSet, calcVertexLength, convertPolygonPointList2VertexSet, createBoundDatFile, returnRunningLengthValue
from .cluz_mpsetup import makeBoundMatrixDict
from .cluz_make_file_dicts import makeAbundancePUKeyDict, writeBoundDatFile
from .cluz_mpfunctions import makeMPPatchDict
from .cluz_messages import clearProgressBar, emptyPolgyonPUIDSetErrorMessage, makeProgressBar, infoMessage
from .cluz_mpoutputs import makePatchAreaLists


#### Display distributions of conservation features ###
def createDistributionMapShapefile(setupObject, distShapeFilePathName, selectedFeatIDList):
    distFileName = os.path.basename(distShapeFilePathName)
    makeBaseDistributionMapShapefile(setupObject, distShapeFilePathName)

    distrLayer = QgsVectorLayer(distShapeFilePathName, distFileName, "ogr")
    addPUIDValuesToBaseDistributionMapShapefile(distrLayer, selectedFeatIDList)
    abundValuesDict = dict()
    for aValue in selectedFeatIDList:
        abundValuesDict[aValue] = list()

    distrFeatures = distrLayer.getFeatures()
    distrIDFieldIndex = distrLayer.fields().indexFromName('Unit_ID')
    distrLayer.startEditing()

    progressBar = makeProgressBar('Displaying conservation feature data')
    polyTotalCount = distrLayer.featureCount()
    polyCount = 1
    for distrFeature in distrFeatures:
        distrPURow = distrFeature.id()
        distrGeom = distrFeature.geometry()
        distrArea = distrGeom.area()
        distrAttributes = distrFeature.attributes()
        distrID = distrAttributes[distrIDFieldIndex]

        progressBar.setValue((polyCount/polyTotalCount) * 100)
        polyCount += 1

        for featID in selectedFeatIDList:
            featFieldIndex = distrLayer.fields().indexFromName('F_' + str(featID))
            try:
                puAbundDict = setupObject.abundPUKeyDict[distrID]
                abundValue = puAbundDict[featID]
            except KeyError:
                abundValue = 0
            aFeatAbundValueTupleList = abundValuesDict[featID]
            aFeatAbundValueTupleList.append((abundValue, distrArea))
            abundValuesDict[featID] = aFeatAbundValueTupleList

            distrLayer.changeAttributeValue(distrPURow, featFieldIndex, abundValue)

    distrLayer.commitChanges()
    clearProgressBar()
    return abundValuesDict


def makeBaseDistributionMapShapefile(setupObject, distShapeFilePathName):
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    puIDField = puLayer.fields().indexFromName('Unit_ID')
    newFields = QgsFields()
    newFields.append(QgsField('Unit_ID', QVariant.Int))
    writer = QgsVectorFileWriter(distShapeFilePathName, "System", newFields, QgsWkbTypes.MultiPolygon, puLayer.dataProvider().crs(), "ESRI Shapefile")


    puFeatures = puLayer.getFeatures()
    #Make distribution shapefile copying PU polygons and ID field
    for puFeature in puFeatures:
        puGeom = puFeature.geometry()
        puAttributes = puFeature.attributes()
        puID = puAttributes[puIDField]
        featAttribList = [puID]

        distFeat = QgsFeature()
        distFeat.setGeometry(puGeom)
        distFeat.setAttributes(featAttribList)
        writer.addFeature(distFeat)

    del writer


def addPUIDValuesToBaseDistributionMapShapefile(distrLayer, selectedFeatIDList):
    distrProvider = distrLayer.dataProvider()
    for aFeatID in selectedFeatIDList:
        distrProvider.addAttributes([QgsField('F_' + str(aFeatID), QVariant.Double, "double", 12, 3)])
        distrLayer.updateFields()


#### Identify features in selected units ###

def returnStringAmountPerStatus(setupObject, selectedPUDetailsDict, statusValue, featID):
    decPrec = setupObject.decimalPlaces
    try:
        featAmount = selectedPUDetailsDict[statusValue][featID]
        featAmountRound = round(float(featAmount), decPrec)
        featAmountString = format(featAmountRound, '.' + str(decPrec) + 'f')

    except KeyError:
        featAmountString = '0'

    return featAmountString


def returnStringShortfall(setupObject, featID):
    decPrec = setupObject.decimalPlaces
    targetAmount = setupObject.targetDict[featID][3]
    conAmount = setupObject.targetDict[featID][4]
    if conAmount >= targetAmount:
        stringShortfall = 'Target met'
    else:
        shortValue = targetAmount - conAmount
        shortValueRound = round(float(shortValue), decPrec)
        stringShortfall = format(shortValueRound, '.' + str(decPrec) + 'f')

    return stringShortfall


#### Calculate richness scores ###

def makeFeatIDSetFromFeatTypeSet(setupObject, selectedTypeSet):
    selectedFeatIDSet = set()
    for featID in setupObject.targetDict:
        featType = setupObject.targetDict[featID][1]
        if featType in selectedTypeSet:
            selectedFeatIDSet.add(featID)

    return selectedFeatIDSet


def produceCountField(setupObject, countFieldName, selectedFeatIDSet):
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    provider = puLayer.dataProvider()
    idFieldOrder = puLayer.fields().indexFromName('Unit_ID')

    provider.addAttributes([QgsField(countFieldName, QVariant.Int)])
    puLayer.updateFields()
    countFieldOrder = puLayer.fields().indexFromName(countFieldName)

    progressBar = makeProgressBar('Producing the feature count field')
    polyTotalCount = puLayer.featureCount()
    polyCount = 1

    countDict = dict()
    for puID in setupObject.abundPUKeyDict:
        progressBar.setValue((polyCount/polyTotalCount) * 50)
        polyCount += 1
        featCount = 0
        puFeatDict = setupObject.abundPUKeyDict[puID]
        for featID in puFeatDict:
            featAmount = puFeatDict[featID]
            if featAmount > 0 and featID in selectedFeatIDSet:
                featCount += 1
        countDict[puID] = featCount

    polyCount = 1
    puFeatures = puLayer.getFeatures()
    puLayer.startEditing()
    for puFeature in puFeatures:
        progressBar.setValue((50 + polyCount/polyTotalCount) * 50)
        polyCount += 1

        puRow = puFeature.id()
        puAttributes = puFeature.attributes()
        puID = puAttributes[idFieldOrder]
        try:
            countValue = countDict[puID]
        except KeyError:
            countValue = 0
        puLayer.changeAttributeValue(puRow, countFieldOrder, countValue, True)

    clearProgressBar()
    puLayer.commitChanges()


def produceRestrictedRangeField(setupObject, rangeFieldName, selectedFeatIDSet):
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    provider = puLayer.dataProvider()
    idFieldOrder = puLayer.fields().indexFromName('Unit_ID')

    puIDSet = set()
    puFeatures = puLayer.getFeatures()
    for puFeature in puFeatures:
        puAttributes = puFeature.attributes()
        puID = puAttributes[idFieldOrder]
        puIDSet.add(puID)

    scoreDict, highScorePUID = makeRestrictedRangeDict(setupObject, selectedFeatIDSet, puIDSet)

    puLayer.startEditing()
    provider.addAttributes([QgsField(rangeFieldName, QVariant.Double)])
    puLayer.updateFields()
    rangeFieldOrder = puLayer.fields().indexFromName(rangeFieldName)

    progressBar = makeProgressBar('Producing restricted range richness field')
    polyCount = 1
    polyTotalCount = puLayer.featureCount()

    puFeatures = puLayer.getFeatures()
    puLayer.startEditing()
    for puFeature in puFeatures:
        progressBar.setValue((polyCount/polyTotalCount) * 100)
        polyCount += 1

        puRow = puFeature.id()
        puAttributes = puFeature.attributes()
        puID = puAttributes[idFieldOrder]
        try:
            rangeValue = scoreDict[puID]
        except KeyError:
            rangeValue = 0
        puLayer.changeAttributeValue(puRow, rangeFieldOrder, rangeValue, True)

    clearProgressBar()
    puLayer.commitChanges()


def makeRestrictedRangeDict(setupObject, selectedFeatIDSet, puIDSet):
    scoreDict = dict()
    highScoreValue = -1
    highScorePUID = -1

    for puID in puIDSet:
        rangeScore = 0
        try:
            puFeatDict = setupObject.abundPUKeyDict[puID]
        except KeyError:
            puFeatDict = dict()
        puFeatList = puFeatDict.keys()
        for featID in puFeatList:
            if featID in selectedFeatIDSet:
                featAmount = puFeatDict[featID]
                featTotal = setupObject.targetDict[featID][5]
                featScore = featAmount / featTotal
                rangeScore += featScore
        scoreDict[puID] = rangeScore
        if rangeScore > highScoreValue:
            highScoreValue = rangeScore
            highScorePUID = puID

    return scoreDict, highScorePUID


####Make portfolio details

def makePortfolioPUDetailsDict():
    portfolioPUDetailsDict = dict()
    portfolioPUDetailsDict['statusDetailsBool'] = False
    portfolioPUDetailsDict['spatialDetailsBool'] = False
    portfolioPUDetailsDict['sfDetailsBool'] = False
    portfolioPUDetailsDict['patchFeatDetailsBool'] = False
    portfolioPUDetailsDict['peDetailsBool'] = False

    return portfolioPUDetailsDict


def addStatusDetailsToPortfolioDict(setupObject, portfolioPUDetailsDict):
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    puFeatures = puLayer.getFeatures()
    idFieldIndex = puLayer.fields().indexFromName('Unit_ID')
    statusFieldIndex = puLayer.fields().indexFromName('Status')
    puDict, areaDict = makePUDictFromCLUZPortfolio(setupObject)

    runningStatusDict = {'Available': [0, 0, 0], 'Conserved': [0, 0, 0], 'Earmarked': [0, 0, 0], 'Excluded': [0, 0, 0]} #status, area, cost, PU count
    for puFeature in puFeatures:
        puAttributes = puFeature.attributes()
        puID = puAttributes[idFieldIndex]
        puStatusText = str(puAttributes[statusFieldIndex])
        runningStatusDict = updatePortfolioStatusDict(runningStatusDict, puDict, areaDict, puID, puStatusText)

    portfolioPUDetailsDict['statusDetailsBool'] = True
    portfolioPUDetailsDict['statusDataDict'] = makeStatusDataDict(runningStatusDict)

    return portfolioPUDetailsDict


def makePUDictFromCLUZPortfolio(setupObject):
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    puFeatures = puLayer.getFeatures()
    idFieldIndex = puLayer.fields().indexFromName('Unit_ID')
    areaFieldIndex = puLayer.fields().indexFromName('Area')
    costFieldIndex = puLayer.fields().indexFromName('Cost')
    statusFieldIndex = puLayer.fields().indexFromName('Status')

    puDict = dict()
    puStatusDict = {'Available': 0, 'Conserved': 2, 'Earmarked': 2, 'Excluded': 3}

    areaDict = dict()

    for puFeature in puFeatures:
        puAttributes = puFeature.attributes()
        puID = puAttributes[idFieldIndex]
        puArea = puAttributes[areaFieldIndex]
        puCost = puAttributes[costFieldIndex]
        puStatusText = str(puAttributes[statusFieldIndex])
        puStatus = puStatusDict[puStatusText]

        puDict[puID] = [puCost, puStatus]
        areaDict[puID] = puArea

    return puDict, areaDict


def updatePortfolioStatusDict(portfolioStatusDict, puDict, areaDict, puID, puStatusText):
    puArea = areaDict[puID]
    puCost = puDict[puID][0]
    puList = portfolioStatusDict[puStatusText]
    [runningArea, runningCost, runningPUCount] = puList
    puList = [runningArea + puArea, runningCost + puCost, runningPUCount + 1]
    portfolioStatusDict[puStatusText] = puList

    return portfolioStatusDict


def makeStatusDataDict(runningStatusDict):
    statusDataDict = dict()
    [availableArea, availableCost, availablePUCount] = runningStatusDict['Available']
    [conservedArea, conservedCost, conservedPUCount] = runningStatusDict['Conserved']
    [earmarkedArea, earmarkedCost, earmarkedPUCount] = runningStatusDict['Earmarked']
    [excludedArea, excludedCost, excludedPUCount] = runningStatusDict['Excluded']

    regionArea = availableArea + conservedArea + earmarkedArea + excludedArea
    regionCost = availableCost + conservedCost + earmarkedCost + excludedCost
    regionPUCount = availablePUCount + conservedPUCount + earmarkedPUCount + excludedPUCount

    portfolioArea = conservedArea + earmarkedArea
    portfolioCost = conservedCost + earmarkedCost
    portfolioPUCount = conservedPUCount + earmarkedPUCount

    statusDataDict['Region'] = [regionArea, regionCost, regionPUCount]
    statusDataDict['Portfolio'] = [portfolioArea, portfolioCost, portfolioPUCount]
    statusDataDict['Available'] = runningStatusDict['Available']
    statusDataDict['Conserved'] = runningStatusDict['Conserved']
    statusDataDict['Earmarked'] = runningStatusDict['Earmarked']
    statusDataDict['Excluded'] = runningStatusDict['Excluded']

    return statusDataDict


def addSpatialDetailsToPortfolioDict(setupObject, portfolioPUDetailsDict):
    puDict, patchDict, dummyZoneDict = makePatchDictBasedOnDummyZoneFile(setupObject)
    spatialDataDict = makeSpatialDataDict(setupObject, puDict, patchDict, dummyZoneDict)
    portfolioPUDetailsDict['spatialDetailsBool'] = True
    portfolioPUDetailsDict['spatialDataDict'] = spatialDataDict

    return portfolioPUDetailsDict


def makePatchDictBasedOnDummyZoneFile(setupObject):
    puDict, areaDict = makePUDictFromCLUZPortfolio(setupObject)
    minpatchDataDict = {'areaDictionary': areaDict}
    boundMatrixDict = checkMakeBoundDatFile(setupObject, puDict)
    minpatchDataDict['boundaryMatrixDictionary'] = boundMatrixDict
    dummyZoneDict = makeDummyZoneDict(puDict)
    minpatchDataDict['zoneDictionary'] = dummyZoneDict
    patchDict = makeMPPatchDict(puDict, minpatchDataDict)

    return puDict, patchDict, dummyZoneDict


def makeDummyZoneDict(puDict):
    dummyZoneDict = {}
    for puID in puDict:
        dummyZoneDict[puID] = [1, 0, 0]

    return dummyZoneDict


def makeSpatialDataDict(setupObject, puDict, patchDict, dummyZoneDict):
    spatialDataDict = dict()
    allAreaList, validAreaList = makePatchAreaLists(patchDict, dummyZoneDict) #validAreaList is irrelevant
    allAreaList.sort()
    if len(allAreaList) > 0:
        spatialDataDict['patchCount'] = len(allAreaList)
        spatialDataDict['patchMedian'] = statistics.median(allAreaList)
        spatialDataDict['patchSmallest'] = allAreaList[0]
        spatialDataDict['patchLargest'] = allAreaList[-1]
    else:
        spatialDataDict['patchCount'] = 0
        spatialDataDict['patchMedian'] = 0
        spatialDataDict['patchSmallest'] = 0
        spatialDataDict['patchLargest'] = 0

    boundMatrixDict = checkMakeBoundDatFile(setupObject, puDict)
    spatialDataDict['totalBoundLength'] = calcTotalBoundLength(boundMatrixDict, puDict)

    return spatialDataDict

def checkMakeBoundDatFile(setupObject, puDict):
    boundDatFilePath = setupObject.inputPath + os.sep + 'bound.dat'
    if os.path.exists(boundDatFilePath):
        boundMatrixDict = makeBoundMatrixDict(boundDatFilePath, puDict)
    else:
        infoMessage('Creating Bound.dat file', 'CLUZ uses the Marxan bound.dat file to calculate the patch statistics. This did not exist and so has been created.')
        extEdgeBool = False
        createBoundDatFile(setupObject, extEdgeBool)
        boundMatrixDict = makeBoundMatrixDict(boundDatFilePath, puDict)

    return boundMatrixDict


def makeSpatialIndex_SpatialDicts(puLayer):
    unitIDFieldIndex = puLayer.dataProvider().indexFromName('Unit_ID')
    puPolygonDict = dict()
    puIDGeomDict = dict()
    spatialIndex = QgsSpatialIndex()
    for aPolygon in puLayer.getFeatures():
        puPolygonDict[aPolygon.id()] = aPolygon
        puIDGeomDict[aPolygon.attributes()[unitIDFieldIndex]] = aPolygon.geometry()
        spatialIndex.insertFeature(aPolygon)

    return spatialIndex, puPolygonDict, puIDGeomDict


def calcTotalBoundLength(boundaryMatrixDict, puDict):
    totalBoundLength = 0

    for id1Value in boundaryMatrixDict:
        puBoundDict = boundaryMatrixDict[id1Value]
        for id2Value in puBoundDict:
            if id2Value >= id1Value:
                boundValue = puBoundDict[id2Value]
                conCount = 0
                id1StatusValue = puDict[id1Value][1]
                id2StatusValue = puDict[id2Value][1]

                if id1StatusValue == 1 or id1StatusValue == 2:
                    conCount += 1
                if id2StatusValue == 1 or id2StatusValue == 2:
                    conCount += 1
                if conCount == 1:
                    totalBoundLength += boundValue
                #Allow for external edges
                if conCount == 2 and id1Value == id2Value:
                    totalBoundLength += boundValue

    return totalBoundLength


def makePatchFeatDataDict(setupObject, patchDict):
    if setupObject.setupStatus == 'files_checked':
        if setupObject.abundPUKeyDict == 'blank':
            setupObject.abundPUKeyDict = makeAbundancePUKeyDict(setupObject)

    patchFeatDataDict = dict()
    for patchID in patchDict:
        patchFeatPresenceSet = set()
        patchPUIDList = patchDict[patchID][2]
        for puID in patchPUIDList:
            try:
                puIDFeatSet = set(setupObject.abundPUKeyDict[puID].keys())
                patchFeatPresenceSet = patchFeatPresenceSet.union(puIDFeatSet)
            except KeyError:
                pass
        for featID in patchFeatPresenceSet:
            try:
                featCount = patchFeatDataDict[featID]
            except KeyError:
                featCount = 0
            featCount += 1
            patchFeatDataDict[featID] = featCount

    return patchFeatDataDict


def makeFullSFValueList(setupObject, sfFieldName):
    sfValueList = list()
    puLayer = QgsVectorLayer(setupObject.puPath, "Planning units", "ogr")
    puFeatures = puLayer.getFeatures()
    sfFieldIndex = puLayer.fields().indexFromName(sfFieldName)
    statusFieldIndex = puLayer.fields().indexFromName('Status')

    for puFeature in puFeatures:
        puAttributes = puFeature.attributes()
        puSFValue = puAttributes[sfFieldIndex]
        if puSFValue >= 0:
            puStatusText = puAttributes[statusFieldIndex]
            if puStatusText == 'Available' or puStatusText == 'Earmarked':
                sfValueList.append(puSFValue)

    return sfValueList


def makeSFDetailsToPortfolioDict(portfolioPUDetailsDict, sfValueList, sfRunsValue):
    sfDataDict = dict()
    sfValueList.sort()

    zeroSFCount, greaterThanZeroCount = countSFValuesZeroesGreaterThanZero(sfValueList)

    sfDataDict[0] = ['Equals 0', str(zeroSFCount)]
    sfDataDict[1] = ['Greater than 0', str(greaterThanZeroCount)]
    sfDataDict[2] = ['---', '---']

    sfDataDictKey = 3
    sfQuartileTupleList = makeSFQuartileTupleList(sfRunsValue)
    for (rangeName, minRangeValue, maxRangeValue) in sfQuartileTupleList:
        sfRangeValueList = makeSFRangeValueList(sfValueList, minRangeValue, maxRangeValue)
        finalRangeName = rangeName + ': ' + str(minRangeValue) + " - " + str(maxRangeValue)
        sfDataDict[sfDataDictKey] = [finalRangeName, str(len(sfRangeValueList))]
        sfDataDictKey += 1
    sfDataDict[7] = ['---', '---']

    top5pcValue = int(sfRunsValue * 0.95)
    top5pcValueName = "Top 5% of SF values" + ': ' + str(top5pcValue) + " - " + str(sfRunsValue)
    sfDataDict[8] = [top5pcValueName, str(len(makeSFRangeValueList(sfValueList, top5pcValue, sfRunsValue)))]
    sfDataDict[9] = ['Max SF: ' + str(sfRunsValue), str(sfValueList.count(sfRunsValue))]

    portfolioPUDetailsDict["sfDetailsBool"] = True
    portfolioPUDetailsDict["sfDataDict"] = sfDataDict

    return portfolioPUDetailsDict


def countSFValuesZeroesGreaterThanZero(fullSFValueList):
    zeroSFCount, greaterThanZeroCount = 0, 0
    for aValue in fullSFValueList:
        if aValue == 0:
            zeroSFCount += 1
        elif aValue > 0:
            greaterThanZeroCount += 1

    return zeroSFCount, greaterThanZeroCount


def makeSFRangeValueList(fullSFValueList, minRange, maxRange):
    sfValueList = list()
    for aValue in fullSFValueList:
        if aValue >= minRange and aValue <= maxRange:
            sfValueList.append(aValue)

    return sfValueList


def makeSFQuartileTupleList(sfRunsValue):
    sfQuartileTupleList = list()
    sfQuartileTupleList.append(("1st Quartile", 1, int(sfRunsValue * 0.25)))
    sfQuartileTupleList.append(("2nd Quartile", int(sfRunsValue * 0.25) + 1, int(sfRunsValue * 0.5)))
    sfQuartileTupleList.append(("3rd Quartile", int(sfRunsValue * 0.5) + 1, int(sfRunsValue * 0.75)))
    sfQuartileTupleList.append(("4th Quartile", int(sfRunsValue * 0.75) + 1, sfRunsValue))

    return sfQuartileTupleList