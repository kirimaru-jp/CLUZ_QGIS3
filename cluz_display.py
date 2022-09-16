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

from qgis.core import QgsProject, QgsVectorLayer, QgsCategorizedSymbolRenderer, QgsFillSymbol, QgsRendererCategory
from qgis.core import QgsRendererRange, QgsGraduatedSymbolRenderer, QgsCoordinateReferenceSystem, QgsRectangle
from qgis.utils import iface

import os


def makePULayerActive(setupObject):
    try:
        puLayer = QgsProject.instance().mapLayersByName('Planning units')[0]
        iface.setActiveLayer(puLayer)
    except IndexError:
        pass


def returnLowestUnusedFileNameNumber(dirPath, fileNameBase, extTypeText):
    fileNameNumber = 1
    while os.path.exists(dirPath + os.sep + fileNameBase + str(fileNameNumber) + extTypeText):
        fileNameNumber += 1

    return fileNameNumber


def removeThenAddPULayer(setupObject, addLayerFudge): # This is a way of refreshing PU Layer so it shows newly added fields; addLayerFudge copes with QGIS not counting newly added layers
    iface.mapCanvas().refreshAllLayers()
    allLayers = iface.mapCanvas().layers()
    puLayerPositionInTOC = -1
    positionInTOC = 0
    for aLayer in allLayers:
        if aLayer.name() == 'Planning units':
            puLayer = aLayer
            QgsProject.instance().removeMapLayers([puLayer.id()])
            iface.mapCanvas().refresh()
            puLayerPositionInTOC = positionInTOC
        positionInTOC += 1
    if puLayerPositionInTOC > -1:
        puLayerPositionInTOC += addLayerFudge
        addPULayer(setupObject, puLayerPositionInTOC)


def addPULayer(setupObject, legendPosition):
    root = QgsProject.instance().layerTreeRoot()
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    categoryList = makePULayerLegendCategory()
    myRenderer = QgsCategorizedSymbolRenderer('', categoryList)
    myRenderer.setClassAttribute('Status')
    puLayer.setRenderer(myRenderer)

    QgsProject.instance().addMapLayer(puLayer, False)
    root.insertLayer(legendPosition, puLayer)

    iface.setActiveLayer(puLayer)
    layerCRSText = puLayer.crs().authid()
    layerCRS = QgsCoordinateReferenceSystem(layerCRSText)
    iface.mapCanvas().setDestinationCrs(layerCRS)
    iface.mapCanvas().zoomToFeatureExtent(puLayer.extent())
    iface.mapCanvas().refresh()


def updatePULayerToShowChangesByShiftingExtent():# This is a way of refreshing PU Layer so it displays changes in values
    canvasExtent = iface.mapCanvas().extent()
    extMinX, extMaxX = canvasExtent.xMinimum(), canvasExtent.xMaximum()
    extMinY, extMaxY = canvasExtent.yMinimum(), canvasExtent.yMaximum()
    xShift = (extMaxX - extMinX) * 0.0001
    shiftMinX, shiftMaxX = extMinX + xShift, extMaxX + xShift
    iface.mapCanvas().setExtent(QgsRectangle(shiftMinX, extMinY, shiftMaxX, extMaxY))
    iface.mapCanvas().refresh()


def makePULayerLegendCategory():
    categoryList = list()

    #Set category 1
    cat1Value = 'Available'
    cat1Label = 'Available'
    cat1Symbol = QgsFillSymbol.createSimple({'style': 'solid', 'color': '#99ff99', 'color_border': '#99ff99'})
    myCat1 = QgsRendererCategory(cat1Value, cat1Symbol, cat1Label)
    categoryList.append(myCat1)

    #Set category 2
    cat2Value = 'Earmarked'
    cat2Label = 'Earmarked'
    cat2Symbol = QgsFillSymbol.createSimple({'style': 'solid', 'color': '#33cc33', 'color_border': '#33cc33'})
    myCat2 = QgsRendererCategory(cat2Value, cat2Symbol, cat2Label)
    categoryList.append(myCat2)

    #Set category 3
    cat3Value = 'Conserved'
    cat3Label = 'Conserved'
    cat3Symbol = QgsFillSymbol.createSimple({'style': 'solid', 'color': '#006633', 'color_border': '#006633'})
    myCat3 = QgsRendererCategory(cat3Value, cat3Symbol, cat3Label)
    categoryList.append(myCat3)

    #Set category 4
    cat4Value = 'Excluded'
    cat4Label = 'Excluded'
    cat4Symbol = QgsFillSymbol.createSimple({'style': 'solid', 'color': '#730083', 'color_border': '#730083'})
    myCat4 = QgsRendererCategory(cat4Value, cat4Symbol, cat4Label)
    categoryList.append(myCat4)

    return categoryList


