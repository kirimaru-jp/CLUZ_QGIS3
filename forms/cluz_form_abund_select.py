# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Bob\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\cluz3\forms\cluz_form_abund_select.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_abundSelectDialog(object):
    def setupUi(self, abundSelectDialog):
        abundSelectDialog.setObjectName("abundSelectDialog")
        abundSelectDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        abundSelectDialog.resize(700, 580)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(abundSelectDialog.sizePolicy().hasHeightForWidth())
        abundSelectDialog.setSizePolicy(sizePolicy)
        abundSelectDialog.setMinimumSize(QtCore.QSize(700, 580))
        abundSelectDialog.setMaximumSize(QtCore.QSize(700, 580))
        self.featLabel = QtWidgets.QLabel(abundSelectDialog)
        self.featLabel.setGeometry(QtCore.QRect(130, 20, 551, 16))
        self.featLabel.setMinimumSize(QtCore.QSize(350, 10))
        self.featLabel.setObjectName("featLabel")
        self.featListWidget = QtWidgets.QListWidget(abundSelectDialog)
        self.featListWidget.setGeometry(QtCore.QRect(130, 40, 551, 480))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.featListWidget.sizePolicy().hasHeightForWidth())
        self.featListWidget.setSizePolicy(sizePolicy)
        self.featListWidget.setMinimumSize(QtCore.QSize(450, 480))
        self.featListWidget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.featListWidget.setObjectName("featListWidget")
        self.okButton = QtWidgets.QPushButton(abundSelectDialog)
        self.okButton.setGeometry(QtCore.QRect(250, 540, 75, 23))
        self.okButton.setObjectName("okButton")
        self.cancelButton = QtWidgets.QPushButton(abundSelectDialog)
        self.cancelButton.setGeometry(QtCore.QRect(370, 540, 75, 23))
        self.cancelButton.setObjectName("cancelButton")
        self.logoLabel = QtWidgets.QLabel(abundSelectDialog)
        self.logoLabel.setGeometry(QtCore.QRect(-10, 20, 130, 380))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logoLabel.sizePolicy().hasHeightForWidth())
        self.logoLabel.setSizePolicy(sizePolicy)
        self.logoLabel.setMinimumSize(QtCore.QSize(130, 350))
        self.logoLabel.setText("")
        self.logoLabel.setPixmap(QtGui.QPixmap(":/images/images/setup_logo.png"))
        self.logoLabel.setObjectName("logoLabel")

        self.retranslateUi(abundSelectDialog)
        self.cancelButton.clicked.connect(abundSelectDialog.close)
        QtCore.QMetaObject.connectSlotsByName(abundSelectDialog)

    def retranslateUi(self, abundSelectDialog):
        _translate = QtCore.QCoreApplication.translate
        abundSelectDialog.setWindowTitle(_translate("abundSelectDialog", "Select features for Abundance table"))
        self.featLabel.setText(_translate("abundSelectDialog", "Display all or select conservation features to display in abundance table"))
        self.okButton.setText(_translate("abundSelectDialog", "OK"))
        self.cancelButton.setText(_translate("abundSelectDialog", "Cancel"))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    abundSelectDialog = QtWidgets.QDialog()
    ui = Ui_abundSelectDialog()
    ui.setupUi(abundSelectDialog)
    abundSelectDialog.show()
    sys.exit(app.exec_())

