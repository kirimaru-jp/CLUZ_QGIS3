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

import csv
import os
import subprocess
import time

from .cluz_functions5 import makeBestParallelFile, checkNumRunsParaDict, makeSummedParallelFile, makeParameterValueList, checkNumParallelAnalysesValueParaDict, addBestMarxanOutputToPUShapefile, makeMarxanBatFile
from .cluz_functions5 import waitingForParallelMarxan, checkInitialPropValueParaDict, checkMissingPropValueParaDict, makeAnalysisResultsDict, addSummedMarxanOutputToPUShapefile, makeCalibrateOutputFile, waitingForMarxan
from .cluz_functions5 import returnOutputName, makeMarxanInputFile, makeParallelAnalysesDetailsList, checkNumIterParaDict, checkPermissionToUseMarxanFolderParaDict, checkBlmValueParaDict

from .cluz_display import displayGraduatedLayer, reloadPULayer, displayBestOutput
from .cluz_messages import warningMessage


################### Marxan Dialog#########################
def setDialogParameters(MarxanDialog, setupObject):
    MarxanDialog.boundLineEdit.setVisible(False)

    MarxanDialog.iterLineEdit.setText(str(setupObject.numIter))
    MarxanDialog.runLineEdit.setText(str(setupObject.numRuns))
    outputName = returnOutputName(setupObject)
    MarxanDialog.outputLineEdit.setText(outputName)
    MarxanDialog.boundLineEdit.setText(str(setupObject.blmValue))
    MarxanDialog.parallelListWidget.addItems(["2", "3", "4", "5"])
    MarxanDialog.parallelListWidget.setCurrentRow(0)

    if setupObject.boundFlag:
        MarxanDialog.boundCheckBox.setChecked(True)
        MarxanDialog.boundLineEdit.setVisible(True)

    if setupObject.extraOutputsFlag:
        MarxanDialog.extraCheckBox.setChecked(True)

    MarxanDialog.missingLineEdit.setText(str(setupObject.targetProp))
    MarxanDialog.propLineEdit.setText(str(setupObject.startProp))


def makeMarxanRawParameterDict(MarxanDialog, setupObject):
    numIterString = MarxanDialog.iterLineEdit.text()
    numRunString = MarxanDialog.runLineEdit.text()
    outputName = str(MarxanDialog.outputLineEdit.text())
    setupObject.outputName = outputName
    if MarxanDialog.boundCheckBox.isChecked():
        blmValueString = MarxanDialog.boundLineEdit.text()
    else:
        blmValueString = "0"
    missingPropString = MarxanDialog.missingLineEdit.text()
    initialPropString = MarxanDialog.propLineEdit.text()
    extraOutputsBool = MarxanDialog.extraCheckBox.isChecked()

    if MarxanDialog.parallelCheckBox.isChecked():
        numParallelAnalyses = int(MarxanDialog.parallelListWidget.selectedItems()[0].text())
    else:
        numParallelAnalyses = 1

    marxanRawParameterDict = dict()
    marxanRawParameterDict['numIterString'] = numIterString
    marxanRawParameterDict['numRunString'] = numRunString
    marxanRawParameterDict['blmValueString'] = blmValueString
    marxanRawParameterDict['missingPropString'] = missingPropString
    marxanRawParameterDict['initialPropString'] = initialPropString
    marxanRawParameterDict['extraOutputsBool'] = extraOutputsBool
    marxanRawParameterDict['numParallelAnalyses'] = numParallelAnalyses
    marxanRawParameterDict['outputName'] = outputName
    marxanRawParameterDict['marxanPath'] = setupObject.marxanPath

    return marxanRawParameterDict


def makeMarxanParameterDict(setupObject, marxanRawParameterDict):
    marxanParameterDict = dict()
    marxanParameterDict['numIter'] = int(marxanRawParameterDict['numIterString'])
    marxanParameterDict['numRun'] = int(marxanRawParameterDict['numRunString'])
    marxanParameterDict['blmValue'] = float(marxanRawParameterDict['blmValueString'])
    marxanParameterDict['missingProp'] = float(marxanRawParameterDict['missingPropString'])
    marxanParameterDict['initialProp'] = float(marxanRawParameterDict['initialPropString'])

    marxanParameterDict['extraOutputsBool'] = marxanRawParameterDict['extraOutputsBool']
    marxanParameterDict['numParallelAnalyses'] = marxanRawParameterDict['numParallelAnalyses']
    marxanParameterDict['outputName'] = marxanRawParameterDict['outputName']
    marxanParameterDict['extraOutputsBool'] =  marxanRawParameterDict['extraOutputsBool']

    marxanPath = setupObject.marxanPath
    marxanFolderName = os.path.dirname(marxanPath)
    marxanSetupPath = str(marxanFolderName) + os.sep + 'input.dat'
    marxanParameterDict["marxanPath"] = marxanPath
    marxanParameterDict["marxanSetupPath"] = marxanSetupPath

    return marxanParameterDict


