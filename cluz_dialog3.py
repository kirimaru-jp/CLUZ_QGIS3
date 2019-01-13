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

from qgis.PyQt.QtWidgets import QDialog, QFileDialog

from cluz_form_remove import Ui_removeDialog

from .cluz_dialog3_code import removeSelectedFeaturesFromTarget_AbundFiles, updateConTotFieldsTargetDict, returnConTotDict, createFeatureList_Dict
from .cluz_make_file_dicts import updateTargetCSVFromTargetDict, makeAbundancePUKeyDict
from .cluz_messages import successMessage


def recalcUpdateTargetTableDetails(setupObject):
    setupObject.abundPUKeyDict = makeAbundancePUKeyDict(setupObject)
    newConTotDict = returnConTotDict(setupObject)
    targetDict = updateConTotFieldsTargetDict(setupObject, newConTotDict)
    setupObject.targetDict = targetDict
    updateTargetCSVFromTargetDict(setupObject, targetDict)
    successMessage('Target table updated: ', 'process completed.')


class removeDialog(QDialog, Ui_removeDialog):
    def __init__(self, iface, setupObject):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        featStringList, featStringDict = createFeatureList_Dict(setupObject)
        self.featListWidget.addItems(featStringList)

        self.okButton.clicked.connect(lambda: self.removeSelectedFeatures(setupObject, featStringDict))


    def removeSelectedFeatures(self, setupObject, featStringDict):
        removeSelectedFeaturesFromTarget_AbundFiles(self, setupObject, featStringDict)
