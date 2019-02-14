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

from qgis.PyQt.QtWidgets import QFileDialog
from qgis.core import QgsVectorLayer
from qgis.utils import iface

import os
import csv
import time

from .cluz_messages import criticalMessage, warningMessage
from .cluz_make_file_dicts import makeTargetDict
from .cluz_display import addPULayer


class CluzSetupObject:
    def __init__(self):
        #################################################
        self.overRide = False  ###########################
        #################################################

        self.setupStatus = 'blank' #Can be 'values_set', 'values_checked' or 'files_checked'
        self.setupAction = 'blank' #Can be be 'new' or 'open'
        self.setupPath = 'blank'

        #Specify the field names used in the Marxan outputs
        self.bestHeadingFieldNames = ['planning_unit', 'solution']
        self.summedHeadingFieldNames = ['planning_unit', 'number']

        self.decimalPlaces = 2
        self.marxanPath = 'blank'
        self.inputPath = 'blank'
        self.outputPath = 'blank'
        self.puPath = 'blank'
        self.targetPath = 'blank'
        self.abundFileDate = 'blank'
        self.targetFileDate = 'blank'

        #These are the default values
        self.outputName = 'output1'
        self.numIter = 1000000
        self.numRuns = 10
        self.blmValue = 0
        self.boundFlag = False
        self.extraOutputsFlag = False
        self.startProp = 0.2
        self.targetProp = 1

        self.abundPUKeyDict = 'blank'

        self.TableHeadingStyle = '::section {''background-color: lightblue; }'


def checkAllRelevantFiles(CLUZ_Object, setupObject, startDialog, setupDialog):
    checkSetupFileLoaded(CLUZ_Object, setupObject, startDialog, setupDialog)
    openSetupDialogIfSetupFilesIncorrect(CLUZ_Object, setupObject, setupDialog)
    checkCreateAddFiles(setupObject)


def checkSetupFileLoaded(CLUZ_Class, setupObject, startDialog, setupDialog):
    if setupObject.overRide:
        updateSetupObjectFromSetupFile(setupObject, 'C:\\QCLUZ\\cluz_ex1\\ex1.clz')
    else:
        if setupObject.setupPath == 'blank':
            CLUZ_Class.startDialog = startDialog(CLUZ_Class, setupObject)
            CLUZ_Class.startDialog.show()
            CLUZ_Class.startDialog.exec_()

            if setupObject.setupAction == 'new':
                CLUZ_Class.setupDialog = setupDialog(CLUZ_Class, setupObject)
                CLUZ_Class.setupDialog.show()
                CLUZ_Class.setupDialog.exec_()
            elif setupObject.setupAction == 'open':
                (setupPathNameText, fileTypeDetailsText) = QFileDialog.getOpenFileName(None, 'Open existing CLUZ setup file', '*.clz')
                try:
                    updateSetupObjectFromSetupFile(setupObject, setupPathNameText)
                except IOError:
                    pass
            else:
                CLUZ_Class.startDialog.close()


# Checks whether setup, pu, target and abundance file paths are correct. If they
def openSetupDialogIfSetupFilesIncorrect(CLUZ_Class, setupObject, setupDialog):
    if setupObject.setupStatus == 'values_set':
        CLUZ_Class.setupDialog = setupDialog(CLUZ_Class, setupObject)
        # show the dialog
        CLUZ_Class.setupDialog.show()
        # Run the dialog event loop
        CLUZ_Class.setupDialog.exec_()


def checkCreateAddFiles(setupObject):
    setupObject = createAndCheckCLUZFiles(setupObject)
    if setupObject.setupStatus == 'files_checked':
        makeTargetDict(setupObject)
        checkAddPULayer(setupObject)


class MinPatchObject:
    def __init__(self):
        self.setupStatus = 'blank' #Can be 'values_set', 'values_checked' or 'files_checked'


def makeSetupDictFromSetupFile(setupFilePath):
    setupDict = dict()
    with open(setupFilePath, 'rt') as f:
        setupReader = csv.reader(f)
        for aRow in setupReader:
            aList = aRow[0].split(' = ')
            if len(aList) == 2:
                theKey = aList[0]
                theValue = aList[1]
                setupDict[theKey] = theValue

    return setupDict


