# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cluz_form_target.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_targetDialog(object):
    def setupUi(self, targetDialog):
        targetDialog.setObjectName("targetDialog")
        targetDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        targetDialog.resize(750, 500)
        targetDialog.setMinimumSize(QtCore.QSize(750, 500))
        self.gridLayout = QtWidgets.QGridLayout(targetDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.targetTableWidget = QtWidgets.QTableWidget(targetDialog)
        self.targetTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.targetTableWidget.setAlternatingRowColors(True)
        self.targetTableWidget.setObjectName("targetTableWidget")
        self.targetTableWidget.setColumnCount(0)
        self.targetTableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.targetTableWidget, 0, 0, 1, 1)
        self.cancelButton = QtWidgets.QPushButton(targetDialog)
        self.cancelButton.setObjectName("cancelButton")
        self.gridLayout.addWidget(self.cancelButton, 1, 0, 1, 1)

        self.retranslateUi(targetDialog)
        self.cancelButton.clicked.connect(targetDialog.close)
        QtCore.QMetaObject.connectSlotsByName(targetDialog)

    def retranslateUi(self, targetDialog):
        _translate = QtCore.QCoreApplication.translate
        targetDialog.setWindowTitle(_translate("targetDialog", "Target table"))
        self.targetTableWidget.setSortingEnabled(True)
        self.cancelButton.setText(_translate("targetDialog", "Close"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    targetDialog = QtWidgets.QDialog()
    ui = Ui_targetDialog()
    ui.setupUi(targetDialog)
    targetDialog.show()
    sys.exit(app.exec_())

