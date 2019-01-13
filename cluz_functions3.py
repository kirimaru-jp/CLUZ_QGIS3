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

from qgis.core import QgsVectorLayer, NULL

import csv
import os

from .cluz_messages import clearProgressBar, infoMessage, makeProgressBar, warningMessage
from .cluz_make_file_dicts import checkCreateSporderDat, makeTargetDict, returnTempPathName
from .cluz_setup import checkStatusObjectValues, createAndCheckCLUZFiles


############################ Remove features ############################


def remFeaturesFromPuvspr2(setupObject, selectedFeatIDSet):
    puvspr2Path = setupObject.inputPath + os.sep + 'puvspr2.dat'
    tempPuvspr2Path = returnTempPathName(puvspr2Path, 'dat')
    with open(tempPuvspr2Path,'w', newline='') as out_file:
        puvspr2Writer = csv.writer(out_file)
        puvspr2Writer.writerow(['species', 'pu', 'amount'])

        with open(puvspr2Path, 'rt') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if int(row[0]) not in selectedFeatIDSet:
                    puvspr2Writer.writerow(row)

        out_file.close()
        os.remove(puvspr2Path)
        os.rename(tempPuvspr2Path, puvspr2Path)


def remFeaturesFromTargetCsv_Dict(setupObject, selectedFeatIDSet):
    tempTargetPath = returnTempPathName(setupObject.targetPath, "csv")
    with open(tempTargetPath,'w', newline='') as out_file:
        tempTargetWriter = csv.writer(out_file)

        with open(setupObject.targetPath, 'rt') as f:
            reader = csv.reader(f)
            rowHeader = True
            for row in reader:
                if rowHeader:
                    tempTargetWriter.writerow(row)
                    rowHeader = False
                else:
                    featID = int(row[0])
                    if featID in selectedFeatIDSet:
                        pass
                    else:
                        tempTargetWriter.writerow(row)

    out_file.close()
    os.remove(setupObject.targetPath)
    os.rename(tempTargetPath, setupObject.targetPath)

############################ Troubleshoot ############################

def troubleShootCLUZFiles(setupObject):
    setupObject = checkStatusObjectValues(setupObject)
    setupObject = createAndCheckCLUZFiles(setupObject)
    checkCreateSporderDat(setupObject)
    targetErrorSet, targetFeatIDSet = checkTargetCsvFile(setupObject)
    puvspr2AbundErrorSet, puvspr2AbundErrorRowSet, puvspr2PuIDSet, puvspr2FeatIDSet, puvspr2RowNum, puvspr2RecCountDict = checkAbundTableDatFile(setupObject, 'Puvspr2')
    sporderAbundErrorSet, sporderAbundErrorRowSet, sporderPuIDSet, sporderFeatIDSet, sporderRowNum, sporderRecCountDict = checkAbundTableDatFile(setupObject, 'Sporder')
    shapeErrorSet, puPuIDSet, duplicateIDText = checkPuShapeFile(setupObject)

    idValuesNotDuplicated = checkIDidValuesNotDuplicated(targetFeatIDSet, puvspr2FeatIDSet, puvspr2PuIDSet, puPuIDSet)
    abundDatFilesSame = checkAbundDatFilesSame(puvspr2PuIDSet, sporderPuIDSet, puvspr2FeatIDSet, sporderFeatIDSet, puvspr2RowNum, sporderRowNum, puvspr2RecCountDict, sporderRecCountDict)

    pushTargetTableErrorMessages(targetErrorSet)
    pushAbundTableFileErrorMessages(puvspr2AbundErrorSet, 'Puvspr2')
    pushAbundTableRowErrorMessages(puvspr2AbundErrorRowSet, 'Puvspr2')
    pushAbundTableFileErrorMessages(sporderAbundErrorSet, 'Sporder')
    pushAbundTableRowErrorMessages(sporderAbundErrorRowSet, 'Sporder')
    pushPuShapeFileErrorMessages(shapeErrorSet, duplicateIDText)

    combinedErrorSet = targetErrorSet|puvspr2AbundErrorSet|puvspr2AbundErrorRowSet|sporderAbundErrorSet|sporderAbundErrorRowSet|shapeErrorSet

    if len(combinedErrorSet) == 0 and idValuesNotDuplicated and abundDatFilesSame:
        makeTargetDict(setupObject)
        infoMessage('Status: ', 'no problems were found and the Target table has been updated to ensure it reflects the current data.')


