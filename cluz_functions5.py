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


from .cluz_messages import clearProgressBar, emptyPolgyonPUIDSetErrorMessage, makeProgressBar, warningMessage, criticalMessage
from .cluz_make_file_dicts import writeBoundDatFile


############################ Produce Marxan input files ############################

def createSpecDatFile(setupObject):
    specDatPathName = setupObject.inputPath + os.sep + 'spec.dat'
    with open(specDatPathName,'w', newline='') as out_file:
        specDatWriter = csv.writer(out_file)
        specDatWriter.writerow(['id', 'name', 'target', 'spf', 'type'])
    
        targetDict = setupObject.targetDict
        featList = list(targetDict.keys())
        featList.sort()

        progressBar = makeProgressBar('Making a new spec.dat file')
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
            featType = featList[1]
            specDatWriter.writerow([aFeat, featName, featTarget, featSpf, featType])
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


def createPuDatFile(setupObject):
    decPrec = setupObject.decimalPlaces
    puDatPathName = setupObject.inputPath + os.sep + 'pu.dat'

    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    puFeatures = puLayer.getFeatures()
    puIDField = puLayer.fields().indexFromName('Unit_ID')
    puCostField = puLayer.fields().indexFromName('Cost')
    puStatusField = puLayer.fields().indexFromName('Status')

    progressBar = makeProgressBar('Making a new pu.dat file')
    polyCount = 1
    polyTotalCount = puLayer.featureCount()

    with open(puDatPathName,'w', newline='') as out_file:
        puDatWriter = csv.writer(out_file)
        puDatWriter.writerow(['id', 'cost', 'status', 'xloc', 'yloc'])
        puStatusDict = {'Available': 0, 'Earmarked': 2, 'Conserved': 2, 'Excluded': 3}

        for puFeature in puFeatures:
            progressBar.setValue((polyCount/polyTotalCount) * 100)
            polyCount += 1
            puDatRowList = makePUDatRowList(puFeature, puStatusDict, puIDField, puCostField, puStatusField, decPrec)
            puDatWriter.writerow(puDatRowList)
    clearProgressBar()


def makePUDatRowList(puFeature, puStatusDict, puIDField, puCostField, puStatusField, decPrec):
    puAttributes = puFeature.attributes()
    puID = puAttributes[puIDField]
    puCost = puAttributes[puCostField]
    puStatus = puAttributes[puStatusField]
    puStatusCode = puStatusDict[puStatus]

    puCentroid = puFeature.geometry().centroid()
    rawXCoord = puCentroid.asPoint().x()
    xCoord = round(float(rawXCoord), decPrec)
    xCoord = format(xCoord, "." + str(decPrec) + "f")

    rawYCoord = puCentroid.asPoint().y()
    yCoord = round(float(rawYCoord), decPrec)
    yCoord = format(yCoord, "." + str(decPrec) + "f")

    puDatRowList = [puID, puCost, puStatusCode, xCoord, yCoord]

    return puDatRowList


def createBoundDatFile(setupObject, extEdgeBool):
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    puIDFieldIndex = puLayer.fields().indexFromName('Unit_ID')
    puIDGeomDict = makePUIDGeomDict(puLayer, puIDFieldIndex)
    vertexList, emptyPolgyonPUIDSet = makeVertexList(puIDGeomDict)
    vertexList.sort()
    boundResultsDict = makeBoundResultDict(vertexList)
    if len(emptyPolgyonPUIDSet) > 0:
        emptyPolgyonPUIDSetErrorMessage(emptyPolgyonPUIDSet)

    writeBoundDatFile(setupObject, boundResultsDict, extEdgeBool)


def makePUIDGeomDict(puLayer, puIDFieldIndex):
    puIDGeomDict = dict()

    progressBar = makeProgressBar('Processing planning unit shapefile spatial data')
    polyCount = 1
    polyTotalCount = puLayer.featureCount()

    for aPolygon in puLayer.getFeatures():
        progressBar.setValue((polyCount/polyTotalCount) * 100)
        polyCount += 1
        puIDGeomDict[aPolygon.attributes()[puIDFieldIndex]] = aPolygon.geometry()
    clearProgressBar()

    return puIDGeomDict


