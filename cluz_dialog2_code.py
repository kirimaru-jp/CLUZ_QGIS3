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

from qgis.core import QgsProject, QgsVectorLayer

import csv
import os

from .cluz_messages import warningMessage, successMessage
from .cluz_make_file_dicts import makePuvspr2DatFile, addFeaturesToTargetCsvFile, makeTargetDict, makeAbundancePUKeyDict, makeSporderDatFile
from .cluz_functions2 import addAbundDictToAbundPUKeyDict, createTargetPuvspr2SporderFiles, addFeaturesFromAddAbundDictToPuvspr2File, createPULayer, makeVecAddAbundDict

########################## Make new CLUZ files #########################

def check_MakeNewCLUZFiles(createDialog):
    shapefileOKBool = checkShapefile(createDialog)
    conversionFormatOKBool = checkConversionFormat(createDialog)
    inputFolderOKBool = checkInputFolderPath(createDialog)
    targetTableOKBool = checkTargetTable(createDialog)


    if shapefileOKBool and conversionFormatOKBool and inputFolderOKBool and targetTableOKBool:
        createPULayer(createDialog)
        createTargetPuvspr2SporderFiles(createDialog)
        successMessage('Task completed', 'The CLUZ planning unit layer, blank abundance and target tables have been created. You can now use them when creating the CLUZ setup file.')
        createDialog.close()


def checkShapefile(createDialog):
    shapefileOKBool = True
    if createDialog.puLineEdit.text() == '':
        warningMessage('Shapefile error', 'No shapefile was specified.')
        shapefileOKBool = False

    if shapefileOKBool:
        puLayer = QgsVectorLayer(createDialog.puLineEdit.text(), 'Shapefile', 'ogr')
        layerGeomType = puLayer.geometryType()
        puProvider = puLayer.dataProvider()
        puIdFieldOrder = puProvider.fieldNameIndex('Unit_ID')
        puCostFieldOrder = puProvider.fieldNameIndex('Area')
        puAreaFieldOrder = puProvider.fieldNameIndex('Cost')
        puStatusFieldOrder = puProvider.fieldNameIndex('Status')

        if layerGeomType != 2:
            warningMessage('Incorrect format', 'The specified shapefile is not a polygon layer.')
            shapefileOKBool = False

        if puIdFieldOrder != -1 or puCostFieldOrder != -1 or puAreaFieldOrder != -1 or puStatusFieldOrder != -1:
            warningMessage('Incorrect format', 'The specified shapefile cannot contain fields named Unit_ID, Area, Cost or Status as these will be created here. Please remove/rename these fields and try again.')
            shapefileOKBool = False

    return shapefileOKBool


def checkConversionFormat(createDialog):
    conversionFormatOKBool = True
    try:
        convFactor = float(createDialog.convLineEdit.text())
        if conversionFormatOKBool and convFactor <= 0:
            warningMessage('Incorrect format', 'The specified conversion format is in an incorrect format. It should be a number greater than 0.')
            conversionFormatOKBool = False
    except ValueError:
        warningMessage('Incorrect format', 'The specified conversion format is in an incorrect format. It should be a number greater than 0.')
        conversionFormatOKBool = False

    return conversionFormatOKBool


def checkInputFolderPath(createDialog):
    inputFolderOKBool = True
    if createDialog.inputLineEdit.text() == '':
        warningMessage('No folder specified', 'You need to specify the input folder where the puvspr2.dat file will be saved.')
        inputFolderOKBool = False
    else:
        if os.access(os.path.dirname(createDialog.inputLineEdit.text()), os.W_OK):
            pass
        else:
            warningMessage('Incorrect format', 'You do not have access to the specified input folder.')
            inputFolderOKBool = False

    return inputFolderOKBool


