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


from qgis.PyQt.QtCore import QSettings, QCoreApplication, QTranslator, qVersion
from qgis.PyQt.QtWidgets import QMenu, QAction
from qgis.PyQt.QtGui import QIcon

import os

# # Import the code for the Setup Object
from .cluz_setup import CluzSetupObject

from .cluz_dialog1 import startDialog, setupDialog
from .cluz_dialog2 import createDialog, convertVecDialog, convertCsvDialog
from .cluz_dialog3 import removeDialog
from .cluz_dialog4 import distributionDialog, identifySelectedDialog, richnessDialog, irrepDialog, portfolioDialog
from .cluz_dialog5 import inputsDialog, marxanDialog, loadDialog, calibrateDialog
from .cluz_dialog6 import minpatchDialog
from .cluz_dialog7 import targetDialog, abundSelectDialog, metDialog, changeStatusDialog, IdentifyTool
from .cluz_dialog8 import aboutDialog

# Initialize Qt resources from file resources.py
import resources_rc

from .cluz_functions3 import troubleShootCLUZFiles
from .cluz_make_file_dicts import checkCreateSporderDat, makeAbundancePUKeyDict
from .cluz_dialog5 import checkCluzIsNotRunningOnMac, checkMarxanPath
from .cluz_functions7 import changeBestToEarmarkedPUs, changeEarmarkedToAvailablePUs
from .cluz_setup import checkAllRelevantFiles
from .cluz_dialog3 import recalcUpdateTargetTableDetails



class Cluz:
    def __init__(self, iface):
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'cluz_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


    def initGui(self):
        self.cluz_menu = QMenu(self.iface.mainWindow())
        self.cluz_menu.setTitle("CLUZ")
        cluzMenuBar = self.iface.mainWindow().menuBar()
        cluzMenuBar.insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.cluz_menu)
#
        # Create the Setup Object
        setupObject = CluzSetupObject()

        self.cluz_toolbar = self.iface.addToolBar("CLUZ")

        # Create action that will start plugin configuration
        self.SetupAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_menu_setup.png"), "View and edit CLUZ setup file", self.iface.mainWindow())

        self.CreateAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_menu_create.png"), "Create initial CLUZ files", self.iface.mainWindow())
        self.ConvertVecAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_menu_convpoly.png"), "Convert polyline or polygon themes to Marxan abundance data", self.iface.mainWindow())
        self.ConvertCsvAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_menu_convcsv.png"), "Import fields from table to Marxan abundance file", self.iface.mainWindow())

        self.RemoveAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_menu_rem.png"), "Remove features from CLUZ tables", self.iface.mainWindow())
        self.RecalcAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_menu_recalc.png"), "Recalculate target table data", self.iface.mainWindow())
        self.TroubleAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_menu_trouble.png"), "Troubleshoot all CLUZ files", self.iface.mainWindow())

        self.DistributionAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_menu_dist.png"), "Display distributions of conservation features", self.iface.mainWindow())
        self.IdentifySelectedAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_menu_selident.png"), "Identify features in selected units", self.iface.mainWindow())
        self.RichnessAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_menu_richness.png"), "Calculate richness scores", self.iface.mainWindow())
        self.IrrepAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_menu_irrep.png"), "Calculate irreplaceability values", self.iface.mainWindow())
        self.PortfolioAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_menu_portfolio.png"), "Calculate portfolio characteristics", self.iface.mainWindow())

        self.InputsAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_menu_marxcreate.png"), "Create Marxan input files", self.iface.mainWindow())
        self.MarxanAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_menu_marxan.png"), "Launch Marxan", self.iface.mainWindow())
        self.LoadAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_menu_load.png"), "Load previous Marxan outputs", self.iface.mainWindow())
        self.CalibrateAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_menu_calibrate.png"), "Calibrate Marxan parameters", self.iface.mainWindow())

        self.MinPatchAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_menu_minpatch.png"), "Launch MinPatch", self.iface.mainWindow())
