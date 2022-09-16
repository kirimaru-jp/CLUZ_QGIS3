# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Bob\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\cluz3\forms\cluz_form_convert_vec.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_convertVecDialog(object):
    def setupUi(self, convertVecDialog):
        convertVecDialog.setObjectName("convertVecDialog")
        convertVecDialog.resize(634, 525)
        convertVecDialog.setMinimumSize(QtCore.QSize(630, 520))
        self.logoLabel = QtWidgets.QLabel(convertVecDialog)
        self.logoLabel.setGeometry(QtCore.QRect(-10, 20, 120, 380))
        self.logoLabel.setText("")
        self.logoLabel.setPixmap(QtGui.QPixmap(":/images/images/setup_logo.png"))
        self.logoLabel.setObjectName("logoLabel")
        self.selectLabel = QtWidgets.QLabel(convertVecDialog)
        self.selectLabel.setGeometry(QtCore.QRect(140, 20, 471, 16))
        self.selectLabel.setObjectName("selectLabel")
        self.selectListWidget = QtWidgets.QListWidget(convertVecDialog)
        self.selectListWidget.setGeometry(QtCore.QRect(140, 50, 481, 171))
        self.selectListWidget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.selectListWidget.setObjectName("selectListWidget")
        self.horizontalLayoutWidget = QtWidgets.QWidget(convertVecDialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(210, 450, 311, 41))
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
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(convertVecDialog)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(140, 230, 391, 41))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.idfieldLabel = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.idfieldLabel.setMinimumSize(QtCore.QSize(141, 22))
        self.idfieldLabel.setObjectName("idfieldLabel")
        self.horizontalLayout_2.addWidget(self.idfieldLabel)
        self.idfieldLineEdit = QtWidgets.QLineEdit(self.horizontalLayoutWidget_2)
        self.idfieldLineEdit.setObjectName("idfieldLineEdit")
        self.horizontalLayout_2.addWidget(self.idfieldLineEdit)
        self.verticalLayoutWidget = QtWidgets.QWidget(convertVecDialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(140, 290, 481, 78))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.noneRadioButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.noneRadioButton.setMinimumSize(QtCore.QSize(431, 22))
        self.noneRadioButton.setChecked(True)
        self.noneRadioButton.setObjectName("noneRadioButton")
        self.verticalLayout.addWidget(self.noneRadioButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.userRadioButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.userRadioButton.setMinimumSize(QtCore.QSize(0, 22))
        self.userRadioButton.setObjectName("userRadioButton")
        self.verticalLayout.addWidget(self.userRadioButton)
        self.horizontalLayoutWidget_3 = QtWidgets.QWidget(convertVecDialog)
        self.horizontalLayoutWidget_3.setGeometry(QtCore.QRect(160, 370, 331, 41))
        self.horizontalLayoutWidget_3.setObjectName("horizontalLayoutWidget_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_3)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.convLabel = QtWidgets.QLabel(self.horizontalLayoutWidget_3)
        self.convLabel.setMinimumSize(QtCore.QSize(141, 22))
        self.convLabel.setObjectName("convLabel")
        self.horizontalLayout_3.addWidget(self.convLabel)
        self.convLineEdit = QtWidgets.QLineEdit(self.horizontalLayoutWidget_3)
        self.convLineEdit.setObjectName("convLineEdit")
        self.horizontalLayout_3.addWidget(self.convLineEdit)

        self.retranslateUi(convertVecDialog)
        self.cancelButton.clicked.connect(convertVecDialog.close)
        self.userRadioButton.toggled['bool'].connect(self.convLabel.setEnabled)
        self.userRadioButton.toggled['bool'].connect(self.convLineEdit.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(convertVecDialog)

    def retranslateUi(self, convertVecDialog):
        _translate = QtCore.QCoreApplication.translate
        convertVecDialog.setWindowTitle(_translate("convertVecDialog", "Convert polylines or polygons to abundance data"))
        self.selectLabel.setText(_translate("convertVecDialog", "Select themes to import data into Marxan"))
        self.okButton.setText(_translate("convertVecDialog", "OK"))
        self.cancelButton.setText(_translate("convertVecDialog", "Cancel"))
        self.idfieldLabel.setText(_translate("convertVecDialog", "Layer ID field name"))
        self.noneRadioButton.setText(_translate("convertVecDialog", "No conversion (results will be in layer measurement units)"))
        self.userRadioButton.setText(_translate("convertVecDialog", "User defined conversion"))
        self.convLabel.setText(_translate("convertVecDialog", "Area conversion value"))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    convertVecDialog = QtWidgets.QDialog()
    ui = Ui_convertVecDialog()
    ui.setupUi(convertVecDialog)
    convertVecDialog.show()
    sys.exit(app.exec_())