def checkTargetTable(createDialog):
    targetTableOKBool = True
    if createDialog.targetLineEdit.text() == '':
        warningMessage('No file specified', 'You need to specify the name and path for the new target file.')
        targetTableOKBool = False
    else:
        if os.access(os.path.dirname(createDialog.targetLineEdit.text()), os.W_OK):
            pass
        else:
            warningMessage('Incorrect format', 'You cannot save the target table into the specified folder because you do not have access.')
            targetTableOKBool = False

        if createDialog.targetLineEdit.text()[-4:] != '.csv':
            warningMessage('Incorrect format', 'Your target table must be a .csv file.')
            targetTableOKBool = False

    return targetTableOKBool


##################### Import vec data #################################

def checkAddLayerListConvertVecDialog(ConvertVecDialog):
    layerNameList = loadThemesList()
    if len(layerNameList) == 0:
        warningMessage('No suitable layers', 'Please add to the project the polyline or polygon shapefiles that you want to import.')
        ConvertVecDialog.okButton.setEnabled(False)
    ConvertVecDialog.selectListWidget.addItems(layerNameList)


def loadThemesList():
    listMapItems = QgsProject.instance().mapLayers()
    layerNameList = list()
    for nameCode, layer in listMapItems.items():
        layerName = layer.name()
        layerGeomType = layer.geometryType()
        if layerName != "Planning units" and layerGeomType != 0:
            layerNameList.append(str(layerName))

    return layerNameList


def checkLayerFactorConvertVec(ConvertVecDialog):
    layerFactorCheck = True
    layerList = list()

    idFieldName = ConvertVecDialog.idfieldLineEdit.text()
    selectedLayerNameList = [item.text() for item in ConvertVecDialog.selectListWidget.selectedItems()]
    if len(selectedLayerNameList) == 0:
        ConvertVecDialog.close()
        warningMessage('No layers selected', 'No layers were selected.')
        layerFactorCheck = False
    else:
        listMapItems = QgsProject.instance().mapLayers()
        for nameCode, layer in listMapItems.items():
            layerName = layer.name()
            if layerName in selectedLayerNameList:
                layerList.append(layer)
        for aLayer in layerList:
            provider = aLayer.dataProvider()
            aLayerName = aLayer.name()
            idFieldOrder = provider.fieldNameIndex(idFieldName)
            if idFieldOrder == -1:
                ConvertVecDialog.close()
                warningMessage('Layer format error with ' + aLayerName, 'The specified ID field ' + idFieldName + ' is not in the layer ' + aLayerName + '.')
                layerFactorCheck = False
            else:
                idField = provider.fields().field(idFieldOrder)
                idFieldType = idField.typeName()
                if idFieldType != 'Integer' and idFieldType != 'Integer64':
                    ConvertVecDialog.close()
                    warningMessage('Layer format error' + aLayerName, 'The specified ID field ' + idFieldName + ' does not contain integer values.')
                    layerFactorCheck = False
                    
    return layerList, layerFactorCheck


def checkConvFactorConvertVec(ConvertVecDialog):
    convFactorCheck = True
    if ConvertVecDialog.userRadioButton.isChecked():
        try:
            convFactor = float(ConvertVecDialog.convLineEdit.text())
            if convFactor <= 0:
                ConvertVecDialog.close()
                warningMessage('Incorrect conversion value', 'The conversion value must be a number greater than 0.')
                convFactorCheck = False

        except ValueError:
            ConvertVecDialog.close()
            warningMessage('Incorrect conversion value', 'The conversion value must be a number greater than 0.')
            convFactorCheck = False

    return convFactorCheck


