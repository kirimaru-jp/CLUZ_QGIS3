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

from qgis.PyQt.QtWidgets import QDialog, QFileDialog, QLabel, QTableWidgetItem


import os
import sys

from cluz_form_zones_inputs import Ui_zonesInputsDialog
from cluz_form_zones_marxan import Ui_zonesMarxanDialog

from .cluz_setup import updateClzSetupFile
from .cluz_dialog5_code import check_LoadSummedMarxanResult, setInitialValuesCalibrateDialog, makeMarxanCalibrateRawParameterDict, check_LoadBestMarxanResult, makeMarxanRawParameterDict
from .cluz_dialog5_code import returnMarxanInputValuesOKBool, setDialogParameters, checkSimpleCalibrateAnalysisParameters, launchSingleMarxanAnalysis, launchMultiMarxanAnalysis, returnInitialFieldNames, checkMarxanFilesExistBool
from .zcluz_display import displayZonesSFLayer, removePreviousZonesMarxanLayers, reloadZonesPULayer, displayZonesBestOutput
from .zcluz_functions5 import createZonesFeatDatFile, createZonesTargetDatFile, createZonesPropDatFile, createZonesBLMFile
from .zcluz_functions5 import createZonesPuDatFile, createZonesPUStatusDict, createPuLockDatFile, createPuZoneDatFile
from .zcluz_functions5 import createCostsDatFile, createZonesDatFile, createZonecostDatFile
from .cluz_functions5 import createBoundDatFile
from .zcluz_functions5 import zonesMarxanUpdateSetupObject, addBestZonesMarxanOutputToPUShapefile, addSummedZonesMarxanOutputToPUShapefile
from .zcluz_dialog5_code import makeZonesMarxanRawParameterDict, returnZonesMarxanInputValuesOKBool, checkZonesMarxanFilesExistBool, launchZonesMarxanAnalysis, setZonesDialogParameters, makeZonesMarxanParameterDict
from .cluz_messages import criticalMessage, successMessage


class zonesInputsDialog(QDialog, Ui_zonesInputsDialog):
    def __init__(self, iface, setupObject):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.boundextBox.setEnabled(False)
        self.okButton.clicked.connect(lambda: self.setCreateZonesMarxanInputFiles(setupObject))


    def setCreateZonesMarxanInputFiles(self, setupObject):
        messageStringList = list()
        if self.targetBox.isChecked():
            createZonesFeatDatFile(setupObject)
            messageStringList.append('feat.dat')
            createZonesTargetDatFile(setupObject)
            messageStringList.append('zonetarget.dat')
            createZonesPropDatFile(setupObject)
            messageStringList.append('zonecontrib.dat')

        if self.puBox.isChecked():
            createZonesPuDatFile(setupObject)
            messageStringList.append('pu.dat')
            zonesPUStatusDict = createZonesPUStatusDict(setupObject)
            createPuLockDatFile(setupObject, zonesPUStatusDict)
            messageStringList.append('pulock.dat')
            createPuZoneDatFile(setupObject, zonesPUStatusDict)
            messageStringList.append('puzone.dat')

        if self.zonesBox.isChecked():
            createZonesDatFile(setupObject)
            messageStringList.append('zones.dat')
            createCostsDatFile(setupObject)
            messageStringList.append('costs.dat')
            createZonecostDatFile(setupObject)
            messageStringList.append('zonecost.dat')

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


class zonesMarxanDialog(QDialog, Ui_zonesMarxanDialog):
    def __init__(self, iface, setupObject, targetsMetAction):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        setZonesDialogParameters(self, setupObject)
        self.startButton.clicked.connect(lambda: self.runZonesMarxan(setupObject, targetsMetAction))


    def runZonesMarxan(self, setupObject, targetsMetAction):
        zonesMarxanRawParameterDict = makeZonesMarxanRawParameterDict(self, setupObject)
        zonesMarxanInputValuesOKBool = returnZonesMarxanInputValuesOKBool(zonesMarxanRawParameterDict)
        zonesMarxanFilesExistBool = checkZonesMarxanFilesExistBool(setupObject)
        if zonesMarxanInputValuesOKBool and zonesMarxanFilesExistBool:
            zonesMarxanParameterDict = makeZonesMarxanParameterDict(setupObject, zonesMarxanRawParameterDict)
            createZonesFeatDatFile(setupObject)
            if self.boundZoneCheckBox:
                setupObject = createZonesBLMFile(self, setupObject)

            setupObject = zonesMarxanUpdateSetupObject(self, setupObject, zonesMarxanParameterDict)
            updateClzSetupFile(setupObject, True) #saveSuccessfulBool = True
            self.close()

            bestOutputFile, summedOutputFile = launchZonesMarxanAnalysis(setupObject, zonesMarxanParameterDict)

            addBestZonesMarxanOutputToPUShapefile(setupObject, bestOutputFile, 'Best')
            addSummedZonesMarxanOutputToPUShapefile(setupObject, summedOutputFile)

            reloadZonesPULayer(setupObject)
            removePreviousZonesMarxanLayers()
            displayZonesBestOutput(setupObject, zonesMarxanParameterDict)
            displayZonesSFLayer(setupObject, zonesMarxanParameterDict)

            targetsMetAction.setEnabled(True)


