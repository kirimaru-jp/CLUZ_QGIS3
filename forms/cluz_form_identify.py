# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cluz_form_identify.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_identifyDialog(object):
    def setupUi(self, identifyDialog):
        identifyDialog.setObjectName("identifyDialog")
        identifyDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        identifyDialog.resize(632, 300)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(identifyDialog.sizePolicy().hasHeightForWidth())
        identifyDialog.setSizePolicy(sizePolicy)
        self.gridLayout = QtWidgets.QGridLayout(identifyDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.identifyTableWidget = QtWidgets.QTableWidget(identifyDialog)
        self.identifyTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.identifyTableWidget.setObjectName("identifyTableWidget")
        self.identifyTableWidget.setColumnCount(0)
        self.identifyTableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.identifyTableWidget, 0, 0, 1, 1)
        self.closeButton = QtWidgets.QPushButton(identifyDialog)
        self.closeButton.setObjectName("closeButton")
        self.gridLayout.addWidget(self.closeButton, 1, 0, 1, 1)

        self.retranslateUi(identifyDialog)
        self.closeButton.clicked.connect(identifyDialog.close)
        QtCore.QMetaObject.connectSlotsByName(identifyDialog)

    def retranslateUi(self, identifyDialog):
        _translate = QtCore.QCoreApplication.translate
        identifyDialog.setWindowTitle(_translate("identifyDialog", "Identify Tool"))
        self.closeButton.setText(_translate("identifyDialog", "Close"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    identifyDialog = QtWidgets.QDialog()
    ui = Ui_identifyDialog()
    ui.setupUi(identifyDialog)
    identifyDialog.show()
    sys.exit(app.exec_())

