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

import csv

from .cluz_messages import criticalMessage, warningMessage
from .cluz_checkup import checkFilesAndReturnSetupFileOKBool, checkStatusObjectValues
from .cluz_checkup import createAndCheckTargetFile, createAndCheckPuvspr2File, createAndCheckPuLayerFile, checkAddPULayer
from .zcluz_checkup import createAndCheckZonesFile, createAndCheckZonesPuLayerFile, checkAddZonesPULayer, createAndCheckZonesTargetFile
from .cluz_make_file_dicts import makeTargetDict
from .zcluz_make_file_dicts import makeZonesTargetDict, makeZonesDict, makeZonesPropDict, makeZonesTargetZonesDict, makeZonesBLMDictFromSetupFile


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
        self.zonesPath = 'blank'
        self.abundFileDate = 'blank'
        self.targetFileDate = 'blank'

        #These are the default values
        self.analysisType = 'Marxan'
        self.outputName = 'output1'
        self.numIter = 1000000
        self.numRuns = 10
        self.boundFlag = False
        self.blmValue = 0
        self.zonesBoundFlag = False
        self.extraOutputsFlag = False
        self.startProp = 0.2
        self.targetProp = 1

        self.abundPUKeyDict = 'blank'
        self.zonesBLMDict = 'blank'

        self.TableHeadingStyle = '::section {''background-color: lightblue; }'


def checkAllRelevantFiles(CLUZ_Object, setupObject, startDialog, setupDialog):
    checkSetupFileLoaded(CLUZ_Object, setupObject, startDialog, setupDialog)
    openSetupDialogIfSetupFilesIncorrect(CLUZ_Object, setupObject, setupDialog)
    checkCreateAddFiles(setupObject)


def checkSetupFileLoaded(CLUZ_Class, setupObject, startDialog, setupDialog):
    if setupObject.overRide:
        # updateSetupObjectFromSetupFile(setupObject, 'C:\\Users\\rjsmi\\Dropbox\\new_NE_CLUZ_analysis\\nnr low - home.clz')
        # updateSetupObjectFromSetupFile(setupObject, 'C:\\Users\\rjsmi\\Dropbox\\Q-CLUZ\\cluz_ex1\\ex1.clz')
        # updateSetupObjectFromSetupFile(setupObject, 'C:\\Users\\rjsmi\\Dropbox\\Q-CLUZ\\mzones1\\mzones1.clz')
        updateSetupObjectFromSetupFile(setupObject, 'C:\\Users\\rjsmi\\Dropbox\\Research\\BBOWT_project\\CLUZ\\BBOWT_Bob_Home.clz')
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
        analysisType = setupDict['analysis_type']
    except KeyError:
        analysisType = 'Marxan'
    try:
        setupObject.analysisType = analysisType
        decPlaceText = setupDict['decimal_places']
        setupObject.setupPath = setupFilePath
        setupObject.marxanPath = setupDict['marxan_path']
        setupObject.inputPath = setupDict['input_dir']
        setupObject.outputPath = setupDict['output_dir']
        setupObject.puPath = setupDict['unit_theme']
        setupObject.targetPath = setupDict['target_table']
        if analysisType == 'MarxanWithZones':
            setupObject.zonesPath = setupDict['zones_table']
        setupObject.outputName = setupDict['output_name']
        numIterText = setupDict['num_iterations']
        numRunText = setupDict['num_runs']
        numBlmText = setupDict['blm']
        setupObject.boundFlag = setupDict['bound_flag']
        if setupDict['bound_flag'] == 'True':
            setupObject.boundFlag = True
        else:
            setupObject.boundFlag = False
        if setupDict['extra_flag'] == 'True':
            setupObject.extraOutputsFlag = True
        else:
            setupObject.extraOutputsFlag = False
        startPropText = setupDict['start_prop']
        targetPropText = setupDict['target_prop']
        if analysisType == 'MarxanWithZones':
            if setupDict['zones_bound_flag'] == 'True':
                setupObject.zonesBoundFlag = True
            else:
                setupObject.zonesBoundFlag = False
            setupObject.zonesBLMDict = makeZonesBLMDictFromSetupFile(setupDict)

        setupFileOK = checkFilesAndReturnSetupFileOKBool(setupObject, analysisType, decPlaceText, numIterText, numRunText, numBlmText, startPropText, targetPropText)

    except KeyError:
        warningMessage('Setup file incorrect format', 'The specified setup file does not contain all of the correct factors. Please correct this.')
        setupFileOK = False

    if setupFileOK is True:
        setupObject.setupStatus = 'values_set'
        setupObject = checkStatusObjectValues(setupObject)
        if setupObject.setupStatus == 'values_checked':
            setupObject.setupPath = setupFilePath

    return setupObject