def makeVertexList(puIDGeomDict):
    vertexList = list()

    progressBar = makeProgressBar('Extracting the vertex data from the planning unit shapefile')
    progressCount = 1
    numPUs = len(puIDGeomDict)

    emptyPolgyonPUIDSet = set()
    for puID in puIDGeomDict:
        progressBar.setValue((progressCount/numPUs) * 100)
        progressCount += 1

        puGeom = puIDGeomDict[puID]
        puVertexSet = makeNewPUVertexSet(puGeom)
        if len(puVertexSet) == 0:
            emptyPolgyonPUIDSet.add(puID)
        else:
            for aVertex in puVertexSet:
                vertexList.append((aVertex, puID))
    clearProgressBar()

    return vertexList, emptyPolgyonPUIDSet


def makeBoundResultDict(vertexList):
    boundResultsDict = dict()
    rowNum = 0
    listLength = len(vertexList) - 1

    progressBar = makeProgressBar('Extracting the vertex data from the planning unit shapefile')
    totRowNum = len(vertexList)

    while rowNum < listLength:
        progressBar.setValue((rowNum/totRowNum) * 100)

        (vertexA, puIDA) = vertexList[rowNum]
        (vertexB, puIDB) = vertexList[rowNum + 1]
        if vertexA != vertexB:
            rowNum += 1
        else:
            puDictKey = (puIDA, puIDB)
            boundResultsDict[puDictKey] = returnRunningLengthValue(boundResultsDict, vertexA, puDictKey)
            if puIDA == puIDB:
                rowNum += 1
            else:
                rowNum += 2
    clearProgressBar()

    return boundResultsDict


def returnRunningLengthValue(boundResultsDict, aVertex, puDictKey):
    vertexLength = calcVertexLength(aVertex)
    try:
        runningLengthValue = boundResultsDict[puDictKey]
        runningLengthValue += vertexLength
    except KeyError:
        runningLengthValue = vertexLength

    return runningLengthValue


def makeNewPUVertexSet(puGeom):
    if puGeom.isMultipart():
        polygonList = puGeom.asMultiPolygon()[0] #
    else:
        polygonList = list()
        polygonList.append(puGeom.asPolygon())

    aPolyPointList = list()
    for aPolygon in polygonList:
        polyXYList = list()
        for aQgsPointXY in aPolygon:
            polyXYList.append((aQgsPointXY.x(), aQgsPointXY.y())) #THIS FALLS OVER WHEN PU FILE HAS TOPOLOGY ERRORS
        aPolyPointList.append(polyXYList)

    puVertexSet = convertPolygonPointList2VertexSet(aPolyPointList)

    return puVertexSet


def calcVertexLength(aVertex):
    (x1, y1, x2, y2) = aVertex
    xLength = x2 - x1
    yLength = y2 - y1
    vertexLength = math.sqrt(xLength**2 + yLength**2)

    return vertexLength


def convertPolygonPointList2VertexSet(polyPointList): #This deals with multi polygon planning units
    vertexSet = set()
    for aPolygonPointList in polyPointList:
        listLength = len(aPolygonPointList)
        for aNumber in range(0, listLength - 1):
            x1 = aPolygonPointList[aNumber][0]
            y1 = aPolygonPointList[aNumber][1]
            x2 = aPolygonPointList[aNumber + 1][0]
            y2 = aPolygonPointList[aNumber + 1][1]
            if x1 > x2:
                finalX1 = x2
                finalX2 = x1
            else:
                finalX1 = x1
                finalX2 = x2
            if y1 > y2:
                finalY1 = y2
                finalY2 = y1
            else:
                finalY1 = y1
                finalY2 = y2
            vecTuple = (finalX1, finalY1, finalX2, finalY2)
            vertexSet.add(vecTuple)

    return vertexSet


########################### Marxan dialog ###########################

