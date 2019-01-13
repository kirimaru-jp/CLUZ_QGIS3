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

import copy
import os

from .cluz_mpoutputs import makeMPPatchStatsDict, makeRunZoneFeaturePropStatsDict, printMPSummedResults, produceMPSummedDict, printMPPatchStats, updateMPSummedDict, printMPZoneStats, producePatchResultsDict, printMPRunResults, printMPZoneFeaturePropStats, makeRunZoneStatsDict
from .cluz_mpfunctions import makeMPPatchDict, makeMPCostDict, remSmallPatchesFromUnitDict, createMPRunningUnitDictionary, addConservedPUs, runSimWhittle, addMPPatches
from .cluz_messages import successMessage
from .cluz_display import removePreviousMinPatchLayers, displayGraduatedLayer, reloadPULayer, displayBestOutput
from .cluz_mpsetup import makeMPMarxanFileList
from .cluz_functions5 import addBestMarxanOutputToPUShapefile, addSummedMarxanOutputToPUShapefile

def runMinPatch(setupObject, minpatchObject, minpatchDataDict):
    marxanNameString = minpatchObject.marxanFileName + '_r'
    finalNameString = 'mp_' + marxanNameString
    marxanSolFileList = makeMPMarxanFileList(setupObject, marxanNameString)

    preMarxanUnitDict = minpatchDataDict['initialUnitDictionary']
    summedSolDict = produceMPSummedDict(preMarxanUnitDict)
    patchResultsDict = dict()
    zoneStatsDict = dict()
    zoneFeaturePropStatsDict = dict()

    bestPortfolioCost = -1
    continueBool = True

    for marxanSolFilePath in marxanSolFileList:
        runningUnitDict = createMPRunningUnitDictionary(minpatchDataDict, marxanSolFilePath)
        patchDict = makeMPPatchDict(runningUnitDict, minpatchDataDict)

        if minpatchDataDict['patch_stats'] and continueBool:
            beforePatchStatsDict = makeMPPatchStatsDict(patchDict, minpatchDataDict)

        if minpatchDataDict['rem_small_patch'] and continueBool:
            runningUnitDict = remSmallPatchesFromUnitDict(minpatchDataDict,runningUnitDict, patchDict, marxanSolFilePath)

        if minpatchDataDict['add_patches'] and continueBool:
            runningUnitDict, continueBool = addMPPatches(minpatchDataDict, runningUnitDict, marxanSolFilePath)

        if minpatchDataDict['whittle_polish'] and continueBool:
            runningUnitDict = runSimWhittle(runningUnitDict, minpatchDataDict, marxanSolFilePath)

        runningUnitDict = addConservedPUs(runningUnitDict,minpatchDataDict)

        if minpatchDataDict['patch_stats'] and continueBool:
            patchDict = makeMPPatchDict(runningUnitDict, minpatchDataDict)
            afterPatchStatsDict = makeMPPatchStatsDict(patchDict, minpatchDataDict)

        if continueBool:
            outputFilePath = marxanSolFilePath.replace(marxanNameString, finalNameString)
            printMPRunResults(minpatchDataDict, runningUnitDict, outputFilePath)

            costDict = makeMPCostDict(minpatchDataDict, runningUnitDict)
            totalCost = costDict['totalBoundaryCost'] + costDict['totalUnitCost']

            if minpatchDataDict['patch_stats']:
                patchResultsDict = producePatchResultsDict(patchResultsDict, marxanSolFilePath, beforePatchStatsDict, afterPatchStatsDict, costDict)

            if minpatchDataDict['zone_stats']:
                zoneNameString = os.path.basename(marxanSolFilePath)
                zoneStatsDict[zoneNameString] = makeRunZoneStatsDict(minpatchDataDict, runningUnitDict)
                zoneFeaturePropStatsDict[zoneNameString] = makeRunZoneFeaturePropStatsDict(minpatchDataDict, runningUnitDict)

            if bestPortfolioCost == -1:
                bestPortfolioCost = totalCost
                bestPortfolio = copy.deepcopy(runningUnitDict)

            if bestPortfolioCost != -1 and totalCost < bestPortfolioCost:
                bestPortfolioCost = totalCost
                bestPortfolio = copy.deepcopy(runningUnitDict)

            summedDict = updateMPSummedDict(summedSolDict,runningUnitDict)

    if continueBool:
        bestFileName = setupObject.outputPath + os.sep + 'mp_' + minpatchObject.marxanFileName + '_best.txt'
        printMPRunResults(minpatchDataDict, bestPortfolio, bestFileName)

        summedFileName = setupObject.outputPath + os.sep + 'mp_' + minpatchObject.marxanFileName + '_summed.txt'
        printMPSummedResults(summedDict, summedFileName)

        if minpatchDataDict['patch_stats']:
            patchstatsFileName = setupObject.outputPath + os.sep + 'mp_' + minpatchObject.marxanFileName + '_patchstats.csv'
            printMPPatchStats(patchResultsDict, patchstatsFileName)

        if minpatchDataDict['zone_stats']:
            zoneStatsBaseFileName = setupObject.outputPath + os.sep + 'mp_' + minpatchObject.marxanFileName
            printMPZoneStats(minpatchDataDict, zoneStatsDict, zoneStatsBaseFileName)
            printMPZoneFeaturePropStats(minpatchDataDict, zoneFeaturePropStatsDict, zoneStatsBaseFileName)

        addBestMarxanOutputToPUShapefile(setupObject, bestFileName, 'MP_Best')
        addSummedMarxanOutputToPUShapefile(setupObject, summedFileName, 'MP_SF_Scr')

        reloadPULayer(setupObject)
        removePreviousMinPatchLayers()
        bestLayerName = 'MP Best (' + minpatchObject.marxanFileName + ')'
        summedLayerName = 'MP SF_Score (' + minpatchObject.marxanFileName + ')'
        displayBestOutput(setupObject, 'MP_Best', bestLayerName)
        displayGraduatedLayer(setupObject, 'MP_SF_Scr', summedLayerName, 1) #1 is SF legend code

        successMessage('MinPatch results', 'MinPatch has completed the analysis and the results files are in the specified output folder.')




