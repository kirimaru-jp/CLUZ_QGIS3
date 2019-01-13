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

import os
import csv
import re

from .cluz_messages import clearProgressBar, makeProgressBar, warningMessage


def makeTargetDict(setupObject):
    targetDict = dict()
    targetCSVFilePath = setupObject.targetPath
    try:
        with open(targetCSVFilePath, 'rt') as f:
            targetReader = csv.reader(f)

            origHeaderList = next(targetReader)
            headerList = list() #convert to lowercase so it doesn't matter whether the headers or lowercase, uppercase or a mix
            for aHeader in origHeaderList:
                headerList.append(aHeader.lower())

            for aRow in targetReader:
                featID = int(aRow[headerList.index('id')])
                featList = makeTargetDictRowFeatList(aRow, headerList)
                targetDict[featID] = featList

    except ValueError:
        warningMessage('Target table error', 'The Target table is incorrectly formatted. Please use the Troubleshoot all CLUZ files function to identify the problem.')
        targetDict = 'blank'

    return targetDict


def makeTargetDictRowFeatList(aRow, headerList):
    featName = str(aRow[headerList.index('name')])
    featType = int(aRow[headerList.index('type')])
    featSpf = float(aRow[headerList.index('spf')])
    featTarget = float(aRow[headerList.index('target')])
    featConserved = float(aRow[headerList.index('conserved')])
    featTotal = float(aRow[headerList.index('total')])
    featPc_Target = float(aRow[headerList.index('pc_target')])
    featList = [featName, featType, featSpf, featTarget, featConserved, featTotal, featPc_Target]

    return featList


def returnRoundedValue(setupObject, rawValue):
    decPrec = setupObject.decimalPlaces
    limboValue = round(float(rawValue), decPrec)
    finalValue = format(limboValue, "." + str(decPrec) + "f")

    return finalValue


def removePrefixMakeIDValue(aString):
    numList = re.findall(r'[0-9]+', aString)
    revNumList = numList[::-1]
    if len(revNumList) > 0:
        idValue = int(revNumList[0])
    else:
        idValue = ''

    return idValue


def makeTargetDialogRowList(setupObject):
    targetFileHeaderList = makeTargetFileHeaderList(setupObject)
    targetFileDataRowCount = returnTargetFileDataRowCount(setupObject)

    rawTargetDialogDict  = makeRawTargetDialogDict(setupObject)
    targetDialogRowList = list()
    targetDialogRowList.append(targetFileHeaderList)

    numericColsList = list()

    targetDialogDict = dict()
    for colName in targetFileHeaderList:
        rawValueList = rawTargetDialogDict[colName]
        valueList, ColTypeIntOrFloat = formatRawValueList_IdentifyNumericalCols(setupObject, colName, rawValueList)
        targetDialogDict[colName] = valueList
        if ColTypeIntOrFloat:
            numericColsList.append(colName.lower()) # Turned to lower case to allow later comparisons

    for aRow in range(0, targetFileDataRowCount):
        rowList = list()
        for colName in targetFileHeaderList:
            rowList.append(targetDialogDict[colName][aRow])
        targetDialogRowList.append(rowList)

    return targetDialogRowList, numericColsList


def makeTargetFileHeaderList(setupObject):
    targetCSVFilePath = setupObject.targetPath
    try:
        with open(targetCSVFilePath, 'rt') as f:
            targetReader = csv.reader(f)
            targetFileHeaderList = next(targetReader)

    except ValueError:
        targetFileHeaderList = 'blank'

    return targetFileHeaderList


def returnTargetFileDataRowCount(setupObject):
    targetCSVFilePath = setupObject.targetPath
    with open(targetCSVFilePath, 'rt') as f:
        countReader = csv.reader(f)
        next(countReader)
        targetFileDataRowCount = sum(1 for row in countReader)

    return targetFileDataRowCount