# class loadDialog(QDialog, Ui_loadDialog):
#     def __init__(self, iface, setupObject):
#         QDialog.__init__(self)
#         self.iface = iface
#         self.setupUi(self)
#
#         self.bestLabel.setVisible(False)
#         self.bestLineEdit.setVisible(False)
#         self.bestNameLineEdit.setVisible(False)
#         self.bestButton.setVisible(False)
#         self.summedLabel.setVisible(False)
#         self.summedLineEdit.setVisible(False)
#         self.summedNameLineEdit.setVisible(False)
#         self.summedButton.setVisible(False)
#
#         bestName, summedName = returnInitialFieldNames(setupObject)
#         self.bestNameLineEdit.setText(bestName)
#         self.summedNameLineEdit.setText(summedName)
#
#         self.bestButton.clicked.connect(self.setBestPath)
#         self.summedButton.clicked.connect(self.setSummedPath)
#         self.okButton.clicked.connect(lambda: self.loadPreviousMarxanResults(setupObject))
#
#
#     def setBestPath(self):
#         (bestPathNameText, fileTypeDetailsText) = QFileDialog.getOpenFileName(self, 'Select Marxan best portfolio output', '*.txt')
#         if bestPathNameText is not None:
#             self.bestLineEdit.setText(bestPathNameText)
#
#
#     def setSummedPath(self):
#         (summedPathNameText, fileTypeDetailsText) = QFileDialog.getOpenFileName(self, 'Select Marxan summed solution output', '*.txt')
#         if summedPathNameText is not None:
#             self.summedLineEdit.setText(summedPathNameText)
#
#
#     def loadPreviousMarxanResults(self, setupObject):
#         check_LoadBestMarxanResult(self, setupObject)
#         check_LoadSummedMarxanResult(self, setupObject)
#
#
# class calibrateDialog(QDialog, Ui_calibrateDialog):
#     def __init__(self, iface, setupObject):
#         QDialog.__init__(self)
#         self.iface = iface
#         self.setupUi(self)
#         setInitialValuesCalibrateDialog(self, setupObject)
#         self.paraComboBox.activated.connect(self.combo_chosen)
#
#         self.saveResultsButton.clicked.connect(self.saveResultsFile)
#         self.runButton.clicked.connect(lambda: self.runSimpleCalibrateAnalysis(setupObject))
#
#
#     def combo_chosen(self):
#         self.iterLabel.setEnabled(True)
#         self.iterLineEdit.setEnabled(True)
#         self.runLabel.setEnabled(True)
#         self.runLineEdit.setEnabled(True)
#         self.boundLabel.setEnabled(True)
#         self.boundLineEdit.setEnabled(True)
#         parameterText = self.paraComboBox.currentText()
#         if parameterText == 'Number of iterations':
#             self.iterLabel.setEnabled(False)
#             self.iterLineEdit.setEnabled(False)
#         elif parameterText == 'Number of runs':
#             self.runLabel.setEnabled(False)
#             self.runLineEdit.setEnabled(False)
#         elif parameterText == 'BLM':
#             self.boundLabel.setEnabled(False)
#             self.boundLineEdit.setEnabled(False)
#
#
#     def saveResultsFile(self):
#         (resultsFilePath, fileTypeDetailsText) = QFileDialog.getSaveFileName(self, 'Save Calibration results file', '*.csv')
#         self.resultsLineEdit.setText(resultsFilePath)
#
#
#     def runSimpleCalibrateAnalysis(self, setupObject):
#         calibrateRawParameterDict = makeMarxanCalibrateRawParameterDict(self)
#         checkSimpleCalibrateAnalysisParameters(self, setupObject, calibrateRawParameterDict)