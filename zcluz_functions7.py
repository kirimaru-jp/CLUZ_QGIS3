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
from qgis.core import QgsVectorLayer, QgsExpression, QgsFeatureRequest
from qgis.utils import iface

from .cluz_messages import successMessage, checkChangeEarmarkedToAvailablePU, warningMessage
from .cluz_make_file_dicts import updateTargetCSVFromTargetDict
from .cluz_display import updatePULayerToShowChangesByShiftingExtent


def returnZonesMainTargetsMetTuple(setupObject):
    numTargets = 0
    numTargetsMet = 0
    targetDict = setupObject.targetDict
    for aFeat in targetDict:
        targetList = targetDict[aFeat]
        targetAmount = targetList[3]
        conAmount = 0
        for zonePosition in range(1, len(setupObject.zonesDict)):
            conListPos = 6 + (2 * len(setupObject.zonesDict)) + zonePosition
            conAmount += targetList[conListPos]
        if targetAmount > 0:
            numTargets += 1
            if conAmount >= targetAmount:
                numTargetsMet += 1

    return numTargetsMet, numTargets


def returnZonesTargetsMetTuple(setupObject, selectedZoneID):
    numZoneTargets = 0
    numZonesTargetsMet = 0
    targetDict = setupObject.targetDict
    for aFeat in targetDict:
        targetList = targetDict[aFeat]
        targetListPos = 6 + (1 * len(setupObject.zonesDict)) + selectedZoneID
        targetAmount = targetList[targetListPos]
        conListPos = 6 + (2 * len(setupObject.zonesDict)) + selectedZoneID
        conAmount = targetList[conListPos]
        if targetAmount > 0:
            numZoneTargets += 1
            if conAmount >= targetAmount:
                numZonesTargetsMet += 1

    return numZonesTargetsMet, numZoneTargets


def returnSelectedZoneIDFromChangeStatusPanel(ZonesChangeStatusDialog):
    zoneString = str(ZonesChangeStatusDialog.zonesNameComboBox.currentText())
    zoneID = int(zoneString.split(' - ')[0][5:])

    return zoneID


def returnBeforeAfterPUZonesStatusDicts(setupObject, changeStatusType, changeLockedPUsBool, selectedZoneID):
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    qgis.utils.iface.setActiveLayer(puLayer)
    puLayer = qgis.utils.iface.activeLayer()
    puLayer.startEditing()
    beforePUZonesStatusDict = makeBeforePUZonesStatusDict(setupObject)
    afterPUZonesStatusDict = makeAfterPUZonesStatusDict(beforePUZonesStatusDict, selectedZoneID, changeStatusType, changeLockedPUsBool)

    return beforePUZonesStatusDict, afterPUZonesStatusDict


def makeBeforePUZonesStatusDict(setupObject):
    beforePUZonesStatusDict = dict()

    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    qgis.utils.iface.setActiveLayer(puLayer)
    puLayer = qgis.utils.iface.activeLayer()
    provider = puLayer.dataProvider()
    idFieldOrder = provider.fieldNameIndex('Unit_ID')

    selectedPUs = puLayer.selectedFeatures()
    puLayer.startEditing()

    for aPU in selectedPUs:
        puZoneStatusDict = dict()
        puID = aPU.attributes()[idFieldOrder]
        for zoneID in list(setupObject.zonesDict):
            statusFieldName = 'Z' + str(zoneID) + '_Status'
            zoneStatusFieldOrder = provider.fieldNameIndex(statusFieldName)
            zoneStatus = aPU.attributes()[zoneStatusFieldOrder]
            puZoneStatusDict[zoneID] = zoneStatus
        beforePUZonesStatusDict[puID] = puZoneStatusDict

    return beforePUZonesStatusDict


def makeAfterPUZonesStatusDict(beforePUZonesStatusDict, selectedZoneID, changeStatusType, changeExcLockPUsBool):
    afterPUZonesStatusDict = dict()
    for puID in beforePUZonesStatusDict:
        beforePUIDZoneStatusDict = beforePUZonesStatusDict[puID]
        otherZonesStatusList = makeOtherZonesStatusList(beforePUIDZoneStatusDict, selectedZoneID)
        origZoneStatusType = beforePUIDZoneStatusDict[selectedZoneID]
        changeStatusPUsBool = checkChangeStatusPUsBool(origZoneStatusType, changeStatusType, otherZonesStatusList)

        if changeExcLockPUsBool is False and changeStatusPUsBool is False:
            pass
        else:
            afterPUIDZoneStatusDict = dict()
            afterPUIDZoneStatusDict[selectedZoneID] = changeStatusType
            for zoneID in beforePUIDZoneStatusDict:
                if zoneID != selectedZoneID:
                    origOtherZoneStatusType = beforePUIDZoneStatusDict[zoneID]
                    newOtherZoneStatusType = returnOtherZoneStatusType(changeStatusType, origOtherZoneStatusType)
                    afterPUIDZoneStatusDict[zoneID] = newOtherZoneStatusType
            afterPUZonesStatusDict[puID] = afterPUIDZoneStatusDict

    return afterPUZonesStatusDict


