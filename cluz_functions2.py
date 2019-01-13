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

from qgis.core import QgsVectorLayer
from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsField, QgsApplication, QgsProcessingFeedback


import processing
from processing.core.Processing import Processing
Processing.initialize()

import os
import csv

from .cluz_messages import *
from .cluz_make_file_dicts import *


def makeVecAddAbundDict(setupObject, layerList, idFieldName, convFactor):
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')

    layerNumber = 1
    for aLayer in layerList:
        layerGeomType = aLayer.geometryType()
        infoMessage('Processing files:', 'intersecting layer ' + str(layerNumber) + '...')
        outputLayer = makeIntersectionOutputLayer(puLayer, aLayer)

        if layerGeomType == 1:
            addAbundDict, addFeatIDSet, attributeFeatureError = makeAddAbundDictFromLineVecFile(setupObject, outputLayer, idFieldName, convFactor)
        elif layerGeomType == 2:
            addAbundDict, addFeatIDSet, attributeFeatureError = makeAddAbundDictFromPolyVecFile(setupObject, outputLayer, idFieldName, convFactor)
            
        if attributeFeatureError:
            warningMessage('Layer warning: ', 'layer ' + str(aLayer.name()) + ' contains at least one feature that produces fragments with no spatial characteristics when intersected with the planning units.')

    addFeatIDList = list(addFeatIDSet)
    addFeatIDList.sort()

    return addAbundDict, addFeatIDList


def makeIntersectionOutputLayer(puLayer, aLayer):
    feedback = QgsProcessingFeedback()
    intersectParamsDict = { 'INPUT' : aLayer, 'INPUT_FIELDS' : [], 'OUTPUT' : 'memory:', 'OVERLAY' : puLayer, 'OVERLAY_FIELDS' : [] }
    intersectResults = processing.run('native:intersection', intersectParamsDict, feedback=feedback)
    outputLayer = intersectResults['OUTPUT']

    return outputLayer


def makeAddAbundDictFromLineVecFile(setupObject, outputLayer, idFieldName, convFactor):
    addAbundDict = dict()
    addFeatIDSet = set()
    decPrec = setupObject.decimalPlaces

    outputIDField = outputLayer.fields().indexFromName('Unit_ID')
    outputFeatIDField = outputLayer.fields().indexFromName(idFieldName)
    outputFeatures = outputLayer.getFeatures()

    attributeFeatureError = False
    for outputFeature in outputFeatures:
        outputAttributes = outputFeature.attributes()
        unitID = outputAttributes[outputIDField]
        featID = outputAttributes[outputFeatIDField]
        addFeatIDSet.add(featID)

        try:
            finalShapeAmount = calcFeatLineLengthInPU(outputFeature, convFactor, decPrec)
        except AttributeError:
            finalShapeAmount = -1
      
        if finalShapeAmount > 0:
            try:
                puAddAbundDict = addAbundDict[unitID]
            except KeyError:
                puAddAbundDict = {}
            try:
                addAmount = puAddAbundDict[featID]
            except KeyError:
                addAmount = 0
            addAmount += finalShapeAmount
            puAddAbundDict[featID] = addAmount
            addAbundDict[unitID] = puAddAbundDict
        else:
            attributeFeatureError = True

    return addAbundDict, addFeatIDSet, attributeFeatureError


def makeAddAbundDictFromPolyVecFile(setupObject, outputLayer, idFieldName, convFactor):
    addAbundDict = dict()
    addFeatIDSet = set()
    decPrec = setupObject.decimalPlaces

    outputIDField = outputLayer.fields().indexFromName('Unit_ID')
    outputFeatIDField = outputLayer.fields().indexFromName(idFieldName)
    outputFeatures = outputLayer.getFeatures()

    attributeFeatureError = False
    for outputFeature in outputFeatures:
        outputAttributes = outputFeature.attributes()
        unitID = outputAttributes[outputIDField]
        featID = outputAttributes[outputFeatIDField]
        addFeatIDSet.add(featID)

        try:
            finalShapeAmount = calcFeatPolygonAreaInPU(outputFeature, convFactor, decPrec)
        except AttributeError:
            finalShapeAmount = -1
      
        if finalShapeAmount > 0:
            try:
                puAddAbundDict = addAbundDict[unitID]
            except KeyError:
                puAddAbundDict = {}
            try:
                addAmount = puAddAbundDict[featID]
            except KeyError:
                addAmount = 0
            addAmount += finalShapeAmount
            puAddAbundDict[featID] = addAmount
            addAbundDict[unitID] = puAddAbundDict
        else:
            attributeFeatureError = True

    return addAbundDict, addFeatIDSet, attributeFeatureError


