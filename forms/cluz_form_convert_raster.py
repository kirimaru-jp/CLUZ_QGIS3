# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\rjsmi\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\cluz\forms\cluz_form_convert_raster.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_convertRasterDialog(object):
    def setupUi(self, convertRasterDialog):
        convertRasterDialog.setObjectName("convertRasterDialog")
        convertRasterDialog.resize(634, 400)
        convertRasterDialog.setMinimumSize(QtCore.QSize(630, 400))
        self.logoLabel = QtWidgets.QLabel(convertRasterDialog)
        self.logoLabel.setGeometry(QtCore.QRect(-10, 20, 120, 380))
        self.logoLabel.setText("")
        self.logoLabel.setPixmap(QtGui.QPixmap(":/images/images/setup_logo.png"))
        self.logoLabel.setObjectName("logoLabel")
        self.selectLabel = QtWidgets.QLabel(convertRasterDialog)
        self.selectLabel.setGeometry(QtCore.QRect(140, 20, 471, 16))
        self.selectLabel.setObjectName("selectLabel")
        self.selectListWidget = QtWidgets.QListWidget(convertRasterDialog)
        self.selectListWidget.setGeometry(QtCore.QRect(140, 50, 481, 111))
        self.selectListWidget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.selectListWidget.setObjectName("selectListWidget")
        self.horizontalLayoutWidget = QtWidgets.QWidget(convertRasterDialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(210, 340, 311, 41))
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
        self.verticalLayoutWidget = QtWidgets.QWidget(convertRasterDialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(140, 180, 481, 78))
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
        self.horizontalLayoutWidget_3 = QtWidgets.QWidget(convertRasterDialog)
        self.horizontalLayoutWidget_3.setGeometry(QtCore.QRect(160, 260, 331, 41))
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

        self.retranslateUi(convertRasterDialog)
        self.cancelButton.clicked.connect(convertRasterDialog.close)
        self.userRadioButton.toggled['bool'].connect(self.convLabel.setEnabled)
        self.userRadioButton.toggled['bool'].connect(self.convLineEdit.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(convertRasterDialog)

    def retranslateUi(self, convertRasterDialog):
        _translate = QtCore.QCoreApplication.translate
        convertRasterDialog.setWindowTitle(_translate("convertRasterDialog", "Convert raster layer to abundance data"))
        self.selectLabel.setText(_translate("convertRasterDialog", "Select layers to import data into Marxan (must be single band rasters with integer values)"))
        self.okButton.setText(_translate("convertRasterDialog", "OK"))
        self.cancelButton.setText(_translate("convertRasterDialog", "Cancel"))
        self.noneRadioButton.setText(_translate("convertRasterDialog", "No conversion (results will be in layer measurement units)"))
        self.userRadioButton.setText(_translate("convertRasterDialog", "User defined conversion"))
        self.convLabel.setText(_translate("convertRasterDialog", "Area conversion value"))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    convertRasterDialog = QtWidgets.QDialog()
    ui = Ui_convertRasterDialog()
    ui.setupUi(convertRasterDialog)
    convertRasterDialog.show()
    sys.exit(app.exec_())