def checkChangeStatusPUsBool(origZoneStatusType, changeStatusType, otherZonesStatusList):
    changeStatusPUsBool = True
    if origZoneStatusType == changeStatusType:
        changeStatusPUsBool = False
    if origZoneStatusType == 'Excluded' or origZoneStatusType == 'Locked':
        changeStatusPUsBool = False
    if changeStatusType == 'Earmarked' and 'Locked' in otherZonesStatusList:
        changeStatusPUsBool = False

    return changeStatusPUsBool


def returnOtherZoneStatusType(changeStatusType, origOtherZoneStatusType):
    changeZoneStatusTypeDict = dict()
    changeZoneStatusTypeDict[('Available', 'Available')] = 'Available'
    changeZoneStatusTypeDict[('Available', 'Earmarked')] = 'Earmarked'
    changeZoneStatusTypeDict[('Available', 'Excluded')] = 'Excluded'
    changeZoneStatusTypeDict[('Available', 'Locked')] = 'Available'
    changeZoneStatusTypeDict[('Earmarked', 'Available')] = 'Available'
    changeZoneStatusTypeDict[('Earmarked', 'Earmarked')] = 'Available'
    changeZoneStatusTypeDict[('Earmarked', 'Excluded')] = 'Excluded'
    changeZoneStatusTypeDict[('Earmarked', 'Locked')] = 'Available'
    changeZoneStatusTypeDict[('Excluded', 'Available')] = 'Available'
    changeZoneStatusTypeDict[('Excluded', 'Earmarked')] = 'Earmarked'
    changeZoneStatusTypeDict[('Excluded', 'Excluded')] = 'Excluded'
    changeZoneStatusTypeDict[('Excluded', 'Locked')] = 'Locked'
    changeZoneStatusTypeDict[('Locked', 'Available')] = 'Available'
    changeZoneStatusTypeDict[('Locked', 'Earmarked')] = 'Available'
    changeZoneStatusTypeDict[('Locked', 'Excluded')] = 'Excluded'
    changeZoneStatusTypeDict[('Locked', 'Locked')] = 'Available'
    newOtherZoneStatusType = changeZoneStatusTypeDict[(changeStatusType, origOtherZoneStatusType)]

    return newOtherZoneStatusType


def makeOtherZonesStatusList(beforeChangePUZonesStatusDict, selectedZoneID):
    otherZonesStatusList = list()
    for zoneID in beforeChangePUZonesStatusDict:
        if zoneID != selectedZoneID:
            otherZonesStatusList.append(beforeChangePUZonesStatusDict[zoneID])

    return otherZonesStatusList


def makeZonesSelectedStatusBalanceDict(beforePUZonesStatusDict, afterPUZonesStatusDict):
    zonesSelectedStatusBalanceDict = dict()
    for puID in afterPUZonesStatusDict:
        try:
            puIDZoneStatusBalanceDict = zonesSelectedStatusBalanceDict[puID]
        except KeyError:
            puIDZoneStatusBalanceDict = dict()
        beforePUStatusDict = beforePUZonesStatusDict[puID]
        afterPUStatusDict = afterPUZonesStatusDict[puID]
        for zoneID in afterPUStatusDict:
            beforeStatus = beforePUStatusDict[zoneID]
            afterStatus = afterPUStatusDict[zoneID]
            puIDZoneStatusBalanceDict[zoneID] = returnStatusBalanceValue(beforeStatus, afterStatus)
        zonesSelectedStatusBalanceDict[puID] = puIDZoneStatusBalanceDict

    return zonesSelectedStatusBalanceDict


def returnStatusBalanceValue(beforeStatus, afterStatus):
    recodeDict = {'Available': False, 'Earmarked': True, 'Excluded': False, 'Locked': True}
    beforeBool = recodeDict[beforeStatus]
    afterBool = recodeDict[afterStatus]

    balanceValue = 0
    if beforeBool and afterBool is False:
        balanceValue = -1
    elif beforeBool is False and afterBool:
        balanceValue = 1

    return balanceValue


