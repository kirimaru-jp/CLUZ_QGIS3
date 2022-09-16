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

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QApplication, QDialog, QFileDialog, QTableWidgetItem
from qgis.PyQt.QtGui import QColor
from PyQt5 import QtCore, QtGui, QtWidgets

from qgis.core import QgsGeometry, QgsVectorLayer, QgsFeatureRequest
from qgis.utils import iface

import csv
import os

from .cluz_make_file_dicts import updateTargetCSVFromTargetDict, returnRoundedValue
from .cluz_functions7 import changeStatusPuLayer, updateTargetDictWithChanges, undoStatusChangeInPuLayer, calcChangeAbundDict, returnTargetsMetTuple, makeIdentDict
from .cluz_messages import warningMessage
from .cluz_dialog3_code import returnConTotDict, updateConTotFieldsTargetDict


class QCustomTableWidgetItem (QtWidgets.QTableWidgetItem): # Designed so column sort is based on value of number, not string of number
    def __init__ (self, value):
        super(QCustomTableWidgetItem, self).__init__(str('%s' % value))

    def __lt__ (self, other):
        if isinstance(other, QCustomTableWidgetItem):
            selfDataValue  = float(self.data(QtCore.Qt.EditRole))
            otherDataValue = float(other.data(QtCore.Qt.EditRole))
            return selfDataValue < otherDataValue
        else:
            return QtGui.QTableWidgetItem.__lt__(self, other)


#### Produce target table ###

def addTargetTableData(targetTable, setupObject):
    pcValueUpdate = False
    targetDialogRowList = setupObject.targetDialogRowList
    targetHeaderList = targetDialogRowList.pop(0)
    targetDialogRowList.sort()
    lowerHeaderList = list()
    for aHeader in targetHeaderList:
        lowerHeaderList.append(aHeader.lower())

    targetTable.targetTableWidget.clear()
    targetTable.targetTableWidget.setColumnCount(len(targetHeaderList))
    insertRowNumber = 0
    for aRow in targetDialogRowList:
        pcValue = aRow[lowerHeaderList.index('pc_target')]
        targetValue = float(aRow[lowerHeaderList.index('target')])
        consValue = float(aRow[lowerHeaderList.index('ear+cons')])

        if targetValue <= 0:
            limboPCValue = '-1'
        else:
            limboPCValue = consValue / targetValue
            limboPCValue *= 100
            limboPCValue = returnRoundedValue(setupObject, limboPCValue)

        if float(limboPCValue) != float(pcValue):
            pcValueUpdate = True
        aRow[lowerHeaderList.index('pc_target')] = limboPCValue

        addTargetTableRow(targetTable, setupObject, aRow, targetHeaderList, [], insertRowNumber)
        insertRowNumber += 1

    targetTable.targetTableWidget.setHorizontalHeaderLabels(targetHeaderList)

    for aColValue in range(len(targetHeaderList)):
        targetTable.targetTableWidget.resizeColumnToContents(aColValue)

    if pcValueUpdate:
        updateTargetCSVFromTargetDict(setupObject, setupObject.targetDict)


def addTargetTableRow(targetTable, setupObject, aRow, targetHeaderList, decPrecHeaderNameList, insertRowNumber):
    targetTable.targetTableWidget.insertRow(insertRowNumber)
    for aColValue in range(len(targetHeaderList)):
        headerName = targetHeaderList[aColValue].lower()
        tableValue = aRow[aColValue]
        if headerName in decPrecHeaderNameList:
            tableValue = round(float(tableValue), setupObject.decimalPlaces)
            tableValue = format(tableValue, '.' + str(setupObject.decimalPlaces) + 'f')
        if headerName in setupObject.numericColsList:
            targTableItem = QCustomTableWidgetItem(tableValue)
        else:
            targTableItem = QTableWidgetItem(str(tableValue))
        if headerName == 'target':
            targetValue = tableValue
        elif headerName == 'ear+cons':
            conservedValue = tableValue
        if headerName == 'pc_target' and str(tableValue) == '-1':
            targTableItem.setForeground(QColor.fromRgb(128, 128, 128))
        elif headerName == 'pc_target' and float(tableValue) >= 0:
            if float(conservedValue) < float(targetValue):
                targTableItem.setForeground(QColor.fromRgb(255, 0, 0))
            else:
                targTableItem.setForeground(QColor.fromRgb(0, 102, 51))

        targetTable.targetTableWidget.setItem(insertRowNumber, aColValue, targTableItem)

        targetTable.targetTableWidget.horizontalHeader().setStyleSheet(setupObject.TableHeadingStyle)
        targetTable.targetTableWidget.verticalHeader().hide()