def returnOutputName(setupObject):
    oldOutputName = setupObject.outputName
    outputPath = setupObject.outputPath
    oldOutputBestName = outputPath + os.sep + oldOutputName + '_best.txt'

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
        newName = outputPath + os.sep + oldOutputNameStem + str(nameSuffix) + '_best.txt'
        while os.path.isfile(newName):
            nameSuffix += 1
            newName = outputPath + os.sep + oldOutputNameStem + str(nameSuffix) + '_best.txt'

        outputName = oldOutputNameStem + str(nameSuffix)
    else:
        outputName = oldOutputName

    return outputName


def checkNumIterParaDict(numIter):
    checkBool = True
    try:
        int(numIter)
        if int(numIter) < 10000:
            warningMessage('Input error', 'The number of iterations must be higher than 10000 because it must be be higher than the NUMTEMP value used in Marxan (see the Marxan manual for more details).')
            checkBool = False
    except ValueError:
        warningMessage('Input error', 'The number of iterations must be an integer')
        checkBool = False

    return checkBool


def checkNumRunsParaDict(numRun, checkBool):
    try:
        int(numRun)
        if int(numRun) < 1:
            warningMessage('Input error', 'The number of runs must be 1 or a larger whole number')
            checkBool = False
    except ValueError:
        warningMessage('Input error', 'The number of runs must be an integer.')
        checkBool = False

    return checkBool


def checkBlmValueParaDict(blmValue, checkBool):
    try:
        float(blmValue)
        if float(blmValue) < 0:
            warningMessage('Input error', 'The boundary length modifier must be a non-negative number.')
            checkBool = False
    except ValueError:
        warningMessage('Input error', 'The boundary length modifier must be a non-negative number.')
        checkBool = False

    return checkBool


def checkMissingPropValueParaDict(missingProp, checkBool):
    try:
        float(missingProp)
        if float(missingProp) < 0 or float(missingProp) > 1:
            checkBool = False
            warningMessage('Input error', 'The species proportion value must be a number between 0 and 1.')
    except ValueError:
        checkBool = False
        warningMessage('Input error', 'The species proportion value must be a number between 0 and 1.')

    return checkBool


def checkInitialPropValueParaDict(initialProp, checkBool):
    try:
        float(initialProp)
        if float(initialProp) < 0 or float(initialProp) > 1:
            checkBool = False
            warningMessage('Input error', 'The proportion of planning units randomly included at the beginning of each run must be a number between 0 and 1.')
    except ValueError:
        checkBool = False
        warningMessage('Input error', 'The proportion of planning units randomly included at the beginning of each run must be a number between 0 and 1.')

    return checkBool


def checkNumParallelAnalysesValueParaDict(numRunString, numParallelAnalyses, checkBool):
    try:
        if int(numRunString) < numParallelAnalyses:
            checkBool = False
            warningMessage('Input error', 'The number of parallel analyses must be less than the specified number of runs.')
    except ValueError:
        pass

    return checkBool


def checkPermissionToUseMarxanFolderParaDict(marxanParameterDict, marxanInputValuesBool):
    marxanPathText = marxanParameterDict['marxanPath']
    marxanFolder = os.path.dirname(marxanPathText)
    marxanInputPath = marxanFolder + os.sep + 'input.dat'
    try:
        with open(marxanInputPath,'w', newline='') as marxanFile:
            marxanWriter = csv.writer(marxanFile)
    except PermissionError:
        criticalMessage('Permission problem', 'You do not have permission to save files in the specified Marxan folder. CLUZ needs this to create input.dat and .bat files in the Marxan folder. Please move Marxan to a folder where you do have permission to save files.')
        marxanInputValuesBool = False

    return marxanInputValuesBool


def makeMarxanInputFile(setupObject, marxanParameterDict):
    if marxanParameterDict['extraOutputsBool']:
        extraOutputValue = '2'
    else:
        extraOutputValue = '0'
    if os.path.isfile(marxanParameterDict['marxanPath']):
        writeMarxanInputFile(setupObject, marxanParameterDict, extraOutputValue)