def makeRawTargetDialogDict(setupObject):
    rawTargetDialogDict = dict()
    targetCSVFilePath = setupObject.targetPath
    try:
        with open(targetCSVFilePath, 'rt') as f:
            targetReader = csv.reader(f)
            targetFileHeaderList = next(targetReader)

            for aRow in targetReader:
                for aCol in range(0, len(targetFileHeaderList)):
                    colName = targetFileHeaderList[aCol]
                    try:
                        rawColumnValuesList = rawTargetDialogDict[colName]
                    except KeyError:
                        rawColumnValuesList = list()
                    rawColumnValuesList.append(aRow[aCol])
                    rawTargetDialogDict[colName] = rawColumnValuesList
    except ValueError:
        rawTargetDialogDict = 'blank'

    return rawTargetDialogDict


def formatRawValueList_IdentifyNumericalCols(setupObject, colName, rawValueList):
    countIntList = list()
    countFloatList = list()
    ColTypeIntOrFloat = False
    for aValue in rawValueList:
        try:
            countIntList.append(int(aValue))
        except ValueError:
            pass
        try:
            countFloatList.append(float(aValue))
        except ValueError:
            pass

    valueList = list()
    if len(rawValueList) == len(countIntList):
        ColTypeIntOrFloat = True
        for aValue in rawValueList:
            valueList.append(int(aValue))
    elif len(rawValueList) != len(countIntList) and len(rawValueList) == len(countFloatList):
        ColTypeIntOrFloat = True
        for aValue in rawValueList:
            floatValue = float(aValue)
            roundedValue = returnRoundedValue(setupObject, floatValue)
            valueList.append(float(roundedValue))
    else:
        for aValue in rawValueList:
            valueList.append(aValue)

    return valueList, ColTypeIntOrFloat


def makeAbundancePUKeyDict(setupObject):
    abundPUKeyDict = dict()
    abundPUKeyDictCorrect = True
    puvspr2FilePath = setupObject.inputPath + os.sep + 'puvspr2.dat'

    with open(puvspr2FilePath, 'rt') as f:
        countReader = csv.reader(f)
        rowTotalCount = sum(1 for row in countReader)
    progressBar = makeProgressBar('Processing target file')
    rowCount = 1


    with open(puvspr2FilePath, 'rt') as f:
        abundReader = csv.reader(f)
        next(abundReader)
        for aRow in abundReader:
            progressBar.setValue((rowCount/rowTotalCount) * 100)
            rowCount += 1
            try:
                featID = int(aRow[0])
                puID = int(aRow[1])
                abundValue = float(aRow[2])
                try:
                    puAbundDict = abundPUKeyDict[puID]
                except KeyError:
                    puAbundDict = {}
                puAbundDict[featID] = abundValue
                abundPUKeyDict[puID] = puAbundDict
            except ValueError:
                abundPUKeyDictCorrect = False

    clearProgressBar()

    if abundPUKeyDictCorrect is False:
        warningMessage('Target table error', 'The Target table is incorrectly formatted. Please use the Troubleshoot all CLUZ files function to identify the problem.')
        abundPUKeyDict = 'blank'

    return abundPUKeyDict


def makePuvspr2DatFile(setupObject):
    inputPathName = setupObject.inputPath
    puvspr2DatPathName = inputPathName + os.sep + 'puvspr2.dat'

    abundPUKeyDict = setupObject.abundPUKeyDict
    puList = list(abundPUKeyDict.keys())
    puList.sort()

    progressBar = makeProgressBar('Making a new puvspr2.dat file')
    rowTotalCount = len(puList)
    rowCount = 1

    with open(puvspr2DatPathName,'w', newline='') as puvspr2DatFile:
        puvspr2DatWriter = csv.writer(puvspr2DatFile)
        puvspr2DatWriter.writerow(['species', 'pu', 'amount'])
        for puID in puList:
            progressBar.setValue((rowCount/rowTotalCount) * 100)
            rowCount += 1

            aPUAbundDict = abundPUKeyDict[puID]
            aFeatList = list(aPUAbundDict.keys())
            aFeatList.sort()
            for featID in aFeatList:
                featAmount = aPUAbundDict[featID]
                puvspr2DatWriter.writerow([featID, puID, featAmount])
    clearProgressBar()


