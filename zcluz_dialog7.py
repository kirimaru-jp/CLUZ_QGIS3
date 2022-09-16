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

from PyQt5.QtCore import Qt
from qgis.PyQt.QtWidgets import QApplication, QDialog, QFileDialog, QTableWidgetItem
from qgis.gui import QgsMapTool
from qgis.core import *

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")
from cluz_form_zones import Ui_zonesDialog
from cluz_form_zones_change import Ui_ZonesChangeStatusDialog

from .cluz_display import updatePULayerToShowChangesByShiftingExtent
from .zcluz_functions7 import returnZonesMainTargetsMetTuple, returnZonesTargetsMetTuple, returnSelectedZoneIDFromChangeStatusPanel
from .zcluz_make_file_dicts import makeZonesDict
from .zcluz_dialog7_code import zonesDialogKeyPressEvent, addZonesTableData, makeZonesNameList, zonesChangeStatusOfPULayer_UpdateTargetTable, zonesUndoStatusOfPULayer_UpdateTargetTable

######################## Zones table ##########################

class zonesDialog(QDialog, Ui_zonesDialog):
    def __init__(self, iface, setupObject):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.clip = QApplication.clipboard()
        if setupObject.zonesDict != 'blank':
            self.loadZonestDictData(setupObject)

    def loadZonestDictData(self, setupObject):
        addZonesTableData(self, setupObject)


    def keyPressEvent(self, e):
        zonesDialogKeyPressEvent(self, e)


class zonesChangeStatusDialog(QDialog, Ui_ZonesChangeStatusDialog):
    def __init__(self, iface, setupObject):
        QDialog.__init__(self, None, Qt.WindowStaysOnTopHint)
        self.iface = iface
        self.setupUi(self)

        zonesNameList = makeZonesNameList(setupObject)
        self.zonesNameComboBox.addItems(zonesNameList)
        selectedZoneID = list(setupObject.zonesDict.keys())[0]
        targetsMetCount, targetCount = returnZonesMainTargetsMetTuple(setupObject)
        self.zonesMainTargetsMetLabel.setText("Targets met: " + str(targetsMetCount) + " of " + str(targetCount))
        (zoneTargetsMetCount, zoneTargetCount) = returnZonesTargetsMetTuple(setupObject, selectedZoneID)
        self.zonesZoneTargetsMetLabel.setText('Zone ' + str(selectedZoneID) + ' targets met: ' + str(zoneTargetsMetCount) + ' of ' + str(zoneTargetCount))
        self.undoButton.setEnabled(False)

        self.zonesNameComboBox.activated.connect(lambda: self.updateZoneTargetDetails(setupObject))
        self.changeButton.clicked.connect(lambda: self.changeStatus(setupObject))
        self.undoButton.clicked.connect(lambda: self.undoStatusChange(setupObject))


    def updateZoneTargetDetails(self, setupObject):
        selectedZoneID = returnSelectedZoneIDFromChangeStatusPanel(self)
        (zoneTargetsMetCount, zoneTargetCount) = returnZonesTargetsMetTuple(setupObject, selectedZoneID)
        self.zonesZoneTargetsMetLabel.setText('Zone ' + str(selectedZoneID) + ' targets met: ' + str(zoneTargetsMetCount) + ' of ' + str(zoneTargetCount))


    def changeStatus(self, setupObject):
        zonesChangeStatusOfPULayer_UpdateTargetTable(self, setupObject)


    def undoStatusChange(self, setupObject):
        zonesUndoStatusOfPULayer_UpdateTargetTable(self, setupObject)
        updatePULayerToShowChangesByShiftingExtent()