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

from qgis.PyQt.QtCore import Qt, QVariant
from qgis.PyQt.QtWidgets import QTableWidgetItem
from qgis.PyQt.QtGui import QColor

from qgis.core import QgsVectorLayer, QgsField
from qgis.utils import iface

import csv
import os

from .cluz_make_file_dicts import returnRoundedValue, returnLowestUnusedFileNameNumber
from .cluz_functions4 import returnStringAmountPerStatus, makePatchFeatDataDict, produceCountField, produceRestrictedRangeField, makeSFDetailsToPortfolioDict, returnStringShortfall
from .cluz_functions4 import createDistributionMapShapefile, makeFeatIDSetFromFeatTypeSet, makeFullSFValueList, makePatchDictBasedOnDummyZoneFile
from .cluz_messages import clearProgressBar, makeProgressBar, warningMessage
from .cluz_display import displayGraduatedLayer, displayDistributionMaps

#### Display distributions of conservation features ###

def loadDistributionFeatureList(distributionDialog, setupObject):
    featList = list(setupObject.targetDict.keys())
    featList.sort()
    featStringList = list()
    for aFeat in featList:
        aString = str(aFeat) + ' - ' + setupObject.targetDict[aFeat][0]
        featStringList.append(aString)
    distributionDialog.featListWidget.addItems(featStringList)


def setInitialDistribtuionShapeFilePath(distributionDialog, setupObject):
    dirPathText = os.path.dirname(setupObject.puPath)
    distShapeFileNameNumber = returnLowestUnusedFileNameNumber(dirPathText, 'cluz_dist', '.shp')
    distShapeFileFullPath = str(dirPathText) + os.sep + 'cluz_dist' + str(distShapeFileNameNumber) + '.shp'
    distributionDialog.filePathlineEdit.setText(distShapeFileFullPath)
    
    
def create_displayDistributionMaps(distributionDialog, setupObject):
    if distributionDialog.intervalRadioButton.isChecked():
        legendType = 'equal_interval'
    else:
        legendType = 'equal_area'
    distShapeFilePathName = distributionDialog.filePathlineEdit.text()
    selectedFeatList = [item.text() for item in distributionDialog.featListWidget.selectedItems()]
    selectedFeatIDList = [int(item.split(' - ')[0]) for item in selectedFeatList]

    abundValuesDict = createDistributionMapShapefile(setupObject, distShapeFilePathName, selectedFeatIDList)
    displayDistributionMaps(setupObject, distShapeFilePathName, abundValuesDict, legendType, selectedFeatIDList)

    distributionDialog.close()


#### Identify features in selected units ###

def returnSelectedPUIDDict(setupObject):
    selectedPUIDDict = dict()

    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    iface.setActiveLayer(puLayer)
    puLayer = iface.activeLayer()
    provider = puLayer.dataProvider()
    idFieldIndex = provider.fieldNameIndex('Unit_ID')
    statusFieldIndex = provider.fieldNameIndex('Status')

    selectedPUs = puLayer.selectedFeatures()
    for aPU in selectedPUs:
        puID = int(aPU.attributes()[idFieldIndex])
        puStatus = str(aPU.attributes()[statusFieldIndex])
        selectedPUIDDict[puID] = puStatus

    return selectedPUIDDict


def returnSelectedPUDetailsDict(setupObject, selectedPUIDDict):
    selectedPUDetailsDict = dict()
    for puID in selectedPUIDDict:
        puStatus = selectedPUIDDict[puID]
        try:
            puAbundDict = setupObject.abundPUKeyDict[puID]
        except KeyError:
            puAbundDict = dict()
        try:
            statusDetailsDict = selectedPUDetailsDict[puStatus]
        except KeyError:
            statusDetailsDict = dict()

        for featID in puAbundDict:
            try:
                featAmount = puAbundDict[featID]
            except KeyError:
                featAmount = 0
            try:
                featRunningAmount = statusDetailsDict[featID]
            except KeyError:
                featRunningAmount = 0
            featRunningAmount += featAmount
            statusDetailsDict[featID] = featRunningAmount

        selectedPUDetailsDict[puStatus] = statusDetailsDict

    return selectedPUDetailsDict