def checkTargetCsvFile(setupObject):
    targetCSVFilePath = setupObject.targetPath
    featIDList = list()

    with open(targetCSVFilePath, 'rt') as f:
        countReader = csv.reader(f)
        rowTotalCount = sum(1 for row in countReader)

    progressBar = makeProgressBar('Processing target file')
    rowCount = 1

    with open(targetCSVFilePath, 'rt') as f:
        targetReader = csv.reader(f)
        origHeaderList = next(targetReader)
        headerList = list() #convert to lowercase so it doesn't matter whether the headers or lowercase, uppercase or a mix
        for aHeader in origHeaderList:
            headerList.append(aHeader.lower())

        targetErrorSet = set()
        for aRow in targetReader:
            progressBar.setValue((rowCount/rowTotalCount)*100)
            rowCount += 1

            featIDString = aRow[headerList.index('id')]
            featNameString = aRow[headerList.index('name')]
            featTypeString = aRow[headerList.index('type')]
            featSpfString = aRow[headerList.index('spf')]
            featTargetString = aRow[headerList.index('target')]
            featConservedString = aRow[headerList.index('conserved')]
            featTotalString = aRow[headerList.index('total')]
            featPc_TargetString = aRow[headerList.index('pc_target')]

            featIDList, targetErrorSet = checkFeatIDString(featIDList, featIDString, targetErrorSet)
            targetErrorSet = checkFeatNameString(featNameString, targetErrorSet)
            targetErrorSet = checkFeatTypeString(featTypeString, targetErrorSet)
            targetErrorSet = checkFeatSpfString(featSpfString, targetErrorSet)
            targetErrorSet = checkFeatTargetString(featTargetString, targetErrorSet)
            targetErrorSet = checkFeatConservedString(featConservedString, targetErrorSet)
            targetErrorSet = checkFeatTotalString(featTotalString, targetErrorSet)
            targetErrorSet = checkFeatPc_TargetString(featPc_TargetString, targetErrorSet)

        targetErrorSet = checkForDuplicateFeatIDs(featIDList, targetErrorSet)

    clearProgressBar()

    return targetErrorSet, set(featIDList)


def checkFeatIDString(featIDList, featIDString, errorSet):
    if featIDString == '':
        errorSet.add('featIDBlank')
    else:
        try:
            featIDList.append(int(featIDString))
            if int(featIDString) < 0:
                errorSet.add('featIDNotInt')
        except ValueError:
            errorSet.add('featIDNotInt')

    return featIDList, errorSet


def checkFeatNameString(featNameString, errorSet):
    if featNameString == '':
        errorSet.add('featNameBlank')

    featNameStringIsANumberBool = False
    try:
        float(featNameString)
        featNameStringIsANumberBool = True
    except ValueError:
        pass

    if featNameStringIsANumberBool is False and any(i.isdigit() for i in featNameString):
        errorSet.add('featNameWrongFormat')

    return errorSet


def checkFeatTypeString(featTypeString, errorSet):
    if featTypeString == '':
        errorSet.add('featTypeBlank')
    else:
        try:
            int(featTypeString)
            if int(featTypeString) < 0:
                errorSet.add('featTypeNotInt')
        except ValueError:
            errorSet.add('featTypeNotInt')

    return errorSet


def checkFeatSpfString(featSpfString, errorSet):
    if featSpfString == '':
        errorSet.add('featSpfBlank')
    else:
        try:
            float(featSpfString)
            if float(featSpfString) < 0:
                errorSet.add('featSpfNotFloat')
        except ValueError:
            errorSet.add('featSpfNotFloat')

    return errorSet


def checkFeatTargetString(featTargetString, errorSet):
    if featTargetString == '':
        errorSet.add('featTargetBlank')
    else:
        try:
            float(featTargetString)
            if float(featTargetString) < 0:
                errorSet.add('featTargetNotFloat')
        except ValueError:
            errorSet.add('featTargetNotFloat')

    return errorSet