def returnMarxanInputValuesOKBool(marxanParameterDict):
    marxanInputValuesOKBool = checkNumIterParaDict(marxanParameterDict['numIterString'])
    marxanInputValuesOKBool = checkNumRunsParaDict(marxanParameterDict['numRunString'], marxanInputValuesOKBool)
    marxanInputValuesOKBool = checkBlmValueParaDict(marxanParameterDict['blmValueString'], marxanInputValuesOKBool)
    marxanInputValuesOKBool = checkMissingPropValueParaDict(marxanParameterDict['missingPropString'], marxanInputValuesOKBool)
    marxanInputValuesOKBool = checkInitialPropValueParaDict(marxanParameterDict['initialPropString'], marxanInputValuesOKBool)
    marxanInputValuesOKBool = checkNumParallelAnalysesValueParaDict(marxanParameterDict['numRunString'], marxanParameterDict['numParallelAnalyses'], marxanInputValuesOKBool)
    marxanInputValuesOKBool = checkPermissionToUseMarxanFolderParaDict(marxanParameterDict, marxanInputValuesOKBool)

    return marxanInputValuesOKBool


def checkMarxanFilesExistBool(setupObject):
    marxanFilesExistBool = True
    puDatPath = setupObject.inputPath + os.sep + 'pu.dat'
    specDatPath = setupObject.inputPath + os.sep + 'spec.dat'
    puvspr2DatPath = setupObject.inputPath + os.sep + 'puvspr2.dat'

    if os.path.exists(puDatPath) is False:
        warningMessage('Missing Marxan file','There is no pu.dat file in the specified Marxan input folder. Please create the file using the Create Marxan input files function')
        marxanFilesExistBool = False
    if os.path.exists(specDatPath) is False:
        warningMessage('Missing Marxan file','There is no spec.dat file in the specified Marxan input folder. Please create the file using the Create Marxan input files function')
        marxanFilesExistBool = False
    if os.path.exists(puvspr2DatPath) is False:
        warningMessage('Missing Marxan file','There is no puvspr2.dat file in the specified Marxan input folder. Please create one')
        marxanFilesExistBool = False

    return marxanFilesExistBool


def launchSingleMarxanAnalysis(setupObject, marxanParameterDict):
    makeMarxanInputFile(setupObject, marxanParameterDict)
    marxanBatFileName = makeMarxanBatFile(setupObject)
    subprocess.Popen([marxanBatFileName])
    waitingForMarxan(setupObject, marxanParameterDict['outputName'])
    bestOutputFile = setupObject.outputPath + os.sep + marxanParameterDict['outputName'] + '_best.txt'
    summedOutputFile = setupObject.outputPath + os.sep + marxanParameterDict['outputName'] + '_ssoln.txt'

    return bestOutputFile, summedOutputFile


def launchMultiMarxanAnalysis(setupObject, marxanParameterDict):
    combinedOutputName = marxanParameterDict['outputName']
    parallelAnalysesDetailsList = makeParallelAnalysesDetailsList(marxanParameterDict)
    for (numRun, parallelOutputName) in parallelAnalysesDetailsList:
        marxanParameterDict['numRun'] = numRun
        marxanParameterDict['outputName'] = parallelOutputName
        makeMarxanInputFile(setupObject, marxanParameterDict)
        marxanBatFileName = makeMarxanBatFile(setupObject)
        subprocess.Popen([marxanBatFileName])
        time.sleep(2)

    waitingForParallelMarxan(setupObject, parallelAnalysesDetailsList)

    makeBestParallelFile(setupObject, combinedOutputName, parallelAnalysesDetailsList)
    bestOutputFile = setupObject.outputPath + os.sep + combinedOutputName + '_best.txt'

    makeSummedParallelFile(setupObject, combinedOutputName, parallelAnalysesDetailsList)
    summedOutputFile = setupObject.outputPath + os.sep + combinedOutputName + '_ssoln.txt'

    return bestOutputFile, summedOutputFile


