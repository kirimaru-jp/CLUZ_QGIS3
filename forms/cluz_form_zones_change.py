# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\rjsmi\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\cluz\forms\cluz_form_zones_change.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ZonesChangeStatusDialog(object):
    def setupUi(self, ZonesChangeStatusDialog):
        ZonesChangeStatusDialog.setObjectName("ZonesChangeStatusDialog")
        ZonesChangeStatusDialog.resize(468, 509)
        ZonesChangeStatusDialog.setMinimumSize(QtCore.QSize(390, 430))
        self.logoLabel = QtWidgets.QLabel(ZonesChangeStatusDialog)
        self.logoLabel.setGeometry(QtCore.QRect(10, 20, 51, 51))
        self.logoLabel.setText("")
        self.logoLabel.setPixmap(QtGui.QPixmap("images/marxan_logo_small.png"))
        self.logoLabel.setObjectName("logoLabel")
        self.horizontalLayoutWidget = QtWidgets.QWidget(ZonesChangeStatusDialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(80, 450, 281, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.changeButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.changeButton.setObjectName("changeButton")
        self.horizontalLayout.addWidget(self.changeButton)
        self.undoButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.undoButton.setObjectName("undoButton")
        self.horizontalLayout.addWidget(self.undoButton)
        self.closeButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.closeButton.setObjectName("closeButton")
        self.horizontalLayout.addWidget(self.closeButton)
        self.statusGroupBox = QtWidgets.QGroupBox(ZonesChangeStatusDialog)
        self.statusGroupBox.setGeometry(QtCore.QRect(80, 20, 351, 341))
        self.statusGroupBox.setTitle("")
        self.statusGroupBox.setObjectName("statusGroupBox")
        self.verticalLayoutWidget = QtWidgets.QWidget(ZonesChangeStatusDialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(90, 80, 331, 271))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.zonesAvailableButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.zonesAvailableButton.setChecked(True)
        self.zonesAvailableButton.setObjectName("zonesAvailableButton")
        self.verticalLayout.addWidget(self.zonesAvailableButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.zonesEarmarkedButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.zonesEarmarkedButton.setObjectName("zonesEarmarkedButton")
        self.verticalLayout.addWidget(self.zonesEarmarkedButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem1)
        self.zonesChangeCheckBox = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.zonesChangeCheckBox.setObjectName("zonesChangeCheckBox")
        self.verticalLayout.addWidget(self.zonesChangeCheckBox)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem2)
        self.zonesLockedButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.zonesLockedButton.setEnabled(False)
        self.zonesLockedButton.setObjectName("zonesLockedButton")
        self.verticalLayout.addWidget(self.zonesLockedButton)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem3)
        self.zonesExcludedButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.zonesExcludedButton.setEnabled(False)
        self.zonesExcludedButton.setObjectName("zonesExcludedButton")
        self.verticalLayout.addWidget(self.zonesExcludedButton)
        self.zonesZoneTargetsMetLabel = QtWidgets.QLabel(ZonesChangeStatusDialog)
        self.zonesZoneTargetsMetLabel.setGeometry(QtCore.QRect(90, 410, 191, 16))
        self.zonesZoneTargetsMetLabel.setObjectName("zonesZoneTargetsMetLabel")
        self.zonesMainTargetsMetLabel = QtWidgets.QLabel(ZonesChangeStatusDialog)
        self.zonesMainTargetsMetLabel.setGeometry(QtCore.QRect(90, 380, 191, 16))
        self.zonesMainTargetsMetLabel.setObjectName("zonesMainTargetsMetLabel")
        self.zonesNameComboBox = QtWidgets.QComboBox(ZonesChangeStatusDialog)
        self.zonesNameComboBox.setGeometry(QtCore.QRect(150, 40, 271, 22))
        self.zonesNameComboBox.setObjectName("zonesNameComboBox")
        self.zonesNameLabel = QtWidgets.QLabel(ZonesChangeStatusDialog)
        self.zonesNameLabel.setGeometry(QtCore.QRect(90, 40, 71, 16))
        self.zonesNameLabel.setObjectName("zonesNameLabel")

        self.retranslateUi(ZonesChangeStatusDialog)
        self.closeButton.clicked.connect(ZonesChangeStatusDialog.close)
        self.zonesChangeCheckBox.clicked['bool'].connect(self.zonesLockedButton.setEnabled)
        self.zonesChangeCheckBox.clicked['bool'].connect(self.zonesExcludedButton.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(ZonesChangeStatusDialog)

    def retranslateUi(self, ZonesChangeStatusDialog):
        _translate = QtCore.QCoreApplication.translate
        ZonesChangeStatusDialog.setWindowTitle(_translate("ZonesChangeStatusDialog", "Change Status panel"))
        self.changeButton.setText(_translate("ZonesChangeStatusDialog", "Change"))
        self.undoButton.setText(_translate("ZonesChangeStatusDialog", "Undo"))
        self.closeButton.setText(_translate("ZonesChangeStatusDialog", "Close"))
        self.zonesAvailableButton.setText(_translate("ZonesChangeStatusDialog", "Set as Available"))
        self.zonesEarmarkedButton.setText(_translate("ZonesChangeStatusDialog", "Set as Earmarked"))
        self.zonesChangeCheckBox.setText(_translate("ZonesChangeStatusDialog", "Allow changes\n"
"to Locked and\n"
"Excluded status"))
        self.zonesLockedButton.setText(_translate("ZonesChangeStatusDialog", "Set as Locked In"))
        self.zonesExcludedButton.setText(_translate("ZonesChangeStatusDialog", "Set as Excluded"))
        self.zonesZoneTargetsMetLabel.setText(_translate("ZonesChangeStatusDialog", "Zone targets met: unspecified"))
        self.zonesMainTargetsMetLabel.setText(_translate("ZonesChangeStatusDialog", "Targets met: X of Y"))
        self.zonesNameLabel.setText(_translate("ZonesChangeStatusDialog", "Zone name"))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ZonesChangeStatusDialog = QtWidgets.QDialog()
    ui = Ui_ZonesChangeStatusDialog()
    ui.setupUi(ZonesChangeStatusDialog)
    ZonesChangeStatusDialog.show()
    sys.exit(app.exec_())

