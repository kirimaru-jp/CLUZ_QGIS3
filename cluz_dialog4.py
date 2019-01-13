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
from qgis.PyQt.QtWidgets import QDialog, QFileDialog, QApplication

from cluz_form_distribution import Ui_distributionDialog
from cluz_form_identify_selected import Ui_identifySelectedDialog
from cluz_form_richness import Ui_richnessDialog
from cluz_form_irrep import Ui_irrepDialog
from cluz_form_portfolio import Ui_portfolioDialog
from cluz_form_portfolio_results import Ui_portfolioResultsDialog

from .cluz_dialog4_code import addDetailsToSfTab, removeSuperfluousTabs, identifySelectedKeyPressEventCode, setInitialDistribtuionShapeFilePath, loadDistributionFeatureList, returnSelectedPUDetailsDict, portfolioSfTabDialogKeyPressEvent, checkIfSfRunsValueIsOK, returnRichnessRestrictedRangeResults, makeSelectedFeatIDSet, create_displayDistributionMaps, addDetailsToSpatialTab, makeSFFieldList, returnSelectedPUIDDict, addSelectedIdentifyDataToTableWidget, returnInitialFieldName, produceTypeTextList, addPatchFeatDetailsToPortfolioDict, portfolioStatusTabDialogKeyPressEvent, addIrrepResults, addFormatting_HeadingsToTableWidget, addSfDetailsToPortfolioDict, returnRichnessCountResults, portfolioSpatialTabDialogKeyPressEvent, checkRichnessTypeCodesSelected_OptionsSelected, portfolioPatchTabDialogKeyPressEvent, makeIrrepDictOutputFile, addDetailsToPatchFeatTab, addDetailsToStatusTab
from .cluz_irrep import calcPortfolioSizeUsingRRRichness, makeIrrepDict, returnSpecifiedStatusPUIDSet, makeIrrepInitVarDict
from .cluz_messages import successMessage
from .cluz_functions4 import addStatusDetailsToPortfolioDict, makePortfolioPUDetailsDict, addSpatialDetailsToPortfolioDict
from .cluz_display import displayIrrepResults, removeThenAddPULayer


class distributionDialog(QDialog, Ui_distributionDialog):
    def __init__(self, iface, setupObject):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        loadDistributionFeatureList(self, setupObject)
        setInitialDistribtuionShapeFilePath(self, setupObject)

        self.filePathButton.clicked.connect(self.setDistShapeFile)
        self.okButton.clicked.connect(lambda: self.runDisplayDistributionMaps(setupObject))


    def setDistShapeFile(self):
        (distShapefilePathNameText, fileTypeDetailsText)  = QFileDialog.getSaveFileName(self, 'Save new shapefile', '*.shp')
        self.filePathlineEdit.setText(distShapefilePathNameText)


    def runDisplayDistributionMaps(self, setupObject):
        create_displayDistributionMaps(self, setupObject)


class identifySelectedDialog(QDialog, Ui_identifySelectedDialog):
    def __init__(self, iface, setupObject):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.clip = QApplication.clipboard()
        selectedPUIDDict = returnSelectedPUIDDict(setupObject)
        selectedPUDetailsDict = returnSelectedPUDetailsDict(setupObject, selectedPUIDDict)
        self.showSelectedIdentifyData(setupObject, selectedPUDetailsDict)


    def showSelectedIdentifyData(self, setupObject, selectedPUDetailsDict):
        if len(selectedPUDetailsDict) > 0:
            self.identifySelectedTableWidget.clear()
            self.identifySelectedTableWidget.setColumnCount(8)
            addSelectedIdentifyDataToTableWidget(self, setupObject, selectedPUDetailsDict)
            addFormatting_HeadingsToTableWidget(self, setupObject)
            self.setWindowTitle('Details of ' + str(len(selectedPUDetailsDict)) + ' planning units.')
        else:
            self.setWindowTitle('No planning units selected')


    def keyPressEvent(self, e):
        identifySelectedKeyPressEventCode(self, e)


