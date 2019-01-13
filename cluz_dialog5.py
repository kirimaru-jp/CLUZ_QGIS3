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

from qgis.PyQt.QtWidgets import QDialog, QFileDialog

import os
import sys

from cluz_form_inputs import Ui_inputsDialog
from cluz_form_marxan import Ui_marxanDialog
from cluz_form_load import Ui_loadDialog
from cluz_form_calibrate import Ui_calibrateDialog

from .cluz_setup import updateClzSetupFile
from .cluz_dialog5_code import check_LoadSummedMarxanResult, setInitialValuesCalibrateDialog, makeMarxanParameterDict, makeMarxanCalibrateRawParameterDict, check_LoadBestMarxanResult, makeMarxanRawParameterDict, returnMarxanInputValuesOKBool, setDialogParameters, checkSimpleCalibrateAnalysisParameters, launchSingleMarxanAnalysis, launchMultiMarxanAnalysis, returnInitialFieldNames
from .cluz_display import displayGraduatedLayer, removePreviousMarxanLayers, reloadPULayer, displayBestOutput
from .cluz_functions5 import createPuDatFile, marxanUpdateSetupObject, addBestMarxanOutputToPUShapefile, createBoundDatFile, createSpecDatFile, addSummedMarxanOutputToPUShapefile
from .cluz_messages import criticalMessage, successMessage

class inputsDialog(QDialog, Ui_inputsDialog):
    def __init__(self, iface, setupObject):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.boundextBox.setEnabled(False)
        self.okButton.clicked.connect(lambda: self.setCreateMarxanInputFiles(setupObject))


    def setCreateMarxanInputFiles(self, setupObject):
        messageStringList = list()
        if self.targetBox.isChecked():
            createSpecDatFile(setupObject)
            messageStringList.append('spec.dat')

        if self.puBox.isChecked():
            createPuDatFile(setupObject)
            messageStringList.append('pu.dat')

        if self.boundBox.isChecked():
            if self.boundextBox.isChecked() and self.boundextBox.isEnabled():
                extEdgeBool = True
            else:
                extEdgeBool = False
            createBoundDatFile(setupObject, extEdgeBool)
            messageStringList.append('bound.dat')

        if len(messageStringList) > 0:
            messageString = ''
            for aString in messageStringList:
                messageString += aString + ', '
            finalMessageString = messageString[:-2]
            successMessage('Marxan files:', 'the following files have been produced: ' + finalMessageString)

        self.close()


def checkCluzIsNotRunningOnMac():
    marxanBool = True
    if sys.platform.startswith('darwin'):
        criticalMessage('CLUZ and MacOS', 'The current version of CLUZ cannot run Marxan on Mac computers. Sorry about that. Instead, you can run Marxan indepedently and load the results into CLUZ.')
        marxanBool = False
        
    return marxanBool


def checkMarxanPath(setupObject, marxanBool):
    if setupObject.marxanPath == 'blank':
        criticalMessage('Marxan path missing', 'The location of Marxan has not been specified. CLUZ will now open the CLUZ setup dialog box, so please specify a correct version.')
        marxanBool = False
    if os.path.exists(setupObject.marxanPath) is False:
        criticalMessage('Incorrect Marxan path', 'Marxan cannot be found at the specified pathway. CLUZ will now open the CLUZ setup dialog box, so please specify a correct version.')
        marxanBool = False
        
    return marxanBool


