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

import copy
import math

from .cluz_functions4 import makeRestrictedRangeDict
from .cluz_messages import clearProgressBar, makeProgressBar, warningMessage



def returnSpecifiedStatusPUIDSet(setupObject, specifiedStatusSet):
    puLayer = QgsVectorLayer(setupObject.puPath, "Planning units", "ogr")
    provider = puLayer.dataProvider()
    idFieldIndex = provider.fieldNameIndex("Unit_ID")
    statusFieldIndex = provider.fieldNameIndex("Status")

    specifiedStatusPUIDSet = set()
    puFeatures = puLayer.getFeatures()
    for puFeature in puFeatures:
        puAttributes = puFeature.attributes()
        puID = int(puAttributes[idFieldIndex])
        puStatusText = str(puAttributes[statusFieldIndex])
        if puStatusText in specifiedStatusSet:
            specifiedStatusPUIDSet.add(puID)

    return specifiedStatusPUIDSet


def calcPortfolioSizeUsingRRRichness(setupObject, puSet, calcIrrepForAllPUs):
    runningPUSet = copy.deepcopy(puSet)
    unmetTargetFeatIDDict = createUnmetTargetFeatIDDict(setupObject, calcIrrepForAllPUs)
    unmetTargetFeatIDSet = set(unmetTargetFeatIDDict.keys())
    if calcIrrepForAllPUs:
        selectedPUIDSet = set()
    else:
        selectedPUIDSet = returnSpecifiedStatusPUIDSet(setupObject, {"Conserved", "Earmarked"})
    runningRichnessScore = -1 #Dummy value to get things started

    progressBar = makeProgressBar('Estimating portfolio size')
    rowTotalCount = len(runningPUSet)

    while (len(unmetTargetFeatIDDict) > 0 and runningRichnessScore > 0) or (len(unmetTargetFeatIDDict) > 0 and runningRichnessScore == -1):
        rowCount = rowTotalCount - len(runningPUSet)
        progressBar.setValue((rowCount/rowTotalCount) * 100)

        scoreDict, highScorePUID = makeRestrictedRangeDict(setupObject, unmetTargetFeatIDSet, runningPUSet)
        runningRichnessScore = scoreDict[highScorePUID]
        runningPUSet.remove(highScorePUID)
        selectedPUIDSet.add(highScorePUID)
        unmetTargetFeatIDDict = updateUnmetTargetFeatIDDict(setupObject, unmetTargetFeatIDDict, highScorePUID)
        unmetTargetFeatIDSet = set(unmetTargetFeatIDDict.keys())
    clearProgressBar()

    if len(unmetTargetFeatIDDict) > 0 and runningRichnessScore == 0:
        warningMessage('Targets cannot be met', 'At least one target cannot be met because the amount of that feature in the Available, Conserved and Earmarked planning units is less than its target. This process will terminate.')
        selectedPUIDSet = set()

    return len(selectedPUIDSet)


def createUnmetTargetFeatIDDict(setupObject, calcIrrepForAllPUs):
    unmetTargetFeatIDDict = dict()
    for featID in setupObject.targetDict:
        if calcIrrepForAllPUs:
            featTargetShortfall = setupObject.targetDict[featID][3]
        else:
            featTargetShortfall = setupObject.targetDict[featID][3] - setupObject.targetDict[featID][4]
        if featTargetShortfall > 0:
            unmetTargetFeatIDDict[featID] = featTargetShortfall

    return unmetTargetFeatIDDict


def updateUnmetTargetFeatIDDict(setupObject, unmetTargetFeatIDDict, highScorePUID):
    puAbundDict = setupObject.abundPUKeyDict[highScorePUID]
    for featID in puAbundDict:
        try:
            origShortfall = unmetTargetFeatIDDict[featID]
            newShortfall = origShortfall - puAbundDict[featID]
            if newShortfall <= 0:
                unmetTargetFeatIDDict.pop(featID)
            else:
                unmetTargetFeatIDDict[featID] = newShortfall
        except KeyError:
            pass

    return unmetTargetFeatIDDict


def makeIrrepInitVarDict(portfolioSize, totNumSites):
    initVarDict = dict()
    mult = calcMultiplier(totNumSites)
    wt_include = float(portfolioSize) / float(totNumSites)
    wt_exclude = 1 - wt_include
    initVarDict["portfolioSize"] = portfolioSize
    initVarDict["totNumSites"] = totNumSites
    initVarDict["mult"] = mult
    initVarDict["wt_include"] = wt_include
    initVarDict["wt_exclude"] = wt_exclude

    return initVarDict