def checkCreateSporderDat(setupObject):
    if setupObject.setupStatus == 'files_checked':
        inputPathName = setupObject.inputPath
        sporderDatName = inputPathName + os.sep + 'sporder.dat'
        if os.path.isfile(sporderDatName) is False:
            makeSporderDatFile(setupObject)


def makeSporderDatFile(setupObject):
    sporderDict = makeSporderDict(setupObject)
    featList = list(sporderDict.keys())
    featList.sort()

    if setupObject.abundPUKeyDict == 'blank':
        setupObject.abundPUKeyDict = makeAbundancePUKeyDict(setupObject)
    inputPathName = setupObject.inputPath
    sporderPathName = inputPathName + os.sep + 'sporder.dat'

    progressBar = makeProgressBar('Making a new sporder.dat file')
    rowTotalCount = len(featList)
    rowCount = 1

    with open(sporderPathName, 'w', newline='') as out_file:
        sporderWriter = csv.writer(out_file)
        sporderWriter.writerow(['species', 'pu', 'amount'])


        for featID in featList:
            progressBar.setValue((rowCount/rowTotalCount) * 100)
            rowCount += 1

            aPUDict = sporderDict[featID]
            aPUList = list(aPUDict.keys())
            aPUList.sort()
            for puID in aPUList:
                featAmount = aPUDict[puID]
                sporderWriter.writerow([featID, puID, featAmount])
    clearProgressBar()

def makeSporderDict(setupObject):
    sporderDict = dict()
    abundPUKeyDict = setupObject.abundPUKeyDict
    for puID in abundPUKeyDict:
        featDict = abundPUKeyDict[puID]
        for featID in featDict:
            featAmount = featDict[featID]
            try:
                puDict = sporderDict[featID]
            except KeyError:
                puDict = dict()
            puDict[puID] = featAmount
            sporderDict[featID] = puDict

    return sporderDict


def updateTargetCSVFromTargetDict(setupObject, targetDict):
    decPrec = setupObject.decimalPlaces
    targetCSVFilePath = setupObject.targetPath
    textRows = list()
    with open(targetCSVFilePath, 'rt') as in_file:
        targetReader = csv.reader(in_file)
        origHeaderList = next(targetReader)
        textRows.append(origHeaderList)
        lowerHeaderList = list() #convert to lowercase so it doesn't matter whether the headers or lowercase, uppercase or a mix
        for aHeader in origHeaderList:
            lowerHeaderList.append(aHeader.lower())

        for aRow in targetReader:
            featID = int(aRow[lowerHeaderList.index('id')])
            featTarget = float(aRow[lowerHeaderList.index('target')])
            pcTarget = returnPCTargetValueForTargetTable(targetDict, featID, featTarget, decPrec)

            aRow[lowerHeaderList.index('conserved')] = targetDict[featID][4]
            aRow[lowerHeaderList.index('total')] = targetDict[featID][5]
            aRow[lowerHeaderList.index('pc_target')] = pcTarget
            textRows.append(aRow)

    with open(targetCSVFilePath,'w', newline='') as out_file:
        targetWriter = csv.writer(out_file)
        for bRow in textRows:
            targetWriter.writerow(bRow)


def returnPCTargetValueForTargetTable(targetDict, featID, featTarget, decPrec):
    if featTarget > 0:
        pcTarget = targetDict[featID][4] / featTarget
        pcTarget *= 100
        pcTarget = round(float(pcTarget), decPrec)
        pcTarget = format(pcTarget, "." + str(decPrec) + "f")
    else:
        pcTarget = -1

    return pcTarget