def addSelectedIdentifyDataToTableWidget(IdentifySelectedDialog, setupObject, selectedPUDetailsDict):
    featIDList = list(setupObject.targetDict.keys())
    featIDList.sort()
    for rowNumber in range(0, len(featIDList)):
        featID = featIDList[rowNumber]
        IdentifySelectedDialog.identifySelectedTableWidget.insertRow(rowNumber)
        featIDTableItem = QTableWidgetItem(str(featID))
        featNameTableItem = QTableWidgetItem(str(setupObject.targetDict[featID][0]))
        avaIDTableItem = QTableWidgetItem(str(returnStringAmountPerStatus(setupObject, selectedPUDetailsDict, 'Available', featID)))
        conIDTableItem = QTableWidgetItem(str(returnStringAmountPerStatus(setupObject, selectedPUDetailsDict, 'Conserved', featID)))
        earIDTableItem = QTableWidgetItem(str(returnStringAmountPerStatus(setupObject, selectedPUDetailsDict, 'Earmarked', featID)))
        exlIDTableItem = QTableWidgetItem(str(returnStringAmountPerStatus(setupObject, selectedPUDetailsDict, 'Excluded', featID)))
        featTarget = returnRoundedValue(setupObject, setupObject.targetDict[featID][3])
        featTargetTableItem = QTableWidgetItem(featTarget)
        featShortfallTableItem = QTableWidgetItem(returnStringShortfall(setupObject, featID))

        IdentifySelectedDialog.identifySelectedTableWidget.setItem(rowNumber, 0, featIDTableItem)
        IdentifySelectedDialog.identifySelectedTableWidget.setItem(rowNumber, 1, featNameTableItem)
        IdentifySelectedDialog.identifySelectedTableWidget.setItem(rowNumber, 2, avaIDTableItem)
        conIDTableItem.setForeground(QColor.fromRgb(0, 153, 51))
        IdentifySelectedDialog.identifySelectedTableWidget.setItem(rowNumber, 3, conIDTableItem)
        earIDTableItem.setForeground(QColor.fromRgb(51, 204, 51))
        IdentifySelectedDialog.identifySelectedTableWidget.setItem(rowNumber, 4, earIDTableItem)
        IdentifySelectedDialog.identifySelectedTableWidget.setItem(rowNumber, 5, exlIDTableItem)
        IdentifySelectedDialog.identifySelectedTableWidget.setItem(rowNumber, 6, featTargetTableItem)
        if returnStringShortfall(setupObject, featID) == 'Target met':
            featShortfallTableItem.setForeground(QColor.fromRgb(128, 128, 128))
        IdentifySelectedDialog.identifySelectedTableWidget.setItem(rowNumber, 7, featShortfallTableItem)


def addFormatting_HeadingsToTableWidget(IdentifySelectedDialog, setupObject):
    headerList = ['ID  ', 'Name  ', 'Available  ', 'Conserved  ', 'Earmarked  ', 'Excluded  ', 'Target  ', 'Target shortfall  ']
    IdentifySelectedDialog.identifySelectedTableWidget.setHorizontalHeaderLabels(headerList)
    IdentifySelectedDialog.identifySelectedTableWidget.horizontalHeader().setStyleSheet(setupObject.TableHeadingStyle)
    IdentifySelectedDialog.identifySelectedTableWidget.verticalHeader().hide()
    for aColValue in range(len(headerList)):
        IdentifySelectedDialog.identifySelectedTableWidget.resizeColumnToContents(aColValue)


def identifySelectedKeyPressEventCode(IdentifySelectedDialog, e): # http://stackoverflow.com/questions/24971305/copy-pyqt-table-selection-including-column-and-row-headers
    if e.modifiers() & Qt.ControlModifier:
        selected = IdentifySelectedDialog.identifySelectedTableWidget.selectedRanges()
        if e.key() == Qt.Key_C: #copy
            s = ''
            for r in range(selected[0].topRow(), selected[0].bottomRow() + 1):
                for c in range(selected[0].leftColumn(), selected[0].rightColumn()+1):
                    try:
                        s += str(IdentifySelectedDialog.identifySelectedTableWidget.item(r, c).text()) + '\t'
                    except AttributeError:
                        s += '\t'
                s = s[:-1] + '\n' #eliminate last '\t'
            IdentifySelectedDialog.clip.setText(s)


#### Calculate richness scores ###