def writeMarxanInputFile(setupObject, marxanParameterDict, extraOutputValue):
    with open(marxanParameterDict['marxanSetupPath'],'w', newline='') as marxanFile:
        marxanWriter = csv.writer(marxanFile)

        header1 = 'Input file for Marxan program, written by Ian Ball, Hugh Possingham and Matt Watts.'
        header2 = 'This file was generated using CLUZ, written by Bob Smith'
        marxanWriter.writerow([header1])
        marxanWriter.writerow([header2])
        marxanWriter.writerow([])

        marxanWriter.writerow(['General Parameters'])
        marxanWriter.writerow(['VERSION 0.1'])
        marxanWriter.writerow(['BLM ' + str(marxanParameterDict['blmValue'])])
        marxanWriter.writerow(['PROP  ' + str(marxanParameterDict['initialProp'])])
        marxanWriter.writerow(['RANDSEED -1'])
        marxanWriter.writerow(['BESTSCORE  10'])
        marxanWriter.writerow(['NUMREPS ' + str(marxanParameterDict['numRun'])])
        marxanWriter.writerow([])

        marxanWriter.writerow(['Annealing Parameters'])
        marxanWriter.writerow(['NUMITNS ' + str(marxanParameterDict['numIter'])])
        marxanWriter.writerow(['STARTTEMP -1.00000000000000E+0000'])
        marxanWriter.writerow(['COOLFAC  6.00000000000000E+0000'])
        marxanWriter.writerow(['NUMTEMP 10000'])
        marxanWriter.writerow([])

        marxanWriter.writerow(['Cost Threshold'])
        marxanWriter.writerow(['COSTTHRESH  0.00000000000000E+0000'])
        marxanWriter.writerow(['THRESHPEN1  1.40000000000000E+0001'])
        marxanWriter.writerow(['THRESHPEN2  1.00000000000000E+0000'])
        marxanWriter.writerow([])

        marxanWriter.writerow(['Input Files'])
        marxanWriter.writerow(['INPUTDIR ' + setupObject.inputPath])
        marxanWriter.writerow(['SPECNAME spec.dat'])
        marxanWriter.writerow(['PUNAME pu.dat'])
        marxanWriter.writerow(['PUVSPRNAME puvspr2.dat'])
        marxanWriter.writerow(['MATRIXSPORDERNAME sporder.dat'])
        marxanWriter.writerow(['BOUNDNAME bound.dat'])
        marxanWriter.writerow([])

        marxanWriter.writerow(['Save Files'])
        marxanWriter.writerow(['SCENNAME ' + marxanParameterDict['outputName']])
        marxanWriter.writerow(['SAVERUN ' + extraOutputValue])
        marxanWriter.writerow(['SAVEBEST 2'])
        marxanWriter.writerow(['SAVESUMMARY 2'])
        marxanWriter.writerow(['SAVESCEN ' + extraOutputValue])
        marxanWriter.writerow(['SAVETARGMET 2'])
        marxanWriter.writerow(['SAVESUMSOLN 2'])
        marxanWriter.writerow(['SAVELOG ' + extraOutputValue])
        marxanWriter.writerow(['OUTPUTDIR ' + setupObject.outputPath])
        marxanWriter.writerow([])

        marxanWriter.writerow(['Program control.'])
        marxanWriter.writerow(['RUNMODE 1'])
        marxanWriter.writerow(['MISSLEVEL  ' + str(marxanParameterDict['missingProp'])])
        marxanWriter.writerow(['ITIMPTYPE 0'])
        marxanWriter.writerow(['HEURTYPE -1'])
        marxanWriter.writerow(['CLUMPTYPE 0'])
        marxanWriter.writerow(['VERBOSITY 3'])
        marxanWriter.writerow([])


def makeParallelAnalysesDetailsList(marxanParameterDict):
    parallelAnalysesDetailsList = list()
    runBlock = int(marxanParameterDict['numRun']) // marxanParameterDict['numParallelAnalyses']
    shortfallRuns = int(marxanParameterDict['numRun']) - (runBlock * marxanParameterDict['numParallelAnalyses'])
    blockList = [runBlock] * (marxanParameterDict['numParallelAnalyses'] - 1)
    blockList.append(runBlock + shortfallRuns)
    outputNameSuffixValue = 1
    for aBlockValue in blockList:
        outputNameBlock = marxanParameterDict['outputName'] + '_' + str(outputNameSuffixValue)
        blockTuple = (aBlockValue, outputNameBlock)
        parallelAnalysesDetailsList.append(blockTuple)
        outputNameSuffixValue += 1

    return parallelAnalysesDetailsList