def updateSetupObjectFromSetupFile(setupObject, setupFilePath):
    setupDict = makeSetupDictFromSetupFile(setupFilePath)

    try:
        decPlaceText = setupDict['decimal_places']
        setupObject.setupPath = setupFilePath
        setupObject.marxanPath = setupDict['marxan_path']
        setupObject.inputPath = setupDict['input_dir']
        setupObject.outputPath = setupDict['output_dir']
        setupObject.puPath = setupDict['unit_theme']
        setupObject.targetPath = setupDict['target_table']
        setupObject.outputName = setupDict['output_name']
        numIterText = setupDict['num_iterations']
        numRunText = setupDict['num_runs']
        numBlmText = setupDict['blm']
        setupObject.boundFlag = setupDict['bound_flag']
        setupObject.extraOutputsFlag = setupDict['extra_flag']
        startPropText = setupDict['start_prop']
        targetPropText = setupDict['target_prop']

        setupFileOK = checkFilesAndReturnSetupFileOKBool(setupObject, decPlaceText, numIterText, numRunText, numBlmText, startPropText, targetPropText)

    except KeyError:
        warningMessage('Setup file incorrect format', 'The specified setup file does not contain all of the correct factors. Please correct this.')
        setupFileOK = False

    if setupFileOK is True:
        setupObject.setupStatus = 'values_set'
        setupObject = checkStatusObjectValues(setupObject)
        if setupObject.setupStatus == 'values_checked':
            setupObject.setupPath = setupFilePath

    return setupObject


def checkFilesAndReturnSetupFileOKBool(setupObject, decPlaceText, numIterText, numRunText, numBlmText, startPropText, targetPropText):
    setupFileOK = True
    try:
        setupObject.decimalPlaces = int(decPlaceText)
        if setupObject.decimalPlaces > 5:
            setupObject.decimalPlaces = 5
    except ValueError:
        warningMessage('Setup file incorrect format', 'The specified decimal place value in the setup file is not an integer. Please correct this.')
        setupFileOK = False
    try:
        setupObject.numIter = int(numIterText)
    except ValueError:
        warningMessage('Setup file incorrect format', 'The specified number of iterations in the setup file is not an integer. Please correct this.')
        setupFileOK = False
    try:
        setupObject.numRuns = int(numRunText)
    except ValueError:
        warningMessage('Setup file incorrect format', 'The specified number of runs in the setup file is not an integer. Please correct this.')
        setupFileOK = False
    try:
        setupObject.blmValue = float(numBlmText)
    except ValueError:
        warningMessage('Setup file incorrect format', 'The BLM value in the setup file is not a number. Please correct this.')
        setupFileOK = False
    try:
        setupObject.startProp = float(startPropText)
    except ValueError:
        warningMessage('Setup file incorrect format', 'The start proportion value in the setup file is not a number. Please correct this.')
        setupFileOK = False
    try:
        setupObject.targetProp = float(targetPropText)
    except ValueError:
        warningMessage('Setup file incorrect format', 'The target proportion value in the setup file is not a number. Please correct this.')
        setupFileOK = False

    return setupFileOK


def checkStatusObjectValues(setupObject):
    setupFileCorrectBool = True

    setupFileCorrectBool = checkDecPlacesValue(setupObject, setupFileCorrectBool)
    setupFileCorrectBool = checkNumItersValue(setupObject, setupFileCorrectBool)
    setupFileCorrectBool = checkNumRunsValue(setupObject, setupFileCorrectBool)
    setupFileCorrectBool = checkBlmValue(setupObject, setupFileCorrectBool)
    setupFileCorrectBool = checkStartProp(setupObject, setupFileCorrectBool)
    setupFileCorrectBool = checkCLUZFilePaths(setupObject, setupFileCorrectBool)
    
    foldersOKBool = checkFolderValues(setupObject)

    if setupFileCorrectBool and foldersOKBool:
        setupObject.setupStatus = 'values_checked'

    return setupObject


