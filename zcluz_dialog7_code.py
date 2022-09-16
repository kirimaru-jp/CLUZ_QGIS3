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

from .cluz_make_file_dicts import returnRoundedValue
from .zcluz_make_file_dicts import updateZonesTargetCSVFromTargetDict
from .zcluz_dialog3_code import returnZonesEarLockTotDict, updateZonesEarLockTotFieldsTargetDict
from .zcluz_functions7 import changeZonesStatusPuLayer, returnSelectedZoneIDFromChangeStatusPanel, returnBeforeAfterPUZonesStatusDicts, makeZonesSelectedStatusBalanceDict, calcZonesChangeAbundDict, updateZonesTargetDictWithChanges #,  undoStatusChangeInPuLayer, calcChangeAbundDict, returnTargetsMetTuple, makeIdentDict
from .zcluz_functions7 import returnZonesMainTargetsMetTuple, returnZonesTargetsMetTuple, zonesSelectUndoPlanningUnits


from .cluz_messages import warningMessage


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

def addZonesTargetTableData(targetTable, setupObject):
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
        earLockValue = float(aRow[lowerHeaderList.index('ear+lock')])

        if targetValue <= 0:
            limboPCValue = '-1'
        else:
            limboPCValue = earLockValue / targetValue
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
        updateZonesTargetCSVFromTargetDict(setupObject, setupObject.targetDict)


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
        elif headerName == 'ear+lock':
            earLockValue = tableValue
        if headerName == 'pc_target' and str(tableValue) == '-1':
            targTableItem.setForeground(QColor.fromRgb(128, 128, 128))
        elif headerName == 'pc_target' and float(tableValue) >= 0:
            if float(earLockValue) < float(targetValue):
                targTableItem.setForeground(QColor.fromRgb(255, 0, 0))
            else:
                targTableItem.setForeground(QColor.fromRgb(0, 102, 51))

        targetTable.targetTableWidget.setItem(insertRowNumber, aColValue, targTableItem)

        targetTable.targetTableWidget.horizontalHeader().setStyleSheet(setupObject.TableHeadingStyle)
        targetTable.targetTableWidget.verticalHeader().hide()


def targetDialogKeyPressEvent(zonesTargetDialog, e): # http://stackoverflow.com/questions/24971305/copy-pyqt-table-selection-including-column-and-row-headers
    if e.modifiers() & Qt.ControlModifier:
        selected = zonesTargetDialog.targetTableWidget.selectedRanges()
        if e.key() == Qt.Key_C: #copy
            s = ''
            for r in range(selected[0].topRow(), selected[0].bottomRow() + 1):
                for c in range(selected[0].leftColumn(), selected[0].rightColumn()+1):
                    try:
                        s += str(zonesTargetDialog.targetTableWidget.item(r, c).text()) + '\t'
                    except AttributeError:
                        s += '\t'
                s = s[:-1] + '\n' #eliminate last '\t'
            zonesTargetDialog.clip.setText(s)


### Produce zones table ###

def addZonesTableData(zonesTable, setupObject):
    zonesHeaderList = ['Id', 'Name']

    zonesTable.zonesTableWidget.clear()
    zonesTable.zonesTableWidget.setColumnCount(len(zonesHeaderList))
    insertRowNumber = 0
    for zoneID in setupObject.zonesDict:
        zonesTable.zonesTableWidget.insertRow(insertRowNumber)
        zoneName = setupObject.zonesDict[zoneID]
        zonesTable.zonesTableWidget.setItem(insertRowNumber, 0, QCustomTableWidgetItem(str(zoneID)))
        zonesTable.zonesTableWidget.setItem(insertRowNumber, 1, QCustomTableWidgetItem(zoneName))
        insertRowNumber += 1

    zonesTable.zonesTableWidget.setHorizontalHeaderLabels(zonesHeaderList)

    for aColValue in range(len(zonesHeaderList)):
        zonesTable.zonesTableWidget.resizeColumnToContents(aColValue)

    zonesTable.zonesTableWidget.horizontalHeader().setStyleSheet(setupObject.TableHeadingStyle)
    zonesTable.zonesTableWidget.verticalHeader().hide()