####################### Load previous results ##################################

def returnInitialFieldNames(setupObject):
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    fieldNameList = [field.name() for field in puLayer.fields()]
    bestName = 'IMP_BEST'
    bestSuffix = ''
    if bestName in fieldNameList:
        bestSuffix = 1
        while (bestName + str(bestSuffix)) in fieldNameList:
            bestSuffix += 1
    finalBestName = bestName + str(bestSuffix)

    summedName = 'IMP_SUM'
    summedSuffix = ''
    if summedName in fieldNameList:
        summedSuffix = 1
        while (summedName + str(summedSuffix)) in fieldNameList:
            summedSuffix += 1
    finalSummedName = summedName + str(summedSuffix)

    return finalBestName, finalSummedName


def check_LoadBestMarxanResult(LoadDialog, setupObject):
    bestFieldName = LoadDialog.bestNameLineEdit.text()
    if LoadDialog.bestCheckBox.isChecked():
        bestPath = LoadDialog.bestLineEdit.text()
    else:
        bestPath = 'blank'

    progressBool = checkBestFieldName(setupObject, bestFieldName)
    if progressBool:
        LoadDialog.close()
        if bestPath != 'blank':
            if os.path.isfile(bestPath):
                with open(bestPath, 'rt') as f:
                    bestReader = csv.reader(f)
                    bestHeader = next(bestReader, None)  # skip the headers
                if bestHeader == setupObject.bestHeadingFieldNames:
                    addBestMarxanOutputToPUShapefile(setupObject, bestPath, bestFieldName)
                    bestShapefileName = bestFieldName
                    displayBestOutput(setupObject, bestFieldName, bestShapefileName)
                else:
                    warningMessage('Invalid file','The specified Marxan best output file is incorrectly formatted. It must contain only two fields named planning_unit and solution.')
            else:
                warningMessage('Incorrect pathname','The specified pathname for the Marxan best output is invalid. Please choose another one.')
        if bestPath != 'blank':
            reloadPULayer(setupObject)


def checkBestFieldName(setupObject, bestFieldName):
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    fieldNameList = [field.name() for field in puLayer.fields()]
    progressBool = True
    if bestFieldName in fieldNameList:
        warningMessage('Best field name duplication', 'The planning unit theme already contains a field named ' + bestFieldName + '. Please choose another name.')
        progressBool = False
    if len(bestFieldName) > 10:
        warningMessage('Invalid field name', 'The Best field name cannot be more than 10 characters long.')
        progressBool = False
        
    return progressBool


def check_LoadSummedMarxanResult(LoadDialog, setupObject):
    summedFieldName = LoadDialog.summedNameLineEdit.text()
    if LoadDialog.summedCheckBox.isChecked():
        summedPath = LoadDialog.summedLineEdit.text()
    else:
        summedPath = 'blank'
        
    progressBool = checkSummedFieldName(setupObject, summedFieldName)
    if progressBool:
        LoadDialog.close()
        if summedPath != 'blank':
            if os.path.isfile(summedPath):
                with open(summedPath, 'rt') as f:
                    summedReader = csv.reader(f)
                    summedHeader = next(summedReader, None)  # skip the headers
                if summedHeader == setupObject.summedHeadingFieldNames:
                    addSummedMarxanOutputToPUShapefile(setupObject, summedPath, summedFieldName)
                    summedShapefileName = summedFieldName
                    displayGraduatedLayer(setupObject, summedFieldName, summedShapefileName, 1) #1 is SF legend code
                else:
                    warningMessage('Invalid file', 'The specified Marxan summed output file is incorrectly formatted. It must contain only two fields named planning_unit and number')
            else:
                warningMessage('Incorrect pathname','The specified pathname for the Marxan summed output is invalid. Please choose another one')
        if  summedPath != 'blank':
            reloadPULayer(setupObject)


def checkSummedFieldName(setupObject, summedFieldName):
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    fieldNameList = [field.name() for field in puLayer.fields()]
    progressBool = True
    if summedFieldName in fieldNameList:
        warningMessage('Summed field name duplication', 'The planning unit theme already contains a field named ' + summedFieldName + '. Please choose another name.')
        progressBool = False
    if len(summedFieldName) > 10:
        warningMessage('Invalid field name', 'The Summed field name cannot be more than 10 characters long.')
        progressBool = False

    return progressBool