def checkFeatConservedString(featConservedString, errorSet):
    if featConservedString == '':
        errorSet.add('featConservedBlank')
    else:
        try:
            if float(featConservedString) < 0:
                errorSet.add('featConservedNotFloat')
        except ValueError:
            errorSet.add('featConservedNotFloat')

    return errorSet


def checkFeatTotalString(featTotalString, errorSet):
    if featTotalString == '':
        errorSet.add('featTotalBlank')
    else:
        try:
            if float(featTotalString) < 0:
                errorSet.add('featTotalNotFloat')
        except ValueError:
            errorSet.add('featTotalNotFloat')

    return errorSet


def checkFeatPc_TargetString(featPc_TargetString, errorSet):
    if featPc_TargetString == '':
        errorSet.add('featPc_TargetBlank')
    elif featPc_TargetString == '-1':
        pass
    else:
        try:
            if float(featPc_TargetString) < 0:
                errorSet.add('featPc_TargetNotFloat')
        except ValueError:
            errorSet.add('featPc_TargetNotFloat')

    return errorSet


def checkForDuplicateFeatIDs(featIDList, errorSet):
    if len(featIDList) != len(set(featIDList)):
        errorSet.add('duplicateFeatID')

    return errorSet


def checkIDidValuesNotDuplicated(targetFeatIDSet, puvspr2FeatIDSet, puvspr2PuIDSet, puPuIDSet):
    idValuesNotDuplicated = True
    idValuesNotDuplicated = checkIDsMatchInTargetTableAndPuvspr2(targetFeatIDSet, puvspr2FeatIDSet, idValuesNotDuplicated)
    idValuesNotDuplicated = checkIDsMatchInPULayerAndPuvspr2(puvspr2PuIDSet, puPuIDSet, idValuesNotDuplicated)

    return idValuesNotDuplicated

def checkAbundDatFilesSame(puvspr2PuIDSet, sporderPuIDSet, puvspr2FeatIDSet, sporderFeatIDSet, puvspr2RowNum, sporderRowNum, puvspr2RecCountDict, sporderRecCountDict):
    abundDatFilesSame = True
    if puvspr2PuIDSet != sporderPuIDSet or puvspr2FeatIDSet != sporderFeatIDSet or puvspr2RowNum != sporderRowNum or puvspr2RecCountDict != sporderRecCountDict:
        warningMessage('puvspr2.dat and sporder.dat: ', 'The two files do not contain the same data. Delete the sporder.dat file in the input folder and CLUZ will create a new one in the correct format.')
        abundDatFilesSame = False

    return abundDatFilesSame

def pushTargetTableErrorMessages(targetErrorSet):
    for anError in targetErrorSet:
        if anError == 'featIDBlank':
            warningMessage('Target Table: ', 'at least one of the Feature ID values is blank.')
        if anError == 'featIDNotInt':
            warningMessage('Target Table: ', 'at least one of the Feature ID values is not a positive integer.')
        if anError == 'featNameBlank':
            warningMessage('Target Table: ', 'at least one of the Name values is blank.')
        if anError == 'featTypeBlank':
            warningMessage('Target Table: ', 'at least one of the Type values is blank.')
        if anError == 'featTypeNotInt':
            warningMessage('Target Table: ', 'at least one of the Type values is not a positve integer.')
        if anError == 'featSpfBlank':
            warningMessage('Target Table: ', 'at least one of the SPF values is blank.')
        if anError == 'featSpfNotFloat':
            warningMessage('Target Table: ', 'at least one of the SPF values is not a positive number.')
        if anError == 'featTargetBlank':
            warningMessage('Target Table: ', 'at least one of the Target values is blank.')
        if anError == 'featTargetNotFloat':
            warningMessage('Target Table: ', 'at least one of the Target values is not a positive number.')
        if anError == 'featConservedBlank':
            warningMessage('Target Table: ', 'at least one of the Conserved values is blank.')
        if anError == 'featConservedNotFloat':
            warningMessage('Target Table: ', 'at least one of the Conserved values is not a positive number.')
        if anError == 'featTotalBlank':
            warningMessage('Target Table: ', 'at least one of the Total values is blank.')
        if anError == 'featTotalNotFloat':
            warningMessage('Target Table: ', 'at least one of the Total values is not a positive number.')
        if anError == 'featPc_TargetBlank':
            warningMessage('Target Table: ', 'at least one of the % target met values is blank.')
        if anError == 'featPc_TargetNotFloat':
            warningMessage('Target Table: ', 'at least one of the % target met values is not a positive number (not including features with a target of 0, which are automatically given a % target of -1).')
        if anError == 'duplicateFeatID':
            warningMessage('Target Table: ', 'at least one of the Feature IDs appears twice in the Feature ID field.')
        if anError == 'featNameWrongFormat':
            warningMessage('Target Table: ', 'at least one of the Feature names is in the wrong format. They cannot contain letters and numbers.')


