# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Bob\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\cluz3\forms\cluz_form_start.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_startDialog(object):
    def setupUi(self, startDialog):
        startDialog.setObjectName("startDialog")
        startDialog.resize(500, 300)
        startDialog.setMinimumSize(QtCore.QSize(500, 300))
        self.horizontalLayoutWidget = QtWidgets.QWidget(startDialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(180, 230, 181, 41))
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
        self.graphicLabel = QtWidgets.QLabel(startDialog)
        self.graphicLabel.setGeometry(QtCore.QRect(20, 30, 51, 51))
        self.graphicLabel.setText("")
        self.graphicLabel.setPixmap(QtGui.QPixmap(":/images/images/marxan_logo_small.png"))
        self.graphicLabel.setObjectName("graphicLabel")
        self.verticalLayoutWidget = QtWidgets.QWidget(startDialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(160, 20, 232, 181))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setMinimumSize(QtCore.QSize(230, 0))
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.openRadioButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.openRadioButton.setMinimumSize(QtCore.QSize(211, 20))
        self.openRadioButton.setChecked(True)
        self.openRadioButton.setObjectName("openRadioButton")
        self.verticalLayout.addWidget(self.openRadioButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem1)
        self.createButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.createButton.setMinimumSize(QtCore.QSize(211, 20))
        self.createButton.setCheckable(True)
        self.createButton.setObjectName("createButton")
        self.verticalLayout.addWidget(self.createButton)

        self.retranslateUi(startDialog)
        self.cancelButton.clicked.connect(startDialog.close)
        QtCore.QMetaObject.connectSlotsByName(startDialog)

    def retranslateUi(self, startDialog):
        _translate = QtCore.QCoreApplication.translate
        startDialog.setWindowTitle(_translate("startDialog", "Select or create CLUZ setup file"))
        self.okButton.setText(_translate("startDialog", "OK"))
        self.cancelButton.setText(_translate("startDialog", "Cancel"))
        self.label.setText(_translate("startDialog", "The selected action cannot continue because a CLUZ setup file has not been specified.\n"
"\n"
"Please open an existing setup file or create a new one."))
        self.openRadioButton.setText(_translate("startDialog", "Open existing setup file"))
        self.createButton.setText(_translate("startDialog", "Create new setup file"))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    startDialog = QtWidgets.QDialog()
    ui = Ui_startDialog()
    ui.setupUi(startDialog)
    startDialog.show()
    sys.exit(app.exec_())