def zonesDialogKeyPressEvent(zonesDialog, e): # http://stackoverflow.com/questions/24971305/copy-pyqt-table-selection-including-column-and-row-headers
    if e.modifiers() & Qt.ControlModifier:
        selected = zonesDialog.zonesTableWidget.selectedRanges()
        if e.key() == Qt.Key_C: #copy
            s = ''
            for r in range(selected[0].topRow(), selected[0].bottomRow() + 1):
                for c in range(selected[0].leftColumn(), selected[0].rightColumn()+1):
                    try:
                        s += str(zonesDialog.zonesTableWidget.item(r, c).text()) + '\t'
                    except AttributeError:
                        s += '\t'
                s = s[:-1] + '\n' #eliminate last '\t'
            zonesDialog.clip.setText(s)

######################## Produce Met dialog ##########################

def makeZonesNameList(setupObject):
    zonesNameList = list()
    for zoneID in list(setupObject.zonesDict):
        zoneLayerName = 'Zone ' + str(zoneID) + ' - ' + setupObject.zonesDict[zoneID]
        zonesNameList.append(zoneLayerName)

    return zonesNameList

def zonesChangeStatusOfPULayer_UpdateTargetTable(ZonesChangeStatusDialog, setupObject):
    if ZonesChangeStatusDialog.zonesAvailableButton.isChecked():
        statusType = 'Available'
    elif ZonesChangeStatusDialog.zonesEarmarkedButton.isChecked():
        statusType = 'Earmarked'
    elif ZonesChangeStatusDialog.zonesLockedButton.isChecked():
        statusType = 'Locked'
    else :
        statusType = 'Excluded'

    changeLockedPUsBool = ZonesChangeStatusDialog.zonesChangeCheckBox.isChecked()
    selectedZoneID = returnSelectedZoneIDFromChangeStatusPanel(ZonesChangeStatusDialog)

    beforePUZonesStatusDict, afterPUZonesStatusDict = returnBeforeAfterPUZonesStatusDicts(setupObject, statusType, changeLockedPUsBool, selectedZoneID)
    zonesSelectedStatusBalanceDict = makeZonesSelectedStatusBalanceDict(beforePUZonesStatusDict, afterPUZonesStatusDict)
    changeZonesStatusPuLayer(setupObject, afterPUZonesStatusDict)
    zonesChangeAbundDict = calcZonesChangeAbundDict(setupObject, zonesSelectedStatusBalanceDict)
    targetDict = updateZonesTargetDictWithChanges(setupObject, zonesChangeAbundDict)
    setupObject.targetDict = targetDict
    updateZonesTargetCSVFromTargetDict(setupObject, targetDict)

    (mainTargetsMetCount, mainTargetCount) = returnZonesMainTargetsMetTuple(setupObject)
    ZonesChangeStatusDialog.zonesMainTargetsMetLabel.setText('Targets met: ' + str(mainTargetsMetCount) + ' of ' + str(mainTargetCount))
    (zoneTargetsMetCount, zoneTargetCount) = returnZonesTargetsMetTuple(setupObject, selectedZoneID)
    ZonesChangeStatusDialog.zonesZoneTargetsMetLabel.setText('Zone ' + str(selectedZoneID) +' targets met: ' + str(zoneTargetsMetCount) + ' of ' + str(zoneTargetCount))

    setupObject.beforePUZonesStatusDict = beforePUZonesStatusDict
    ZonesChangeStatusDialog.undoButton.setEnabled(True)


