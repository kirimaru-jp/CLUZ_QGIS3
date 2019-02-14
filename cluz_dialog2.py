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

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")
from cluz_form_create import Ui_createDialog
from cluz_form_convert_vec import Ui_convertVecDialog
from cluz_form_convert_csv import Ui_convertCsvDialog

from .cluz_functions2 import makeCsvAddAbundDict
from .cluz_dialog2_code import check_MakeNewCLUZFiles, checkAddLayerListConvertVecDialog, checkLayerFactor, check_AddCsvFilePath, checkConvFactor, create_UpdateAbundDataFromVecFile
from .cluz_dialog2_code import checkConvFactorConvertVec, addCSVDictToAbundDict_UpdatePuvspr2TargetFiles, checkLayerFactorConvertVec, makeErrorLayerString
from .cluz_messages import criticalMessage


class createDialog(QDialog, Ui_createDialog):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.convLineEdit.setText('1')

        self.puButton.clicked.connect(self.setShapefilePath)
        self.inputButton.clicked.connect(self.setInputPath)
        self.targetButton.clicked.connect(self.setTargetPath)
        self.okButton.clicked.connect(self.createNewCLUZFiles)


    def setShapefilePath(self):
        (shapefilePathNameText, fileTypeDetailsText) = QFileDialog.getOpenFileName(self, 'Select shapefile', '*.shp')
        if shapefilePathNameText is not None:
            self.puLineEdit.setText(shapefilePathNameText)


    def setInputPath(self):
        inputPathNameRawText = QFileDialog.getExistingDirectory(self, 'Select input folder')
        inputPathNameText = os.path.abspath(inputPathNameRawText)
        if inputPathNameText is not None:
            self.inputLineEdit.setText(inputPathNameText)


    def setTargetPath(self):
        (targetPathNameText, fileTypeDetailsText) = QFileDialog.getSaveFileName(self, 'Specify target table name', '*.csv', '*.csv')
        if targetPathNameText is not None:
            self.targetLineEdit.setText(targetPathNameText)


    def createNewCLUZFiles(self):
        check_MakeNewCLUZFiles(self)


class convertVecDialog(QDialog, Ui_convertVecDialog):
    def __init__(self, iface, setupObject):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        checkAddLayerListConvertVecDialog(self)
        self.idfieldLineEdit.setText("ID")
        self.convLineEdit.setText("1")
        self.convLineEdit.setEnabled(False)
        self.convLabel.setEnabled(False)

        self.okButton.clicked.connect(lambda: self.convertLayersToAbundTable(setupObject))


    def convertLayersToAbundTable(self, setupObject):
        layerList, layerFactorCheck = checkLayerFactorConvertVec(self)
        convFactorCheck = checkConvFactorConvertVec(self)

        if layerFactorCheck and convFactorCheck:
            errorLayerList = create_UpdateAbundDataFromVecFile(self, setupObject, layerList)
            if len(errorLayerList) > 0:
                errorLayerString = makeErrorLayerString(errorLayerList)
                criticalMessage('Error processing layers', errorLayerString)


class convertCsvDialog(QDialog, Ui_convertCsvDialog):
    def __init__(self, iface, setupObject):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        self.idfieldComboBox.setEnabled(False)
        self.convLineEdit.setText("1")
        self.convLineEdit.setEnabled(False)
        self.convLabel.setEnabled(False)
        self.noneRadioButton.setChecked(True)

        self.browseButton.clicked.connect(self.setCsvFilePath)
        self.okButton.clicked.connect(lambda: self.convertCSVToAbundTable(setupObject))


    def setCsvFilePath(self):
        (csvPathNameText, fileTypeDetailsText) = QFileDialog.getOpenFileName(self, 'Select CSV file', '*.csv')
        check_AddCsvFilePath(self, csvPathNameText)

    def convertCSVToAbundTable(self, setupObject):
        layerFactorCheck = checkLayerFactor(self)
        convFactorCheck = checkConvFactor(self, layerFactorCheck)

        if layerFactorCheck and convFactorCheck:
            addAbundDict, featIDList, continueBool = makeCsvAddAbundDict(self, setupObject)
            if continueBool:
                addCSVDictToAbundDict_UpdatePuvspr2TargetFiles(setupObject, addAbundDict, featIDList)

        self.close()