def checkDecPlacesValue(setupObject, setupFileCorrectBool):
    try:
        setupObject.decimalPlaces = int(setupObject.decimalPlaces)
        if setupObject.decimalPlaces < 0:
            warningMessage('Setup file incorrect format', 'The specified value in the CLUZ setup file for number of decimal places cannot be a negative value. Please correct this.')
            setupFileCorrectBool = False
    except ValueError:
        warningMessage('Setup file incorrect format', 'The specified value in the CLUZ setup file for number of decimal places in the Abundance and Target tables is not an integer. Please correct this.')
        setupFileCorrectBool = False
        
    return setupFileCorrectBool


def checkNumItersValue(setupObject, setupFileCorrectBool):
    try:
        setupObject.numIter = int(setupObject.numIter)
        if setupObject.numIter < 0:
            warningMessage('Setup file incorrect format', 'The specified value in the CLUZ setup file for number of Marxan iterations cannot be a negative value. Please correct this.')
            setupFileCorrectBool = False
    except ValueError:
        warningMessage('Setup file incorrect format', 'The specified number of iterations in the setup file is not an integer. Please correct this.')
        setupFileCorrectBool = False
        
    return setupFileCorrectBool


def checkNumRunsValue(setupObject, setupFileCorrectBool):
    try:
        setupObject.numRuns = int(setupObject.numRuns)
        if setupObject.numRuns < 0:
            warningMessage('Setup file incorrect format', 'The specified value in the CLUZ setup file for number of Marxan runs cannot be a negative value. Please correct this.')
            setupFileCorrectBool = False
    except ValueError:
        warningMessage('Setup file incorrect format', 'The specified number of runs in the setup file is not an integer. Please correct this.')   
        setupFileCorrectBool = False
        
    return setupFileCorrectBool        


def checkBlmValue(setupObject, setupFileCorrectBool):
    try:
        setupObject.blmValue = float(setupObject.blmValue)
        if setupObject.blmValue < 0:
            warningMessage('Setup file incorrect format', 'The specified BLM value in the CLUZ setup file cannot be a negative value. Please correct this.')
            setupFileCorrectBool = False
    except ValueError:
        warningMessage('Setup file incorrect format', 'The BLM value in the setup file is not a number. Please correct this.')  
        setupFileCorrectBool = False
        
    return setupFileCorrectBool


def checkStartProp(setupObject, setupFileCorrectBool):
    try:
        setupObject.startProp = float(setupObject.startProp)
        if setupObject.startProp < 0 or setupObject.startProp > 1:
            warningMessage('Setup file incorrect format', 'The specified proportion of planning units initially selected by Marxan as specified in the CLUZ setup has to be between 0 and 1. Please correct this.')
            setupFileCorrectBool = False
    except ValueError:
        warningMessage('Setup file incorrect format', 'The start proportion value in the setup file is not a number. Please correct this.')
        setupFileCorrectBool = False
        
    return setupFileCorrectBool


def checkTargetProp(setupObject, setupFileCorrectBool):
    try:
        setupObject.targetProp = float(setupObject.targetProp)
        if setupObject.targetProp < 0 or setupObject.targetProp > 1:
            warningMessage('Setup file incorrect format', 'The specified proportion of a target that needs to be achieved for Marxan to report that the target has been met as specified in the CLUZ setup has to be between 0 and 1. Please correct this.')
            setupFileCorrectBool = False
    except ValueError:
        warningMessage('Setup file incorrect format', 'The target proportion value in the setup file is not a number. Please correct this.')
        setupFileCorrectBool = False
        
    return setupFileCorrectBool