def displayDistributionMaps(setupObject, distShapeFilePathName, abundValuesDict, legendType, selectedFeatIDList):
    colourDict = makeColourDict()
    colourKey = 1

    for featID in selectedFeatIDList:
        rangeList = list()
        colourList = colourDict[colourKey]
        colourKey += 1
        if colourKey > len(list(colourDict.keys())):
            colourKey = 1

        aDistLayerName = setupObject.targetDict[int(featID)][0]
        aDistLayer = QgsVectorLayer(distShapeFilePathName, aDistLayerName, 'ogr')
        aDistLayerFieldName = 'F_' + str(featID)
        aFeatAbundValueTupleList = abundValuesDict[featID]
        if legendType == 'equal_interval':
            legendValCatList = calcEqualIntervalLegendClasses(setupObject, aFeatAbundValueTupleList)
        if legendType == 'equal_area':
            legendValCatList = calcEqualAreaLegendClasses(setupObject, aFeatAbundValueTupleList)
        for aValue in range(0, 5):
            minValue = legendValCatList[aValue]
            maxValue = legendValCatList[aValue + 1]
            myColour = colourList[aValue]
            mySymbol = QgsFillSymbol.createSimple({'style': 'solid', 'color': myColour, 'color_border': myColour})
            theRange = QgsRendererRange(minValue, maxValue, mySymbol, str(minValue) + ' - ' + str(maxValue))
            rangeList.insert(0, theRange)

        myRenderer = QgsGraduatedSymbolRenderer('', rangeList)
        myRenderer.setMode(QgsGraduatedSymbolRenderer.EqualInterval)
        myRenderer.setClassAttribute(aDistLayerFieldName)
        aDistLayer.setRenderer(myRenderer)
        aDistLayer.setOpacity(0.6)
        QgsProject.instance().addMapLayer(aDistLayer)

    iface.mapCanvas().refresh()


def makeColourDict():
    colourDict = dict()
    colourDict[1] = ['#FEE1E1','#FE8787','#FF0000','#AE0000','#630000']
    colourDict[2] = ['#FEEEE1','#FEBC87','#FE8828','#D15D00','#863C00']
    colourDict[3] = ['#FEFAE1','#FEEC87','#FEDD28','#D1B100','#867100']
    colourDict[4] = ['#F6FEE1','#DCFE87','#C1FE28','#95D100','#608600']
    colourDict[5] = ['#E1FEFE','#87FEFE','#28FEFE','#00D6D6','#009A9A']
    colourDict[6] = ['#E6FEE6','#88FE87','#00FF00','#02A900','#015400']
    colourDict[7] = ['#E1FEF5','#87FEDA','#28FEBD','#00D192','#00865D']
    colourDict[8] = ['#E1E1FE','#8789FE','#282CFE','#0004D1','#000286']
    colourDict[9] = ['#FAD7FE','#F587FE','#DD00EF','#A500B3','#5C0063']
    colourDict[10] = ['#FEE1F6','#FE87DE','#FE28C4','#D10098','#860062']
    colourDict[11] = ['#F5F5F5','#B9B9B9','#7D7D7D','#414141','#000000']
    colourDict[12] = ['#FFEABE','#E0B986','#BC865D','#8B5445','#5A2D2D']

    return colourDict


def calcEqualIntervalLegendClasses(setupObject, aFeatAbundValueTupleList):
    decPrec = setupObject.decimalPlaces
    abundList = list()
    for aTuple in aFeatAbundValueTupleList:
        abundValue = aTuple[0]
        if abundValue > 0:
            abundList.append(abundValue)

    if len(abundList) > 0:
        minValue = min(abundList)
        minValue = round(float(minValue), decPrec)
        maxValue = max(abundList)
        maxValue = round(float(maxValue), decPrec)
    else:
        minValue = 0
        maxValue = 0

    incValue = (maxValue - minValue) / 5
    no2Value = round(minValue + (1 * incValue), decPrec)
    no3Value = round(minValue + (2 * incValue), decPrec)
    no4Value = round(minValue + (3 * incValue), decPrec)
    no5Value = round(minValue + (4 * incValue), decPrec)

    legendValCatList = [minValue, no2Value, no3Value, no4Value, no5Value, maxValue]

    return legendValCatList