class richnessDialog(QDialog, Ui_richnessDialog):
    def __init__(self, iface, setupObject):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        finalCountFieldName = returnInitialFieldName(setupObject, 'F_COUNT')
        finalRangeFieldName = returnInitialFieldName(setupObject, "RES_RANGE")
        self.countLineEdit.setText(finalCountFieldName)
        self.rangeLineEdit.setText(finalRangeFieldName)
        typeList = produceTypeTextList(setupObject)
        self.typeListWidget.addItems(typeList)

        self.okButton.clicked.connect(lambda: self.createRichnessResults(setupObject))


    def createRichnessResults(self, setupObject):
        selectedFeatIDSet = makeSelectedFeatIDSet(self, setupObject)
        puLayer = QgsVectorLayer(setupObject.puPath, 'Planning units', 'ogr')
        fieldNameList = [field.name() for field in puLayer.fields()]

        progressBool = checkRichnessTypeCodesSelected_OptionsSelected(self, selectedFeatIDSet)
        addLayerFudge = 0 #Added because QGIS doesn't recognise new layers that have been added when counting position of puLayer

        if self.countBox.isChecked() and progressBool:
            returnRichnessCountResults(self, setupObject, fieldNameList, selectedFeatIDSet)
            addLayerFudge += 1

        if self.rangeBox.isChecked() and progressBool:
            returnRichnessRestrictedRangeResults(self, setupObject, fieldNameList, selectedFeatIDSet)
            addLayerFudge += 1

        if progressBool:
            successMessage('Richness results', 'The fields have been successfully added to the planning unit layer attribute table.')
            removeThenAddPULayer(setupObject, addLayerFudge)
            self.close()


class irrepDialog(QDialog, Ui_irrepDialog):
    def __init__(self, iface, setupObject):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        finalIrrepFieldName = returnInitialFieldName(setupObject, 'SUM_IRR')
        self.irrepLineEdit.setText(finalIrrepFieldName)
        self.outputLabel.setVisible(False)
        self.outputLineEdit.setVisible(False)
        self.browseButton.setVisible(False)

        self.browseButton.clicked.connect(self.setIrrepOutputFilePath)
        self.okButton.clicked.connect(lambda: self.runReturnIrrepDetails(setupObject))


    def setIrrepOutputFilePath(self):
        (irrepOutputFilePathNameText, fileTypeDetailsText)  = QFileDialog.getSaveFileName(self, 'Save irreplaceability output file', '*.csv')
        self.outputLineEdit.setText(irrepOutputFilePathNameText)


    def runReturnIrrepDetails(self, setupObject):
        if self.allRadioButton.isChecked():
            statusSet = {'Available', 'Conserved', 'Earmarked', 'Excluded'}
            calcIrrepForAllPUs = True #Assumes every PU is Available, giving 'pure' irrep values
        else:
            statusSet = {'Available'}
            calcIrrepForAllPUs = False #Calculates irrep values based on target shortfalls of existing Conserved and Excluded areas

        puSet = returnSpecifiedStatusPUIDSet(setupObject, statusSet)
        portfolioSize = calcPortfolioSizeUsingRRRichness(setupObject, puSet, calcIrrepForAllPUs)
        initVarDict = makeIrrepInitVarDict(portfolioSize, len(puSet))
        irrepDict = makeIrrepDict(setupObject, initVarDict, puSet, calcIrrepForAllPUs)
        addIrrepResults(setupObject, irrepDict, self.irrepLineEdit.text(), statusSet)
        displayIrrepResults(setupObject, self.irrepLineEdit.text())
        if self.outputCheckBox.isChecked():
            makeIrrepDictOutputFile(setupObject, irrepDict, self.outputLineEdit.text(), puSet)

        self.close()


class portfolioDialog(QDialog, Ui_portfolioDialog):
    def __init__(self, iface, setupObject):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        self.sfComboBox.addItems(makeSFFieldList(setupObject))
        self.sfComboBox.setEnabled(False)
        self.sfFieldLabel.setEnabled(False)
        self.sfRunsLabel.setVisible(False)
        self.sfRunsLineEdit.setVisible(False)
        self.equalityCheckBox.setVisible(False)

        self.okButton.clicked.connect(lambda: self.runReturnPortfolioDetails(setupObject))


    def runReturnPortfolioDetails(self, setupObject):
        portfolioPUDetailsDict = makePortfolioPUDetailsDict()
        sfRunsValueIsOKBool = checkIfSfRunsValueIsOK(self)
        if sfRunsValueIsOKBool:
            if self.puDetailsCheckBox.isChecked():
                portfolioPUDetailsDict = addStatusDetailsToPortfolioDict(setupObject, portfolioPUDetailsDict)
            if self.spatialCheckBox.isChecked():
                portfolioPUDetailsDict = addSpatialDetailsToPortfolioDict(setupObject, portfolioPUDetailsDict)
            if self.patchTargetCheckBox.isChecked():
                portfolioPUDetailsDict = addPatchFeatDetailsToPortfolioDict(setupObject, portfolioPUDetailsDict)
            if self.sfCheckBox.isChecked():
                portfolioPUDetailsDict = addSfDetailsToPortfolioDict(self, setupObject, portfolioPUDetailsDict)

        if sfRunsValueIsOKBool:
            self.close()

            if len(portfolioPUDetailsDict) > 0:
                self.portfolioResultsDialog = portfolioResultsDialog(self, portfolioPUDetailsDict, setupObject)
                self.portfolioResultsDialog.show()
                self.portfolioResultsDialog.exec_()