def checkCLUZFilePaths(setupObject, setupFileCorrectBool):
    inputPath = setupObject.inputPath
    if inputPath == 'blank':
        warningMessage('Missing input folder', 'The input folder has not been specified. Please open the View and Edit CLUZ setup file function and update the information.')
        setupFileCorrectBool = False
    elif os.path.exists(inputPath) is False:
        warningMessage('Incorrect input folder', 'The specified input folder cannot be found. Please open the View and Edit CLUZ setup file function and update the information.')
        setupFileCorrectBool = False

    outputPath = setupObject.outputPath
    if outputPath == 'blank':
        warningMessage('Missing output folder', 'The output folder has not been specified. Please open the View and Edit CLUZ setup file function and update the information.')
        setupFileCorrectBool = False
    elif os.path.exists(outputPath) is False:
        warningMessage('Incorrect output folder', 'The specified output folder cannot be found. Please open the View and Edit CLUZ setup file function and update the information.')
        setupFileCorrectBool = False
        
    puPath = setupObject.puPath
    if puPath == 'blank':
        warningMessage('Missing planning unit shapefile', 'The planning unit shapefile has not been specified. Please open the View and Edit CLUZ setup file function and update the information.')
        setupFileCorrectBool = False
    elif os.path.exists(puPath) is False:
        warningMessage('Incorrect planning unit shapefile path', 'The specified planning unit shapefile cannot be found. Please open the View and Edit CLUZ setup file function and update the information.')
        setupFileCorrectBool = False

    puvspr2Path = setupObject.inputPath + os.sep + 'puvspr2.dat'
    if os.path.exists(puvspr2Path) is False:
        warningMessage('Incorrect puvspr2 path', 'The puvspr2.dat file cannot be found. Please add it to the specified input folder.')
        setupFileCorrectBool = False

    targetPath = setupObject.targetPath
    if targetPath == 'blank':
        warningMessage('Missing target table', 'The target table has not been specified. Please open the View and Edit CLUZ setup file function and update the information.')
        setupFileCorrectBool = False
    elif os.path.exists(targetPath) is False:
        warningMessage('Incorrect target table path', 'The specified target table cannot be found. Please open the View and Edit CLUZ setup file function and update the information.')
        setupFileCorrectBool = False

    return setupFileCorrectBool


def checkFolderValues(setupObject):
    foldersOKBool = True
    if os.path.isfile(setupObject.marxanPath) is False:
        warningMessage('Setup file incorrect format', 'The specified Marxan file cannot be found. Please correct this.')
        foldersOKBool = False
    else:
        marxanDirPath = os.path.dirname(setupObject.marxanPath)
        if setupObject.marxanPath == 'blank' or setupObject.marxanPath == '':
            warningMessage('Marxan path invalid', 'The Marxan path is missing.')
            foldersOKBool = False
        elif os.path.isdir(marxanDirPath) is False:
            warningMessage('Marxan path invalid', 'The specified folder containing Marxan does not exist.')
            foldersOKBool = False
        elif os.access(marxanDirPath, os.W_OK) is False:
            warningMessage('Marxan path invalid', 'Running Marxan involves CLUZ creating a new input file in the folder where Marxan is stored. You do not have permission to save files into the specified folder so please move Marxan to a folder where you do have permission.')
            foldersOKBool = False

    return foldersOKBool


def updateClzSetupFile(setupObject, saveSuccessfulBool):
    setupFilePath = setupObject.setupPath
    try:
        with open(setupFilePath,'w', newline='') as setupFile:
            setupWriter = csv.writer(setupFile)

            setupWriter.writerow(['decimal_places = ' + str(setupObject.decimalPlaces)])
            setupWriter.writerow(['marxan_path = ' + setupObject.marxanPath])
            setupWriter.writerow(['input_dir = ' + setupObject.inputPath])
            setupWriter.writerow(['output_dir = ' + setupObject.outputPath])
            setupWriter.writerow(['unit_theme = ' + setupObject.puPath])
            setupWriter.writerow(['target_table = ' + setupObject.targetPath])
            setupWriter.writerow(['output_name = ' + setupObject.outputName])
            setupWriter.writerow(['num_iterations = ' + str(setupObject.numIter)])
            setupWriter.writerow(['num_runs = ' + str(setupObject.numRuns)])
            setupWriter.writerow(['blm = ' + str(setupObject.blmValue)])
            setupWriter.writerow(['bound_flag = ' + str(setupObject.boundFlag)])
            setupWriter.writerow(['extra_flag = ' + str(setupObject.extraOutputsFlag)])
            setupWriter.writerow(['start_prop = ' + str(setupObject.startProp)])
            setupWriter.writerow(['target_prop = ' + str(setupObject.targetProp)])
    except PermissionError:
        criticalMessage('Failed to save', 'You do not have permission to save the CLUZ setup file in the specified folder.')
        saveSuccessfulBool = False

    return saveSuccessfulBool