def writeBoundDatFile(setupObject, boundResultsDict, extEdgeBool):
    boundDatFilePath = setupObject.inputPath + os.sep + 'bound.dat'

    progressBar = makeProgressBar('Saving bound.dat file')
    rowTotalCount = len(boundResultsDict)
    rowCount = 1

    with open(boundDatFilePath,'w', newline='') as out_file:
        boundDatWriter = csv.writer(out_file)
        boundDatWriter.writerow(['id1', 'id2', 'boundary'])
        keyList = list(boundResultsDict.keys())
        keyList.sort()
        for aKey in keyList:
            progressBar.setValue((rowCount/rowTotalCount) * 100)
            rowCount += 1

            (id1, id2) = aKey
            rawAmount = boundResultsDict[aKey]
            aAmount = round(float(rawAmount), setupObject.decimalPlaces)
            aAmount = format(aAmount, '.' + str(setupObject.decimalPlaces) + 'f')
            if id1 != id2:
                boundDatWriter.writerow([id1, id2, aAmount])
            if id1 == id2 and extEdgeBool == True:
                boundDatWriter.writerow([id1, id2, aAmount])
    clearProgressBar()


def returnLowestUnusedFileNameNumber(dirPath, fileNameBase, extTypeText):
    fileNameNumber = 1
    while os.path.exists(dirPath + os.sep + fileNameBase + str(fileNameNumber) + extTypeText):
        fileNameNumber += 1

    return fileNameNumber


############### Add data to target table from Add data from Vec files #################

def addFeaturesToTargetCsvFile(setupObject, addAbundDict, featIDList):
    tempTargetPath = returnTempPathName(setupObject.targetPath, 'csv')
    with open(tempTargetPath,'w', newline='') as tempTargetFile:
        tempTargetWriter = csv.writer(tempTargetFile)

        puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
        addTargetDict = makeAddTargetDict(puLayer, addAbundDict, featIDList)

        with open(setupObject.targetPath, 'rt') as f:
            reader = csv.reader(f)
            for row in reader:
                tempTargetWriter.writerow(row)

            addTargetList = list(addTargetDict.keys())
            addTargetList.sort()
            for featID in addTargetList:
                (featCon, featTotal) = addTargetDict[featID]
                row = [str(featID), 'blank', '0', '0', '0', str(featCon), str(featTotal), '-1']
                tempTargetWriter.writerow(row)

    tempTargetFile.close()
    os.remove(setupObject.targetPath)
    os.rename(tempTargetPath, setupObject.targetPath)


def makeAddTargetDict(puLayer, addAbundDict, featIDList):
    puFeatures = puLayer.getFeatures()
    unitIDField = puLayer.fields().indexFromName('Unit_ID')
    unitStatusField = puLayer.fields().indexFromName('Status')

    addTargetDict = dict()
    for featID in featIDList:
        addTargetDict[featID] = (0, 0) #[Con amount, total amount]

    for puFeature in puFeatures:
        puAttributes = puFeature.attributes()
        puID = puAttributes[unitIDField]
        puStatus = puAttributes[unitStatusField]

        for bFeatID in featIDList:
            try:
                puAddAbundDict = addAbundDict[puID]
                featAmount = puAddAbundDict[bFeatID]
                featCon, featTotal = addTargetDict[bFeatID]
                featTotal += featAmount
                if puStatus == 'Conserved' or puStatus == 'Earmarked':
                    featCon += featAmount
                addTargetDict[bFeatID] = (featCon, featTotal)
            except KeyError:
                pass

    return addTargetDict


############### For all #################

def returnTempPathName(pathString, fileType):
    suffixString = '.' + fileType
    tempNumber = 0
    while os.path.exists(pathString.replace(suffixString, '_tmp' + str(tempNumber) + suffixString)):
        tempNumber += 1
    tempPathName = pathString.replace(suffixString, '_tmp' + str(tempNumber) + suffixString)

    return tempPathName