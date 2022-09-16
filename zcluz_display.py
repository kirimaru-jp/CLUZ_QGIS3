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


# def returnLowestUnusedFileNameNumber(dirPath, fileNameBase, extTypeText):
#     fileNameNumber = 1
#     while os.path.exists(dirPath + os.sep + fileNameBase + str(fileNameNumber) + extTypeText):
#         fileNameNumber += 1
#
#     return fileNameNumber
#
#
# def removeThenAddPULayer(setupObject, addLayerFudge): # This is a way of refreshing PU Layer so it shows newly added fields; addLayerFudge copes with QGIS not counting newly added layers
#     iface.mapCanvas().refreshAllLayers()
#     allLayers = iface.mapCanvas().layers()
#     puLayerPositionInTOC = -1
#     positionInTOC = 0
#     for aLayer in allLayers:
#         if aLayer.name() == 'Planning units':
#             puLayer = aLayer
#             QgsProject.instance().removeMapLayers([puLayer.id()])
#             iface.mapCanvas().refresh()
#             puLayerPositionInTOC = positionInTOC
#         positionInTOC += 1
#     if puLayerPositionInTOC > -1:
#         puLayerPositionInTOC += addLayerFudge
#         addPULayer(setupObject, puLayerPositionInTOC)
#
#
def addZonesPULayers(setupObject, legendPosition):
    allLayers = iface.mapCanvas().layers()
    layerNameList = list()
    for aLayer in allLayers:
        layerNameList.append(aLayer.name)

    root = QgsProject.instance().layerTreeRoot()
    for zoneID in list(setupObject.zonesDict)[::-1]:
        zonePULayerName = 'Z' + str(zoneID) + ' Planning units'
        statusField = 'Z' + str(zoneID) + '_Status'

        if not QgsProject.instance().mapLayersByName(zonePULayerName):
            puLayer = QgsVectorLayer(setupObject.puPath, zonePULayerName, 'ogr')
            categoryList = makeZonesPULayerLegendCategory()
            myRenderer = QgsCategorizedSymbolRenderer('', categoryList)
            myRenderer.setClassAttribute(statusField)
            puLayer.setRenderer(myRenderer)

            QgsProject.instance().addMapLayer(puLayer, False)
            root.insertLayer(legendPosition, puLayer)
            iface.setActiveLayer(puLayer)

            layerCRSText = puLayer.crs().authid()
            layerCRS = QgsCoordinateReferenceSystem(layerCRSText)
            iface.mapCanvas().setDestinationCrs(layerCRS)
            iface.mapCanvas().zoomToFeatureExtent(puLayer.extent())
            iface.mapCanvas().refresh()


def checkZonesPULayerPresent(setupObject):
    allLayers = iface.mapCanvas().layers()
    puLayerPresentBool = True
    zonePUNameList = list()
    for aZoneNum in range(0, len(setupObject.zonesDict)):
        zonePULayerName = 'Z' + str(aZoneNum + 1) + ' Planning units'
        zonePUNameList.append(zonePULayerName)

    zonesLayerCount = 0
    for aLayer in allLayers:
        if aLayer.name() in zonePUNameList:
            zonesLayerCount += 1
            zonePUNameList.remove(aLayer.name())

    if zonesLayerCount != 3:
        puLayerPresentBool = False

    return puLayerPresentBool


# def updatePULayerToShowChangesByShiftingExtent():# This is a way of refreshing PU Layer so it displays changes in values
#     canvasExtent = iface.mapCanvas().extent()
#     extMinX, extMaxX = canvasExtent.xMinimum(), canvasExtent.xMaximum()
#     extMinY, extMaxY = canvasExtent.yMinimum(), canvasExtent.yMaximum()
#     xShift = (extMaxX - extMinX) * 0.005
#     shiftMinX, shiftMaxX = extMinX + xShift, extMaxX + xShift
#     iface.mapCanvas().setExtent(QgsRectangle(shiftMinX, extMinY, shiftMaxX, extMaxY))
#     iface.mapCanvas().refresh()
#
#
def makeZonesPULayerLegendCategory():
    categoryList = []
    #Set category 1
    cat1Value = 'Locked'
    cat1Label = 'Locked'
    cat1Symbol = QgsFillSymbol.createSimple({'style': 'solid', 'color': '#006633', 'color_border': '#006633'})
    myCat1 = QgsRendererCategory(cat1Value, cat1Symbol, cat1Label)
    categoryList.append(myCat1)

    #Set category 2
    cat2Value = 'Excluded'
    cat2Label = 'Excluded'
    cat2Symbol = QgsFillSymbol.createSimple({'style': 'solid', 'color': '#730083', 'color_border': '#730083'})
    myCat2 = QgsRendererCategory(cat2Value, cat2Symbol, cat2Label)
    categoryList.append(myCat2)

    #Set category 3
    cat3Value = 'Available'
    cat3Label = 'Available'
    cat3Symbol = QgsFillSymbol.createSimple({'style': 'solid', 'color': '#99ff99', 'color_border': '#99ff99'})
    myCat3 = QgsRendererCategory(cat3Value, cat3Symbol, cat3Label)
    categoryList.append(myCat3)

    #Set category 4
    cat4Value = 'Earmarked'
    cat4Label = 'Earmarked'
    cat4Symbol = QgsFillSymbol.createSimple({'style': 'solid', 'color': '#33cc33', 'color_border': '#33cc33'})
    myCat4 = QgsRendererCategory(cat4Value, cat4Symbol, cat4Label)
    categoryList.append(myCat4)

    return categoryList