class marxanDialog(QDialog, Ui_marxanDialog):
    def __init__(self, iface, setupObject, targetsMetAction):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        setDialogParameters(self, setupObject)
        self.startButton.clicked.connect(lambda: self.runMarxan(setupObject, targetsMetAction))


    def runMarxan(self, setupObject, targetsMetAction):
        marxanRawParameterDict = makeMarxanRawParameterDict(self, setupObject)
        marxanInputValuesOKBool = returnMarxanInputValuesOKBool(marxanRawParameterDict)
        if marxanInputValuesOKBool:
            marxanParameterDict = makeMarxanParameterDict(setupObject, marxanRawParameterDict)
            createSpecDatFile(setupObject)

            setupObject = marxanUpdateSetupObject(setupObject, marxanParameterDict)
            saveSuccessfulBool = True
            updateClzSetupFile(setupObject, saveSuccessfulBool)
            self.close()

            bestLayerName = 'Best (' + marxanParameterDict['outputName'] + ')' #OutputName is overwritten in parallel analyses, so specifying these names here
            summedLayerName = 'SF_Score (' + marxanParameterDict['outputName'] + ')' #OutputName is overwritten in parallel analyses, so specifying these names here

            if marxanParameterDict['numParallelAnalyses'] == 1:
                bestOutputFile, summedOutputFile = launchSingleMarxanAnalysis(setupObject, marxanParameterDict)
            else:
                bestOutputFile, summedOutputFile = launchMultiMarxanAnalysis(setupObject, marxanParameterDict)

            addBestMarxanOutputToPUShapefile(setupObject, bestOutputFile, 'Best')
            addSummedMarxanOutputToPUShapefile(setupObject, summedOutputFile, 'SF_Score')

            reloadPULayer(setupObject)
            removePreviousMarxanLayers()
            displayBestOutput(setupObject, 'Best', bestLayerName)
            displayGraduatedLayer(setupObject, 'SF_Score', summedLayerName, 1) #1 is SF legend code

            targetsMetAction.setEnabled(True)


class loadDialog(QDialog, Ui_loadDialog):
    def __init__(self, iface, setupObject):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        self.bestLabel.setVisible(False)
        self.bestLineEdit.setVisible(False)
        self.bestNameLineEdit.setVisible(False)
        self.bestButton.setVisible(False)
        self.summedLabel.setVisible(False)
        self.summedLineEdit.setVisible(False)
        self.summedNameLineEdit.setVisible(False)
        self.summedButton.setVisible(False)

        bestName, summedName = returnInitialFieldNames(setupObject)
        self.bestNameLineEdit.setText(bestName)
        self.summedNameLineEdit.setText(summedName)

        self.bestButton.clicked.connect(self.setBestPath)
        self.summedButton.clicked.connect(self.setSummedPath)
        self.okButton.clicked.connect(lambda: self.loadPreviousMarxanResults(setupObject))


    def setBestPath(self):
        (bestPathNameText, fileTypeDetailsText) = QFileDialog.getOpenFileName(self, 'Select Marxan best portfolio output', '*.txt')
        if bestPathNameText is None:
            self.bestLineEdit.setText(bestPathNameText)

    def setSummedPath(self):
        (summedPathNameText, fileTypeDetailsText) = QFileDialog.getOpenFileName(self, 'Select Marxan summed solution output', '*.txt')
        if summedPathNameText is None:
            self.summedLineEdit.setText(summedPathNameText)


    def loadPreviousMarxanResults(self, setupObject):
        check_LoadBestMarxanResult(self, setupObject)
        check_LoadSummedMarxanResult(self, setupObject)


class calibrateDialog(QDialog, Ui_calibrateDialog):
    def __init__(self, iface, setupObject):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        setInitialValuesCalibrateDialog(self, setupObject)
        self.paraComboBox.activated.connect(self.combo_chosen)

        self.saveResultsButton.clicked.connect(self.saveResultsFile)
        self.runButton.clicked.connect(lambda: self.runSimpleCalibrateAnalysis(setupObject))


    def combo_chosen(self):
        self.iterLabel.setEnabled(True)
        self.iterLineEdit.setEnabled(True)
        self.runLabel.setEnabled(True)
        self.runLineEdit.setEnabled(True)
        self.boundLabel.setEnabled(True)
        self.boundLineEdit.setEnabled(True)
        parameterText = self.paraComboBox.currentText()
        if parameterText == 'Number of iterations':
            self.iterLabel.setEnabled(False)
            self.iterLineEdit.setEnabled(False)
        elif parameterText == 'Number of runs':
            self.runLabel.setEnabled(False)
            self.runLineEdit.setEnabled(False)
        elif parameterText == 'BLM':
            self.boundLabel.setEnabled(False)
            self.boundLineEdit.setEnabled(False)


    def saveResultsFile(self):
        (resultsFilePath, fileTypeDetailsText) = QFileDialog.getSaveFileName(self, 'Save Calibration results file', '*.csv')
        self.resultsLineEdit.setText(resultsFilePath)


    def runSimpleCalibrateAnalysis(self, setupObject):
        calibrateRawParameterDict = makeMarxanCalibrateRawParameterDict(self)
        checkSimpleCalibrateAnalysisParameters(self, setupObject, calibrateRawParameterDict)