def calcFeatLineLengthInPU(outputFeature, convFactor, decPrec):
    outputGeom = outputFeature.geometry()
    intersectShapeAmount = outputGeom.length()
    shapeAmount = intersectShapeAmount / convFactor
    finalShapeAmount = round(shapeAmount, decPrec)

    return finalShapeAmount


def calcFeatPolygonAreaInPU(outputFeature, convFactor, decPrec):
    outputGeom = outputFeature.geometry()
    intersectShapeAmount = outputGeom.area()
    shapeAmount = intersectShapeAmount / convFactor
    finalShapeAmount = round(shapeAmount, decPrec)

    return finalShapeAmount


####################### Import csv file ###############################

def makeCsvAddAbundDict(ConvertCsvDialog, setupObject):
    csvFilePath = ConvertCsvDialog.csvFileLineEdit.text()
    convFactor = float(ConvertCsvDialog.convLineEdit.text())
    rawUnitIDFieldName = ConvertCsvDialog.idfieldComboBox.currentText()
    addAbundDict = dict()
    featIDList = list()
    continueBool = True
    unitIDFieldName = str(rawUnitIDFieldName)# Removes u from beginning of string

    csvFile = open(csvFilePath, 'rt')
    abundDataReader = csv.reader(csvFile)
    fileHeaderList = next(abundDataReader)
    fileHeaderList.remove(unitIDFieldName)
    featHeaderDict = dict()
    for aFeatHeader in fileHeaderList:
        featID = removePrefixMakeIDValue(aFeatHeader)
        featHeaderDict[aFeatHeader] = featID
        featIDList.append(featID)

    if len(set(featIDList).intersection(set(setupObject.targetDict.keys()))) != 0:
        warningMessage('Duplicate features', 'The feature ID values in the table duplicate some of those in the abundance table. This process will terminate.')
        continueBool = False
    if featIDList.count('') != 0:
        warningMessage('Missing ID code', 'One of the fields containing abundance data in the specified table does not contain any numerical characters and so does not specify the feature ID. This process will terminate.')
        continueBool = False

    if continueBool:
        addAbundDict = makeAddAbundDictFromCSVFile(csvFilePath, featHeaderDict, fileHeaderList, unitIDFieldName, convFactor)

    return addAbundDict, featIDList, continueBool


def makeAddAbundDictFromCSVFile(csvFilePath, featHeaderDict, fileHeaderList, unitIDFieldName, convFactor):
    addAbundDict = dict()
    with open(csvFilePath, 'rt') as f:
        dataDict = csv.DictReader(f)
        for aDict in dataDict:
            puID = int(aDict[unitIDFieldName])
            for aHeader in fileHeaderList:
                origAbundValue = float(aDict[aHeader])
                abundValue = origAbundValue / convFactor
                featID = featHeaderDict[aHeader]
                if abundValue > 0:
                    try:
                        puAddAbundDict = addAbundDict[puID]
                    except KeyError:
                        puAddAbundDict = dict()
                    try:
                        addAmount = puAddAbundDict[featID]
                    except KeyError:
                        addAmount = 0
                    addAmount += abundValue
                    puAddAbundDict[featID] = addAmount
                    addAbundDict[puID] = puAddAbundDict

    return addAbundDict


