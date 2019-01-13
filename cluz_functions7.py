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

import qgis
from qgis.core import QgsVectorLayer
from qgis.utils import iface

from .cluz_messages import successMessage, checkChangeEarmarkedToAvailablePU, warningMessage
from .cluz_make_file_dicts import updateTargetCSVFromTargetDict
from .cluz_display import updatePULayerToShowChangesByShiftingExtent


def returnTargetsMetTuple(setupObject):
    numTargets = 0
    numTargetsMet = 0
    targetDict = setupObject.targetDict
    for aFeat in targetDict:
        targetList = targetDict[aFeat]
        targetAmount = targetList[3]
        conAmount = targetList[4]
        if targetAmount > 0:
            numTargets += 1
            if conAmount >= targetAmount:
                numTargetsMet += 1

    return numTargetsMet, numTargets


def changeStatusPuLayer(setupObject, changeStatusType, changeLockedPUsBool):
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    qgis.utils.iface.setActiveLayer(puLayer)
    puLayer = qgis.utils.iface.activeLayer()
    provider = puLayer.dataProvider()
    idFieldOrder = provider.fieldNameIndex('Unit_ID')
    statusFieldOrder = provider.fieldNameIndex('Status')

    selectedPUs = puLayer.selectedFeatures()
    puLayer.startEditing()

    selectedPUIDStatusDict = dict()
    for aPU in selectedPUs:
        puRow = aPU.id()
        puID = aPU.attributes()[idFieldOrder]
        puStatus = aPU.attributes()[statusFieldOrder]
        if changeLockedPUsBool:
            selectedPUIDStatusDict[puID] = puStatus
            puLayer.changeAttributeValue(puRow, statusFieldOrder, changeStatusType)
        else:
            if puStatus == 'Available' or puStatus == 'Earmarked':
                if puStatus != changeStatusType:
                    selectedPUIDStatusDict[puID] = str(puStatus)
                    puLayer.changeAttributeValue(puRow, statusFieldOrder, changeStatusType)

    puLayer.commitChanges()
    puLayer.removeSelection()

    return selectedPUIDStatusDict


def calcChangeAbundDict(setupObject, selectedPUIDStatusDict, statusType):
    statusBoolDict = {"Available": False, "Conserved": True, "Earmarked": True, "Excluded": False}
    changeStatusBoolType = statusBoolDict[statusType]

    changeAbundDict = dict()
    for puID in selectedPUIDStatusDict:
        puStatus = selectedPUIDStatusDict[puID]
        currentStatusBoolType = statusBoolDict[puStatus]

        if currentStatusBoolType is False and changeStatusBoolType:
            try:
                puAbundDict = setupObject.abundPUKeyDict[puID]
                for featID in puAbundDict:
                    abundValue = puAbundDict[featID]
                    try:
                        runningChange = changeAbundDict[featID]
                    except KeyError:
                        runningChange = 0
                    runningChange += abundValue
                    changeAbundDict[featID] = runningChange
            except KeyError:
                pass

        if currentStatusBoolType and changeStatusBoolType is False:
            try:
                puAbundDict = setupObject.abundPUKeyDict[puID]
                for featID in puAbundDict:
                    abundValue = puAbundDict[featID]
                    try:
                        runningChange = changeAbundDict[featID]
                    except KeyError:
                        runningChange = 0
                    runningChange -= abundValue
                    changeAbundDict[featID] = runningChange
            except KeyError:
                pass

    return changeAbundDict


def updateTargetDictWithChanges(setupObject, changeAbundDict):
    targetDict = setupObject.targetDict
    for theFeatID in changeAbundDict:
        changeAmount = changeAbundDict[theFeatID]
        targetList = setupObject.targetDict[theFeatID]
        conAmount = targetList[4]
        newAmount = conAmount + changeAmount
        targetList[4] = newAmount
        targetDict[theFeatID] = targetList

    return targetDict


# ####################################################################http://www.opengis.ch/2015/04/29/performance-for-mass-updating-features-on-layers/
def undoStatusChangeInPuLayer(setupObject):
    selectedPUIDStatusDict = setupObject.selectedPUIDStatusDict
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    provider = puLayer.dataProvider()
    puIDFieldOrder = provider.fieldNameIndex('Unit_ID')
    statusFieldOrder = provider.fieldNameIndex('Status')

    puLayer.startEditing()
    if statusFieldOrder != -1:
        puFeatures = puLayer.getFeatures()
        for puFeature in puFeatures:
            puRow = puFeature.id()
            puAttributes = puFeature.attributes()
            puID = puAttributes[puIDFieldOrder]
            try:
                backupPuStatus = selectedPUIDStatusDict[puID]
                if backupPuStatus == 'Available' or backupPuStatus == 'Earmarked' or backupPuStatus == 'Conserved' or backupPuStatus == 'Excluded':
                    puLayer.changeAttributeValue(puRow, statusFieldOrder, backupPuStatus)
            except KeyError:
                pass

    puLayer.commitChanges()
    iface.mapCanvas().refresh()


