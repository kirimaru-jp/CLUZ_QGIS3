# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Bob\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\cluz\forms\cluz_form_zones_marxan.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_zonesMarxanDialog(object):
    def setupUi(self, zonesMarxanDialog):
        zonesMarxanDialog.setObjectName("zonesMarxanDialog")
        zonesMarxanDialog.resize(700, 430)
        zonesMarxanDialog.setMinimumSize(QtCore.QSize(700, 430))
        self.label = QtWidgets.QLabel(zonesMarxanDialog)
        self.label.setGeometry(QtCore.QRect(10, 0, 180, 380))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/images/images/marxan_logo.png"))
        self.label.setObjectName("label")
        self.horizontalLayoutWidget = QtWidgets.QWidget(zonesMarxanDialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(290, 370, 291, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.startButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.startButton.setMinimumSize(QtCore.QSize(0, 16))
        self.startButton.setObjectName("startButton")
        self.horizontalLayout.addWidget(self.startButton)
        self.closeButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.closeButton.setMinimumSize(QtCore.QSize(0, 16))
        self.closeButton.setObjectName("closeButton")
        self.horizontalLayout.addWidget(self.closeButton)
        self.tabWidget = QtWidgets.QTabWidget(zonesMarxanDialog)
        self.tabWidget.setGeometry(QtCore.QRect(200, 20, 480, 340))
        self.tabWidget.setObjectName("tabWidget")
        self.tab1 = QtWidgets.QWidget()
        self.tab1.setObjectName("tab1")
        self.formLayoutWidget = QtWidgets.QWidget(self.tab1)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 20, 431, 151))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.iterLineEdit = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.iterLineEdit.setMinimumSize(QtCore.QSize(0, 24))
        self.iterLineEdit.setObjectName("iterLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.iterLineEdit)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(1, QtWidgets.QFormLayout.LabelRole, spacerItem)
        self.runLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.runLabel.setMinimumSize(QtCore.QSize(150, 24))
        self.runLabel.setObjectName("runLabel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.runLabel)
        self.runLineEdit = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.runLineEdit.setMinimumSize(QtCore.QSize(0, 24))
        self.runLineEdit.setObjectName("runLineEdit")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.runLineEdit)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(5, QtWidgets.QFormLayout.LabelRole, spacerItem1)
        self.outputLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.outputLabel.setMinimumSize(QtCore.QSize(150, 24))
        self.outputLabel.setObjectName("outputLabel")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.outputLabel)
        self.outputLineEdit = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.outputLineEdit.setMinimumSize(QtCore.QSize(0, 24))
        self.outputLineEdit.setObjectName("outputLineEdit")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.outputLineEdit)
        self.iterLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.iterLabel.setMinimumSize(QtCore.QSize(150, 24))
        self.iterLabel.setObjectName("iterLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.iterLabel)
        self.gridLayoutWidget = QtWidgets.QWidget(self.tab1)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 170, 431, 80))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.boundCheckBox = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.boundCheckBox.setMinimumSize(QtCore.QSize(180, 24))
        self.boundCheckBox.setObjectName("boundCheckBox")
        self.gridLayout.addWidget(self.boundCheckBox, 0, 0, 1, 1)
        self.boundLineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.boundLineEdit.setMinimumSize(QtCore.QSize(0, 24))
        self.boundLineEdit.setText("")
        self.boundLineEdit.setObjectName("boundLineEdit")
        self.gridLayout.addWidget(self.boundLineEdit, 0, 1, 1, 1)
        self.extraCheckBox = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.extraCheckBox.setMinimumSize(QtCore.QSize(280, 24))
        self.extraCheckBox.setObjectName("extraCheckBox")
        self.gridLayout.addWidget(self.extraCheckBox, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tab1, "")
        self.extraTab = QtWidgets.QWidget()
        self.extraTab.setObjectName("extraTab")
        self.formLayoutWidget_2 = QtWidgets.QWidget(self.extraTab)
        self.formLayoutWidget_2.setGeometry(QtCore.QRect(10, 20, 431, 131))
        self.formLayoutWidget_2.setObjectName("formLayoutWidget_2")
        self.formLayout_2 = QtWidgets.QFormLayout(self.formLayoutWidget_2)
        self.formLayout_2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_2.setContentsMargins(0, 0, 0, 0)
        self.formLayout_2.setObjectName("formLayout_2")
        self.propLabel = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.propLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.propLabel.setObjectName("propLabel")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.propLabel)
        self.propLineEdit = QtWidgets.QLineEdit(self.formLayoutWidget_2)
        self.propLineEdit.setMinimumSize(QtCore.QSize(0, 24))
        self.propLineEdit.setObjectName("propLineEdit")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.propLineEdit)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout_2.setItem(1, QtWidgets.QFormLayout.LabelRole, spacerItem2)
        self.missingLabel = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.missingLabel.setMinimumSize(QtCore.QSize(0, 40))
        self.missingLabel.setWordWrap(True)
        self.missingLabel.setObjectName("missingLabel")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.missingLabel)
        self.missingLineEdit = QtWidgets.QLineEdit(self.formLayoutWidget_2)
        self.missingLineEdit.setMinimumSize(QtCore.QSize(0, 24))
        self.missingLineEdit.setObjectName("missingLineEdit")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.missingLineEdit)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout_2.setItem(3, QtWidgets.QFormLayout.LabelRole, spacerItem3)
        self.blmTableWidget = QtWidgets.QTableWidget(self.extraTab)
        self.blmTableWidget.setGeometry(QtCore.QRect(60, 190, 250, 121))
        self.blmTableWidget.setObjectName("blmTableWidget")
        self.blmTableWidget.setColumnCount(0)
        self.blmTableWidget.setRowCount(0)
        self.boundZoneCheckBox = QtWidgets.QCheckBox(self.extraTab)
        self.boundZoneCheckBox.setGeometry(QtCore.QRect(10, 160, 201, 24))
        self.boundZoneCheckBox.setMinimumSize(QtCore.QSize(180, 24))
        self.boundZoneCheckBox.setObjectName("boundZoneCheckBox")
        self.tabWidget.addTab(self.extraTab, "")

        self.retranslateUi(zonesMarxanDialog)
        self.tabWidget.setCurrentIndex(1)
        self.closeButton.clicked.connect(zonesMarxanDialog.close)
        self.boundCheckBox.clicked['bool'].connect(self.boundLineEdit.setVisible)
        self.boundZoneCheckBox.clicked['bool'].connect(self.blmTableWidget.setVisible)
        QtCore.QMetaObject.connectSlotsByName(zonesMarxanDialog)

    def retranslateUi(self, zonesMarxanDialog):
        _translate = QtCore.QCoreApplication.translate
        zonesMarxanDialog.setWindowTitle(_translate("zonesMarxanDialog", "Launch Marxan"))
        self.startButton.setText(_translate("zonesMarxanDialog", "Start Marxan with Zones"))
        self.closeButton.setText(_translate("zonesMarxanDialog", "Close"))
        self.runLabel.setText(_translate("zonesMarxanDialog", "Number of runs"))
        self.outputLabel.setText(_translate("zonesMarxanDialog", "Output file name"))
        self.iterLabel.setText(_translate("zonesMarxanDialog", "Number of iterations"))
        self.boundCheckBox.setText(_translate("zonesMarxanDialog", "Include boundary cost (BLM)"))
        self.extraCheckBox.setText(_translate("zonesMarxanDialog", "Produce extra Marxan outputs"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab1), _translate("zonesMarxanDialog", "Standard options"))
        self.propLabel.setText(_translate("zonesMarxanDialog", "Starting proportion"))
        self.missingLabel.setText(_translate("zonesMarxanDialog", "Species missing if target proportion is lower than"))
        self.boundZoneCheckBox.setText(_translate("zonesMarxanDialog", "Include zones boundary cost (BLM)"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.extraTab), _translate("zonesMarxanDialog", "Advanced options"))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    zonesMarxanDialog = QtWidgets.QDialog()
    ui = Ui_zonesMarxanDialog()
    ui.setupUi(zonesMarxanDialog)
    zonesMarxanDialog.show()
    sys.exit(app.exec_())

