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

from PyQt5.QtCore import Qt
from qgis.PyQt.QtWidgets import QApplication, QDialog, QFileDialog, QTableWidgetItem
from qgis.gui import QgsMapTool
from qgis.core import *

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")
from cluz_form_target import Ui_targetDialog
from cluz_form_abund_select import Ui_abundSelectDialog
from cluz_form_abund import Ui_abundDialog
from cluz_form_met import Ui_metDialog
from cluz_form_change import Ui_ChangeStatusDialog
from cluz_form_identify import Ui_identifyDialog

from .cluz_dialog7_code import targetDialogKeyPressEvent, loadMarxanResultsMetDialog, metDialogKeyPressEvent, loadAbundSelectFeatureList, setIdentifyDialogWindowTitle, addTargetTableData, addIdentifyDataToTableWidget, undoStatusofPULayer_UpdateTargetTable, identifyDialogKeyPressEvent, returnPointPUIDList, changeStatusofPULayer_UpdateTargetTable, loadAbundDictData, abundDialogKeyPressEvent, makeIdentifyData
from .cluz_functions7 import returnTargetsMetTuple
from .cluz_make_file_dicts import makeTargetDict, makeTargetDialogRowList
from .cluz_display import updatePULayerToShowChangesByShiftingExtent


######################## Target table ##########################

class targetDialog(QDialog, Ui_targetDialog):
    def __init__(self, iface, setupObject):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.clip = QApplication.clipboard()
        targetDict = makeTargetDict(setupObject)
        targetDialogRowList, numericColsList = makeTargetDialogRowList(setupObject)
        if targetDict != 'blank':
            setupObject.targetDict = targetDict
            setupObject.targetDialogRowList = targetDialogRowList
            setupObject.numericColsList = numericColsList
            self.loadTargetDictData(setupObject)

    def loadTargetDictData(self, setupObject):
        addTargetTableData(self, setupObject)


    def keyPressEvent(self, e):
        targetDialogKeyPressEvent(self, e)


##################### Abund table #######################################


class abundSelectDialog(QDialog, Ui_abundSelectDialog):
    def __init__(self, iface, setupObject):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        featStringDict = loadAbundSelectFeatureList(self, setupObject)
        self.okButton.clicked.connect(lambda: self.displayAbundValues(setupObject, featStringDict))


    def displayAbundValues(self, setupObject, featStringDict):
        selectedFeatIDList = [featStringDict[item.text()] for item in self.featListWidget.selectedItems()]
        if len(selectedFeatIDList) == 0:
            selectedFeatIDList = setupObject.targetDict.keys()
        self.close()

        self.abundDialog = abundDialog(self, setupObject, selectedFeatIDList)
        self.abundDialog.show()
        self.abundDialog.exec_()


class abundDialog(QDialog, Ui_abundDialog):
    def __init__(self, iface, setupObject, selectedFeatIDList):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.clip = QApplication.clipboard()
        loadAbundDictData(self, setupObject, selectedFeatIDList)


    def keyPressEvent(self, e):
        abundDialogKeyPressEvent(self, e)


class IdentifyTool(QgsMapTool):
    def __init__(self, canvas, setupObject):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.setupObject = setupObject

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()

        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

    def canvasReleaseEvent(self, event):
        #Get the click
        x = event.pos().x()
        y = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

        self.identifyDialog = identifyDialog(self, self.setupObject, point)
        # show the dialog
        self.identifyDialog.show()
        # Run the dialog event loop
        self.identifyDialog.exec_()

    def activate(self):
        pass

    def deactivate(self):
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True


class metDialog(QDialog, Ui_metDialog):
    def __init__(self, iface, setupObject):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.clip = QApplication.clipboard()
        loadMarxanResultsMetDialog(self, setupObject)
        self.setWindowTitle('Marxan Targets Met table for analysis ' + setupObject.outputName)

    def keyPressEvent(self, e):
        metDialogKeyPressEvent(self, e)


class changeStatusDialog(QDialog, Ui_ChangeStatusDialog):
    def __init__(self, iface, setupObject):
        QDialog.__init__(self, None, Qt.WindowStaysOnTopHint)
        self.iface = iface
        self.setupUi(self)

        targetsMetCount, targetCount = returnTargetsMetTuple(setupObject)
        self.targetsMetLabel.setText("Targets met: " + str(targetsMetCount) + " of " + str(targetCount))
        self.undoButton.setEnabled(False)
        self.changeButton.clicked.connect(lambda: self.changeStatus(setupObject))
        self.undoButton.clicked.connect(lambda: self.undoStatusChange(setupObject))


    def changeStatus(self, setupObject):
        changeStatusofPULayer_UpdateTargetTable(self, setupObject)


    def undoStatusChange(self, setupObject):
        undoStatusofPULayer_UpdateTargetTable(self, setupObject)
        updatePULayerToShowChangesByShiftingExtent()


class identifyDialog(QDialog, Ui_identifyDialog):
    def __init__(self, iface, setupObject, point):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.clip = QApplication.clipboard()

        selectedPUIDList = returnPointPUIDList(setupObject, point)
        identDict, targetMetDict = makeIdentifyData(setupObject, selectedPUIDList)
        titleString = setIdentifyDialogWindowTitle(selectedPUIDList, identDict)

        if len(identDict.keys()) > 0:
            self.identDict = identDict
            self.targetMetDict = targetMetDict
            self.showIdentifyData(setupObject)
            self.setWindowTitle(titleString)

        self.setWindowTitle(titleString)

    def showIdentifyData(self, setupObject):
        self.identifyTableWidget.clear()
        self.identifyTableWidget.setColumnCount(7)
        addIdentifyDataToTableWidget(self.identifyTableWidget, setupObject, self.targetMetDict, self.identDict)

        headerList = ['ID ', 'Name ', 'Amount ', 'As % of total ', 'Target ', 'As % of target ', '% of target currently met ']
        self.identifyTableWidget.setHorizontalHeaderLabels(headerList)
        for aColValue in range(len(headerList)):
            self.identifyTableWidget.resizeColumnToContents(aColValue)

    def keyPressEvent(self, e):
        identifyDialogKeyPressEvent(self, e)