def zonesUndoStatusOfPULayer_UpdateTargetTable(ZonesChangeStatusDialog, setupObject):
    selectedZoneID = returnSelectedZoneIDFromChangeStatusPanel(ZonesChangeStatusDialog)
    zonesSelectUndoPlanningUnits(setupObject)
    changeZonesStatusPuLayer(setupObject, setupObject.beforePUZonesStatusDict)
    newConTotDict = returnZonesEarLockTotDict(setupObject)
    targetDict = updateZonesEarLockTotFieldsTargetDict(setupObject, newConTotDict)
    updateZonesTargetCSVFromTargetDict(setupObject, targetDict)
    setupObject.targetDict = targetDict

    (mainTargetsMetCount, mainTargetCount) = returnZonesMainTargetsMetTuple(setupObject)
    ZonesChangeStatusDialog.zonesMainTargetsMetLabel.setText('Targets met: ' + str(mainTargetsMetCount) + ' of ' + str(mainTargetCount))
    (zoneTargetsMetCount, zoneTargetCount) = returnZonesTargetsMetTuple(setupObject, selectedZoneID)
    ZonesChangeStatusDialog.zonesZoneTargetsMetLabel.setText('Zone ' + str(selectedZoneID) +' targets met: ' + str(zoneTargetsMetCount) + ' of ' + str(zoneTargetCount))

    setupObject.beforePUZonesStatusDict = 'blank'
    ZonesChangeStatusDialog.undoButton.setEnabled(False)
    iface.mapCanvas().refresh()


