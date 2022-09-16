# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Bob\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\cluz\forms\cluz_form_inputs.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_inputsDialog(object):
    def setupUi(self, inputsDialog):
        inputsDialog.setObjectName("inputsDialog")
        inputsDialog.resize(620, 390)
        inputsDialog.setMinimumSize(QtCore.QSize(620, 390))
        self.horizontalLayoutWidget = QtWidgets.QWidget(inputsDialog)
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
        self.inputsLabel = QtWidgets.QLabel(inputsDialog)
        self.inputsLabel.setGeometry(QtCore.QRect(190, 30, 421, 16))
        self.inputsLabel.setObjectName("inputsLabel")
        self.verticalLayoutWidget = QtWidgets.QWidget(inputsDialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(190, 60, 371, 151))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.targetBox = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.targetBox.setObjectName("targetBox")
        self.verticalLayout.addWidget(self.targetBox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.puBox = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.puBox.setObjectName("puBox")
        self.verticalLayout.addWidget(self.puBox)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem1)
        self.boundBox = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.boundBox.setObjectName("boundBox")
        self.verticalLayout.addWidget(self.boundBox)
        self.boundextBox = QtWidgets.QCheckBox(inputsDialog)
        self.boundextBox.setGeometry(QtCore.QRect(230, 220, 351, 24))
        self.boundextBox.setMinimumSize(QtCore.QSize(0, 24))
        self.boundextBox.setObjectName("boundextBox")
        self.label = QtWidgets.QLabel(inputsDialog)
        self.label.setGeometry(QtCore.QRect(10, 0, 180, 380))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/images/images/marxan_logo.png"))
        self.label.setObjectName("label")

        self.retranslateUi(inputsDialog)
        self.cancelButton.clicked.connect(inputsDialog.close)
        self.boundBox.clicked['bool'].connect(self.boundextBox.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(inputsDialog)

    def retranslateUi(self, inputsDialog):
        _translate = QtCore.QCoreApplication.translate
        inputsDialog.setWindowTitle(_translate("inputsDialog", "Create Marxan files"))
        self.okButton.setText(_translate("inputsDialog", "OK"))
        self.cancelButton.setText(_translate("inputsDialog", "Cancel"))
        self.inputsLabel.setText(_translate("inputsDialog", "Create the following Marxan files from the CLUZ files:"))
        self.targetBox.setText(_translate("inputsDialog", "Target file (spec.dat)"))
        self.puBox.setText(_translate("inputsDialog", "Planning unit file (pu.dat)"))
        self.boundBox.setText(_translate("inputsDialog", "Boundary file (bound.dat)"))
        self.boundextBox.setText(_translate("inputsDialog", "Include planning region boundaries"))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    inputsDialog = QtWidgets.QDialog()
    ui = Ui_inputsDialog()
    ui.setupUi(inputsDialog)
    inputsDialog.show()
    sys.exit(app.exec_())