def createAndCheckCLUZFiles(setupObject):
    if setupObject.setupStatus == 'values_checked':
        checkBool = True
        checkBool = createAndCheckTargetFile(setupObject, checkBool)
        checkBool = createAndCheckPuvspr2File(setupObject, checkBool)
        checkBool = createAndCheckPuLayerFile(setupObject, checkBool)
        if checkBool:
            setupObject.targetDict = makeTargetDict(setupObject)
            setupObject.setupStatus = 'files_checked'

    return setupObject


def createAndCheckTargetFile(setupObject, checkBool):
    targetCSVFilePath = setupObject.targetPath
    setupObject.targetFileDate = time.ctime(os.path.getmtime(targetCSVFilePath))
    targetFileFieldNameList = ['id', 'name', 'type', 'spf', 'target', 'conserved', 'total', 'pc_target']
    try:
        with open(targetCSVFilePath, 'rt') as f:
            targetReader = csv.reader(f)
            origHeaderList = next(targetReader)

        lowercaseHeaderList = list()
        for aHeader in origHeaderList:
            lowercaseHeader = aHeader.lower()
            lowercaseHeaderList.append(lowercaseHeader)

        for aHeader in targetFileFieldNameList:
            if lowercaseHeaderList.count(aHeader) == 0:
                warningMessage('Formatting error:', 'the Target table is missing a ' + aHeader + ' field. Please select a table with the correct format.')
                checkBool = False
    except FileNotFoundError:
        checkBool = False

    return checkBool


def createAndCheckPuvspr2File(setupObject, checkBool):
    puvspr2FilePath = setupObject.inputPath + os.sep + 'puvspr2.dat'
    with open(puvspr2FilePath, 'rt') as f:
        puvspr2Reader = csv.reader(f)
        puvspr2HeaderList = next(puvspr2Reader)
        if puvspr2HeaderList != ['species', 'pu', 'amount']:
            warningMessage('Formatting error: ', 'the puvspr2.dat file in the input folder is incorrectly formatted and should only have the following header names: species, pu, amount.')
            checkBool = False

    return checkBool


def createAndCheckPuLayerFile(setupObject, checkBool):
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    fields = puLayer.fields()
    fieldDetailsList = list()
    titleText = 'Formatting error: '
    mainText = 'The planning unit shapefile must contain a field named '
    for aField in fields:
        fieldDetailsList.append((str(aField.name()), str(aField.typeName())))
    if fieldDetailsList.count(('Unit_ID', 'Integer')) == 0 and fieldDetailsList.count(('Unit_ID', 'Integer64')) == 0:
        warningMessage(titleText, mainText + 'Unit_ID containing integer values.')
        checkBool = False
    if fieldDetailsList.count(('Area', 'Real')) == 0:
        warningMessage(titleText, mainText + 'Area containing real number values.')
        checkBool = False
    if fieldDetailsList.count(('Cost', 'Real')) == 0:
        warningMessage(titleText, mainText+ 'Cost containing real number values.')
        checkBool = False
    if fieldDetailsList.count(('Status', 'String')) == 0:
        warningMessage(titleText, mainText + 'Status containing text values.')
        checkBool = False

    return checkBool


def checkPULayerPresent():
    allLayers = iface.mapCanvas().layers()
    puLayerPresentBool = False
    for aLayer in allLayers:
        if aLayer.name() == 'Planning units':
            puLayerPresentBool = True

    return puLayerPresentBool


def checkAddPULayer(setupObject):
    if setupObject.setupStatus == 'files_checked':
        if not checkPULayerPresent():
            addPULayer(setupObject, 0) # 0 = Position


def returnFeatIDSetFromAbundPUKeyDict(setupObject):
    featIDSet = set()
    abundPUKeyDict = setupObject.abundPUKeyDict
    for puID in abundPUKeyDict:
        featIDList = abundPUKeyDict[puID].keys()
        for featID in featIDList:
            featIDSet.add(featID)

    return featIDSet