def checkAbundTableDatFile(setupObject, abundTableType):
    abundFilePath, abundFileNameText = returnAbundTableParameters(abundTableType, setupObject)
        
    recCountDict = dict() #Used to check whether there are the same number of records per feature in puvspr2.dat and sporder.dat files
    abundErrorSet, unitIDSet, featIDSet = set(), set(), set()
    rowNum = 2
    abundErrorRowSet = set()
    prevIDValueForChecking = -99

    with open(abundFilePath, 'rt') as f:
        countReader = csv.reader(f)
        progressBar = makeProgressBar('Processing ' + abundTableType + ' file')
        rowTotalCount = sum(1 for row in countReader)
        rowCount = 1

    with open(abundFilePath, 'rt') as f:
        abundFileReader = csv.reader(f)
        next(abundFileReader)

        for aRow in abundFileReader:
            progressBar.setValue((rowCount/rowTotalCount) * 100)
            rowCount += 1
            featID, unitID, featAmount = aRow[0:3]
            abundErrorSet, abundErrorRowSet = checkAbundTableFileWrongNumColumns(abundErrorSet, abundErrorRowSet, aRow, rowNum)
            abundErrorSet, abundErrorRowSet = checkAbundTableFileNotOrdered(abundErrorSet, abundErrorRowSet, abundTableType, featID, unitID, prevIDValueForChecking, rowNum)
            abundErrorSet, abundErrorRowSet, featIDSet, recCountDict = checkAbundTableFileFeatID(abundErrorSet, abundErrorRowSet, featID, featIDSet, recCountDict, rowNum)
            abundErrorSet, abundErrorRowSet, unitIDSet = checkAbundTableFilePUID(abundErrorSet, abundErrorRowSet, unitID, unitIDSet, rowNum)
            abundErrorSet, abundErrorRowSet  = checkAbundTableFileFeatAmount(abundErrorSet, abundErrorRowSet, featAmount, rowNum)

            rowNum += 1
            prevIDValueForChecking = updatePrevIDValueForChecking(abundTableType, prevIDValueForChecking, featID, unitID)
    clearProgressBar()


    return abundErrorSet, abundErrorRowSet, unitIDSet, featIDSet, rowNum, recCountDict


def returnAbundTableParameters(abundTableType, setupObject):
    if abundTableType == 'Puvspr2':
        abundFilePath = setupObject.inputPath + os.sep + 'puvspr2.dat'
        abundFileNameText = 'puvspr2.dat'
    elif abundTableType == 'Sporder':
        abundFilePath = setupObject.inputPath + os.sep + 'sporder.dat'
        abundFileNameText = 'sporder.dat'

    return abundFilePath, abundFileNameText


def updatePrevIDValueForChecking(abundTableType, prevIDValueForChecking, featID, unitID):
    if abundTableType == 'Puvspr2':
        prevIDValueForChecking = unitID
    elif abundTableType == 'Sporder':
        prevIDValueForChecking = featID
       
    return prevIDValueForChecking


def checkAbundTableFileWrongNumColumns(errorSet, errorRowSet, aRow, rowNum):
    if len(aRow) != 3:
        errorSet.add('wrongNumColumns')
        errorRowSet.add(rowNum)
        
    return errorSet, errorRowSet
        
        