#         # self.PatchesAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_menu_portfolio.png"), "Show patches from Marxan or MinPatch output file", self.iface.mainWindow())

        self.AboutAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_menu_about.png"), "About CLUZ", self.iface.mainWindow())

        self.TargetAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_target.png"), "Open target table", self.iface.mainWindow())
        self.AbundAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_abund.png"), "Open abundance table", self.iface.mainWindow())
        self.EarmarkedToAvailableAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_ear_avail.png"), "Change the status of the Earmarked units to Available", self.iface.mainWindow())
        self.BestToEarmarkedAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_best_ear.png"), "Change the status of the Best units to Earmarked", self.iface.mainWindow())
        self.TargetsMetAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_target_met.png"), "Open Marxan results table", self.iface.mainWindow())
        self.TargetsMetAction.setEnabled(False)
        self.ChangeAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_change.png"), "Change planning unit status", self.iface.mainWindow())
        self.IdentifyAction = QAction(QIcon(os.path.dirname(__file__) + "/icons/cluz_identify.png"), "Identify features in planning unit", self.iface.mainWindow())

        # connect the action to the run method
        self.SetupAction.triggered.connect(lambda: self.runSetupDialog(setupObject))
        self.CreateAction.triggered.connect(self.runCreateDialog)
        self.ConvertVecAction.triggered.connect(lambda: self.convertPolylinePolygonToAbundanceData(setupObject))
        self.ConvertCsvAction.triggered.connect(lambda: self.convertCsvToAbundanceData(setupObject))

        self.RemoveAction.triggered.connect(lambda: self.runRemoveFeatures(setupObject))
        self.RecalcAction.triggered.connect(lambda: self.recalcTargetTable(setupObject))
        self.TroubleAction.triggered.connect(lambda: self.runTroubleShoot(setupObject))

        self.DistributionAction.triggered.connect(lambda: self.runShowDistributionFeatures(setupObject))
        self.IdentifySelectedAction.triggered.connect(lambda: self.runIdentifyFeaturesInSelected(setupObject))
        self.RichnessAction.triggered.connect(lambda: self.calcRichness(setupObject))
        self.IrrepAction.triggered.connect(lambda: self.calcIrrepValues(setupObject))
        self.PortfolioAction.triggered.connect(lambda: self.calcPortfolioDetails(setupObject))

        self.InputsAction.triggered.connect(lambda: self.runCreateMarxanInputFiles(setupObject))
        self.MarxanAction.triggered.connect(lambda: self.runMarxan(setupObject, self.TargetsMetAction))
        self.LoadAction.triggered.connect(lambda: self.loadPrevMarxanResults(setupObject))
        self.CalibrateAction.triggered.connect(lambda: self.runCalibrate(setupObject))

        self.MinPatchAction.triggered.connect(lambda: self.runMinPatch(setupObject))
#         # self.PatchesAction.triggered.connect(lambda: self.runShowPatches(setupObject))

        self.AboutAction.triggered.connect(lambda: self.runShowAboutDialog(setupObject))

        self.TargetAction.triggered.connect(lambda: self.runTargetDialog(setupObject))
        self.AbundAction.triggered.connect(lambda: self.runAbundSelectDialog(setupObject))
        self.EarmarkedToAvailableAction.triggered.connect(lambda: self.changeEarmarkedToAvailable(setupObject))

        self.BestToEarmarkedAction.triggered.connect(lambda: self.changeBestToEarmarked(setupObject))
        self.TargetsMetAction.triggered.connect(lambda: self.targetsMetDialog(setupObject))
        self.ChangeAction.triggered.connect(lambda: self.runChangeStatusDialog(setupObject))
        self.IdentifyAction.triggered.connect(lambda: self.showFeaturesInPU(setupObject))

        # Add actions to CLUZ menu
        self.cluz_menu.addAction(self.SetupAction)
        self.cluz_menu.addSeparator()
        self.cluz_menu.addAction(self.CreateAction)
        self.cluz_menu.addAction(self.ConvertVecAction)
        self.cluz_menu.addAction(self.ConvertCsvAction)
        self.cluz_menu.addSeparator()
        self.cluz_menu.addAction(self.RemoveAction)
        self.cluz_menu.addAction(self.RecalcAction)
        self.cluz_menu.addAction(self.TroubleAction)
        self.cluz_menu.addSeparator()
        self.cluz_menu.addAction(self.DistributionAction)
        self.cluz_menu.addAction(self.IdentifySelectedAction)
        self.cluz_menu.addAction(self.RichnessAction)
        # self.cluz_menu.addAction(self.IrrepAction)
        self.cluz_menu.addAction(self.PortfolioAction)
        self.cluz_menu.addSeparator()
        self.cluz_menu.addAction(self.InputsAction)
        self.cluz_menu.addAction(self.MarxanAction)
        self.cluz_menu.addAction(self.LoadAction)
        self.cluz_menu.addAction(self.CalibrateAction)
        self.cluz_menu.addSeparator()
        self.cluz_menu.addAction(self.MinPatchAction)