# def loadMarxanResultsMetDialog(MetDialog, setupObject):
#     targetMetDict, targetMetHeaderList = createTargetMetDict(setupObject)
#     targetMetDict = checkAddFeatureNamesToMarxanResultsMetDialog(setupObject, targetMetDict)
#
#     targetIDList = list(targetMetDict.keys())
#     targetIDList.sort()
#
#     MetDialog.metTableWidget.clear()
#     MetDialog.metTableWidget.setColumnCount(len(targetMetHeaderList))
#
#     insertRowNumber = 0
#     for aFeat in targetIDList:
#         MetDialog.metTableWidget.insertRow(insertRowNumber)
#         aRowList = targetMetDict[aFeat]
#         aRowList.insert(0, aFeat)
#         for aColValue in range(len(targetMetHeaderList)):
#             aColName = targetMetHeaderList[aColValue]
#             featValue = aRowList[aColValue]
#             if aColName in ['Feature Name', 'Target Met']:
#                 metTableItem = QTableWidgetItem(str(featValue))
#             else:
#                 metTableItem = QCustomTableWidgetItem(featValue)
#             MetDialog.metTableWidget.setItem(insertRowNumber,aColValue,metTableItem)
#
#         insertRowNumber += 1
#
#         MetDialog.metTableWidget.setHorizontalHeaderLabels(targetMetHeaderList)
#
#     for aColValue in range(len(targetMetHeaderList)):
#         MetDialog.metTableWidget.resizeColumnToContents(aColValue)
#
#     MetDialog.metTableWidget.horizontalHeader().setStyleSheet(setupObject.TableHeadingStyle)
#     MetDialog.metTableWidget.verticalHeader().hide()
#
#
# def checkAddFeatureNamesToMarxanResultsMetDialog(setupObject, targetMetDict):
#     warningBool = False
#     for featID in targetMetDict:
#         featList = targetMetDict[featID]
#         if featList != setupObject.targetDict[featID][0]:
#             featList[0] = setupObject.targetDict[featID][0]
#             targetMetDict[featID] = featList
#             warningBool = True
#
#     if warningBool:
#         warningMessage('Updated Marxan results output', 'The Marxan results ("..._mvbest.txt") file did not include the feature names so these have been added from the CLUZ target file.')
#
#     return targetMetDict
#
#
# def createTargetMetDict(setupObject):
#     targetMetDict = dict()
#     with open(setupObject.outputPath + os.sep + setupObject.outputName + '_mvbest.txt', 'rt') as f:
#         targetMetReader = csv.reader(f)
#         targetMetHeaderList = next(targetMetReader, None)
#         for row in targetMetReader:
#             puID = int(row.pop(0))
#             targetMetDict[puID] = row
#
#     return targetMetDict, targetMetHeaderList
#
#
# def metDialogKeyPressEvent(MetDialog, e): # http://stackoverflow.com/questions/24971305/copy-pyqt-table-selection-including-column-and-row-headers
#     if e.modifiers() & Qt.ControlModifier:
#         selected = MetDialog.metTableWidget.selectedRanges()
#         if e.key() == Qt.Key_C: #copy
#             s = ''
#             for r in range(selected[0].topRow(), selected[0].bottomRow() + 1):
#                 for c in range(selected[0].leftColumn(), selected[0].rightColumn()+1):
#                     try:
#                         s += str(MetDialog.metTableWidget.item(r, c).text()) + '\t'
#                     except AttributeError:
#                         s += '\t'
#                 s = s[:-1] + '\n' #eliminate last '\t'
#             MetDialog.clip.setText(s)
#
#
# ################### Identify features in planning unit ###########################
# def returnPointPUIDList(setupObject, point):
#     pointPUIDList = list()
#     pntGeom = QgsGeometry.fromPointXY(point)
#
#     puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
#     puProvider = puLayer.dataProvider()
#     puIdFieldOrder = puProvider.fieldNameIndex('Unit_ID')
#
#     selectList = list()
#     for feature in puLayer.getFeatures():
#         if feature.geometry().intersects(pntGeom):
#             selectList.append(feature.id())
#     if len(selectList) > 0:
#         featID = selectList[0]
#         puRequest = QgsFeatureRequest().setFilterFids([featID])
#         for puFeature in puLayer.getFeatures(puRequest):
#             puAttributes = puFeature.attributes()
#             puID = puAttributes[puIdFieldOrder]
#             pointPUIDList.append(puID)
#
#     return pointPUIDList
#
#
# def makeIdentifyData(setupObject, selectedPUIDList):
#     identDict = dict()
#     targetMetDict = dict()
#     for puID in selectedPUIDList:
#         try:
#             puAbundDict = setupObject.abundPUKeyDict[puID]
#             identDict, targetMetDict = makeIdentDict(setupObject.targetDict, puAbundDict)
#         except KeyError:
#             pass
#
#     return identDict, targetMetDict
#
#
# def setIdentifyDialogWindowTitle(selectedPUIDList, identDict):
#     titleString = 'No planning unit selected'
#     if len(selectedPUIDList) > 0:
#         puID = selectedPUIDList[0]
#         if len(identDict) > 0:
#             titleString = 'Planning unit ' + str(puID) + ': list of features'
#         else:
#             titleString = 'Planning unit ' + str(puID) + ': does not contain any features'
#
#     return titleString
#
#
# def addIdentifyDataToTableWidget(identifyTableWidget, setupObject, targetMetDict, identDict):
#     featIDList = list(identDict.keys())
#     featIDList.sort()
#     for aRow in range(0, len(featIDList)):
#         identifyTableWidget.insertRow(aRow)
#         featID = featIDList[aRow]
#         featIdentifyList = identDict[featID]
#         for aCol in range(0, len(featIdentifyList)):
#             featValue = featIdentifyList[aCol]
#             featIDItem = QTableWidgetItem(featValue)
#             if aCol == 6:
#                 targetMetStatus = targetMetDict[featID]
#                 if targetMetStatus == 'Met':
#                     featIDItem.setForeground(QColor.fromRgb(0, 102, 51))
#                 elif targetMetStatus == 'Not met':
#                     featIDItem.setForeground(QColor.fromRgb(255, 0, 0))
#                 else:
#                     featIDItem.setForeground(QColor.fromRgb(128, 128, 128))
#             identifyTableWidget.setItem(aRow, aCol, featIDItem)
#
#     identifyTableWidget.horizontalHeader().setStyleSheet(setupObject.TableHeadingStyle)
#     identifyTableWidget.verticalHeader().hide()
#
#
# def identifyDialogKeyPressEvent(identifyDialog, e): # http://stackoverflow.com/questions/24971305/copy-pyqt-table-selection-including-column-and-row-headers
#     if e.modifiers() & Qt.ControlModifier:
#         selected = identifyDialog.identifyTableWidget.selectedRanges()
#         if e.key() == Qt.Key_C: #copy
#             s = ''
#             for r in range(selected[0].topRow(), selected[0].bottomRow() + 1):
#                 for c in range(selected[0].leftColumn(), selected[0].rightColumn()+1):
#                     try:
#                         s += str(identifyDialog.identifyTableWidget.item(r, c).text()) + '\t'
#                     except AttributeError:
#                         s += '\t'
#                 s = s[:-1] + '\n' #eliminate last '\t'
#             identifyDialog.clip.setText(s)