def checkAbundTableFileNotOrdered(errorSet, errorRowSet, abundTableType, featID, unitID, prevIDValueForChecking, rowNum):
    if abundTableType == 'Puvspr2':
        try:
            if int(unitID) < int(prevIDValueForChecking):
                errorSet.add('notOrderedByPU')
                errorRowSet.add(rowNum)
        except ValueError:
            pass # Format error is picked up elsewhere
    elif abundTableType == 'Sporder':
        try:
            if int(featID) < int(prevIDValueForChecking):
                errorSet.add('notOrderedByFeat')
                errorRowSet.add(rowNum)
        except ValueError:
            pass # Format error is picked up elsewhere

    return errorSet, errorRowSet


def checkAbundTableFileFeatID(errorSet, errorRowSet, featID, featIDSet, recCountDict, rowNum):
    if featID == '':
        errorSet.add('featIDBlank')
        errorRowSet.add(rowNum)
    else:
        try:
            int(featID)
            featIDSet.add(int(featID))
            try:
                recCount = recCountDict[featID]
                recCount += 1
                recCountDict[featID] = recCount
            except KeyError:
                recCountDict[featID] = 1
            if int(featID) < 1:
                errorSet.add('featIDNeg')
                errorRowSet.add(rowNum)
        except ValueError:
            errorSet.add('featIDNotInt')
            errorRowSet.add(rowNum)

    return errorSet, errorRowSet, featIDSet, recCountDict


def checkAbundTableFilePUID(errorSet, errorRowSet, unitID, unitIDSet, rowNum):
    if unitID == '':
        errorSet.add('puIDBlank')
        errorRowSet.add(rowNum)
    else:
        try:
            int(unitID)
            unitIDSet.add(int(unitID))
            if int(unitID) < 1:
                errorSet.add('puIDNeg')
                errorRowSet.add(rowNum)
        except ValueError:
            errorSet.add('puIDNotInt')
            errorRowSet.add(rowNum)
        
    return errorSet, errorRowSet, unitIDSet


def checkAbundTableFileFeatAmount(errorSet, errorRowSet, featAmount, rowNum)   :                 
    if featAmount == '':
        errorSet.add('featAmountBlank')
        errorRowSet.add(rowNum)
    else:
        try:
            float(featAmount)
            if float(featAmount) < 0:
                errorSet.add('featAmountNeg')
                errorRowSet.add(rowNum)
        except ValueError:
            errorSet.add('featAmountNotFloat')
            errorRowSet.add(rowNum)
        
    return errorSet, errorRowSet


def pushAbundTableFileErrorMessages(abundErrorSet, abundFileNameText):
    for anError in abundErrorSet:
        if anError == 'wrongNumColumns':
            warningMessage(abundFileNameText + 'file: ', 'at least one of the rows does not contain 3 values.')
        if anError == 'notOrderedByPU':
            warningMessage(abundFileNameText + 'file: ', 'this file must be ordered by planning unit ID, from smallest to highest value.')
        if anError == 'notOrderedByFeat':
            warningMessage(abundFileNameText + 'file: ', 'this file must be ordered by feature ID, from smallest to highest value.')
        if anError == 'featIDBlank':
            warningMessage(abundFileNameText + 'file: ', 'at least one of the feature ID values is missing.')
        if anError == 'featIDNotInt':
            warningMessage(abundFileNameText + 'file: ', 'at least one of the feature ID values is not an integer.')
        if anError == 'featIDNeg':
            warningMessage(abundFileNameText + 'file: ', 'at least one of the feature ID values is less than 1.')
        if anError == 'puIDBlank':
            warningMessage(abundFileNameText + 'file: ', 'at least one of the planning unit ID values is missing.')
        if anError == 'puIDNotInt':
            warningMessage(abundFileNameText + 'file: ', 'at least one of the planning unit ID values is not an integer.')
        if anError == 'puIDNeg':
            warningMessage(abundFileNameText + 'file: ', 'at least one of the planning unit ID values is less than 1.')
        if anError == 'featAmountBlank':
            warningMessage(abundFileNameText + 'file: ', 'at least one of the amount values is missing.')
        if anError == 'featAmountNotFloat':
            warningMessage(abundFileNameText + 'file: ', 'at least one of the amount values is not a valid number.')
        if anError == 'featAmountNeg':
            warningMessage(abundFileNameText + 'file: ', 'at least one of the amount values is less than 0.')

    return abundErrorSet


