# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Bob\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\cluz3\forms\cluz_form_load.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_loadDialog(object):
    def setupUi(self, loadDialog):
        loadDialog.setObjectName("loadDialog")
        loadDialog.resize(764, 432)
        loadDialog.setMinimumSize(QtCore.QSize(460, 430))
        self.logoLabel = QtWidgets.QLabel(loadDialog)
        self.logoLabel.setGeometry(QtCore.QRect(-10, 20, 120, 380))
        self.logoLabel.setText("")
        self.logoLabel.setPixmap(QtGui.QPixmap(":/images/images/setup_logo.png"))
        self.logoLabel.setObjectName("logoLabel")
        self.horizontalLayoutWidget = QtWidgets.QWidget(loadDialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(309, 350, 191, 41))
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
        self.bestCheckBox = QtWidgets.QCheckBox(loadDialog)
        self.bestCheckBox.setGeometry(QtCore.QRect(150, 20, 591, 17))
        self.bestCheckBox.setObjectName("bestCheckBox")
        self.bestLabel = QtWidgets.QLabel(loadDialog)
        self.bestLabel.setGeometry(QtCore.QRect(170, 90, 571, 16))
        self.bestLabel.setObjectName("bestLabel")
        self.bestNameLineEdit = QtWidgets.QLineEdit(loadDialog)
        self.bestNameLineEdit.setGeometry(QtCore.QRect(170, 110, 241, 20))
        self.bestNameLineEdit.setObjectName("bestNameLineEdit")
        self.summedCheckBox = QtWidgets.QCheckBox(loadDialog)
        self.summedCheckBox.setGeometry(QtCore.QRect(150, 180, 441, 17))
        self.summedCheckBox.setObjectName("summedCheckBox")
        self.summedLabel = QtWidgets.QLabel(loadDialog)
        self.summedLabel.setGeometry(QtCore.QRect(170, 260, 571, 16))
        self.summedLabel.setObjectName("summedLabel")
        self.summedNameLineEdit = QtWidgets.QLineEdit(loadDialog)
        self.summedNameLineEdit.setGeometry(QtCore.QRect(170, 280, 241, 20))
        self.summedNameLineEdit.setObjectName("summedNameLineEdit")
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(loadDialog)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(150, 40, 591, 41))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.bestLineEdit = QtWidgets.QLineEdit(self.horizontalLayoutWidget_2)
        self.bestLineEdit.setMaxLength(32766)
        self.bestLineEdit.setObjectName("bestLineEdit")
        self.horizontalLayout_2.addWidget(self.bestLineEdit)
        self.bestButton = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.bestButton.setObjectName("bestButton")
        self.horizontalLayout_2.addWidget(self.bestButton)
        self.horizontalLayoutWidget_3 = QtWidgets.QWidget(loadDialog)
        self.horizontalLayoutWidget_3.setGeometry(QtCore.QRect(150, 210, 591, 41))
        self.horizontalLayoutWidget_3.setObjectName("horizontalLayoutWidget_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_3)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.summedLineEdit = QtWidgets.QLineEdit(self.horizontalLayoutWidget_3)
        self.summedLineEdit.setObjectName("summedLineEdit")
        self.horizontalLayout_3.addWidget(self.summedLineEdit)
        self.summedButton = QtWidgets.QPushButton(self.horizontalLayoutWidget_3)
        self.summedButton.setObjectName("summedButton")
        self.horizontalLayout_3.addWidget(self.summedButton)

        self.retranslateUi(loadDialog)
        self.cancelButton.clicked.connect(loadDialog.close)
        self.bestCheckBox.clicked['bool'].connect(self.bestLabel.setVisible)
        self.bestCheckBox.clicked['bool'].connect(self.bestNameLineEdit.setVisible)
        self.summedCheckBox.clicked['bool'].connect(self.summedLabel.setVisible)
        self.summedCheckBox.clicked['bool'].connect(self.summedNameLineEdit.setVisible)
        self.bestCheckBox.clicked['bool'].connect(self.bestLineEdit.setVisible)
        self.bestCheckBox.clicked['bool'].connect(self.bestButton.setVisible)
        self.summedCheckBox.clicked['bool'].connect(self.summedLineEdit.setVisible)
        self.summedCheckBox.clicked['bool'].connect(self.summedButton.setVisible)
        QtCore.QMetaObject.connectSlotsByName(loadDialog)

    def retranslateUi(self, loadDialog):
        _translate = QtCore.QCoreApplication.translate
        loadDialog.setWindowTitle(_translate("loadDialog", "Load previous Marxan results"))
        self.okButton.setText(_translate("loadDialog", "OK"))
        self.cancelButton.setText(_translate("loadDialog", "Cancel"))
        self.bestCheckBox.setText(_translate("loadDialog", "Load best solution results (default name is *_best.txt)"))
        self.bestLabel.setText(_translate("loadDialog", "New best field name"))
        self.summedCheckBox.setText(_translate("loadDialog", "Load summed solution results (default name is *_ssoln.txt)"))
        self.summedLabel.setText(_translate("loadDialog", "New summed solution field name"))
        self.bestButton.setText(_translate("loadDialog", "Browse"))
        self.summedButton.setText(_translate("loadDialog", "Browse"))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    loadDialog = QtWidgets.QDialog()
    ui = Ui_loadDialog()
    ui.setupUi(loadDialog)
    loadDialog.show()
    sys.exit(app.exec_())

