# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cluz_form_remove.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_removeDialog(object):
    def setupUi(self, removeDialog):
        removeDialog.setObjectName("removeDialog")
        removeDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        removeDialog.resize(800, 400)
        removeDialog.setMinimumSize(QtCore.QSize(800, 400))
        self.featLabel = QtWidgets.QLabel(removeDialog)
        self.featLabel.setGeometry(QtCore.QRect(120, 20, 661, 16))
        self.featLabel.setMinimumSize(QtCore.QSize(461, 16))
        self.featLabel.setObjectName("featLabel")
        self.featListWidget = QtWidgets.QListWidget(removeDialog)
        self.featListWidget.setGeometry(QtCore.QRect(120, 40, 661, 290))
        self.featListWidget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.featListWidget.setObjectName("featListWidget")
        self.logoLabel = QtWidgets.QLabel(removeDialog)
        self.logoLabel.setGeometry(QtCore.QRect(-20, 20, 131, 351))
        self.logoLabel.setText("")
        self.logoLabel.setPixmap(QtGui.QPixmap(":/plugins/Cluz/icons/icons/setup_logo.png"))
        self.logoLabel.setObjectName("logoLabel")
        self.horizontalLayoutWidget = QtWidgets.QWidget(removeDialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(350, 340, 211, 51))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.okButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.okButton.setMinimumSize(QtCore.QSize(0, 24))
        self.okButton.setObjectName("okButton")
        self.horizontalLayout.addWidget(self.okButton)
        self.cancelButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.cancelButton.setMinimumSize(QtCore.QSize(0, 24))
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)

        self.retranslateUi(removeDialog)
        self.cancelButton.clicked.connect(removeDialog.close)
        QtCore.QMetaObject.connectSlotsByName(removeDialog)

    def retranslateUi(self, removeDialog):
        _translate = QtCore.QCoreApplication.translate
        removeDialog.setWindowTitle(_translate("removeDialog", "Choose features to remove"))
        self.featLabel.setText(_translate("removeDialog", "Select conservation features to remove from the abundance and target tables"))
        self.okButton.setText(_translate("removeDialog", "OK"))
        self.cancelButton.setText(_translate("removeDialog", "Cancel"))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    removeDialog = QtWidgets.QDialog()
    ui = Ui_removeDialog()
    ui.setupUi(removeDialog)
    removeDialog.show()
    sys.exit(app.exec_())