def create_UpdateAbundDataFromVecFile(ConvertVecDialog, setupObject, layerList):
    idFieldName = ConvertVecDialog.idfieldLineEdit.text()
    convFactor = float(ConvertVecDialog.convLineEdit.text())
    addAbundDict, addFeatIDList, errorLayerList = makeVecAddAbundDict(setupObject, layerList, idFieldName, convFactor)
    existingIDSet = set(addFeatIDList).intersection(set(setupObject.targetDict.keys()))
    if len(existingIDSet) > 0:
        produceWarningMessageAboutFeatsAlreadyInAbundTab(ConvertVecDialog, existingIDSet)
    else:
        if setupObject.abundPUKeyDict == 'blank':
            setupObject.abundPUKeyDict = makeAbundancePUKeyDict(setupObject)
        addFeaturesFromAddAbundDictToPuvspr2File(setupObject, addAbundDict)
        setupObject.abundPUKeyDict = makeAbundancePUKeyDict(setupObject)
        makeSporderDatFile(setupObject)

        addFeaturesToTargetCsvFile(setupObject, addAbundDict, addFeatIDList)
        setupObject.targetDict = makeTargetDict(setupObject)
        ConvertVecDialog.close()

    return errorLayerList

        
def produceWarningMessageAboutFeatsAlreadyInAbundTab(ConvertVecDialog, existingIDSet):
    ConvertVecDialog.close()
    listText = ''
    for aID in existingIDSet:
        listText += str(aID) + ', '
    finalListText = listText[0: -2]
    warningMessage('Existing features', 'The abundance table already contains features with ID values of ' + finalListText + '. This process will terminate without adding the new values.')


def makeErrorLayerString(errorLayerList):
    rawErrorLayerString = 'please check your input data, as QGIS was unable to intersect the planning unit layer with the following data layers: '
    for aLayerName in errorLayerList:
        rawErrorLayerString += aLayerName + ' ,'

    errorLayerString = rawErrorLayerString[0:-2]

    return errorLayerString


###############################Import csv data ##############################

def check_AddCsvFilePath(ConvertCsvDialog, csvPathNameText):
    if csvPathNameText != '':
        ConvertCsvDialog.csvFileLineEdit.setText(csvPathNameText)
        csvFile = open(csvPathNameText, 'rt')
        try:
            reader = csv.reader(csvFile)
            fileHeaderList = next(reader)
            ConvertCsvDialog.idfieldComboBox.addItems(fileHeaderList)
            ConvertCsvDialog.idfieldComboBox.setEnabled(True)
        except IOError:
            warningMessage('Input file incorrectly formatted', 'CLUZ cannot read this file. Please check it is a csv file with commas between fields and each row representing a table line')


def checkLayerFactor(ConvertCsvDialog):
    layerFactorCheck = True
    csvFilePath = ConvertCsvDialog.csvFileLineEdit.text()
    if csvFilePath == '':
        ConvertCsvDialog.close()
        warningMessage('No file specified', 'Please specify a csv file to import.')
        layerFactorCheck = False
    elif os.path.isfile(csvFilePath) is False:
        ConvertCsvDialog.close()
        warningMessage('Incorrect format', 'The specified csv file does not exist.')
        layerFactorCheck = False
    else:
        pass

    return layerFactorCheck


def checkConvFactor(ConvertCsvDialog, layerFactorCheck):
    convFactorCheck = True
    if layerFactorCheck:
        if ConvertCsvDialog.userRadioButton.isChecked():
            try:
                convFactor = float(ConvertCsvDialog.convLineEdit.text())
                if convFactor <= 0:
                    ConvertCsvDialog.close()
                    warningMessage('Incorrect conversion value', 'The conversion value must be a number greater than 0.')
                    convFactorCheck = False

            except ValueError:
                ConvertCsvDialog.close()
                warningMessage('Incorrect conversion value', 'The conversion value must be a number greater than 0.')
                convFactorCheck = False

    return convFactorCheck


def addCSVDictToAbundDict_UpdatePuvspr2TargetFiles(setupObject, addAbundDict, featIDList):
    setupObject.abundPUKeyDict = addAbundDictToAbundPUKeyDict(setupObject, addAbundDict)
    makePuvspr2DatFile(setupObject)
    makeSporderDatFile(setupObject)

    addFeaturesToTargetCsvFile(setupObject, addAbundDict, featIDList)
    setupObject.targetDict = makeTargetDict(setupObject)