def targetDialogKeyPressEvent(targetDialog, e): # http://stackoverflow.com/questions/24971305/copy-pyqt-table-selection-including-column-and-row-headers
    if e.modifiers() & Qt.ControlModifier:
        selected = targetDialog.targetTableWidget.selectedRanges()
        if e.key() == Qt.Key_C: #copy
            s = ''
            for r in range(selected[0].topRow(), selected[0].bottomRow() + 1):
                for c in range(selected[0].leftColumn(), selected[0].rightColumn()+1):
                    try:
                        s += str(targetDialog.targetTableWidget.item(r, c).text()) + '\t'
                    except AttributeError:
                        s += '\t'
                s = s[:-1] + '\n' #eliminate last '\t'
            targetDialog.clip.setText(s)


#### Produce abundance table ###

def loadAbundSelectFeatureList(abundSelectTable, setupObject):
    featIDList = list(setupObject.targetDict.keys())
    featIDList.sort()
    featStringList = list()
    featStringDict = dict()
    for aFeat in featIDList:
        aString = str(aFeat) + ' - ' + setupObject.targetDict[aFeat][0]
        featStringList.append(aString)
        featStringDict[aString] = aFeat
    abundSelectTable.featListWidget.addItems(featStringList)

    return featStringDict


def loadAbundDictData(abundTable, setupObject, selectedFeatIDList):
    decPrec = setupObject.decimalPlaces
    abundPUKeyDict = setupObject.abundPUKeyDict
    featSet = set(selectedFeatIDList)
    abundHeaderList = ['PU_ID']
    for aFeatID in featSet:
        abundHeaderList.append('F_' + str(aFeatID))
    abundTable.abundTableWidget.clear()
    abundTable.abundTableWidget.setColumnCount(len(abundHeaderList))

    insertRowNumber = 0
    for puID in abundPUKeyDict:
        abundTable.abundTableWidget.insertRow(insertRowNumber)
        zeroValue = round(0.0, decPrec)
        zeroValue = format(zeroValue, '.' + str(decPrec) + 'f')
        blankString = str(zeroValue)
        puStringList = [blankString] * len(featSet)
        puAbundDict = abundPUKeyDict[puID]
        for featID in puAbundDict:
            if featID in featSet:
                featAmount = puAbundDict[featID]
                featAmount = round(float(featAmount), decPrec)
                featAmount = format(featAmount, '.' + str(decPrec) + 'f')
                featIndex = list(featSet).index(featID)
                puStringList[featIndex] = str(featAmount)
        puStringList.insert(0, str(puID))

        for aColValue in range(len(puStringList)):
            featValue = puStringList[aColValue]
            abundTableItem = QCustomTableWidgetItem(featValue)
            abundTable.abundTableWidget.setItem(insertRowNumber, aColValue, abundTableItem)
        insertRowNumber += 1

    abundTable.abundTableWidget.setHorizontalHeaderLabels(abundHeaderList)

    for aColValue in range(len(abundHeaderList)):
        abundTable.abundTableWidget.resizeColumnToContents(aColValue)

        abundTable.abundTableWidget.horizontalHeader().setStyleSheet(setupObject.TableHeadingStyle)
        abundTable.abundTableWidget.verticalHeader().hide()


def abundDialogKeyPressEvent(abundDialog, e): # http://stackoverflow.com/questions/24971305/copy-pyqt-table-selection-including-column-and-row-headers
    if e.modifiers() & Qt.ControlModifier:
        selected = abundDialog.abundTableWidget.selectedRanges()
        if e.key() == Qt.Key_C: #copy
            s = ''
            for r in range(selected[0].topRow(), selected[0].bottomRow() + 1):
                for c in range(selected[0].leftColumn(), selected[0].rightColumn()+1):
                    try:
                        s += str(abundDialog.abundTableWidget.item(r, c).text()) + '\t'
                    except AttributeError:
                        s += '\t'
                s = s[:-1] + '\n' #eliminate last '\t'
            abundDialog.clip.setText(s)


