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
from cluz_form_minpatch import Ui_minpatchDialog

from .cluz_setup import MinPatchObject

from .cluz_mpmain import runMinPatch
from .cluz_mpsetup import makeMinpatchDataDict
from .cluz_messages import warningMessage
from .cluz_dialog6_code import makeMarxanFileList, checkMinPatchFile, checkMinPatchBLMValue, checkMinPatchSelectedItemsList


class minpatchDialog(QDialog, Ui_minpatchDialog):
    def __init__(self, iface, setupObject):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        inputText = 'Marxan input folder: ' + setupObject.inputPath
        self.inputLabel.setText(inputText)
        outputText = 'Marxan output folder: ' + setupObject.outputPath
        self.outputLabel.setText(outputText)

        self.detailsLineEdit.setText('C://Users//rjsmi//Dropbox//new_NE_CLUZ_analysis//input//minpatch.dat')
        self.blmLineEdit.setText('0')

        marxanFileList = makeMarxanFileList(setupObject)
        if len(marxanFileList) > 0:
            self.fileListWidget.addItems(marxanFileList)
        else:
            self.startButton.setEnabled(False)
            warningMessage('No files found', 'The specified Marxan output folder does not contain any individual portfolio files that can be analysed in MinPatch.')

        self.browseButton.clicked.connect(self.setMinpatchDetailFile)
        self.startButton.clicked.connect(lambda: self.startMinPatch(setupObject))


    def setMinpatchDetailFile(self):
        (minpatchDetailPathNameText, fileTypeDetailsText) = QFileDialog.getOpenFileName(self, 'Select MinPatch details file', '*.dat')
        self.detailsLineEdit.setText(minpatchDetailPathNameText)


    def startMinPatch(self, setupObject):

        minpatchObject = MinPatchObject()
        runMinPatchBool, minpatchObject = checkMinPatchFile(self, minpatchObject)
        runMinPatchBool, minpatchObject = checkMinPatchBLMValue(self, minpatchObject, runMinPatchBool)
        runMinPatchBool, minpatchObject = checkMinPatchSelectedItemsList (self, minpatchObject, runMinPatchBool)

        minpatchObject.removeBool = self.removeCheckBox.isChecked()
        minpatchObject.addBool = self.addCheckBox.isChecked()
        minpatchObject.whittleBool = self.whittleCheckBox.isChecked()

        if runMinPatchBool:
            minpatchDataDict, setupOKBool = makeMinpatchDataDict(setupObject, minpatchObject)
            self.close()
            if setupOKBool:
                runMinPatch(setupObject, minpatchObject, minpatchDataDict)