#         # self.cluz_menu.addAction(self.PatchesAction)
        self.cluz_menu.addSeparator()
        self.cluz_menu.addAction(self.AboutAction)

        # Add actions as buttons on menu bar
        self.cluz_toolbar.addAction(self.TargetAction)
        self.cluz_toolbar.addAction(self.AbundAction)
        self.cluz_toolbar.addAction(self.EarmarkedToAvailableAction)
        self.cluz_toolbar.addAction(self.TargetsMetAction)
        self.cluz_toolbar.addAction(self.BestToEarmarkedAction)
        self.cluz_toolbar.addSeparator()
        self.cluz_toolbar.addAction(self.ChangeAction)
        self.cluz_toolbar.addAction(self.IdentifyAction)
        self.cluz_toolbar.addSeparator()
#
    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&CLUZ", self.SetupAction)
        del self.cluz_toolbar


    def runStartDialog(self, setupObject):
        self.startDialog = startDialog(self, setupObject)
        self.startDialog.show()
        self.startDialog.exec_()


    def runSetupDialog(self, setupObject):
        self.setupDialog = setupDialog(self, setupObject)
        self.setupDialog.show()
        self.setupDialog.exec_()


    def runCreateDialog(self):
        self.createDialog = createDialog(self)
        self.createDialog.show()
        self.createDialog.exec_()


    def convertPolylinePolygonToAbundanceData(self, setupObject):
        checkAllRelevantFiles(self, setupObject, startDialog, setupDialog)
        if setupObject.setupStatus == 'files_checked':
            if setupObject.abundPUKeyDict == 'blank':
                setupObject.abundPUKeyDict = makeAbundancePUKeyDict(setupObject)
            self.convertVecDialog = convertVecDialog(self, setupObject)
            self.convertVecDialog.show()
            self.convertVecDialog.exec_()


    def convertCsvToAbundanceData(self, setupObject):
        checkAllRelevantFiles(self, setupObject, startDialog, setupDialog)
        if setupObject.setupStatus == 'files_checked':
            if setupObject.abundPUKeyDict == 'blank':
                setupObject.abundPUKeyDict = makeAbundancePUKeyDict(setupObject)
            self.convertCsvDialog = convertCsvDialog(self, setupObject)
            self.convertCsvDialog.show()
            self.convertCsvDialog.exec_()


    def runRemoveFeatures(self, setupObject):
        checkAllRelevantFiles(self, setupObject, startDialog, setupDialog)
        if setupObject.setupStatus == 'files_checked':
            if setupObject.abundPUKeyDict == 'blank':
                setupObject.abundPUKeyDict = makeAbundancePUKeyDict(setupObject)
            self.removeDialog = removeDialog(self, setupObject)
            self.removeDialog.show()
            self.removeDialog.exec_()


    def recalcTargetTable(self, setupObject):
        checkAllRelevantFiles(self, setupObject, startDialog, setupDialog)
        if setupObject.setupStatus == 'files_checked':
            recalcUpdateTargetTableDetails(setupObject)


    def runTroubleShoot(self, setupObject):
        checkAllRelevantFiles(self, setupObject, startDialog, setupDialog)
        if setupObject.setupStatus == 'files_checked':
            if setupObject.abundPUKeyDict == 'blank':
                setupObject.abundPUKeyDict = makeAbundancePUKeyDict(setupObject)
            troubleShootCLUZFiles(setupObject)


    def runShowDistributionFeatures(self, setupObject):
        checkAllRelevantFiles(self, setupObject, startDialog, setupDialog)
        if setupObject.setupStatus == 'files_checked':
            if setupObject.abundPUKeyDict == 'blank':
                setupObject.abundPUKeyDict = makeAbundancePUKeyDict(setupObject)
            self.distributionDialog = distributionDialog(self, setupObject)
            self.distributionDialog.show()
            self.distributionDialog.exec_()


    def runIdentifyFeaturesInSelected(self, setupObject):
        checkAllRelevantFiles(self, setupObject, startDialog, setupDialog)
        if setupObject.setupStatus == 'files_checked':
            if setupObject.abundPUKeyDict == 'blank':
                setupObject.abundPUKeyDict = makeAbundancePUKeyDict(setupObject)
            self.Ui_identifySelectedDialog = identifySelectedDialog(self, setupObject)
            self.Ui_identifySelectedDialog.show()
            self.Ui_identifySelectedDialog.exec_()


    def calcRichness(self, setupObject):
        checkAllRelevantFiles(self, setupObject, startDialog, setupDialog)
        if setupObject.setupStatus == 'files_checked':
            if setupObject.abundPUKeyDict == 'blank':
                setupObject.abundPUKeyDict = makeAbundancePUKeyDict(setupObject)
            self.richnessDialog = richnessDialog(self, setupObject)
            self.richnessDialog.show()
            self.richnessDialog.exec_()


    def calcIrrepValues(self, setupObject):
        checkAllRelevantFiles(self, setupObject, startDialog, setupDialog)
        if setupObject.setupStatus == 'files_checked':
            if setupObject.abundPUKeyDict == 'blank':
                setupObject.abundPUKeyDict = makeAbundancePUKeyDict(setupObject)
            self.irrepDialog = irrepDialog(self, setupObject)
            self.irrepDialog.show()
            self.irrepDialog.exec_()


    def calcPortfolioDetails(self, setupObject):
        checkAllRelevantFiles(self, setupObject, startDialog, setupDialog)
        if setupObject.setupStatus == 'files_checked':
            self.portfolioDialog = portfolioDialog(self, setupObject)
            self.portfolioDialog.show()
            self.portfolioDialog.exec_()


    def runCreateMarxanInputFiles(self, setupObject):
        checkAllRelevantFiles(self, setupObject, startDialog, setupDialog)
        if setupObject.setupStatus == "files_checked":
            self.inputsDialog = inputsDialog(self, setupObject)
            self.inputsDialog.show()
            self.inputsDialog.exec_()


    def runMarxan(self, setupObject, targetsMetAction):
        checkAllRelevantFiles(self, setupObject, startDialog, setupDialog)
        if setupObject.setupStatus == "files_checked":
            checkCreateSporderDat(setupObject)
            marxanBool = checkCluzIsNotRunningOnMac()
            if marxanBool:
                marxanBool = checkMarxanPath(setupObject, marxanBool)
                if marxanBool:
                    self.marxanDialog = marxanDialog(self, setupObject, targetsMetAction)
                    self.marxanDialog.show()
                    self.marxanDialog.exec_()
                else:
                    self.setupDialog = setupDialog(self, setupObject)
                    self.setupDialog.show()
                    self.setupDialog.exec_()


    def loadPrevMarxanResults(self, setupObject):
        checkAllRelevantFiles(self, setupObject, startDialog, setupDialog)
        if setupObject.setupStatus == 'files_checked':
            self.loadDialog = loadDialog(self, setupObject)
            self.loadDialog.show()
            self.loadDialog.exec_()


    def runCalibrate(self, setupObject):
        checkAllRelevantFiles(self, setupObject, startDialog, setupDialog)
        if setupObject.setupStatus == 'files_checked':
            checkCreateSporderDat(setupObject)
            marxanBool = checkCluzIsNotRunningOnMac()
            if marxanBool:
                self.calibrateDialog = calibrateDialog(self, setupObject)
                self.calibrateDialog.show()
                self.calibrateDialog.exec_()
            else:
                self.setupDialog = setupDialog(self, setupObject)
                self.setupDialog.show()
                self.setupDialog.exec_()


    def runMinPatch(self, setupObject):
        checkAllRelevantFiles(self, setupObject, startDialog, setupDialog)
        if setupObject.setupStatus == "files_checked":
            self.minpatchDialog = minpatchDialog(self, setupObject)
            self.minpatchDialog.show()
            self.minpatchDialog.exec_()