def returnInitialFieldName(setupObject, fieldName):
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    fieldNameList = [field.name() for field in puLayer.fields()]

    countSuffix = ''
    if fieldName in fieldNameList:
        countSuffix = 1
        while (fieldName + str(countSuffix)) in fieldNameList:
            countSuffix += 1
    finalFieldName = fieldName + str(countSuffix)

    return finalFieldName


def produceTypeTextList(setupObject):
    typeTextList = list()
    typeDict = dict()
    for featID in setupObject.targetDict:
        featType = setupObject.targetDict[featID][1]
        try:
            featCount = typeDict[featType]
            featCount += 1
        except KeyError:
            featCount = 1
        typeDict[featType] = featCount

    typeList = list(typeDict.keys())
    typeList.sort()
    for aType in typeList:
        typeText = 'Type ' + str(aType) + ' (' + str(typeDict[aType]) + ' features)'
        typeTextList.append(typeText)

    return typeTextList


def makeSelectedFeatIDSet(aDialog, setupObject):
    selectedTypeTextList = [item.text() for item in aDialog.typeListWidget.selectedItems()]
    selectedTypeSet = set([int(item.split(" ")[1]) for item in selectedTypeTextList])
    selectedFeatIDSet = makeFeatIDSetFromFeatTypeSet(setupObject, selectedTypeSet)

    return selectedFeatIDSet


def checkRichnessTypeCodesSelected_OptionsSelected(RichnessDialog, selectedFeatIDSet):
    progressBool = True
    if len(selectedFeatIDSet) == 0:
        warningMessage('Calculating richness', 'No type codes have been selected.')
        progressBool = False
    if RichnessDialog.countBox.isChecked() is False and RichnessDialog.rangeBox.isChecked() is False:
        warningMessage('Calculating richness', 'No options have been selected.')
        progressBool = False

    return progressBool


def returnRichnessCountResults(RichnessDialog, setupObject, fieldNameList, selectedFeatIDSet):
    countFieldName = RichnessDialog.countLineEdit.text()
    if countFieldName in fieldNameList:
        warningMessage('Feature Count field name duplication', 'The planning unit layer already contains a field named ' + countFieldName + '. Please choose another name.')
    elif countFieldName == '':
        warningMessage('Feature Count field name blank', 'The Feature Count name field is blank. Please choose a name.')
    elif len(countFieldName) > 10:
        warningMessage('Invalid field name', 'The Feature Count field name cannot be more than 10 characters long.')
    else:
        produceCountField(setupObject, countFieldName, selectedFeatIDSet)
        displayGraduatedLayer(setupObject, countFieldName, 'Feature count', 2) #2 is yellow to green QGIS legend code


def returnRichnessRestrictedRangeResults(RichnessDialog, setupObject, fieldNameList, selectedFeatIDSet):
    rangeFieldName = RichnessDialog.rangeLineEdit.text()
    if rangeFieldName in fieldNameList:
        warningMessage('Restricted Range Richness field name duplication', 'The planning unit layer already contains a field named ' + rangeFieldName + '. Please choose another name.')
    elif rangeFieldName == '':
        warningMessage('Restricted Range Richness field name blank', 'The Restricted Range Richness name field is blank. Please choose a name.')
    elif len(rangeFieldName) > 10:
        warningMessage('Invalid field name', 'The Restricted Range Richness field name cannot be more than 10 characters long.')
    else:
        produceRestrictedRangeField(setupObject, rangeFieldName, selectedFeatIDSet)
        displayGraduatedLayer(setupObject, rangeFieldName, 'Restricted Range score', 2) #2 is yellow to green QGIS legend code


#### Calculate irreplaceability details ###

def addIrrepResults(setupObject, irrepDict, irrepFieldName, statusSet):
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    provider = puLayer.dataProvider()
    idFieldIndex = puLayer.fields().indexFromName("Unit_ID")
    statusFieldIndex = puLayer.fields().indexFromName("Status")

    provider.addAttributes([QgsField(irrepFieldName, QVariant.Double)])
    puLayer.updateFields()
    irrepFieldOrder = provider.fieldNameIndex(irrepFieldName)

    progressBar = makeProgressBar('Adding summed irreplaceability values to planning unit shapefile')
    polyCount = 1
    polyTotalCount = puLayer.featureCount()

    puFeatures = puLayer.getFeatures()
    puLayer.startEditing()
    for puFeature in puFeatures:
        progressBar.setValue((polyCount/polyTotalCount) * 100)
        polyCount += 1

        puRow = puFeature.id()
        puAttributes = puFeature.attributes()
        puID = puAttributes[idFieldIndex]
        puStatus = puAttributes[statusFieldIndex]
        if puStatus in statusSet:
            summedIrrepValue = 0
            try:
                puIrrepDict = irrepDict[puID]
                for featID in puIrrepDict:
                    summedIrrepValue += puIrrepDict[featID]
            except KeyError:
                pass
        else:
            summedIrrepValue = -99
        puLayer.changeAttributeValue(puRow, irrepFieldOrder, summedIrrepValue, True)
    puLayer.commitChanges()
    clearProgressBar()