def updateClzSetupFile(setupObject, saveSuccessfulBool):
    setupFilePath = setupObject.setupPath
    try:
        with open(setupFilePath,'w', newline='') as setupFile:
            setupWriter = csv.writer(setupFile)

            setupWriter.writerow(['analysis_type = ' + str(setupObject.analysisType)])
            setupWriter.writerow(['decimal_places = ' + str(setupObject.decimalPlaces)])
            setupWriter.writerow(['marxan_path = ' + setupObject.marxanPath])
            setupWriter.writerow(['input_dir = ' + setupObject.inputPath])
            setupWriter.writerow(['output_dir = ' + setupObject.outputPath])
            setupWriter.writerow(['unit_theme = ' + setupObject.puPath])
            setupWriter.writerow(['target_table = ' + setupObject.targetPath])
            if setupObject.analysisType == 'MarxanWithZones':
                setupWriter.writerow(['zones_table = ' + setupObject.zonesPath])
            setupWriter.writerow(['output_name = ' + setupObject.outputName])
            setupWriter.writerow(['num_iterations = ' + str(setupObject.numIter)])
            setupWriter.writerow(['num_runs = ' + str(setupObject.numRuns)])
            setupWriter.writerow(['bound_flag = ' + str(setupObject.boundFlag)])
            setupWriter.writerow(['blm = ' + str(setupObject.blmValue)])
            setupWriter.writerow(['extra_flag = ' + str(setupObject.extraOutputsFlag)])
            setupWriter.writerow(['start_prop = ' + str(setupObject.startProp)])
            setupWriter.writerow(['target_prop = ' + str(setupObject.targetProp)])
            if setupObject.analysisType == 'MarxanWithZones':
                setupWriter.writerow(['zones_bound_flag = ' + str(setupObject.zonesBoundFlag)])
                addZonesBLMDictDataToSetupFile(setupWriter, setupObject)

    except PermissionError:
        criticalMessage('Failed to save', 'You do not have permission to save the CLUZ setup file in the specified folder.')
        saveSuccessfulBool = False

    return saveSuccessfulBool


def addZonesBLMDictDataToSetupFile(setupWriter, setupObject):
    zonesBLMLabelList = list(setupObject.zonesBLMDict.keys())
    zonesBLMLabelList.sort()
    for zonesBLMLabel in zonesBLMLabelList:
        finalZonesBLMLabel = 'BLM_' + zonesBLMLabel.replace(' ', '_')
        blmValueString = str(setupObject.zonesBLMDict[zonesBLMLabel])
        setupWriter.writerow([finalZonesBLMLabel + ' = ' + blmValueString])


def checkCreateAddFiles(setupObject):
    setupObject = createAndCheckCLUZFiles(setupObject)
    if setupObject.setupStatus == 'files_checked':
        if setupObject.analysisType == 'Marxan':
            makeTargetDict(setupObject) ######### WHIS IS THIS NEEDED?
            checkAddPULayer(setupObject)
        if setupObject.analysisType == 'MarxanWithZones':
            makeZonesTargetDict(setupObject) ######### WHIS IS THIS NEEDED?
            checkAddZonesPULayer(setupObject)


def createAndCheckCLUZFiles(setupObject):
    if setupObject.setupStatus == 'values_checked' and setupObject.analysisType == 'Marxan':
        checkBool = True
        checkBool = createAndCheckTargetFile(setupObject, checkBool)
        checkBool = createAndCheckPuvspr2File(setupObject, checkBool)
        checkBool = createAndCheckPuLayerFile(setupObject, checkBool)
        if checkBool:
            setupObject.targetDict = makeTargetDict(setupObject)
            setupObject.setupStatus = 'files_checked'

    elif setupObject.setupStatus == 'values_checked' and setupObject.analysisType == 'MarxanWithZones':
        checkBool = True
        checkBool = createAndCheckZonesFile(setupObject, checkBool)
        if checkBool:
            setupObject.zonesDict = makeZonesDict(setupObject)

            checkBool = createAndCheckZonesTargetFile(setupObject, checkBool)
            checkBool = createAndCheckPuvspr2File(setupObject, checkBool)
            checkBool = createAndCheckZonesPuLayerFile(setupObject, checkBool)
            if checkBool:
                setupObject.targetDict = makeZonesTargetDict(setupObject)
                setupObject.zonesPropDict = makeZonesPropDict(setupObject)
                setupObject.zonesTargetDict = makeZonesTargetZonesDict(setupObject)
                setupObject.setupStatus = 'files_checked'

    return setupObject