def calcMultiplier(totNumSites):
    denom = totNumSites - 1
    mult = totNumSites / denom

    return mult


def makeIrrepDict(setupObject, initVarDict, puSet, calcIrrepForAllPUs):
    irrepDict = dict()
    sumFeatAmountDict, sumSqrFeatAmount2Dict = makeSumFeatureAmountDicts(setupObject, puSet)
    targetShortfallDict = createTargetShortfallDict(setupObject, calcIrrepForAllPUs)
    progressBar = makeProgressBar('Calculating irreplaceability values')
    rowTotalCount = len(puSet)
    rowCount = 1

    for puID in puSet:
        progressBar.setValue((rowCount/rowTotalCount) * 100)
        rowCount += 1

        puIDIrrepDict = dict()
        try:
            puAbundDict = setupObject.abundPUKeyDict[puID]
        except KeyError:
            puAbundDict = dict()
        for featID in puAbundDict:
            if featID in setupObject.targetDict:
                puFeatIrrepVal= calcFeatUnitIrreplValue(setupObject, initVarDict, puID, featID, sumFeatAmountDict, sumSqrFeatAmount2Dict, targetShortfallDict)
                puIDIrrepDict[featID] = puFeatIrrepVal
        irrepDict[puID] = puIDIrrepDict
    clearProgressBar()

    return irrepDict


def makeSumFeatureAmountDicts(setupObject, puSet):
    sumFeatAmountDict = dict()
    sumSqrFeatAmount2Dict = dict()

    for puID in puSet:
        try:
            puAbundDict = setupObject.abundPUKeyDict[puID]
        except KeyError:
            puAbundDict = dict()
        for featID in puAbundDict:
            featAmount = puAbundDict[featID]
            try:
                sumFeatAmount = sumFeatAmountDict[featID]
                sumSqrFeatAmount = sumSqrFeatAmount2Dict[featID]
            except KeyError:
                sumFeatAmount = 0
                sumSqrFeatAmount = 0
            sumFeatAmount += featAmount
            sumSqrFeatAmount += featAmount ** 2
            sumFeatAmountDict[featID] = sumFeatAmount
            sumSqrFeatAmount2Dict[featID] = sumSqrFeatAmount

    return sumFeatAmountDict, sumSqrFeatAmount2Dict


def createTargetShortfallDict(setupObject, calcIrrepForAllPUs):
    targetShortfallDict = dict()
    for featID in setupObject.targetDict:
        featName = setupObject.targetDict[featID][0]
        featType = setupObject.targetDict[featID][1]
        featSpf = setupObject.targetDict[featID][2]

        if calcIrrepForAllPUs:
            featTargetShortfall = setupObject.targetDict[featID][3]
        else:
            featTargetShortfall = setupObject.targetDict[featID][3] - setupObject.targetDict[featID][4]

        targetShortfallDict[featID] = [featName, featType, featSpf, featTargetShortfall] # First three values are padding to produce same column numbers as targetDict

    return targetShortfallDict


def calcFeatUnitIrreplValue(setupObject, initVarDict, puID, featID, sumFeatAmountDict, sumSqrFeatAmount2Dict, targetShortfallDict):
    totNumSites = initVarDict["totNumSites"]
    mult = initVarDict["mult"]
    featTarget = targetShortfallDict[featID][3]
    featAmount = setupObject.abundPUKeyDict[puID][featID]
    featAmountSqr = featAmount ** 2
    featSumAmount = (sumFeatAmountDict[featID] - featAmount) * mult
    featSumAmountSqr = (sumSqrFeatAmount2Dict[featID] - featAmountSqr) * mult
    meanFeatAmountPerPU = featSumAmount / totNumSites
    sd = calcStandardDev(featSumAmount, featSumAmountSqr, totNumSites)

    rxRemoved = calcRxRemoved(initVarDict, sd, featAmount, featTarget, meanFeatAmountPerPU, featSumAmount)
    rxIncluded = calcRxIncluded(initVarDict, sd, featAmount, featTarget, meanFeatAmountPerPU)
    rxExcluded = calcRxExcluded(initVarDict, sd, featAmount, featTarget, featSumAmount, meanFeatAmountPerPU)

    if (rxIncluded + rxExcluded) == 0:
        irrepValue = 0
    else:
        irrepValue = calcIrrFeature(initVarDict, rxRemoved, rxIncluded, rxExcluded, featAmount)

    return irrepValue