def makeIrrepDictOutputFile(setupObject, irrepDict, irrepOutputFilePath, puSet):
    puIDList = list(setupObject.abundPUKeyDict.keys())
    puIDList.sort()
    featIDList = list(setupObject.targetDict.keys())
    featIDList.sort()

    headerRow = ['PU_ID']
    for featID in featIDList:
        headerRow.append('FT_' + str(featID))
    NAList = ['NA'] * len(featIDList)

    with open(irrepOutputFilePath,'w', newline='') as irrepOutputFilePath:
        irrepWriter = csv.writer(irrepOutputFilePath)
        irrepWriter.writerow(headerRow)

        for puID in puIDList:
            if puID in puSet:
                row = [str(puID)]
                try:
                    puIrrepDict = irrepDict[puID]
                except KeyError:
                    puIrrepDict = dict()
                for featID in featIDList:
                    try:
                        irrepValue = puIrrepDict[featID]
                    except KeyError:
                        irrepValue = 0
                    row.append(irrepValue)
                irrepWriter.writerow(row)
            else:
                NArow = [str(puID)] + NAList
                irrepWriter.writerow(NArow)


#### Calculate irreplaceability details ###

#### Calculate portfolio details ###
        
def makeSFFieldList(setupObject):
    sfFieldList = list()
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')

    for aField in puLayer.fields():
        if str(aField.typeName()) == 'Integer' and str(aField.name()) != 'Unit_ID':
            sfFieldList.append(aField.name())

    if len(sfFieldList) == 0:
        sfFieldList.append('No suitable fields')

    return sfFieldList


def checkIfSfRunsValueIsOK(self):
    sfRunsValueIsOK = True
    if self.sfCheckBox.isChecked():
        try:
            sfRunsValue = int(self.sfRunsLineEdit.text())
            if sfRunsValue < 1:
                warningMessage('Value error', 'The number of runs value must be an integer greater than 0.')
                sfRunsValueIsOK = False
        except ValueError:
            warningMessage('Value error', 'The number of runs value must be an integer greater than 0.')
            sfRunsValueIsOK = False

    return sfRunsValueIsOK


#### portfolioResultsDialog ###

def removeSuperfluousTabs(portfolioResultsDialog, portfolioPUDetailsDict):
    tabNameRemoveList = list()
    if not portfolioPUDetailsDict['statusDetailsBool']:
        tabNameRemoveList.append('Status results')
    if not portfolioPUDetailsDict['spatialDetailsBool']:
        tabNameRemoveList.append('Spatial results')
    if not portfolioPUDetailsDict['sfDetailsBool']:
        tabNameRemoveList.append('Selection frequency results')
    if not portfolioPUDetailsDict['patchFeatDetailsBool']:
        tabNameRemoveList.append('Patches per feature')
    if not portfolioPUDetailsDict['peDetailsBool']:
        tabNameRemoveList.append('Protection equality')

    for aIter in range(0, len(tabNameRemoveList)):
        for tabIndex in range(0, portfolioResultsDialog.portfolioTabWidget.count()):
            tabName = portfolioResultsDialog.portfolioTabWidget.tabText(tabIndex)
            if tabName in tabNameRemoveList:
                portfolioResultsDialog.portfolioTabWidget.removeTab(tabIndex)
                tabNameRemoveList.remove(tabName)


