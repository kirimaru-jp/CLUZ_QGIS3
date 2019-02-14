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

import copy
import os

from .cluz_setup import updateSetupObjectFromSetupFile, checkStatusObjectValues, checkAddPULayer, createAndCheckCLUZFiles, updateClzSetupFile


def addSetupDialogTextFromSetupObject(setupDialog, setupObject):
    setupDialog.marxanLineEdit.setText(setupObject.marxanPath)
    setupDialog.inputLineEdit.setText(setupObject.inputPath)
    setupDialog.outputLineEdit.setText(setupObject.outputPath)
    setupDialog.puLineEdit.setText(setupObject.puPath)
    setupDialog.targetLineEdit.setText(setupObject.targetPath)
    setupDialog.setPrecValue(setupObject.decimalPlaces)
    if os.path.isfile(setupObject.setupPath):
        setupPathText = os.path.abspath(setupObject.setupPath)
    else:
        setupPathText = 'blank'
    setupPathLabelText = 'Setup file location: ' + setupPathText
    setupDialog.setupPathLabel.setText(setupPathLabelText)


def loadSetupFileCode(setupDialog, setupObject, setupFilePath):
    setupObject = updateSetupObjectFromSetupFile(setupObject, setupFilePath)

    if setupObject.setupStatus == 'values_checked':
        setupObject = createAndCheckCLUZFiles(setupObject)

    if setupObject.setupStatus == "files_checked":
        setupObject.setupAction = "blank"
        setupPathLabelText = os.path.abspath(setupFilePath)
        setupPathLabelText = "Setup file location: " + str(setupPathLabelText)
        setupDialog.setupPathLabel.setText(setupPathLabelText)

        setupDialog.marxanLineEdit.setText(os.path.abspath(setupObject.marxanPath))
        setupDialog.inputLineEdit.setText(os.path.abspath(setupObject.inputPath))
        setupDialog.outputLineEdit.setText(setupObject.outputPath)
        setupDialog.puLineEdit.setText(setupObject.puPath)
        setupDialog.targetLineEdit.setText(setupObject.targetPath)
        setupDialog.setPrecValue(setupObject.decimalPlaces)

        checkAddPULayer(setupObject)


def saveSetupFileCode(setupDialog, setupObject, setupFilePath):
    limboSetupObject = copy.deepcopy(setupObject)
    limboSetupObject.setupStatus = 'blank'

    limboSetupObject.decimalPlaces = int(setupDialog.precComboBox.currentText())
    limboSetupObject.marxanPath = setupDialog.marxanLineEdit.text()
    limboSetupObject.inputPath = setupDialog.inputLineEdit.text()
    limboSetupObject.outputPath = setupDialog.outputLineEdit.text()
    limboSetupObject.puPath = setupDialog.puLineEdit.text()
    limboSetupObject.targetPath = setupDialog.targetLineEdit.text()
    limboSetupObject = checkStatusObjectValues(limboSetupObject)
    saveSuccessfulBool = False

    if limboSetupObject.setupStatus == 'values_checked':
        limboSetupObject = createAndCheckCLUZFiles(limboSetupObject)
    if limboSetupObject.setupStatus == 'files_checked':
        saveSuccessfulBool = True
        copyLimboParametersToSetupObject(setupObject, limboSetupObject)
        saveSuccessfulBool = updateClzSetupFile(setupObject, saveSuccessfulBool)
        if saveSuccessfulBool:
            setupPathLabelText = 'Setup file location: ' + str(setupFilePath)
            setupDialog.setupPathLabel.setText(setupPathLabelText)

            checkAddPULayer(setupObject)

    return saveSuccessfulBool


def copyLimboParametersToSetupObject(setupObject, limboSetupObject):
    setupObject.decimalPlaces = limboSetupObject.decimalPlaces
    setupObject.marxanPath = limboSetupObject.marxanPath
    setupObject.inputPath = limboSetupObject.inputPath
    setupObject.outputPath = limboSetupObject.outputPath
    setupObject.puPath = limboSetupObject.puPath


def saveAsSetupFileCode(setupDialog, setupObject, newSetupFilePath):
    setupObject.decimalPlaces = int(setupDialog.precComboBox.currentText())
    setupObject.marxanPath = setupDialog.marxanLineEdit.text()
    setupObject.inputPath = setupDialog.inputLineEdit.text()
    setupObject.outputPath = setupDialog.outputLineEdit.text()
    setupObject.puPath = setupDialog.puLineEdit.text()
    setupObject.targetPath = setupDialog.targetLineEdit.text()
    setupObject.setupPath = newSetupFilePath

    setupObject = checkStatusObjectValues(setupObject)
    if setupObject.setupStatus == 'values_checked':
        setupObject = createAndCheckCLUZFiles(setupObject)
    if setupObject.setupStatus == 'files_checked':
        saveSuccessfulBool = True
        saveSuccessfulBool = updateClzSetupFile(setupObject, saveSuccessfulBool)
        if saveSuccessfulBool:
            setupPathLabelText = 'Setup file location: ' + str(newSetupFilePath)
            setupDialog.setupPathLabel.setText(setupPathLabelText)
            checkAddPULayer(setupObject)