def changeZonesStatusPuLayer(setupObject, afterPUZonesStatusDict):
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    qgis.utils.iface.setActiveLayer(puLayer)
    puLayer = qgis.utils.iface.activeLayer()
    provider = puLayer.dataProvider()
    idFieldOrder = provider.fieldNameIndex('Unit_ID')
    selectedPUList = list()

    selectedPUs = puLayer.selectedFeatures()
    puLayer.startEditing()

    for aPU in selectedPUs:
        puRow = aPU.id()
        selectedPUList.append(puRow)
        puID = aPU.attributes()[idFieldOrder]
        try:
            afterPUIDZonesStatusDict = afterPUZonesStatusDict[puID]
            for zoneID in afterPUIDZonesStatusDict:
                zoneStatusFieldName = 'Z' + str(zoneID) + '_Status'
                zoneStatusFieldOrder = provider.fieldNameIndex(zoneStatusFieldName)
                finalChangeStatusType = afterPUIDZonesStatusDict[zoneID]
                puLayer.changeAttributeValue(puRow, zoneStatusFieldOrder, finalChangeStatusType)
        except KeyError:
            pass

    setupObject.selectedPUList = selectedPUList
    puLayer.commitChanges()
    puLayer.removeSelection()
    updatePULayerToShowChangesByShiftingExtent()


def calcZonesChangeAbundDict(setupObject, zonesSelectedStatusBalanceDict):
    zonesChangeAbundDict = dict()
    for puID in zonesSelectedStatusBalanceDict:
        puIDZonesStatusBalanceDict = zonesSelectedStatusBalanceDict[puID]
        for zoneID in puIDZonesStatusBalanceDict:
            try:
                zoneIDChangeAbundDict = zonesChangeAbundDict[zoneID]
            except KeyError:
                zoneIDChangeAbundDict = dict()
            try:
                puAbundDict = setupObject.abundPUKeyDict[puID]
            except KeyError:
                puAbundDict = dict() # just to leave things blank
            for featID in puAbundDict:
                abundValue = puAbundDict[featID]
                try:
                    runningChange = zoneIDChangeAbundDict[featID]
                except KeyError:
                    runningChange = 0
                featZoneProp = setupObject.zonesPropDict['Z' + str(zoneID) + '_Prop'][featID]
                changeAmount = abundValue * puIDZonesStatusBalanceDict[zoneID] * featZoneProp
                runningChange += changeAmount
                zoneIDChangeAbundDict[featID] = runningChange
            zonesChangeAbundDict[zoneID] = zoneIDChangeAbundDict

    return zonesChangeAbundDict


def updateZonesTargetDictWithChanges(setupObject, zonesChangeAbundDict):
    targetDict = setupObject.targetDict
    for zoneID in zonesChangeAbundDict:
        aZoneChangeAbundDict = zonesChangeAbundDict[zoneID]
        for featID in aZoneChangeAbundDict:
            changeAmount = zonesChangeAbundDict[zoneID][featID]
            targetList = setupObject.targetDict[featID]

            targetListPos = 6 + (2 * len(setupObject.zonesDict)) + zoneID
            zoneConAmount = targetList[targetListPos]
            newZoneAmount = zoneConAmount + changeAmount
            targetList[targetListPos] = newZoneAmount

            targetDict[featID] = targetList

    return targetDict

def zonesSelectUndoPlanningUnits(setupObject):
    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    qgis.utils.iface.setActiveLayer(puLayer)
    puLayer = qgis.utils.iface.activeLayer()
    puLayer.selectByIds(setupObject.selectedPUList)


# # ####################################################################
# def zonesUndoStatusChangeInPuLayer(setupObject):
#     selectedPUIDStatusDict = setupObject.selectedPUIDStatusDict
#     puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
#     provider = puLayer.dataProvider()
#     puIDFieldOrder = provider.fieldNameIndex('Unit_ID')
#     statusFieldOrder = provider.fieldNameIndex('Status')
#
#     puLayer.startEditing()
#     if statusFieldOrder != -1:
#         puFeatures = puLayer.getFeatures()
#         for puFeature in puFeatures:
#             puRow = puFeature.id()
#             puAttributes = puFeature.attributes()
#             puID = puAttributes[puIDFieldOrder]
#             try:
#                 backupPuStatus = selectedPUIDStatusDict[puID]
#                 if backupPuStatus == 'Available' or backupPuStatus == 'Earmarked' or backupPuStatus == 'Conserved' or backupPuStatus == 'Excluded':
#                     puLayer.changeAttributeValue(puRow, statusFieldOrder, backupPuStatus)
#             except KeyError:
#                 pass
#
#     puLayer.commitChanges()
#     iface.mapCanvas().refresh()