def addDetailsToStatusTab(portfolioResultsDialog, setupObject, statusDataDict):
    portfolioResultsDialog.statusTabTableWidget.clear()
    portfolioResultsDialog.statusTabTableWidget.setColumnCount(4)
    rowNumber = 0
    statusTypeList = ['Available', 'Conserved', 'Earmarked', 'Excluded', 'Portfolio', 'Region']
    for statusType in statusTypeList:
        portfolioResultsDialog.statusTabTableWidget.insertRow(rowNumber)
        statusTableItem = QTableWidgetItem(statusType)
        costString, areaString, countString = returnStatusTabStringValues(setupObject, statusDataDict, statusType)
        costTableItem = QTableWidgetItem(costString)
        areaTableItem = QTableWidgetItem(areaString)
        countTableItem = QTableWidgetItem(countString)
        portfolioResultsDialog.statusTabTableWidget.setItem(rowNumber, 0, statusTableItem)
        portfolioResultsDialog.statusTabTableWidget.setItem(rowNumber, 1, costTableItem)
        portfolioResultsDialog.statusTabTableWidget.setItem(rowNumber, 2, areaTableItem)
        portfolioResultsDialog.statusTabTableWidget.setItem(rowNumber, 3, countTableItem)
        rowNumber += 1
    statusHeaderList = ['Status', 'Total cost', 'Total area', 'No. of planning units']
    portfolioResultsDialog.statusTabTableWidget.setHorizontalHeaderLabels(statusHeaderList)
    for aColValue in range(len(statusHeaderList)):
        portfolioResultsDialog.statusTabTableWidget.resizeColumnToContents(aColValue)
    portfolioResultsDialog.statusTabTableWidget.horizontalHeader().setStyleSheet(setupObject.TableHeadingStyle)
    portfolioResultsDialog.statusTabTableWidget.verticalHeader().hide()
        
        
def returnStatusTabStringValues(setupObject, statusDataDict, statusType):
    decPrec = setupObject.decimalPlaces
    costValue = statusDataDict[statusType][0]
    limboCostValue = round(float(costValue), decPrec)
    costString = format(limboCostValue, '.' + str(decPrec) + 'f')
    areaValue = statusDataDict[statusType][1]
    limboAreaValue = round(float(areaValue), decPrec)
    areaString = format(limboAreaValue, '.' + str(decPrec) + 'f')
    countString = str(statusDataDict[statusType][2])

    return costString, areaString, countString


def addDetailsToSpatialTab(portfolioResultsDialog, setupObject, spatialDataDict):
    portfolioResultsDialog.spatialTabTableWidget.clear()
    portfolioResultsDialog.spatialTabTableWidget.setColumnCount(2)
    rowNumber = 0
    spatialTableItemDict = makeSpatialTableItemDict(setupObject, spatialDataDict)
    for spatialRowOrder in range(0, 5):
        portfolioResultsDialog.spatialTabTableWidget.insertRow(rowNumber)
        descTableItem = QTableWidgetItem(spatialTableItemDict[spatialRowOrder][0])
        valueTableItem = QTableWidgetItem(spatialTableItemDict[spatialRowOrder][1])
        portfolioResultsDialog.spatialTabTableWidget.setItem(rowNumber, 0, descTableItem)
        portfolioResultsDialog.spatialTabTableWidget.setItem(rowNumber, 1, valueTableItem)
        rowNumber += 1
    spatialHeaderList = ['Metric', 'Value']
    portfolioResultsDialog.spatialTabTableWidget.setHorizontalHeaderLabels(spatialHeaderList)
    for aColValue in range(len(spatialHeaderList)):
        portfolioResultsDialog.spatialTabTableWidget.resizeColumnToContents(aColValue)
    portfolioResultsDialog.spatialTabTableWidget.horizontalHeader().setStyleSheet(setupObject.TableHeadingStyle)
    portfolioResultsDialog.spatialTabTableWidget.verticalHeader().hide()


def makeSpatialTableItemDict(setupObject, spatialDataDict):
    decPrec = setupObject.decimalPlaces
    spatialTableItemDict = dict()
    spatialTableItemDict[0] = ['Number of patches', str(spatialDataDict['patchCount'])]

    smallPatchSize = spatialDataDict['patchSmallest']
    limboSmallPatchSize = round(float(smallPatchSize), decPrec)
    smallPatchSizeString = format(limboSmallPatchSize, '.' + str(decPrec) + 'f')
    spatialTableItemDict[1] = ['Area of smallest patch', smallPatchSizeString]

    medianPatchSize = spatialDataDict['patchMedian']
    limboMedianPatchSize = round(float(medianPatchSize), decPrec)
    medianPatchSizeString = format(limboMedianPatchSize, '.' + str(decPrec) + 'f')
    spatialTableItemDict[2] = ['Median area of patches', medianPatchSizeString]

    largePatchSize = spatialDataDict['patchLargest']
    limboLargePatchSize = round(float(largePatchSize), decPrec)
    largePatchSizeString = format(limboLargePatchSize, '.' + str(decPrec) + 'f')
    spatialTableItemDict[3] = ['Area of largest patch', largePatchSizeString]

    boundaryLength = spatialDataDict['totalBoundLength']
    limboBoundaryLength = round(float(boundaryLength), decPrec)
    boundaryString = format(limboBoundaryLength, '.' + str(decPrec) + 'f')
    spatialTableItemDict[4] = ['Portfolio boundary length', boundaryString]

    return spatialTableItemDict