########################### Calibrate Dialog #############################

def setInitialValuesCalibrateDialog(CalibrateDialog, setupObject):
    CalibrateDialog.paraComboBox.addItems(['BLM', 'Number of iterations', 'Number of runs', 'SPF'])
    CalibrateDialog.iterLineEdit.setText(str(setupObject.numIter))
    CalibrateDialog.runLineEdit.setText(str(setupObject.numRuns))
    CalibrateDialog.boundLineEdit.setText(str(setupObject.blmValue))
    CalibrateDialog.boundLabel.setEnabled(False)
    CalibrateDialog.boundLineEdit.setEnabled(False)


def makeMarxanCalibrateRawParameterDict(CalibrateDialog):
    calibrateRawParameterDict = dict()
    calibrateRawParameterDict['numAnalysesText'] = CalibrateDialog.numberLineEdit.text()
    calibrateRawParameterDict['minAnalysesText'] = CalibrateDialog.minLineEdit.text()
    calibrateRawParameterDict['maxAnalysesText'] = CalibrateDialog.maxLineEdit.text()
    calibrateRawParameterDict['outputNameBase'] = CalibrateDialog.outputLineEdit.text()
    calibrateRawParameterDict['resultPathText'] = CalibrateDialog.resultsLineEdit.text()
    
    return calibrateRawParameterDict


def checkSimpleCalibrateAnalysisParameters(CalibrateDialog, setupObject, calibrateRawParameterDict):
    checkBool = checkSimpleCalibrateAnalysisInputtedParameters(calibrateRawParameterDict)

    if checkBool:
        exponentialBool = CalibrateDialog.expCheckBox.isChecked()
        parameterValueList = makeParameterValueList(calibrateRawParameterDict, exponentialBool)
        numIterList, checkBool = checkCalibrateNumIterValue(CalibrateDialog, calibrateRawParameterDict, parameterValueList, checkBool)
        numRunList, checkBool = checkCalibrateNumRunValue(CalibrateDialog, calibrateRawParameterDict, parameterValueList, checkBool)
        blmValueList, checkBool = checkCalibrateBlmValue(CalibrateDialog, calibrateRawParameterDict, parameterValueList, checkBool)

        if checkBool:
            runCalibrateMarxan(setupObject, calibrateRawParameterDict, numRunList, numIterList, blmValueList)
            CalibrateDialog.close()

        
def checkSimpleCalibrateAnalysisInputtedParameters(calibrateRawParameterDict):
    checkBool = True
    if calibrateRawParameterDict['outputNameBase'] == '':
        warningMessage('Incorrect output basename', 'The specified basename for the Marxan output files is blank. Please choose another one')
        checkBool = False
    try:
        numAnalyses = int(calibrateRawParameterDict['numAnalysesText'])
        if numAnalyses < 1:
            warningMessage('Incorrect format', 'The specified number of analysis is incorrectly formatted. It must be an integer and greater than 0.')
            checkBool = False
    except ValueError:
        warningMessage('Incorrect format', 'The specified number of analysis is incorrectly formatted. It must be an integer and greater than 0.')
        checkBool = False
    try:
        minAnalyses = float(calibrateRawParameterDict['minAnalysesText'])
        if minAnalyses < 0:
            warningMessage('Incorrect format', 'The specified minimum value is incorrectly formatted. It must be a number and greater than 0.')
            checkBool = False
    except ValueError:
        warningMessage('Incorrect format', 'The specified minimum value is incorrectly formatted. It must be a number and greater than 0.')
        checkBool = False
    try:
        maxAnalyses = int(calibrateRawParameterDict['maxAnalysesText'])
        if maxAnalyses < 0:
            warningMessage('Incorrect format', 'The specified maximum value is incorrectly formatted. It must be a number and greater than 0.')
            checkBool = False
    except ValueError:
        warningMessage('Incorrect format', 'The specified maximum value is incorrectly formatted. It must be a number and greater than 0.')
        checkBool = False
    if checkBool:
        if maxAnalyses <= minAnalyses:
            warningMessage('Incorrect format', 'The specified maximum value is incorrectly formatted. It must be greater than the specified minimum value.')
            checkBool = False
            
    return checkBool


