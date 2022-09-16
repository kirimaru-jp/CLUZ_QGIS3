# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cluz_form_identify_selected.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_identifySelectedDialog(object):
    def setupUi(self, identifySelectedDialog):
        identifySelectedDialog.setObjectName("identifySelectedDialog")
        identifySelectedDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        identifySelectedDialog.resize(750, 500)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(identifySelectedDialog.sizePolicy().hasHeightForWidth())
        identifySelectedDialog.setSizePolicy(sizePolicy)
        identifySelectedDialog.setMinimumSize(QtCore.QSize(750, 500))
        self.gridLayout = QtWidgets.QGridLayout(identifySelectedDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.identifySelectedTableWidget = QtWidgets.QTableWidget(identifySelectedDialog)
        self.identifySelectedTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.identifySelectedTableWidget.setObjectName("identifySelectedTableWidget")
        self.identifySelectedTableWidget.setColumnCount(0)
        self.identifySelectedTableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.identifySelectedTableWidget, 0, 0, 1, 1)
        self.closeButton = QtWidgets.QPushButton(identifySelectedDialog)
        self.closeButton.setObjectName("closeButton")
        self.gridLayout.addWidget(self.closeButton, 1, 0, 1, 1)

        self.retranslateUi(identifySelectedDialog)
        self.closeButton.clicked.connect(identifySelectedDialog.close)
        QtCore.QMetaObject.connectSlotsByName(identifySelectedDialog)

    def retranslateUi(self, identifySelectedDialog):
        _translate = QtCore.QCoreApplication.translate
        identifySelectedDialog.setWindowTitle(_translate("identifySelectedDialog", "Identify Tool"))
        self.closeButton.setText(_translate("identifySelectedDialog", "Close"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    identifySelectedDialog = QtWidgets.QDialog()
    ui = Ui_identifySelectedDialog()
    ui.setupUi(identifySelectedDialog)
    identifySelectedDialog.show()
    sys.exit(app.exec_())