def addPatchFeatDetailsToPortfolioDict(setupObject, portfolioPUDetailsDict):
    puDict, patchDict, dummyZoneDict = makePatchDictBasedOnDummyZoneFile(setupObject) #Only need patchDict
    patchFeatDataDict = makePatchFeatDataDict(setupObject, patchDict)

    portfolioPUDetailsDict['patchFeatDetailsBool'] = True
    portfolioPUDetailsDict['patchFeatDataDict'] = patchFeatDataDict

    return portfolioPUDetailsDict


def addSfDetailsToPortfolioDict(PortfolioDialog, setupObject, portfolioPUDetailsDict):
    sfFieldName = PortfolioDialog.sfComboBox.currentText()
    sfRunsValue = int(PortfolioDialog.sfRunsLineEdit.text())
    sfValueList = makeFullSFValueList(setupObject, sfFieldName)
    if checkSfRunsValueNotLowerThanMaxSFValue(sfValueList, sfRunsValue):
        portfolioPUDetailsDict = makeSFDetailsToPortfolioDict(portfolioPUDetailsDict, sfValueList, sfRunsValue)

    return portfolioPUDetailsDict


def checkSfRunsValueNotLowerThanMaxSFValue(sfValueList, sfRunsValue):
    sfRunsValueNotLowerThanMaxSFValue = True

    if max(sfValueList) > sfRunsValue:
        warningMessage("Value error", "The specified number of runs value is less than the highest selection frequency value in the specified selection frequency field. Please check the number of runs used in the analysis and update this figure.")
        sfRunsValueNotLowerThanMaxSFValue = False

    return sfRunsValueNotLowerThanMaxSFValue


def addDetailsToSfTab(portfolioResultsDialog, sfDataDict):
    portfolioResultsDialog.sfTabTableWidget.clear()
    portfolioResultsDialog.sfTabTableWidget.setColumnCount(2)
    rowNumber = 0
    sfDictKeyList = range(0, len(sfDataDict))
    for sfDictKey in sfDictKeyList:
        portfolioResultsDialog.sfTabTableWidget.insertRow(rowNumber)
        descTableItem = QTableWidgetItem(sfDataDict[sfDictKey][0])
        valueTableItem = QTableWidgetItem(sfDataDict[sfDictKey][1])
        portfolioResultsDialog.sfTabTableWidget.setItem(rowNumber, 0, descTableItem)
        portfolioResultsDialog.sfTabTableWidget.setItem(rowNumber, 1, valueTableItem)
        rowNumber += 1

    sfHeaderList = ['Selection frequency value range', 'Number of planning units']
    portfolioResultsDialog.sfTabTableWidget.setHorizontalHeaderLabels(sfHeaderList)
    for aColValue in range(len(sfHeaderList)):
        portfolioResultsDialog.sfTabTableWidget.resizeColumnToContents(aColValue)