def displayZonesBestOutput(setupObject, zonesMarxanParameterDict):
    bestLayerName = 'Best (' + zonesMarxanParameterDict['outputName'] + ')'
    bestZonesLayer = QgsVectorLayer(setupObject.puPath, bestLayerName, 'ogr')

    categoryList = list()
    for zoneID in list(setupObject.zonesDict):
        catValue = zoneID
        catLabel = 'Zone ' + str(zoneID)
        catSymbol = returnZoneCatSymbol(zoneID)
        myCat = QgsRendererCategory(catValue, catSymbol, catLabel)
        categoryList.append(myCat)

    myRenderer = QgsCategorizedSymbolRenderer('', categoryList)
    myRenderer.setClassAttribute('Best')
    bestZonesLayer.setRenderer(myRenderer)
    QgsProject.instance().addMapLayer(bestZonesLayer)

    iface.mapCanvas().refresh()


def returnZoneCatSymbol(zoneID):
    colourDict = {1: '#fdbf6f', 2: '#1f78b4', 3: '#b2df8a', 4: '#33a02c', 5: '#fb9a99', 6: '#e31a1c', 7: '#a6cee3', 8: '#ff7f00', 9: '#cab2d6',10: '#6a3d9a', 11: '#ffff99', 12: '#b15928'}
    if zoneID < 13:
        catColour = colourDict[zoneID]
    else:
        catColour = '#e6e6e6'
    catSymbol = QgsFillSymbol.createSimple({'style': 'solid', 'color':catColour, 'color_border': catColour})

    return catSymbol


def reloadZonesPULayer(setupObject):
    root = QgsProject.instance().layerTreeRoot()

    layers = QgsProject.instance().mapLayers()
    nameList = list()
    for QGISFullname, layer in layers.items():
        layerName = str(layer.name())
        nameList.append(layerName)
        if str(layerName.endswith('Planning units')):
            QgsProject.instance().removeMapLayer(layer.id())

    for zoneID in list(setupObject.zonesDict):
        puLayerPosition = nameList.index('Z' + str(zoneID) + ' Planning units')
        puLayer = QgsVectorLayer(setupObject.puPath, 'Z' + str(zoneID) + ' Planning units', 'ogr')
        categoryList = makeZonesPULayerLegendCategory()
        myRenderer = QgsCategorizedSymbolRenderer('', categoryList)
        myRenderer.setClassAttribute('Status')
        puLayer.setRenderer(myRenderer)

        QgsProject.instance().addMapLayer(puLayer, False)
        root.insertLayer(puLayerPosition, puLayer)


def removePreviousZonesMarxanLayers():
    layers = QgsProject.instance().mapLayers()
    for QGISFullname, layer in layers.items():
        layerName = layer.name()
        if str(layerName)[0:6] == 'Best (' or str(layerName)[0:10] == 'SF_Score (':
            QgsProject.instance().removeMapLayer(layer.id())


def displayZonesSFLayer(setupObject, zonesMarxanParameterDict):
    runNumber = zonesMarxanParameterDict['numRun']
    colourList = ['#C5C2C5', '#CDCEB4', '#DEDEA3', '#EEE894', '#FFFA8B', '#FFE273', '#FFAA52', '#FF8541', '#FF6D31', '#FF0000']

    for zoneID in list(setupObject.zonesDict)[::-1]:
        zoneLayerName = str(zoneID) + ' ' + setupObject.zonesDict[zoneID] + ' SF' + ' (' + zonesMarxanParameterDict['outputName'] + ')'
        graduatedLayer = QgsVectorLayer(setupObject.puPath, zoneLayerName, 'ogr')
        fieldName = 'Z' + str(zoneID) + '_' + 'SFreq'

        rangeList = list()
        minValue = 0
        incValue = float(runNumber) / 10


        for aValue in range(0, 10):
            maxValue = minValue + incValue
            if aValue == 9:
                maxValue = runNumber
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