def calcEqualAreaLegendClasses(setupObject, aFeatAbundValueTupleList):
    decPrec = setupObject.decimalPlaces
    totalArea, abundList = makeAbundValuesList(aFeatAbundValueTupleList)
    minValue, maxValue = calcEqualAreaLegendClassesMinMax(abundList)
    minValue = round(float(minValue), decPrec)
    maxValue = round(float(maxValue), decPrec)

    abundTupleList = makeAbundTupleList(aFeatAbundValueTupleList, abundList)
    combinedAreaDict = makeCombinedAreaDict(abundTupleList)

    abundValueList = list(combinedAreaDict.keys())
    abundValueList.sort()
    runningTotalArea = 0
    legendValue1 = 'blank'
    legendValue2 = 'blank'
    legendValue3 = 'blank'
    legendValue4 = 'blank'
    for aValue in abundValueList:
        areaAmount = combinedAreaDict[aValue]
        areaAmount = round(float(areaAmount), decPrec)
        runningTotalArea += areaAmount
        runningProp = runningTotalArea / totalArea
        if legendValue1 == 'blank' and runningProp >= 0.2:
            legendValue1 = aValue
        if legendValue2 == 'blank' and runningProp >= 0.4:
            legendValue2 = aValue
        if legendValue3 == 'blank' and runningProp >= 0.6:
            legendValue3 = aValue
        if legendValue4 == 'blank' and runningProp >= 0.8:
            legendValue4 = aValue

    legendValCatList = [minValue, legendValue1, legendValue2, legendValue3, legendValue4, maxValue]

    return legendValCatList


def calcEqualAreaLegendClassesMinMax(abundList):
    if len(abundList) > 0:
        minValue = abundList[0]
        maxValue = abundList[-1]
    else:
        minValue = 0
        maxValue = 0

    return minValue, maxValue


def makeAbundValuesList(aFeatAbundValueTupleList):
    abundList = list()
    totalArea = 0
    for aTuple in aFeatAbundValueTupleList:
        abundValue = aTuple[0]
        if abundValue > 0:
            abundList.append(aTuple[0])
            totalArea += aTuple[1]
    abundList.sort()

    return totalArea, abundList


def makeAbundTupleList(aFeatAbundValueTupleList, abundList):
    abundTupleList = list()
    while len(abundList) > 0:
        abundValue = abundList.pop(0)
        for aTuple in aFeatAbundValueTupleList:
            if aTuple[0] == abundValue:
                abundTupleList.append(aTuple)
                aFeatAbundValueTupleList.remove(aTuple)

    return abundTupleList


def makeCombinedAreaDict(abundTupleList):
    combinedAreaDict = dict()
    for bTuple in abundTupleList:
        (bAmount, bArea) = bTuple
        try:
            runningArea = combinedAreaDict[bAmount]
        except KeyError:
            runningArea = 0
        runningArea += bArea
        combinedAreaDict[bAmount] = runningArea

    return combinedAreaDict


def displayBestOutput(setupObject, bestFieldName, bestShapefileName):
    bestLayer = QgsVectorLayer(setupObject.puPath, bestShapefileName, 'ogr')

    categoryList = list()
    #Set category 1
    cat1Value = 'Selected'
    cat1Label = 'Selected'
    cat1Symbol = QgsFillSymbol.createSimple({'style': 'solid', 'color': '#ff00ff', 'color_border': '#ff00ff'})
    myCat1 = QgsRendererCategory(cat1Value, cat1Symbol, cat1Label)
    categoryList.append(myCat1)

    myRenderer = QgsCategorizedSymbolRenderer('', categoryList)
    myRenderer.setClassAttribute(bestFieldName)
    bestLayer.setRenderer(myRenderer)
    QgsProject.instance().addMapLayer(bestLayer)

    iface.mapCanvas().refresh()


def reloadPULayer(setupObject):
    root = QgsProject.instance().layerTreeRoot()

    layers = QgsProject.instance().mapLayers()
    nameList = list()
    for QGISFullname, layer in layers.items():
        layerName = str(layer.name())
        nameList.append(layerName)
        if layerName == 'Planning units':
            QgsProject.instance().removeMapLayer(layer.id())

    puLayerPosition = nameList.index('Planning units')
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    categoryList = makePULayerLegendCategory()
    myRenderer = QgsCategorizedSymbolRenderer('', categoryList)
    myRenderer.setClassAttribute('Status')
    puLayer.setRenderer(myRenderer)

    QgsProject.instance().addMapLayer(puLayer, False)
    root.insertLayer(puLayerPosition, puLayer)