#
# def changeBestToEarmarkedPUs(setupObject):
#     puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
#     puProvider = puLayer.dataProvider()
#     idFieldOrder = puProvider.fieldNameIndex('Unit_ID')
#     statusFieldOrder = puProvider.fieldNameIndex('Status')
#     bestFieldOrder = puProvider.fieldNameIndex('Best')
#
#     if bestFieldOrder == -1:
#         warningMessage('Incorrect format', 'The planning unit layer has no field named Best (which is produced by running Marxan). This process will terminate.')
#     else:
#         selectedPUIDStatusDict = changeStatus_makeSelectedPUIDStatusDict(puLayer, idFieldOrder, statusFieldOrder, bestFieldOrder)
#         statusType = 'Earmarked' # This works out the changes needed to update the Best PUs to Earmarked
#         changeAbundDict = calcChangeAbundDict(setupObject, selectedPUIDStatusDict, statusType)
#         updateTargetDictWithChanges(setupObject, changeAbundDict)
#         updateTargetCSVFromTargetDict(setupObject, setupObject.targetDict)
#         successMessage('Process completed', 'Planning units that were selected in the Best portfolio now have Earmarked status and the target table has been updated accordingly.')
#     updatePULayerToShowChangesByShiftingExtent()
#
# def changeStatus_makeSelectedPUIDStatusDict(puLayer, idFieldOrder, statusFieldOrder, bestFieldOrder):
#     selectedPUIDStatusDict = dict()
#     puLayer.startEditing()
#     puFeatures = puLayer.getFeatures()
#     for puFeature in puFeatures:
#         puRow = puFeature.id()
#         puID = puFeature.attributes()[idFieldOrder]
#         puStatus = puFeature.attributes()[statusFieldOrder]
#         bestStatus = puFeature.attributes()[bestFieldOrder]
#         if bestStatus == 'Selected':
#             puLayer.changeAttributeValue(puRow, statusFieldOrder, 'Earmarked')
#             selectedPUIDStatusDict[puID] = puStatus
#     puLayer.commitChanges()
#
#     return selectedPUIDStatusDict
#
#
# def changeEarmarkedToAvailablePUs(setupObject):
#     puLayer = QgsVectorLayer(setupObject.puPath, "Planning units", "ogr")
#     puProvider = puLayer.dataProvider()
#     idFieldOrder = puProvider.fieldNameIndex("Unit_ID")
#     statusFieldOrder = puProvider.fieldNameIndex("Status")
#     changeBool = checkChangeEarmarkedToAvailablePU()
#
#     if changeBool:
#         earmakedPUIDStatusDict = changeStatus_makeEarmakedPUIDStatusDict(puLayer, idFieldOrder, statusFieldOrder)
#         changeAbundDict = calcChangeAbundDict(setupObject, earmakedPUIDStatusDict, "Available")
#         updateTargetDictWithChanges(setupObject, changeAbundDict)
#         updateTargetCSVFromTargetDict(setupObject, setupObject.targetDict)
#         successMessage("Process completed", "Planning units with Earmarked status have been changed to Available status and the target table has been updated accordingly.")
#     updatePULayerToShowChangesByShiftingExtent()
#
#
# def changeStatus_makeEarmakedPUIDStatusDict(puLayer, idFieldOrder, statusFieldOrder):
#     earmarkedPUIDStatusDict = dict()
#     puLayer.startEditing()
#     puFeatures = puLayer.getFeatures()
#     for puFeature in puFeatures:
#         puRow = puFeature.id()
#         puID = puFeature.attributes()[idFieldOrder]
#         puStatus = puFeature.attributes()[statusFieldOrder]
#         if puStatus == 'Earmarked':
#             puLayer.changeAttributeValue(puRow, statusFieldOrder, 'Available')
#             earmarkedPUIDStatusDict[puID] = puStatus
#     puLayer.commitChanges()
#
#     return earmarkedPUIDStatusDict
#
#
# def makeIdentDict(targetDict, puAbundDict):
#     identDict = dict()
#     targetMetDict = dict()
#     for featID in puAbundDict:
#         featAmount = puAbundDict[featID]
#         featName = targetDict[featID][0]
#         featTarget = targetDict[featID][3]
#         conTotal = targetDict[featID][4]
#         featTotal = targetDict[featID][5]
#         propOfTotal = featAmount / featTotal
#         pcOfTotal = propOfTotal * 100
#         pcOfTotalString = str(round(pcOfTotal, 2)) + ' %'
#         if featTarget > 0:
#             if conTotal < featTarget:
#                 targetMetDict[featID] = 'Not met'
#             else:
#                 targetMetDict[featID] = 'Met'
#
#             propOfTarget = featAmount / featTarget
#             pcOfTarget = propOfTarget * 100
#             pcOfTargetString = str(round(pcOfTarget, 2)) + ' %'
#
#             propTargetMet = targetDict[featID][4] / featTarget
#             pcTargetMet = propTargetMet * 100
#             pcTargetMetString = str(round(pcTargetMet, 2)) + ' %'
#         else:
#             pcOfTargetString = 'No target'
#             pcTargetMetString = 'No target'
#             targetMetDict[featID] = 'No target'
#
#         identDict[featID] = [str(featID), featName, str(featAmount), pcOfTotalString, str(featTarget), pcOfTargetString, pcTargetMetString]
#
#     return identDict, targetMetDict
#