def pushAbundTableRowErrorMessages(errorRowSet, abundFileNameText):
    if len(errorRowSet) > 0:
        errorRowList = list(errorRowSet)
        errorRowList.sort()
        messageText = ''
        for aErrorRow in errorRowList:
            messageText += str(aErrorRow) + ' '
        finalMessageText = messageText[:-1]
        warningMessage(abundFileNameText + 'file: ', 'errors are in the following rows: ' + finalMessageText)


def checkPuShapeFile(setupObject):
    puIDList, shapeErrorSet, = list(), set()

    puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
    puFeatures = puLayer.getFeatures()
    unitIDField = puLayer.fields().indexFromName('Unit_ID')
    puAreaField = puLayer.fields().indexFromName('Area')
    puCostField = puLayer.fields().indexFromName('Cost')
    unitStatusField = puLayer.fields().indexFromName('Status')

    progressBar = makeProgressBar('Processing planning unit shapefile')
    polyCount = 1
    polyTotalCount = puLayer.featureCount()

    for puFeature in puFeatures:
        progressBar.setValue((polyCount/polyTotalCount) * 100)
        polyCount += 1

        puAttributes = puFeature.attributes()
        puID = puAttributes[unitIDField]
        puIDList.append(puID)
        shapeErrorSet = checkPuShapeFilePUIDValue(shapeErrorSet, puID)
        shapeErrorSet = checkPuShapeFilePUAreaValue(shapeErrorSet, puAttributes, puAreaField)
        shapeErrorSet = checkPuShapeFilePUCostValue(shapeErrorSet, puAttributes, puCostField)
        shapeErrorSet = checkPuShapeFilePUStatusValue(shapeErrorSet, puAttributes, unitStatusField)
    clearProgressBar()

    shapeErrorSet, puIDSet, duplicateIDText = checkPuShapeFileDuplicatePUIDValue(shapeErrorSet, puIDList)

    return shapeErrorSet, puIDSet, duplicateIDText


def checkPuShapeFilePUIDValue(shapeErrorSet, puID):
    if puID == NULL:#NULL is used for blank values that return QPyNullVariant
        shapeErrorSet.add('puIDBlank')
    else:
        try:
            int(puID)
            if int(puID) < 0:
                shapeErrorSet.add('puIDNotInt')
        except ValueError:
            shapeErrorSet.add('puIDNotInt')

    return shapeErrorSet


def checkPuShapeFilePUAreaValue(shapeErrorSet, puAttributes, puAreaField):
    puArea = puAttributes[puAreaField]
    if puArea == NULL:
        shapeErrorSet.add('puAreaBlank')
    else:
        try:
            float(puArea)
            if float(puArea) < 0:
                shapeErrorSet.add('puAreaNotFloat')
        except ValueError:
            shapeErrorSet.add('puAreaNotFloat')

    return shapeErrorSet


def checkPuShapeFilePUCostValue(shapeErrorSet, puAttributes, puCostField):
    puCost = puAttributes[puCostField]
    if puCost == NULL:
        shapeErrorSet.add('puCostBlank')
    else:
        try:
            float(puCost)
            if float(puCost) < 0:
                shapeErrorSet.add('puCostNotFloat')
        except ValueError:
            shapeErrorSet.add('puCostNotFloat')

    return shapeErrorSet


def checkPuShapeFilePUStatusValue(shapeErrorSet, puAttributes, unitStatusField):
    unitStatus = puAttributes[unitStatusField]
    if not unitStatus in ['Available', 'Conserved', 'Earmarked', 'Excluded']:
        shapeErrorSet.add('puStatusWrong')

    return shapeErrorSet


