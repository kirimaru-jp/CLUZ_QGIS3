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

import csv
import os

from .cluz_messages import warningMessage


def makeMarxanFileList(setupObject):
    marxanFileList = list()

    fileList = os.listdir(setupObject.outputPath)
    analysisSet = set()
    for fileNameString in fileList:
        portfolioIdentifierString = fileNameString[-11:-9]
        if portfolioIdentifierString == '_r':
            analysisSet.add(fileNameString[0:-11])

    for aPathName in analysisSet:
        runPath = aPathName + '_r'
        fileCount = 0
        for bFile in fileList:
            if bFile.startswith(runPath):
                fileCount += 1
        if fileCount > 0:
            marxanFileList.append(aPathName + ' - ' + str(fileCount) + ' files')

    return marxanFileList


def checkMinPatchFile(MinPatchDialog, minpatchObject):
    runMinPatchBool = True
    detailsDatPath = MinPatchDialog.detailsLineEdit.text()
    if os.path.isfile(detailsDatPath):
        with open(detailsDatPath, 'rt') as f:
            detailsReader = csv.reader(f)
            detailsHeader = next(detailsReader, None)  # skip the headers
        if detailsHeader == ['id', 'area', 'zone', 'patch_area', 'radius']:
            minpatchObject.detailsDatPath = detailsDatPath
        else:
            warningMessage('Incorrect format', 'The specified MinPatch details file is incorrectly formatted. It must contain five fields named id, area, zone, patch_area and radius.')
            runMinPatchBool = False
    else:
        warningMessage('Incorrect pathname', 'The specified pathname for the MinPatch details file is invalid. Please choose another one.')
        runMinPatchBool = False
        
    return runMinPatchBool, minpatchObject


def checkMinPatchBLMValue(MinPatchDialog, minpatchObject, runMinPatchBool):
    blmText = MinPatchDialog.blmLineEdit.text()
    try:
        blmNumber = float(blmText)
        if blmNumber >= 0:
            minpatchObject.blm = blmNumber
        else:
            warningMessage('Incorrect BLM format', 'The BLM value must be a non-negative number.')
            runMinPatchBool = False
    except ValueError:
        warningMessage('Incorrect BLM format', 'The BLM value must be a non-negative number.')
        runMinPatchBool = False
        
    return runMinPatchBool, minpatchObject


def checkMinPatchSelectedItemsList (MinPatchDialog, minpatchObject, runMinPatchBool):
    selectedItemsList = MinPatchDialog.fileListWidget.selectedItems()
    if len(selectedItemsList) > 0:
        selectedMarxanFileText = [item.text() for item in MinPatchDialog.fileListWidget.selectedItems()][0]

        suffixText = selectedMarxanFileText.split(' - ')[-1]
        numberText = suffixText.split(' ')[0]
        runNumberLen = len(numberText) + 9 #Calcs length of text to remove from end of string
        minpatchObject.marxanFileName = selectedMarxanFileText[0: -runNumberLen]
    else:
        warningMessage('No files selected', 'Please select one of the sets of files before proceeding.')
        runMinPatchBool = False
        
    return runMinPatchBool, minpatchObject