def addDetailsToPatchFeatTab(portfolioResultsDialog, setupObject, patchFeatDataDict):
    portfolioResultsDialog.patchFeatTabTableWidget.clear()
    portfolioResultsDialog.patchFeatTabTableWidget.setColumnCount(3)
    rowNumber = 0
    featIDList = list(setupObject.targetDict.keys())
    featIDList.sort()
    for featID in featIDList:
        portfolioResultsDialog.patchFeatTabTableWidget.insertRow(rowNumber)
        featIDTableItem = QTableWidgetItem(str(featID))
        featNameTableItem = QTableWidgetItem(setupObject.targetDict[featID][0])
        try:
            countTableItem = QTableWidgetItem(str(patchFeatDataDict[featID]))
        except KeyError:
            countTableItem = QTableWidgetItem(str(0))
        portfolioResultsDialog.patchFeatTabTableWidget.setItem(rowNumber, 0, featIDTableItem)
        portfolioResultsDialog.patchFeatTabTableWidget.setItem(rowNumber, 1, featNameTableItem)
        portfolioResultsDialog.patchFeatTabTableWidget.setItem(rowNumber, 2, countTableItem)
        rowNumber += 1

    sfHeaderList = ['Feature ID', 'Feature name', "Number of patches"]
    portfolioResultsDialog.patchFeatTabTableWidget.setHorizontalHeaderLabels(sfHeaderList)
    for aColValue in range(len(sfHeaderList)):
        portfolioResultsDialog.patchFeatTabTableWidget.resizeColumnToContents(aColValue)
    portfolioResultsDialog.patchFeatTabTableWidget.horizontalHeader().setStyleSheet(setupObject.TableHeadingStyle)
    portfolioResultsDialog.patchFeatTabTableWidget.verticalHeader().hide()


def portfolioStatusTabDialogKeyPressEvent(portfolioResultsDialog, e): # http://stackoverflow.com/questions/24971305/copy-pyqt-table-selection-including-column-and-row-headers
    if e.modifiers() & Qt.ControlModifier:
        selected = portfolioResultsDialog.statusTabTableWidget.selectedRanges()
        if e.key() == Qt.Key_C: #copy
            s = ''
            for r in range(selected[0].topRow(), selected[0].bottomRow() + 1):
                for c in range(selected[0].leftColumn(), selected[0].rightColumn()+1):
                    try:
                        s += str(portfolioResultsDialog.statusTabTableWidget.item(r, c).text()) + '\t'
                    except AttributeError:
                        s += '\t'
                s = s[:-1] + '\n' #eliminate last '\t'
            portfolioResultsDialog.clip.setText(s)


def portfolioSpatialTabDialogKeyPressEvent(portfolioResultsDialog, e): # http://stackoverflow.com/questions/24971305/copy-pyqt-table-selection-including-column-and-row-headers
    if e.modifiers() & Qt.ControlModifier:
        selected = portfolioResultsDialog.spatialTabTableWidget.selectedRanges()
        if e.key() == Qt.Key_C: #copy
            s = ''
            for r in range(selected[0].topRow(), selected[0].bottomRow() + 1):
                for c in range(selected[0].leftColumn(), selected[0].rightColumn()+1):
                    try:
                        s += str(portfolioResultsDialog.spatialTabTableWidget.item(r, c).text()) + '\t'
                    except AttributeError:
                        s += '\t'
                s = s[:-1] + '\n' #eliminate last '\t'
            portfolioResultsDialog.clip.setText(s)


def portfolioSfTabDialogKeyPressEvent(portfolioResultsDialog, e): # http://stackoverflow.com/questions/24971305/copy-pyqt-table-selection-including-column-and-row-headers
    if e.modifiers() & Qt.ControlModifier:
        selected = portfolioResultsDialog.sfTabTableWidget.selectedRanges()
        if e.key() == Qt.Key_C: #copy
            s = ''
            for r in range(selected[0].topRow(), selected[0].bottomRow() + 1):
                for c in range(selected[0].leftColumn(), selected[0].rightColumn()+1):
                    try:
                        s += str(portfolioResultsDialog.sfTabTableWidget.item(r, c).text()) + '\t'
                    except AttributeError:
                        s += '\t'
                s = s[:-1] + '\n' #eliminate last '\t'
            portfolioResultsDialog.clip.setText(s)


def portfolioPatchTabDialogKeyPressEvent(portfolioResultsDialog, e): # http://stackoverflow.com/questions/24971305/copy-pyqt-table-selection-including-column-and-row-headers
    if e.modifiers() & Qt.ControlModifier:
        selected = portfolioResultsDialog.patchFeatTabTableWidget.selectedRanges()
        if e.key() == Qt.Key_C: #copy
            s = ''
            for r in range(selected[0].topRow(), selected[0].bottomRow() + 1):
                for c in range(selected[0].leftColumn(), selected[0].rightColumn()+1):
                    try:
                        s += str(portfolioResultsDialog.patchFeatTabTableWidget.item(r, c).text()) + '\t'
                    except AttributeError:
                        s += '\t'
                s = s[:-1] + '\n' #eliminate last '\t'
            portfolioResultsDialog.clip.setText(s)