class portfolioResultsDialog(QDialog, Ui_portfolioResultsDialog):
    def __init__(self, iface, portfolioPUDetailsDict, setupObject):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.clip = QApplication.clipboard()
        self.portfolioPUDetailsDict = portfolioPUDetailsDict
        removeSuperfluousTabs(self, portfolioPUDetailsDict)
        if portfolioPUDetailsDict["statusDetailsBool"]:
            statusDataDict = portfolioPUDetailsDict["statusDataDict"]
            self.makeStatusTab(setupObject, statusDataDict)
        if portfolioPUDetailsDict["spatialDetailsBool"]:
            spatialDataDict = portfolioPUDetailsDict["spatialDataDict"]
            self.makeSpatialTab(setupObject, spatialDataDict)
        if portfolioPUDetailsDict["sfDetailsBool"]:
            sfDataDict = portfolioPUDetailsDict["sfDataDict"]
            self.makeSfTab(sfDataDict)
        if portfolioPUDetailsDict["patchFeatDetailsBool"]:
            patchFeatDataDict = portfolioPUDetailsDict["patchFeatDataDict"]
            self.makePatchFeatTab(setupObject, patchFeatDataDict)
        if portfolioPUDetailsDict["peDetailsBool"]:
            peDataDict = portfolioPUDetailsDict["peDataDict"]
            self.makePETab(peDataDict)


    def makeStatusTab(self, setupObject, statusDataDict):
        addDetailsToStatusTab(self, setupObject, statusDataDict)


    def makeSpatialTab(self, setupObject, spatialDataDict):
        addDetailsToSpatialTab(self, setupObject, spatialDataDict)


    def makeSfTab(self, sfDataDict):
        addDetailsToSfTab(self, sfDataDict)


    def makePatchFeatTab(self, setupObject, patchFeatDataDict):
        addDetailsToPatchFeatTab(self, setupObject, patchFeatDataDict)

    def keyPressEvent(self, e):
        widgetTabIndex = self.portfolioTabWidget.currentIndex()
        if widgetTabIndex == 0:
            portfolioStatusTabDialogKeyPressEvent(self, e)
        elif widgetTabIndex == 1:
            portfolioSpatialTabDialogKeyPressEvent(self, e)
        elif widgetTabIndex == 2 and self.portfolioPUDetailsDict["sfDetailsBool"]:
            portfolioSfTabDialogKeyPressEvent(self, e)
        elif widgetTabIndex == 2 and self.portfolioPUDetailsDict["sfDetailsBool"] is False:
            portfolioPatchTabDialogKeyPressEvent(self, e)
        elif widgetTabIndex == 3:
            portfolioPatchTabDialogKeyPressEvent(self, e)

#     def makePETab(self, sfDataDict):
#         self.peTabTableWidget.clear()
#         # self.sfTabTableWidget.setColumnCount(2)
#         # rowNumber = 0
#         # sfDictKeyList = range(0, len(sfDataDict))
#         # for sfDictKey in sfDictKeyList:
#         #     self.sfTabTableWidget.insertRow(rowNumber)
#         #     descTableItem = QTableWidgetItem(sfDataDict[sfDictKey][0])
#         #     valueTableItem = QTableWidgetItem(sfDataDict[sfDictKey][1])
#         #     self.sfTabTableWidget.setItem(rowNumber, 0, descTableItem)
#         #     self.sfTabTableWidget.setItem(rowNumber, 1, valueTableItem)
#         #     rowNumber += 1
#         #
#         # sfHeaderList = ['Selection frequency value range', 'Number of planning units']
#         # self.sfTabTableWidget.setHorizontalHeaderLabels(sfHeaderList)
#         # for aColValue in range(len(sfHeaderList)):
#         #     self.sfTabTableWidget.resizeColumnToContents(aColValue)

