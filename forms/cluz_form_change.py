# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\rjsmi\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\cluz\forms\cluz_form_change.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ChangeStatusDialog(object):
    def setupUi(self, ChangeStatusDialog):
        ChangeStatusDialog.setObjectName("ChangeStatusDialog")
        ChangeStatusDialog.resize(380, 400)
        ChangeStatusDialog.setMinimumSize(QtCore.QSize(380, 400))
        self.logoLabel = QtWidgets.QLabel(ChangeStatusDialog)
        self.logoLabel.setGeometry(QtCore.QRect(10, 20, 51, 51))
        self.logoLabel.setText("")
        self.logoLabel.setPixmap(QtGui.QPixmap(":/images/images/marxan_logo_small.png"))
        self.logoLabel.setObjectName("logoLabel")
        self.horizontalLayoutWidget = QtWidgets.QWidget(ChangeStatusDialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(70, 340, 281, 41))
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
        self.statusGroupBox = QtWidgets.QGroupBox(ChangeStatusDialog)
        self.statusGroupBox.setGeometry(QtCore.QRect(70, 20, 281, 271))
        self.statusGroupBox.setTitle("")
        self.statusGroupBox.setObjectName("statusGroupBox")
        self.verticalLayoutWidget = QtWidgets.QWidget(ChangeStatusDialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(80, 20, 271, 271))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.availableButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.availableButton.setChecked(True)
        self.availableButton.setObjectName("availableButton")
        self.verticalLayout.addWidget(self.availableButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.earmarkedButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.earmarkedButton.setObjectName("earmarkedButton")
        self.verticalLayout.addWidget(self.earmarkedButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem1)
        self.changeCheckBox = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.changeCheckBox.setObjectName("changeCheckBox")
        self.verticalLayout.addWidget(self.changeCheckBox)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem2)
        self.conservedButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.conservedButton.setEnabled(False)
        self.conservedButton.setObjectName("conservedButton")
        self.verticalLayout.addWidget(self.conservedButton)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem3)
        self.excludedButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.excludedButton.setEnabled(False)
        self.excludedButton.setObjectName("excludedButton")
        self.verticalLayout.addWidget(self.excludedButton)
        self.targetsMetLabel = QtWidgets.QLabel(ChangeStatusDialog)
        self.targetsMetLabel.setGeometry(QtCore.QRect(80, 310, 191, 16))
        self.targetsMetLabel.setObjectName("targetsMetLabel")

        self.retranslateUi(ChangeStatusDialog)
        self.closeButton.clicked.connect(ChangeStatusDialog.close)
        self.changeCheckBox.clicked['bool'].connect(self.conservedButton.setEnabled)
        self.changeCheckBox.clicked['bool'].connect(self.excludedButton.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(ChangeStatusDialog)

    def retranslateUi(self, ChangeStatusDialog):
        _translate = QtCore.QCoreApplication.translate
        ChangeStatusDialog.setWindowTitle(_translate("ChangeStatusDialog", "Change Status panel"))
        self.changeButton.setText(_translate("ChangeStatusDialog", "Change"))
        self.undoButton.setText(_translate("ChangeStatusDialog", "Undo"))
        self.closeButton.setText(_translate("ChangeStatusDialog", "Close"))
        self.availableButton.setText(_translate("ChangeStatusDialog", "Set as Available"))
        self.earmarkedButton.setText(_translate("ChangeStatusDialog", "Set as Earmarked"))
        self.changeCheckBox.setText(_translate("ChangeStatusDialog", "Allow changes\n"
"to Conserved and\n"
"Excluded status"))
        self.conservedButton.setText(_translate("ChangeStatusDialog", "Set as Conserved"))
        self.excludedButton.setText(_translate("ChangeStatusDialog", "Set as Excluded"))
        self.targetsMetLabel.setText(_translate("ChangeStatusDialog", "Targets met: X of Y"))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ChangeStatusDialog = QtWidgets.QDialog()
    ui = Ui_ChangeStatusDialog()
    ui.setupUi(ChangeStatusDialog)
    ChangeStatusDialog.show()
    sys.exit(app.exec_())

