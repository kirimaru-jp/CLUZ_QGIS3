# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Bob\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\cluz3\forms\cluz_form_setup.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_setupDialog(object):
    def setupUi(self, setupDialog):
        setupDialog.setObjectName("setupDialog")
        setupDialog.resize(832, 457)
        self.gridLayoutWidget = QtWidgets.QWidget(setupDialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(130, 10, 681, 271))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.targetLineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.targetLineEdit.setObjectName("targetLineEdit")
        self.gridLayout.addWidget(self.targetLineEdit, 4, 1, 1, 1)
        self.marxanLineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.marxanLineEdit.setObjectName("marxanLineEdit")
        self.gridLayout.addWidget(self.marxanLineEdit, 0, 1, 1, 1)
        self.marxanLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.marxanLabel.setObjectName("marxanLabel")
        self.gridLayout.addWidget(self.marxanLabel, 0, 0, 1, 1)
        self.outputLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.outputLabel.setObjectName("outputLabel")
        self.gridLayout.addWidget(self.outputLabel, 2, 0, 1, 1)
        self.inputLineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.inputLineEdit.setObjectName("inputLineEdit")
        self.gridLayout.addWidget(self.inputLineEdit, 1, 1, 1, 1)
        self.outputButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.outputButton.setMinimumSize(QtCore.QSize(75, 25))
        self.outputButton.setAutoDefault(False)
        self.outputButton.setObjectName("outputButton")
        self.gridLayout.addWidget(self.outputButton, 2, 2, 1, 1)
        self.puLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.puLabel.setMinimumSize(QtCore.QSize(110, 16))
        self.puLabel.setObjectName("puLabel")
        self.gridLayout.addWidget(self.puLabel, 3, 0, 1, 1)
        self.marxanButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.marxanButton.setMinimumSize(QtCore.QSize(75, 25))
        self.marxanButton.setAutoDefault(False)
        self.marxanButton.setObjectName("marxanButton")
        self.gridLayout.addWidget(self.marxanButton, 0, 2, 1, 1)
        self.puLineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.puLineEdit.setObjectName("puLineEdit")
        self.gridLayout.addWidget(self.puLineEdit, 3, 1, 1, 1)
        self.outputLineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.outputLineEdit.setObjectName("outputLineEdit")
        self.gridLayout.addWidget(self.outputLineEdit, 2, 1, 1, 1)
        self.inputLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.inputLabel.setObjectName("inputLabel")
        self.gridLayout.addWidget(self.inputLabel, 1, 0, 1, 1)
        self.targetLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.targetLabel.setObjectName("targetLabel")
        self.gridLayout.addWidget(self.targetLabel, 4, 0, 1, 1)
        self.inputButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.inputButton.setMinimumSize(QtCore.QSize(75, 25))
        self.inputButton.setAutoDefault(False)
        self.inputButton.setObjectName("inputButton")
        self.gridLayout.addWidget(self.inputButton, 1, 2, 1, 1)
        self.puButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.puButton.setMinimumSize(QtCore.QSize(75, 25))
        self.puButton.setAutoDefault(False)
        self.puButton.setObjectName("puButton")
        self.gridLayout.addWidget(self.puButton, 3, 2, 1, 1)
        self.targetButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.targetButton.setMinimumSize(QtCore.QSize(75, 25))
        self.targetButton.setAutoDefault(False)
        self.targetButton.setObjectName("targetButton")
        self.gridLayout.addWidget(self.targetButton, 4, 2, 1, 1)
        self.setupIconLabel = QtWidgets.QLabel(setupDialog)
        self.setupIconLabel.setGeometry(QtCore.QRect(-10, 20, 120, 380))
        self.setupIconLabel.setText("")
        self.setupIconLabel.setPixmap(QtGui.QPixmap(":/images/images/setup_logo.png"))
        self.setupIconLabel.setObjectName("setupIconLabel")
        self.horizontalLayoutWidget = QtWidgets.QWidget(setupDialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(180, 400, 471, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.saveButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.saveButton.setMinimumSize(QtCore.QSize(90, 25))
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout.addWidget(self.saveButton)
        self.loadButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.loadButton.setMinimumSize(QtCore.QSize(90, 25))
        self.loadButton.setObjectName("loadButton")
        self.horizontalLayout.addWidget(self.loadButton)
        self.saveAsButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.saveAsButton.setMinimumSize(QtCore.QSize(90, 25))
        self.saveAsButton.setObjectName("saveAsButton")
        self.horizontalLayout.addWidget(self.saveAsButton)
        self.cancelButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.cancelButton.setMinimumSize(QtCore.QSize(90, 25))
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.setupPathLabel = QtWidgets.QLabel(setupDialog)
        self.setupPathLabel.setGeometry(QtCore.QRect(160, 330, 651, 31))
        self.setupPathLabel.setObjectName("setupPathLabel")
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(setupDialog)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(130, 290, 681, 41))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.precLabel = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.precLabel.setMinimumSize(QtCore.QSize(500, 24))
        self.precLabel.setObjectName("precLabel")
        self.horizontalLayout_2.addWidget(self.precLabel)
        self.precComboBox = QtWidgets.QComboBox(self.horizontalLayoutWidget_2)
        self.precComboBox.setMinimumSize(QtCore.QSize(0, 24))
        self.precComboBox.setSizeIncrement(QtCore.QSize(0, 16))
        self.precComboBox.setObjectName("precComboBox")
        self.horizontalLayout_2.addWidget(self.precComboBox)

        self.retranslateUi(setupDialog)
        self.cancelButton.clicked.connect(setupDialog.close)
        QtCore.QMetaObject.connectSlotsByName(setupDialog)

    def retranslateUi(self, setupDialog):
        _translate = QtCore.QCoreApplication.translate
        setupDialog.setWindowTitle(_translate("setupDialog", "Setup file settings"))
        self.targetLineEdit.setText(_translate("setupDialog", "blank"))
        self.marxanLineEdit.setText(_translate("setupDialog", "blank"))
        self.marxanLabel.setText(_translate("setupDialog", "Marxan location"))
        self.outputLabel.setText(_translate("setupDialog", "Output directory"))
        self.inputLineEdit.setText(_translate("setupDialog", "blank"))
        self.outputButton.setText(_translate("setupDialog", "Browse..."))
        self.puLabel.setText(_translate("setupDialog", "Planning unit theme"))
        self.marxanButton.setText(_translate("setupDialog", "Browse..."))
        self.puLineEdit.setText(_translate("setupDialog", "blank"))
        self.outputLineEdit.setText(_translate("setupDialog", "blank"))
        self.inputLabel.setText(_translate("setupDialog", "Input directory"))
        self.targetLabel.setText(_translate("setupDialog", "Target table"))
        self.inputButton.setText(_translate("setupDialog", "Browse..."))
        self.puButton.setText(_translate("setupDialog", "Browse..."))
        self.targetButton.setText(_translate("setupDialog", "Browse..."))
        self.saveButton.setText(_translate("setupDialog", "Save"))
        self.loadButton.setText(_translate("setupDialog", "Load"))
        self.saveAsButton.setText(_translate("setupDialog", "Save As..."))
        self.cancelButton.setText(_translate("setupDialog", "Close"))
        self.setupPathLabel.setText(_translate("setupDialog", "Setup file location: blank"))
        self.precLabel.setText(_translate("setupDialog", "Decimal places for numbers in Abundance and Target tables                    "))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    setupDialog = QtWidgets.QDialog()
    ui = Ui_setupDialog()
    ui.setupUi(setupDialog)
    setupDialog.show()
    sys.exit(app.exec_())

