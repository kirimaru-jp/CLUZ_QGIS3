# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Bob\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\cluz\forms\cluz_form_zones_inputs.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_zonesInputsDialog(object):
    def setupUi(self, zonesInputsDialog):
        zonesInputsDialog.setObjectName("zonesInputsDialog")
        zonesInputsDialog.resize(620, 390)
        zonesInputsDialog.setMinimumSize(QtCore.QSize(620, 390))
        self.horizontalLayoutWidget = QtWidgets.QWidget(zonesInputsDialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(280, 300, 201, 51))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.okButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.okButton.setObjectName("okButton")
        self.horizontalLayout.addWidget(self.okButton)
        self.cancelButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.inputsLabel = QtWidgets.QLabel(zonesInputsDialog)
        self.inputsLabel.setGeometry(QtCore.QRect(190, 30, 421, 16))
        self.inputsLabel.setObjectName("inputsLabel")
        self.verticalLayoutWidget = QtWidgets.QWidget(zonesInputsDialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(190, 60, 423, 166))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.targetBox = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.targetBox.setFont(font)
        self.targetBox.setObjectName("targetBox")
        self.verticalLayout.addWidget(self.targetBox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.puBox = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.puBox.setObjectName("puBox")
        self.verticalLayout.addWidget(self.puBox)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem1)
        self.zonesBox = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.zonesBox.setObjectName("zonesBox")
        self.verticalLayout.addWidget(self.zonesBox)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem2)
        self.boundBox = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.boundBox.setObjectName("boundBox")
        self.verticalLayout.addWidget(self.boundBox)
        self.boundextBox = QtWidgets.QCheckBox(zonesInputsDialog)
        self.boundextBox.setGeometry(QtCore.QRect(230, 230, 351, 24))
        self.boundextBox.setMinimumSize(QtCore.QSize(0, 24))
        self.boundextBox.setObjectName("boundextBox")
        self.label = QtWidgets.QLabel(zonesInputsDialog)
        self.label.setGeometry(QtCore.QRect(10, 0, 180, 380))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/images/images/marxan_logo.png"))
        self.label.setObjectName("label")

        self.retranslateUi(zonesInputsDialog)
        self.cancelButton.clicked.connect(zonesInputsDialog.close)
        self.boundBox.clicked['bool'].connect(self.boundextBox.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(zonesInputsDialog)

    def retranslateUi(self, zonesInputsDialog):
        _translate = QtCore.QCoreApplication.translate
        zonesInputsDialog.setWindowTitle(_translate("zonesInputsDialog", "Create Marxan with Zones files"))
        self.okButton.setText(_translate("zonesInputsDialog", "OK"))
        self.cancelButton.setText(_translate("zonesInputsDialog", "Cancel"))
        self.inputsLabel.setText(_translate("zonesInputsDialog", "<html><head/><body><p><span style=\" font-weight:600;\">Create the following Marxan with Zones files from the CLUZ files:</span></p></body></html>"))
        self.targetBox.setText(_translate("zonesInputsDialog", "Target and feature files (feat.dat, zonetarget.dat and zonecontrib.dat)"))
        self.puBox.setText(_translate("zonesInputsDialog", "Planning unit files (pu.dat, puzone.dat and pulock.dat)"))
        self.zonesBox.setText(_translate("zonesInputsDialog", "Zones file (zones.dat, costs.dat and zonecost.dat)"))
        self.boundBox.setText(_translate("zonesInputsDialog", "Boundary file (bound.dat)"))
        self.boundextBox.setText(_translate("zonesInputsDialog", "Include planning region boundaries"))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    zonesInputsDialog = QtWidgets.QDialog()
    ui = Ui_zonesInputsDialog()
    ui.setupUi(zonesInputsDialog)
    zonesInputsDialog.show()
    sys.exit(app.exec_())