def checkPuShapeFileDuplicatePUIDValue(shapeErrorSet, puIDList):
    puIDSet = set(puIDList)
    duplicateIDText = 'The following planning unit ID values appear more than once in the Unit_ID field: '
    if len(puIDList) != len(puIDSet):
        shapeErrorSet.add('duplicateFeatID')
        duplicateSet = set([x for x in puIDList if puIDList.count(x) > 1])
        duplicateList = list(duplicateSet)
        duplicateList.sort()
        for aNum in duplicateList:
            duplicateIDText += str(aNum) + ', '
        duplicateIDText = duplicateIDText[0:-2]

    return shapeErrorSet, puIDSet, duplicateIDText


def pushPuShapeFileErrorMessages(shapeErrorSet, duplicateIDText):
    for anError in shapeErrorSet:
        if anError == 'puIDBlank':
            warningMessage('Planning unit layer: ', 'at least one of the planning unit ID values is blank.')
        if anError == 'duplicateFeatID':
            warningMessage('Planning unit layer: ', duplicateIDText)
        if anError == 'puIDNotInt':
            warningMessage('Planning unit layer: ', 'at least one of the planning unit ID values is not an integer greater than 0.')
        if anError == 'puAreaBlank':
            warningMessage('Planning unit layer: ', 'at least one of the planning unit area values is blank.')
        if anError == 'puAreaNotFloat':
            warningMessage('Planning unit layer: ', 'at least one of the planning unit area values is not a non-negative number.')
        if anError == 'puCostBlank':
            warningMessage('Planning unit layer: ', 'at least one of the planning unit cost values is blank')
        if anError == 'puCostNotFloat':
            warningMessage('Planning unit layer: ', 'at least one of the planning unit cost values is not a non-negative number.')
        if anError == 'puCostNotFloat':
            warningMessage('Planning unit layer: ', 'at least one of the planning unit cost values is not a non-negative number.')
        if anError == 'puStatusWrong':
            warningMessage('Planning unit layer: ', 'at least one of the planning unit status values is incorrect. They should either be Available, Conserved, Earmarked or Excluded.')


def checkIDsMatchInTargetTableAndPuvspr2(targetFeatIDSet, puvspr2FeatIDSet, idValuesNotDuplicated):
    extraTargetFeatIDset, extraAbundFeatIDset = findValuesInOneSet(targetFeatIDSet, puvspr2FeatIDSet)
    if len(extraTargetFeatIDset) > 0:
        errorText = ''
        for aValue in extraTargetFeatIDset:
            errorText += str(aValue) + ', '
        errorText = errorText[: -2]
        warningMessage('Abundance and Target tables: ', 'the following Feature IDs appear in the Target Table but not in the puvspr2.dat file: ' + errorText)
        idValuesNotDuplicated = False
    if len(extraAbundFeatIDset) > 0:
        errorText = ''
        for aValue in extraAbundFeatIDset:
            errorText += str(aValue) + ', '
        errorText = errorText[: -2]
        warningMessage('puvspr2.dat file and Target tables: ', 'the following Feature IDs appear in the puvspr2.dat file but not in the Target table: ' + errorText)
        idValuesNotDuplicated = False

    return idValuesNotDuplicated


def checkIDsMatchInPULayerAndPuvspr2(puvspr2PuIDSet, puPuIDSet, idValuesNotDuplicated):
    extraPuvspr2PuIDSet, extraPUPuIDSet = findValuesInOneSet(puvspr2PuIDSet, puPuIDSet)
    if len(extraPuvspr2PuIDSet) > 0:
        errorText = ''
        for aValue in extraPuvspr2PuIDSet:
            errorText += str(aValue) + ', '
        errorText = errorText[: -2]
        warningMessage('puvspr2.dat file and Planning unit layer: ', 'the following planning unit IDs appear in the puvspr2.dat file but not in the planning unit layer: ' + errorText)
        idValuesNotDuplicated = False

    return idValuesNotDuplicated


def findValuesInOneSet(inputSet1, inputSet2):
    set1 = set()
    set2 = set()
    bigSet = inputSet1.union(inputSet2)
    for aValue in bigSet:
        if aValue in inputSet1 and aValue not in inputSet2:
            set1.add(aValue)
        if aValue not in inputSet1 and aValue in inputSet2:
            set2.add(aValue)

    return set1, set2