def marxanUpdateSetupObject(marxanDialog, setupObject, marxanParameterDict):
    setupObject.outputName = marxanParameterDict['outputName']
    setupObject.numIter = marxanParameterDict['numIter']
    setupObject.numRuns = marxanParameterDict['numRun']
    setupObject.blmValue = marxanParameterDict['blmValue']
    setupObject.boundFlag = marxanDialog.boundCheckBox.isChecked()
    setupObject.extraOutputsFlag = marxanDialog.extraCheckBox.isChecked()
    setupObject.startProp = marxanParameterDict['initialProp']
    setupObject.targetProp = marxanParameterDict['missingProp']

    return setupObject


def makeMarxanBatFile(setupObject):
    marxanFullName = setupObject.marxanPath
    marxanBatFileName = marxanFullName.replace('.exe', '.bat')
    with open(marxanBatFileName,'w', newline='') as batFile:
        batWriter = csv.writer(batFile)
        # Change directory to where Marxan is installed
        batWriter.writerow([ os.path.splitdrive(marxanFullName)[0] ])
        batWriter.writerow(['cd ' + os.path.dirname(marxanFullName)])
        batWriter.writerow([marxanFullName])

    return marxanBatFileName


def waitingForMarxan(setupObject, outputName):
    marxanPathName = setupObject.outputPath + os.sep + outputName + '_best.txt'
    try:
        while os.path.isfile(marxanPathName) is False:
            time.sleep(2)
    except KeyboardInterrupt:
        pass


def waitingForParallelMarxan(setupObject, parallelAnalysesDetailsList):
    marxanPathNameList = list()
    for (numRun, outputName) in parallelAnalysesDetailsList:
        marxanPathNameList.append(setupObject.outputPath + os.sep + outputName + "_best.txt")
    waitingCount = 999
    try:
        while waitingCount > 0:
            waitingCount = 0
            for aMarxanPathName in marxanPathNameList:
                if os.path.isfile(aMarxanPathName) is False:
                    waitingCount += 1
            time.sleep(2)
    except KeyboardInterrupt:
        pass


def makeBestParallelFile(setupObject, mainOutputName, parallelAnalysesDetailsList):
    bestScoreValue = 'blank'
    bestScoreOutputName = 'blank'
    for (numRun, outputName) in parallelAnalysesDetailsList:
        summaryMarxanFile = setupObject.outputPath + os.sep + outputName + '_sum.txt'

        with open(summaryMarxanFile, 'rt') as f:
            reader = csv.reader(f)
            next(reader, None)  # skip the headers
            for row in reader:
                scoreValue = float(row[1])
                if bestScoreValue == 'blank':
                    bestScoreValue = scoreValue
                    bestScoreOutputName = outputName
                elif scoreValue < bestScoreValue:
                    bestScoreValue = scoreValue
                    bestScoreOutputName = outputName

    bestParralelFilePath = setupObject.outputPath + os.sep + bestScoreOutputName + '_best.txt'
    bestFilePath = setupObject.outputPath + os.sep + mainOutputName + '_best.txt'
    shutil.copyfile(bestParralelFilePath, bestFilePath)

    mvbestParralelFilePath = setupObject.outputPath + os.sep + bestScoreOutputName + '_mvbest.txt'
    mvbestFilePath = setupObject.outputPath + os.sep + mainOutputName + '_mvbest.txt'
    shutil.copyfile(mvbestParralelFilePath, mvbestFilePath)


def makeSummedParallelFile(setupObject, mainOutputName, parallelAnalysesDetailsList):
    summedDict = dict()
    for (numRun, outputName) in parallelAnalysesDetailsList:
        summaryMarxanFile = setupObject.outputPath + os.sep + outputName + '_ssoln.txt'

        with open(summaryMarxanFile, 'rt') as f:
            reader = csv.reader(f)
            next(reader, None)  # skip the headers
            for row in reader:
                idValue = int(row[0])
                summedValue = int(row[1])
                try:
                    runningCount = summedDict[idValue]
                except KeyError:
                    runningCount = 0
                runningCount += summedValue
                summedDict[idValue] = runningCount

    summedFilePath = setupObject.outputPath + os.sep + mainOutputName + '_ssoln.txt'
    with open(summedFilePath,'w', newline='') as summedFile:
        summedWriter = csv.writer(summedFile)
        summedWriter.writerow(['planning_unit', 'number'])
        summedPUIDList = list(summedDict.keys())
        summedPUIDList.sort()
        for puID in summedPUIDList:
            summedWriter.writerow([str(puID), str(summedDict[puID])])


