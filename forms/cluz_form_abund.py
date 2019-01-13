# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cluz_form_abund.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_abundDialog(object):
    def setupUi(self, abundDialog):
        abundDialog.setObjectName("abundDialog")
        abundDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        abundDialog.resize(713, 432)
        self.gridLayout = QtWidgets.QGridLayout(abundDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.abundTableWidget = QtWidgets.QTableWidget(abundDialog)
        self.abundTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.abundTableWidget.setAlternatingRowColors(True)
        self.abundTableWidget.setObjectName("abundTableWidget")
        self.abundTableWidget.setColumnCount(0)
        self.abundTableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.abundTableWidget, 0, 0, 1, 1)
        self.cancelButton = QtWidgets.QPushButton(abundDialog)
        self.cancelButton.setObjectName("cancelButton")
        self.gridLayout.addWidget(self.cancelButton, 1, 0, 1, 1)

        self.retranslateUi(abundDialog)
        self.cancelButton.clicked.connect(abundDialog.close)
        QtCore.QMetaObject.connectSlotsByName(abundDialog)

    def retranslateUi(self, abundDialog):
        _translate = QtCore.QCoreApplication.translate
        abundDialog.setWindowTitle(_translate("abundDialog", "Abundance table"))
        self.abundTableWidget.setSortingEnabled(True)
        self.cancelButton.setText(_translate("abundDialog", "Close"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    abundDialog = QtWidgets.QDialog()
    ui = Ui_abundDialog()
    ui.setupUi(abundDialog)
    abundDialog.show()
    sys.exit(app.exec_())