def addAbundDictToAbundPUKeyDict(setupObject, addAbundDict):
    abundPUKeyDict = setupObject.abundPUKeyDict
    for puID in addAbundDict:
        puAddAbundDict = addAbundDict[puID]
        try:
            puAbundDict = setupObject.abundPUKeyDict[puID]
        except KeyError:
            puAbundDict = dict()
        for aFeat in puAddAbundDict:
            aAmount = puAddAbundDict[aFeat]
            puAbundDict[aFeat] = aAmount

        abundPUKeyDict[puID] = puAbundDict

    return abundPUKeyDict


def addFeaturesFromAddAbundDictToPuvspr2File(setupObject, addAbundDict):
    for puID in addAbundDict:
        puAddAbundDict = addAbundDict[puID]
        try:
            puAbundDict = setupObject.abundPUKeyDict[puID]
        except KeyError:
            puAbundDict = dict()
        for featID in puAddAbundDict:
            puAbundDict[featID] = puAddAbundDict[featID]
        setupObject.abundPUKeyDict[puID] = puAbundDict

    makePuvspr2DatFile(setupObject)


def createTargetPuvspr2SporderFiles(createDialog):
    inputPath = createDialog.inputLineEdit.text()
    targetPath = createDialog.targetLineEdit.text()

    with open(targetPath,'w', newline='') as targetFile:
        targetWriter = csv.writer(targetFile)
        targetWriter.writerow(['Id', 'Name', 'Type', 'Target', 'Spf', 'Conserved', 'Total', 'PC_target'])

    with open(inputPath + os.sep + 'puvspr2.dat','w', newline='') as puvspr2File:
        puvspr2Writer = csv.writer(puvspr2File)
        puvspr2Writer.writerow(['Id', 'Name', 'Type', 'Target', 'Spf', 'Conserved', 'Total', 'PC_target'])

    with open(inputPath + os.sep + 'sporder.dat','w', newline='') as sporderFile:
        sporderWriter = csv.writer(sporderFile)
        sporderWriter.writerow(['Id', 'Name', 'Type', 'Target', 'Spf', 'Conserved', 'Total', 'PC_target'])


def createPULayer(createDialog):
    costAsAreaBool = createDialog.equalCheckBox.isChecked()
    convFactor = float(createDialog.convLineEdit.text())
    shapePath = createDialog.puLineEdit.text()
    
    createTargetPuvspr2SporderFiles(createDialog)

    puLayer = QgsVectorLayer(shapePath, 'Shapefile', 'ogr')
    puProvider = puLayer.dataProvider()
    puProvider.addAttributes([QgsField('Unit_ID', QVariant.Int)])
    puProvider.addAttributes([QgsField('Area', QVariant.Double, 'real', 10, 2)])
    puProvider.addAttributes([QgsField('Cost', QVariant.Double, 'real', 10, 2)])
    puProvider.addAttributes([QgsField('Status', QVariant.String)])
    puLayer.updateFields()

    unitIDFieldIndex = puProvider.fieldNameIndex('Unit_ID')
    puAreaFieldIndex = puProvider.fieldNameIndex('Area')
    puCostFieldIndex = puProvider.fieldNameIndex('Cost')
    statusFieldIndex = puProvider.fieldNameIndex('Status')

    progressBar = makeProgressBar('Processing shapefile')
    polyCount = 1
    polyTotalCount = puLayer.featureCount()

    puLayer.startEditing()
    puFeatures = puLayer.getFeatures()
    for puFeature in puFeatures:
        progressBar.setValue((polyCount/polyTotalCount) * 100)
        polyCount += 1

        puRow = puFeature.id()
        unitIDValue = puRow + 1
        puGeom = puFeature.geometry()
        puArea = puGeom.area()
        finalPUArea = puArea / convFactor
        if costAsAreaBool:
            puCost = finalPUArea
        else:
            puCost = 0

        puLayer.changeAttributeValue(puRow, unitIDFieldIndex, unitIDValue, True)
        puLayer.changeAttributeValue(puRow, puCostFieldIndex, puCost, True)
        puLayer.changeAttributeValue(puRow, puAreaFieldIndex, finalPUArea, True)
        puLayer.changeAttributeValue(puRow, statusFieldIndex, 'Available', True)

    clearProgressBar()
    puLayer.commitChanges()