def addBestMarxanOutputToPUShapefile(setupObject, bestOutputFilePath, bestFieldName):
    bestDict = makeBestScoresDict(bestOutputFilePath)
    puLayer = QgsVectorLayer(setupObject.puPath, "Planning units", "ogr")
    idFieldIndex = puLayer.fields().indexFromName("Unit_ID")
    statusFieldIndex = puLayer.fields().indexFromName("Status")

    bestFieldIndex = puLayer.fields().indexFromName(bestFieldName)
    provider = puLayer.dataProvider()
    if bestFieldIndex == -1:
        provider.addAttributes([QgsField(bestFieldName, QVariant.String)])
        puLayer.updateFields()
    bestFieldIndex = provider.fieldNameIndex(bestFieldName)

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
        puStatus = puAttributes[statusFieldIndex]
        bestBool = bestDict[puID]
        if puStatus == 'Conserved':
            bestStatus = 'Conserved'
        elif puStatus != 'Conserved' and bestBool == 1:
            bestStatus = 'Selected'
        else:
            bestStatus = '-'
        puLayer.changeAttributeValue(puRow, bestFieldIndex, bestStatus)
    puLayer.commitChanges()
    clearProgressBar()


def makeBestScoresDict(bestOutputFilePath):
    bestScoresDict = dict()
    with open(bestOutputFilePath, 'rt') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip the headers
        for row in reader:
            puID = int(float(row[0]))
            bestBool = int(float(row[1]))
            bestScoresDict[puID] = bestBool

    return bestScoresDict


def addSummedMarxanOutputToPUShapefile(setupObject, summedOutputFilePath, summedFieldName):
    summedScoreDict = makeSummedScoresDict(summedOutputFilePath)

    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    provider = puLayer.dataProvider()
    idFieldIndex = provider.fieldNameIndex('Unit_ID')
    statusFieldIndex = provider.fieldNameIndex('Status')

    summedFieldIndex = provider.fieldNameIndex(summedFieldName)
    if summedFieldIndex == -1:
        provider.addAttributes([QgsField(summedFieldName, QVariant.Int)])
        puLayer.updateFields()
        summedFieldIndex = provider.fieldNameIndex(summedFieldName)

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
        puStatus = puAttributes[statusFieldIndex]
        if puStatus == 'Conserved':
            summedScore = -99
        else:
            summedScore = summedScoreDict[puID]
        puLayer.changeAttributeValue(puRow, summedFieldIndex, summedScore)
    puLayer.commitChanges()
    clearProgressBar()


def makeSummedScoresDict(summedOutputFile):
    summedScoreDict = dict()
    with open(summedOutputFile, 'rt') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip the headers
        for row in reader:
            puID = int(float(row[0]))
            summedScore = int(float(row[1]))
            summedScoreDict[puID] = summedScore

    return summedScoreDict


def makeParameterValueList(calibrateRawParameterDict, exponentialBool):
    parameterValueList = []
    numAnalyses = float(calibrateRawParameterDict['numAnalysesText'])
    origMinAnalyses = float(calibrateRawParameterDict['minAnalysesText'])
    origMaxAnalyses = float(calibrateRawParameterDict['maxAnalysesText'])

    if exponentialBool:
        if origMinAnalyses == 0:
            minAnalyses = 0.00000000000000000000000000000001
        else:
            minAnalyses = math.log(origMinAnalyses)
        maxAnalyses = math.log(origMaxAnalyses)
    else:
        minAnalyses = origMinAnalyses
        maxAnalyses = origMaxAnalyses

    valIncrease = (maxAnalyses - minAnalyses) / (numAnalyses - 1)

    for aValue in range(0, int(numAnalyses)):
        parameterValue = float(minAnalyses) + (valIncrease * aValue)
        if exponentialBool:
            if origMinAnalyses == 0 and aValue == 0:
                parameterValue = 0
            else:
                parameterValue = math.exp(parameterValue)
        parameterValueList.append(parameterValue)

    return parameterValueList