def removePreviousMarxanLayers():
    layers = QgsProject.instance().mapLayers()
    for QGISFullname, layer in layers.items():
        layerName = layer.name()
        if str(layerName)[0:6] == 'Best (' or str(layerName)[0:10] == 'SF_Score (':
            QgsProject.instance().removeMapLayer(layer.id())


def removePreviousMinPatchLayers():
    layers = QgsProject.instance().mapLayers()
    for QGISFullname, layer in layers.items():
        layerName = layer.name()
        if str(layerName)[0:9] == 'MP Best (' or str(layerName)[0:13] == 'MP SF_Score (':
            QgsProject.instance().removeMapLayer(layer.id())


def displayGraduatedLayer(setupObject, fieldName, layerName, legendCode):
    colourDict = dict()
    colourDict[1] = ['#C5C2C5', '#CDCEB4', '#DEDEA3', '#EEE894', '#FFFA8B', '#FFE273', '#FFAA52', '#FF8541', '#FF6D31', '#FF0000']
    colourDict[2] = ['#FFFFCC', '#E3F3B5', '#C8E89E', '#A9DB8E', '#88CD80', '#68BE70', '#48AE60', '#2B9C50', '#158243', '#006837']

    colourList = colourDict[legendCode]

    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    graduatedLayer = QgsVectorLayer(setupObject.puPath, layerName, 'ogr')
    provider = puLayer.dataProvider()

    puFeatures = puLayer.getFeatures()
    graduatedFieldOrder = provider.fieldNameIndex(fieldName)

    maxCountScore = 0 #This will be used to set highest value in legend
    for puFeature in puFeatures:
        puAttributes = puFeature.attributes()
        puCountScore = puAttributes[graduatedFieldOrder]
        if puCountScore > maxCountScore:
            maxCountScore = puCountScore

    rangeList = list()
    minValue = 0
    incValue = float(maxCountScore) / 10


    for aValue in range(0, 10):
        maxValue = minValue + incValue
        if aValue == 9:
            maxValue = maxCountScore
        myColour = colourList[aValue]
        mySymbol = QgsFillSymbol.createSimple({'style': 'solid', 'color': myColour, 'color_border': myColour})
        minValueDisplay = round(minValue, setupObject.decimalPlaces)
        maxValueDisplay = round(minValue + incValue, setupObject.decimalPlaces)
        theRange = QgsRendererRange(minValueDisplay, maxValueDisplay, mySymbol, str(minValueDisplay) + ' - ' + str(maxValueDisplay))
        minValue = maxValue
        rangeList.insert(0, theRange)

    myRenderer = QgsGraduatedSymbolRenderer('', rangeList)
    myRenderer.setMode(QgsGraduatedSymbolRenderer.EqualInterval)
    myRenderer.setClassAttribute(fieldName)
    graduatedLayer.setRenderer(myRenderer)
    QgsProject.instance().addMapLayer(graduatedLayer)

    iface.mapCanvas().refresh()


def displayIrrepResults(setupObject, fieldName):
    colourList = ['#FFFFBF', '#F4FAA7', '#EAF792', '#DAF57A', '#CAF266', '#B6F051', '#A0ED3B', '#86EB28', '#6DE815', '#4CE600']
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    irrepLayer = QgsVectorLayer(setupObject.puPath, fieldName, 'ogr')
    provider = puLayer.dataProvider()

    puFeatures = puLayer.getFeatures()
    graduatedFieldOrder = provider.fieldNameIndex(fieldName)

    maxCountScore = 0 #This will be used to set highest value in legend
    for puFeature in puFeatures:
        puAttributes = puFeature.attributes()
        puCountScore = puAttributes[graduatedFieldOrder]
        if puCountScore > maxCountScore:
            maxCountScore = puCountScore

    rangeList = list()
    minValue = 0
    incValue = float(maxCountScore) / 10


    for aValue in range(0, 10):
        maxValue = minValue + incValue
        if aValue == 9:
            maxValue = maxCountScore
        myColour = colourList[aValue]
        mySymbol = QgsFillSymbol.createSimple({'style': 'solid', 'color': myColour, 'color_border': myColour})
        theRange = QgsRendererRange(minValue, maxValue, mySymbol, str(minValue) + ' - ' + str(maxValue))
        minValue = maxValue
        rangeList.insert(0, theRange)


    myRenderer = QgsGraduatedSymbolRenderer('', rangeList)
    myRenderer.setMode(QgsGraduatedSymbolRenderer.EqualInterval)
    myRenderer.setClassAttribute(fieldName)
    irrepLayer.setRenderer(myRenderer)
    QgsProject.instance().addMapLayer(irrepLayer)

    iface.mapCanvas().refresh()