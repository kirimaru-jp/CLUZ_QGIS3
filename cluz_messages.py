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

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtCore import Qt

from qgis.core import Qgis
from qgis.utils import iface


######################WHAT ABOUT CRITICAL?


def infoMessage(titleText, mainText):
    iface.messageBar().pushMessage(titleText, mainText, level=Qgis.Info)


def warningMessage(titleText, mainText):
    iface.messageBar().pushMessage(titleText, mainText, level=Qgis.Warning, duration=0)


def criticalMessage(titleText, mainText):
    iface.messageBar().pushMessage(titleText, mainText, level=Qgis.Critical, duration=0)


def successMessage(titleText, mainText):
    iface.messageBar().pushMessage(titleText, mainText, level=Qgis.Success)


def makeProgressBar(progressText):
    iface.messageBar().clearWidgets()
    progressMessageBar = iface.messageBar()
    progressBar = QProgressBar()
    progressBar.setMaximum(100)
    progressBar.setTextVisible(True)
    progressBar.setFormat(progressText)
    progressBar.setAlignment(Qt.AlignCenter)
    progressMessageBar.pushWidget(progressBar)

    return progressBar


def clearProgressBar():
    iface.messageBar().clearWidgets()


def emptyPolgyonPUIDSetErrorMessage(emptyPolgyonPUIDSet):
    emptyPolgyonPUIDList = list(emptyPolgyonPUIDSet)
    emptyPolgyonPUIDList.sort()
    puIDString = ''
    for puID in emptyPolgyonPUIDList:
        puIDString += str(puID) + ', '
    finalPUIDString = puIDString[0:-2]
    warningMessage("Shapefile error", "Planning units with the following ID values have problems with their topology and could not be processed by QGIS: " + finalPUIDString)


def checkChangeEarmarkedToAvailablePU():
    warningTitleText = 'Confirm changes to planning unit status'
    warningMainText = 'This will change the status of the Earmaked planning units to Available. Do you want to continue?'
    warningBool = runYesCancelWarningDialogBox(warningTitleText, warningMainText)
    return warningBool


def runYesCancelWarningDialogBox(titleText, mainText):
    answer = QMessageBox.warning(None, titleText, mainText, QMessageBox.Yes | QMessageBox.Cancel)
    if answer == QMessageBox.Yes:
        warningBool = True
    else:
        warningBool = False

    return warningBool