def makeAnalysisResultsDict(setupObject, marxanParameterDict):
    analysisDict = dict()
    scoreList = list()
    costList = list()
    puCountList = list()
    connectivityCostList = list()
    penaltyList = list()
    mpmList = list()

    summaryTextPath = setupObject.outputPath + os.sep + marxanParameterDict['outputName'] + '_sum.txt'
    if os.path.isfile(summaryTextPath):
        with open(summaryTextPath, 'rt') as f:
            summaryReader = csv.reader(f)
            headerList = next(summaryReader)
            for aRow in summaryReader:
                scoreValue = float(aRow[headerList.index('Score')])
                costValue = float(aRow[headerList.index('Cost')])
                puCountValue = int(aRow[headerList.index('Planning_Units')])
                connectivityCostValue = float(aRow[headerList.index('Connectivity')])
                penaltyValue = float(aRow[headerList.index('Penalty')])
                mpmValue = float(aRow[headerList.index('MPM')])

                scoreList.append(scoreValue)
                costList.append(costValue)
                puCountList.append(puCountValue)
                connectivityCostList.append(connectivityCostValue)
                penaltyList.append(penaltyValue)
                mpmList.append(mpmValue)

        medianScore = statistics.median(scoreList)
        medianCost = statistics.median(costList)
        medianpuCount = statistics.median(puCountList)
        medianConnectivity = statistics.median(connectivityCostList)
        medianPenalty = statistics.median(penaltyList)
        medianMPM = statistics.median(mpmList)

        analysisDict['numIter'] = marxanParameterDict['numIter']
        analysisDict['numRun'] = marxanParameterDict['numRun']
        analysisDict['blmValue'] = marxanParameterDict['blmValue']
        analysisDict['outputName'] = str(marxanParameterDict['outputName'])

        analysisDict['medianScore'] = medianScore
        analysisDict['medianCost'] = medianCost
        analysisDict['medianpuCount'] = medianpuCount
        analysisDict['medianConnectivity'] = medianConnectivity
        analysisDict['medianPenalty'] = medianPenalty
        analysisDict['medianMPM'] = medianMPM

    else:
        warningMessage('No files found', 'The Marxan summary file was not found and so this process will terminate.')

    return analysisDict


def makeCalibrateOutputFile(resultPath, calibrateResultsDict):
    with open(resultPath,'w', newline='') as writerFile:
        calibrateWriter = csv.writer(writerFile)
        header1 = ['Analysis', 'Name', 'Iterations', 'Runs', 'BLM']
        header2 = ['Med Portfolio Cost', 'Med Planning Unit cost', 'Med Boundary length', 'Med Feature Penalty cost', 'Med MPM', 'Med PU Count']
        finalHeaderRow = header1 + header2
        calibrateWriter.writerow(finalHeaderRow)

        analysisNumberList = list(calibrateResultsDict.keys())
        analysisNumberList.sort()
        for aNumber in analysisNumberList:
            analysisDict = calibrateResultsDict[aNumber]

            numIter = analysisDict['numIter']
            numRun = analysisDict['numRun']
            blmValue = analysisDict['blmValue']
            outputName = analysisDict['outputName']

            medianScore = analysisDict['medianScore']
            medianCost = analysisDict['medianCost']
            medianpuCount = analysisDict['medianpuCount']
            medianConnectivity = analysisDict['medianConnectivity']
            medianPenalty = analysisDict['medianPenalty']
            medianMPM = analysisDict['medianMPM']

            rowList1 = [str(aNumber + 1), outputName, str(numIter), str(numRun), str(blmValue)]
            rowList2 = [str(medianScore), str(medianCost), str(medianConnectivity), str(medianPenalty), str(medianMPM), str(medianpuCount)]
            finalRowList = rowList1 + rowList2

            calibrateWriter.writerow(finalRowList)