def calcStandardDev(featSumAmount, featSumAmountSqr, totNumSites):
    step1 = featSumAmountSqr - ((featSumAmount ** 2) / totNumSites) / totNumSites
    sd = math.sqrt(step1)

    return sd


def calcAdjustedPortfolioSize(totNumSites, portfolioSize):
    if portfolioSize > totNumSites / 2.0:
        adjustedPortfolioSize = math.sqrt(totNumSites - portfolioSize) / portfolioSize
    else:
        adjustedPortfolioSize = math.sqrt(portfolioSize) / portfolioSize

    return adjustedPortfolioSize


def calcRxRemoved(initVarDict, sd, featAmount, featTarget, meanFeatAmountPerPU, featSumAmount):
    totNumSites = initVarDict["totNumSites"]
    portfolioSize = initVarDict["portfolioSize"]
    meanTargetPerPortfolioSize = featTarget / (portfolioSize - 1)
    adjustedPortfolioSize = calcAdjustedPortfolioSize(totNumSites - 1, portfolioSize - 1)
    adjSD = sd * adjustedPortfolioSize
    if (featSumAmount - featAmount) < featTarget:
        rxRemoved = 0
    else:
        if adjSD < 0.00000000001:
            if meanFeatAmountPerPU < meanTargetPerPortfolioSize:
                rxRemoved = 0
            else:
                 rxRemoved = 1
        else:
            z = (meanTargetPerPortfolioSize - meanFeatAmountPerPU) / adjSD
            rxRemoved = calcZprob(z)

    return rxRemoved


def calcRxIncluded(initVarDict, sd, featAmount, featTarget, meanFeatAmountPerPU):
    totNumSites = initVarDict["totNumSites"]
    portfolioSize = initVarDict["portfolioSize"]
    meanTargetPerPortfolioSize = (featTarget - featAmount) / (portfolioSize - 1)
    adjustedPortfolioSize = calcAdjustedPortfolioSize(totNumSites - 1, portfolioSize - 1)
    adjSD = sd * adjustedPortfolioSize
    if featAmount >= featTarget:
        rxIncluded = 1
    else:
        if adjSD < 0.00000000001:
            if meanFeatAmountPerPU < meanTargetPerPortfolioSize:
                rxIncluded = 0
            else:
                rxIncluded = 1
        else:
             z = (meanTargetPerPortfolioSize - meanFeatAmountPerPU) / adjSD
             rxIncluded = calcZprob(z)

    return rxIncluded


def calcRxExcluded(initVarDict, sd, featAmount, featTarget, featSumAmount, meanFeatAmountPerPU):
    totNumSites = initVarDict["totNumSites"]
    portfolioSize = initVarDict["portfolioSize"]
    meanTargetPerPortfolioSize = featTarget / portfolioSize
    adjustedPortfolioSize = calcAdjustedPortfolioSize(totNumSites - 1, portfolioSize)
    adjSD = sd * adjustedPortfolioSize
    if (featSumAmount - featAmount) < featTarget:
        rxExcluded = 0
    else:
        if adjSD < 0.00000000001:
            if meanFeatAmountPerPU < meanTargetPerPortfolioSize:
                rxExcluded = 0
            else:
                rxExcluded = 1
        else:
            z = (meanTargetPerPortfolioSize - meanFeatAmountPerPU) / adjSD
            rxExcluded = calcZprob(z)

    return rxExcluded


def calcIrrFeature(initVarDict, rxRemoved, rxIncluded, rxExcluded, featAmount):
    wt_include = initVarDict["wt_include"]
    wt_exclude = initVarDict["wt_exclude"]

    if rxIncluded == 0 and featAmount > 0:
        rxIncluded = 1
    if rxIncluded + rxExcluded == 0:
        irr_feature = 0
    else:
        irr_feature = ((rxIncluded - rxRemoved) * wt_include) / (rxIncluded * wt_include + rxExcluded * wt_exclude)

    return irr_feature


# {----------------------------------------------------------------------------}
def calcZprob(x):
    if x < 0:
        negative = True
        x = 0 - x
    else:
        negative = False
    if x > 50:
        x = 50
    z = 0.3989 * math.exp((0 - math.sqrt(x)) / 2)
    t = 1 / (1 + 0.23164 * x)
    m = t
    q = 0.31938 * m
    m *= t
    q = q - 0.35656 * m
    m *= t
    q = q + 1.78148 * m
    m = m * t
    q = q -1.82126 * m
    m *= t
    q = q + 1.33027 * m
    if negative:
        zprob = 1 - q * z
    else:
        zprob = q * z

    return zprob