#
#
#     def runShowPatches(self, setupObject):
#         checkSetupFileLoaded(self, setupObject)
#         openSetupDialogIfSetupFilesIncorrect(self, setupObject)
#         checkCreateAddFiles(setupObject)
#
#         if setupObject.setupStatus == "files_checked":
#             self.patchesDialog = patchesDialog(self, setupObject)
#             # show the dialog
#             self.patchesDialog.show()
#             # Run the dialog event loop
#             result = self.patchesDialog.exec_()
#

    def runShowAboutDialog(self, setupObject):
        self.aboutDialog = aboutDialog(self, setupObject)
        self.aboutDialog.show()
        self.aboutDialog.exec_()


    def runTargetDialog(self, setupObject):
        checkAllRelevantFiles(self, setupObject, startDialog, setupDialog)
        if setupObject.setupStatus == 'files_checked':
            self.targetDialog = targetDialog(self, setupObject)
            self.targetDialog.show()
            self.targetDialog.exec_()


    def runAbundSelectDialog(self,setupObject):
        checkAllRelevantFiles(self, setupObject, startDialog, setupDialog)
        if setupObject.setupStatus == 'files_checked':
            if setupObject.abundPUKeyDict == 'blank':
                setupObject.abundPUKeyDict = makeAbundancePUKeyDict(setupObject)
            self.abundSelectDialog = abundSelectDialog(self, setupObject)
            self.abundSelectDialog.show()
            self.abundSelectDialog.exec_()


    def changeEarmarkedToAvailable(self, setupObject):
        checkAllRelevantFiles(self, setupObject, startDialog, setupDialog)
        if setupObject.setupStatus == 'files_checked':
            if setupObject.abundPUKeyDict == 'blank':
                setupObject.abundPUKeyDict = makeAbundancePUKeyDict(setupObject)
            changeEarmarkedToAvailablePUs(setupObject)


    def targetsMetDialog(self, setupObject):
        checkAllRelevantFiles(self, setupObject, startDialog, setupDialog)
        self.metDialog = metDialog(self, setupObject)
        self.metDialog.show()
        self.metDialog.exec_()


    def changeBestToEarmarked(self, setupObject):
        checkAllRelevantFiles(self, setupObject, startDialog, setupDialog)
        if setupObject.setupStatus == 'files_checked':
            if setupObject.abundPUKeyDict == 'blank':
                setupObject.abundPUKeyDict = makeAbundancePUKeyDict(setupObject)
            changeBestToEarmarkedPUs(setupObject)


    def runChangeStatusDialog(self, setupObject):
        checkAllRelevantFiles(self, setupObject, startDialog, setupDialog)
        if setupObject.setupStatus == 'files_checked':
            if setupObject.abundPUKeyDict == 'blank':
                setupObject.abundPUKeyDict = makeAbundancePUKeyDict(setupObject)
            self.changeStatusDialog = changeStatusDialog(self, setupObject)
            self.changeStatusDialog.show()
            self.changeStatusDialog.exec_()


    def showFeaturesInPU(self, setupObject):
        checkAllRelevantFiles(self, setupObject, startDialog, setupDialog)
        if setupObject.setupStatus == 'files_checked':
            if setupObject.abundPUKeyDict == 'blank':
                setupObject.abundPUKeyDict = makeAbundancePUKeyDict(setupObject)
            identifyTool = IdentifyTool(self.iface.mapCanvas(), setupObject)
            self.iface.mapCanvas().setMapTool(identifyTool)