def changeBestToEarmarkedPUs(setupObject):
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    puProvider = puLayer.dataProvider()
    idFieldOrder = puProvider.fieldNameIndex('Unit_ID')
    statusFieldOrder = puProvider.fieldNameIndex('Status')
    bestFieldOrder = puProvider.fieldNameIndex('Best')

    if bestFieldOrder == -1:
        warningMessage('Incorrect format', 'The planning unit layer has no field named Best (which is produced by running Marxan). This process will terminate.')
    else:
        selectedPUIDStatusDict = changeStatus_makeSelectedPUIDStatusDict(puLayer, idFieldOrder, statusFieldOrder, bestFieldOrder)
        statusType = 'Earmarked' # This works out the changes needed to update the Best PUs to Earmarked
        changeAbundDict = calcChangeAbundDict(setupObject, selectedPUIDStatusDict, statusType)
        updateTargetDictWithChanges(setupObject, changeAbundDict)
        updateTargetCSVFromTargetDict(setupObject, setupObject.targetDict)
        successMessage('Process completed', 'Planning units that were selected in the Best portfolio now have Earmarked status and the target table has been updated accordingly.')
    updatePULayerToShowChangesByShiftingExtent()

def changeStatus_makeSelectedPUIDStatusDict(puLayer, idFieldOrder, statusFieldOrder, bestFieldOrder):
    selectedPUIDStatusDict = dict()
    puLayer.startEditing()
    puFeatures = puLayer.getFeatures()
    for puFeature in puFeatures:
        puRow = puFeature.id()
        puID = puFeature.attributes()[idFieldOrder]
        puStatus = puFeature.attributes()[statusFieldOrder]
        bestStatus = puFeature.attributes()[bestFieldOrder]
        if bestStatus == 'Selected':
            puLayer.changeAttributeValue(puRow, statusFieldOrder, 'Earmarked')
            selectedPUIDStatusDict[puID] = puStatus
    puLayer.commitChanges()

    return selectedPUIDStatusDict


def changeEarmarkedToAvailablePUs(setupObject):
    puLayer = QgsVectorLayer(setupObject.puPath, "Planning units", "ogr")
    puProvider = puLayer.dataProvider()
    idFieldOrder = puProvider.fieldNameIndex("Unit_ID")
    statusFieldOrder = puProvider.fieldNameIndex("Status")
    changeBool = checkChangeEarmarkedToAvailablePU()
    
    if changeBool:
        earmakedPUIDStatusDict = changeStatus_makeEarmakedPUIDStatusDict(puLayer, idFieldOrder, statusFieldOrder)
        changeAbundDict = calcChangeAbundDict(setupObject, earmakedPUIDStatusDict, "Available")
        updateTargetDictWithChanges(setupObject, changeAbundDict)
        updateTargetCSVFromTargetDict(setupObject, setupObject.targetDict)
        successMessage("Process completed", "Planning units with Earmarked status have been changed to Available status and the target table has been updated accordingly.")
    updatePULayerToShowChangesByShiftingExtent()


def changeStatus_makeEarmakedPUIDStatusDict(puLayer, idFieldOrder, statusFieldOrder):
    earmarkedPUIDStatusDict = dict()
    puLayer.startEditing()
    puFeatures = puLayer.getFeatures()
    for puFeature in puFeatures:
        puRow = puFeature.id()
        puID = puFeature.attributes()[idFieldOrder]
        puStatus = puFeature.attributes()[statusFieldOrder]
        if puStatus == 'Earmarked':
            puLayer.changeAttributeValue(puRow, statusFieldOrder, 'Available')
            earmarkedPUIDStatusDict[puID] = puStatus
    puLayer.commitChanges()

    return earmarkedPUIDStatusDict


def makeIdentDict(targetDict, puAbundDict):
    identDict = dict()
    targetMetDict = dict()
    for featID in puAbundDict:
        featAmount = puAbundDict[featID]
        featName = targetDict[featID][0]
        featTarget = targetDict[featID][3]
        conTotal = targetDict[featID][4]
        featTotal = targetDict[featID][5]
        propOfTotal = featAmount / featTotal
        pcOfTotal = propOfTotal * 100
        pcOfTotalString = str(round(pcOfTotal, 2)) + ' %'
        if featTarget > 0:
            if conTotal < featTarget:
                targetMetDict[featID] = 'Not met'
            else:
                targetMetDict[featID] = 'Met'

            propOfTarget = featAmount / featTarget
            pcOfTarget = propOfTarget * 100
            pcOfTargetString = str(round(pcOfTarget, 2)) + ' %'

            propTargetMet = targetDict[featID][4] / featTarget
            pcTargetMet = propTargetMet * 100
            pcTargetMetString = str(round(pcTargetMet, 2)) + ' %'
        else:
            pcOfTargetString = 'No target'
            pcTargetMetString = 'No target'
            targetMetDict[featID] = 'No target'

        identDict[featID] = [str(featID), featName, str(featAmount), pcOfTotalString, str(featTarget), pcOfTargetString, pcTargetMetString]

    return identDict, targetMetDict