def checkCalibrateNumIterValue(CalibrateDialog, calibrateRawParameterDict, parameterValueList, checkBool):
    if CalibrateDialog.iterLineEdit.isEnabled():
        numIterText = CalibrateDialog.iterLineEdit.text()
        try:
            numIter = int(numIterText)
            numIterList = [numIter] * int(calibrateRawParameterDict['numAnalysesText'])
            if numIter < 10000:
                warningMessage('Incorrect format', 'The specified number of iterations is incorrectly formatted. It must be an integer greater than 10000 (Marxan uses 10000 temperature drops in the simulated annealing process in these analyses and the number of iterations must be greater than the number of temperature drops).')
                checkBool = False
        except ValueError:
            warningMessage('Incorrect format', 'The specified number of iterations is incorrectly formatted. It must be a positive integer.')
            checkBool = False
    else:
        numIterList = parameterValueList
        
    return numIterList, checkBool


def checkCalibrateNumRunValue(CalibrateDialog, calibrateRawParameterDict, parameterValueList, checkBool):
    if CalibrateDialog.runLineEdit.isEnabled():
        numRunText = CalibrateDialog.runLineEdit.text()
        try:
            numRun = int(numRunText)
            numRunList = [numRun] * int(calibrateRawParameterDict['numAnalysesText'])
            if numRun < 1:
                warningMessage('Incorrect format', 'The specified number of runs is incorrectly formatted. It must be a positive integer.')
                checkBool = False
        except ValueError:
            warningMessage('Incorrect format', 'The specified number of runs is incorrectly formatted. It must be a positive integer.')
            checkBool = False
    else:
        numRunList = parameterValueList
        
    return numRunList, checkBool


def checkCalibrateBlmValue(CalibrateDialog, calibrateRawParameterDict, parameterValueList, checkBool):
    if CalibrateDialog.boundLineEdit.isEnabled():
        blmValueText = CalibrateDialog.boundLineEdit.text()
        try:
            blmValue = float(blmValueText)
            blmValueList = [blmValue] * int(calibrateRawParameterDict['numAnalysesText'])
            if blmValue < 0:
                warningMessage('Incorrect format', 'The specified BLM value is incorrectly formatted. It must be a positive number.')
                checkBool = False
        except ValueError:
            warningMessage('Incorrect format', 'The specified BLM value is incorrectly formatted. It must be a positive number.')
            checkBool = False
    else:
        blmValueList = parameterValueList
        
    return blmValueList, checkBool


def runCalibrateMarxan(setupObject, calibrateRawParameterDict, numRunList, numIterList, blmValueList):
    calibrateResultsDict = dict()
    for analysisNumber in range(0, int(calibrateRawParameterDict['numAnalysesText'])):
        marxanParameterDict = makeCalibrateMarxanParameterDict(setupObject, calibrateRawParameterDict, numIterList, numRunList, blmValueList, analysisNumber)
        makeMarxanInputFile(setupObject, marxanParameterDict)
        marxanBatFileName = makeMarxanBatFile(setupObject)
        subprocess.Popen([marxanBatFileName])
        time.sleep(2)
        waitingForMarxan(setupObject, calibrateRawParameterDict['outputNameBase'] + str(analysisNumber + 1))
        calibrateResultsDict[analysisNumber] = makeAnalysisResultsDict(setupObject, marxanParameterDict)
    makeCalibrateOutputFile(calibrateRawParameterDict['resultPathText'], calibrateResultsDict)


def makeCalibrateMarxanParameterDict(setupObject, calibrateRawParameterDict, numIterList, numRunList, blmValueList, analysisNumber):
    missingPropValue = 1.0
    initialPropValue = 0.2
    marxanParameterDict = dict()
    marxanParameterDict['numIter'] = numIterList[analysisNumber]
    marxanParameterDict['numRun'] = numRunList[analysisNumber]
    marxanParameterDict['blmValue'] = blmValueList[analysisNumber]
    marxanParameterDict['missingProp'] = missingPropValue
    marxanParameterDict['initialProp'] = initialPropValue

    marxanParameterDict['outputName'] = calibrateRawParameterDict['outputNameBase'] + str(analysisNumber + 1)
    marxanParameterDict['extraOutputsBool'] = True
    marxanParameterDict['numParallelAnalyses'] = 1

    marxanPath = setupObject.marxanPath
    marxanFolderName = os.path.dirname(marxanPath)
    marxanSetupPath = str(marxanFolderName) + os.sep + 'input.dat'
    marxanParameterDict['marxanPath'] = marxanPath
    marxanParameterDict['marxanSetupPath'] = marxanSetupPath

    return marxanParameterDict