def changeStatusofPULayer_UpdateTargetTable(changeStatusDialog, setupObject):
    if changeStatusDialog.availableButton.isChecked():
        statusType = 'Available'
    elif changeStatusDialog.earmarkedButton.isChecked():
        statusType = 'Earmarked'
    elif changeStatusDialog.conservedButton.isChecked():
        statusType = 'Conserved'
    else :
        statusType = 'Excluded'

    changeLockedPUsBool = changeStatusDialog.changeCheckBox.isChecked()

    selectedPUIDStatusDict = changeStatusPuLayer(setupObject, statusType, changeLockedPUsBool)
    changeAbundDict = calcChangeAbundDict(setupObject, selectedPUIDStatusDict, statusType)
    targetDict = updateTargetDictWithChanges(setupObject, changeAbundDict)
    setupObject.targetDict = targetDict
    updateTargetCSVFromTargetDict(setupObject, targetDict)
    (targetsMetCount, targetCount) = returnTargetsMetTuple(setupObject)
    changeStatusDialog.targetsMetLabel.setText('Targets met: ' + str(targetsMetCount) + ' of ' + str(targetCount))

    setupObject.selectedPUIDStatusDict = selectedPUIDStatusDict
    changeStatusDialog.undoButton.setEnabled(True)


def undoStatusofPULayer_UpdateTargetTable(changeStatusDialog, setupObject):
    undoStatusChangeInPuLayer(setupObject)
    newConTotDict = returnConTotDict(setupObject)
    targetDict = updateConTotFieldsTargetDict(setupObject, newConTotDict)
    updateTargetCSVFromTargetDict(setupObject, targetDict)
    setupObject.targetDict = targetDict

    (targetsMetCount, targetCount) = returnTargetsMetTuple(setupObject)
    changeStatusDialog.targetsMetLabel.setText('Targets met: ' + str(targetsMetCount) + ' of ' + str(targetCount))

    setupObject.selectedPUIDStatusDict = 'blank'
    changeStatusDialog.undoButton.setEnabled(False)
    iface.mapCanvas().refresh()


######################## Produce Met dialog ##########################

def loadMarxanResultsMetDialog(MetDialog, setupObject):
    targetMetDict, targetMetHeaderList = createTargetMetDict(setupObject)
    targetMetDict = checkAddFeatureNamesToMarxanResultsMetDialog(setupObject, targetMetDict)

    targetIDList = list(targetMetDict.keys())
    targetIDList.sort()

    MetDialog.metTableWidget.clear()
    MetDialog.metTableWidget.setColumnCount(len(targetMetHeaderList))

    insertRowNumber = 0
    for aFeat in targetIDList:
        MetDialog.metTableWidget.insertRow(insertRowNumber)
        aRowList = targetMetDict[aFeat]
        aRowList.insert(0, aFeat)
        for aColValue in range(len(targetMetHeaderList)):
            aColName = targetMetHeaderList[aColValue]
            featValue = aRowList[aColValue]
            if aColName in ['Feature Name', 'Target Met']:
                metTableItem = QTableWidgetItem(str(featValue))
            else:
                metTableItem = QCustomTableWidgetItem(featValue)
            MetDialog.metTableWidget.setItem(insertRowNumber,aColValue,metTableItem)

        insertRowNumber += 1

        MetDialog.metTableWidget.setHorizontalHeaderLabels(targetMetHeaderList)

    for aColValue in range(len(targetMetHeaderList)):
        MetDialog.metTableWidget.resizeColumnToContents(aColValue)

    MetDialog.metTableWidget.horizontalHeader().setStyleSheet(setupObject.TableHeadingStyle)
    MetDialog.metTableWidget.verticalHeader().hide()


def checkAddFeatureNamesToMarxanResultsMetDialog(setupObject, targetMetDict):
    warningBool = False
    for featID in targetMetDict:
        featList = targetMetDict[featID]
        if featList != setupObject.targetDict[featID][0]:
            featList[0] = setupObject.targetDict[featID][0]
            targetMetDict[featID] = featList
            warningBool = True

    if warningBool:
        warningMessage('Updated Marxan results output', 'The Marxan results ("..._mvbest.txt") file did not include the feature names so these have been added from the CLUZ target file.')

    return targetMetDict


def createTargetMetDict(setupObject):
    targetMetDict = dict()
    with open(setupObject.outputPath + os.sep + setupObject.outputName + '_mvbest.txt', 'rt') as f:
        targetMetReader = csv.reader(f)
        targetMetHeaderList = next(targetMetReader, None)
        for row in targetMetReader:
            puID = int(row.pop(0))
            targetMetDict[puID] = row

    return targetMetDict, targetMetHeaderList


