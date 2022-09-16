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

from qgis.core import QgsVectorLayer

from .cluz_checkup import returnFeatIDSetFromAbundPUKeyDict
from .cluz_functions3 import remFeaturesFromPuvspr2, remFeaturesFromTargetCsv_Dict
from .cluz_make_file_dicts import makeTargetDict, makeAbundancePUKeyDict, makeSporderDatFile
from .cluz_messages import criticalMessage, successMessage


#######Remove features ##########

def createFeatureList_Dict(setupObject):
    targetFeatIDSet = set(setupObject.targetDict.keys())
    abundFeatIDSet = returnFeatIDSetFromAbundPUKeyDict(setupObject)
    featIDSet = targetFeatIDSet.union(abundFeatIDSet)
    featIDList = list(featIDSet)
    featIDList.sort()

    featStringList = list()
    missingFeatStringList = list() #This is for features that are missing from one or other of the target or abund tables
    featStringDict = dict()
    for aFeat in featIDList:
        try:
            aString = str(aFeat) + ' - ' + setupObject.targetDict[aFeat][0]
            if aFeat in abundFeatIDSet:
                pass
            else:
                aString = '*Target table only* ' + aString
        except KeyError:
            aString = '*Abundance table only * ' + str(aFeat) + ' - blank'
        if aString[0] == '*':
            missingFeatStringList.append(aString)
        else:
            featStringList.append(aString)
        featStringDict[aString] = aFeat
    finalFeatStringList = missingFeatStringList + featStringList

    return finalFeatStringList, featStringDict


def removeSelectedFeaturesFromTarget_AbundFiles(RemoveDialog, setupObject, featStringDict):
    selectedFeatIDList = [featStringDict[item.text()] for item in RemoveDialog.featListWidget.selectedItems()]
    selectedFeatIDSet = set(selectedFeatIDList)
    selectedFeatIDListLength = len(selectedFeatIDList)
    if selectedFeatIDListLength > 0:
        remFeaturesFromPuvspr2(setupObject, selectedFeatIDSet)
        setupObject.abundPUKeyDict = makeAbundancePUKeyDict(setupObject)
        makeSporderDatFile(setupObject)

        remFeaturesFromTargetCsv_Dict(setupObject, selectedFeatIDSet)
        setupObject.targetDict = makeTargetDict(setupObject)

        successMessage('Task successfully completed: ', str(selectedFeatIDListLength) + ' features have been removed.')
        RemoveDialog.close()
    else:
        criticalMessage('No features selected', 'No features were selected and so no changes have been made.')
        RemoveDialog.close()


#######Update target table ##########

def updateConTotFieldsTargetDict(setupObject, newConTotDict):
    targetDict = setupObject.targetDict
    decPrec = setupObject.decimalPlaces
    for featID in targetDict:
        targetList = targetDict[featID]
        featTarget = targetList[3]
        try:
            targetList[4] = newConTotDict[featID][0]
        except KeyError:
            targetList[4] = 0
        try:
            targetList[5] = newConTotDict[featID][1]
        except KeyError:
            targetList[5] = 0

        if featTarget > 0:
            pcTarget = targetDict[featID][4] / featTarget
            pcTarget *= 100
            pcTarget = round(float(pcTarget), decPrec)
            pcTarget = format(pcTarget, "." + str(decPrec) + "f")
        else:
            pcTarget = -1
        targetList[6] = pcTarget

        targetDict[featID] = targetList

    return targetDict


def returnConTotDict(setupObject):
    amountCon_Tot_Dict = dict()

    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    puFeatures = puLayer.getFeatures()
    puIDField = puLayer.fields().indexFromName('Unit_ID')
    puStatusField = puLayer.fields().indexFromName('Status')

    for puFeature in puFeatures:
        puAttributes = puFeature.attributes()
        unitID = puAttributes[puIDField]
        unitStatus = puAttributes[puStatusField]
        try:
            puAbundDict = setupObject.abundPUKeyDict[unitID]
            for featID in puAbundDict:
                featAmount = puAbundDict[featID]
                try:
                    conAmount, totAmount = amountCon_Tot_Dict[featID]
                except KeyError:
                    conAmount, totAmount = [0, 0]

                totAmount += featAmount
                if unitStatus == 'Earmarked' or unitStatus == 'Conserved':
                    conAmount += featAmount

                amountCon_Tot_Dict[featID] = [conAmount, totAmount]
        except KeyError:
            pass

    return amountCon_Tot_Dict

#######Update target table ##########