def metDialogKeyPressEvent(MetDialog, e): # http://stackoverflow.com/questions/24971305/copy-pyqt-table-selection-including-column-and-row-headers
    if e.modifiers() & Qt.ControlModifier:
        selected = MetDialog.metTableWidget.selectedRanges()
        if e.key() == Qt.Key_C: #copy
            s = ''
            for r in range(selected[0].topRow(), selected[0].bottomRow() + 1):
                for c in range(selected[0].leftColumn(), selected[0].rightColumn()+1):
                    try:
                        s += str(MetDialog.metTableWidget.item(r, c).text()) + '\t'
                    except AttributeError:
                        s += '\t'
                s = s[:-1] + '\n' #eliminate last '\t'
            MetDialog.clip.setText(s)


################### Identify features in planning unit ###########################
def returnPointPUIDList(setupObject, point):
    pointPUIDList = list()
    pntGeom = QgsGeometry.fromPointXY(point)

    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    puProvider = puLayer.dataProvider()
    puIdFieldOrder = puProvider.fieldNameIndex('Unit_ID')

    selectList = list()
    for feature in puLayer.getFeatures():
        if feature.geometry().intersects(pntGeom):
            selectList.append(feature.id())
    if len(selectList) > 0:
        featID = selectList[0]
        puRequest = QgsFeatureRequest().setFilterFids([featID])
        for puFeature in puLayer.getFeatures(puRequest):
            puAttributes = puFeature.attributes()
            puID = puAttributes[puIdFieldOrder]
            pointPUIDList.append(puID)

    return pointPUIDList


def makeIdentifyData(setupObject, selectedPUIDList):
    identDict = dict()
    targetMetDict = dict()
    for puID in selectedPUIDList:
        try:
            puAbundDict = setupObject.abundPUKeyDict[puID]
            identDict, targetMetDict = makeIdentDict(setupObject.targetDict, puAbundDict)
        except KeyError:
            pass

    return identDict, targetMetDict


def setIdentifyDialogWindowTitle(selectedPUIDList, identDict):
    titleString = 'No planning unit selected'
    if len(selectedPUIDList) > 0:
        puID = selectedPUIDList[0]
        if len(identDict) > 0:
            titleString = 'Planning unit ' + str(puID) + ': list of features'
        else:
            titleString = 'Planning unit ' + str(puID) + ': does not contain any features'

    return titleString


def addIdentifyDataToTableWidget(identifyTableWidget, setupObject, targetMetDict, identDict):
    featIDList = list(identDict.keys())
    featIDList.sort()
    for aRow in range(0, len(featIDList)):
        identifyTableWidget.insertRow(aRow)
        featID = featIDList[aRow]
        featIdentifyList = identDict[featID]
        for aCol in range(0, len(featIdentifyList)):
            featValue = featIdentifyList[aCol]
            featIDItem = QTableWidgetItem(featValue)
            if aCol == 6:
                targetMetStatus = targetMetDict[featID]
                if targetMetStatus == 'Met':
                    featIDItem.setForeground(QColor.fromRgb(0, 102, 51))
                elif targetMetStatus == 'Not met':
                    featIDItem.setForeground(QColor.fromRgb(255, 0, 0))
                else:
                    featIDItem.setForeground(QColor.fromRgb(128, 128, 128))
            identifyTableWidget.setItem(aRow, aCol, featIDItem)

    identifyTableWidget.horizontalHeader().setStyleSheet(setupObject.TableHeadingStyle)
    identifyTableWidget.verticalHeader().hide()


def identifyDialogKeyPressEvent(identifyDialog, e): # http://stackoverflow.com/questions/24971305/copy-pyqt-table-selection-including-column-and-row-headers
    if e.modifiers() & Qt.ControlModifier:
        selected = identifyDialog.identifyTableWidget.selectedRanges()
        if e.key() == Qt.Key_C: #copy
            s = ''
            for r in range(selected[0].topRow(), selected[0].bottomRow() + 1):
                for c in range(selected[0].leftColumn(), selected[0].rightColumn()+1):
                    try:
                        s += str(identifyDialog.identifyTableWidget.item(r, c).text()) + '\t'
                    except AttributeError:
                        s += '\t'
                s = s[:-1] + '\n' #eliminate last '\t'
            identifyDialog.clip.setText(s)