# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GCWiiManager.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(684, 654)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.source_btn = QtGui.QPushButton(self.centralwidget)
        self.source_btn.setObjectName(_fromUtf8("source_btn"))
        self.verticalLayout_3.addWidget(self.source_btn)
        self.destination_btn = QtGui.QPushButton(self.centralwidget)
        self.destination_btn.setObjectName(_fromUtf8("destination_btn"))
        self.verticalLayout_3.addWidget(self.destination_btn)
        self.exportSelected_btn = QtGui.QPushButton(self.centralwidget)
        self.exportSelected_btn.setObjectName(_fromUtf8("exportSelected_btn"))
        self.verticalLayout_3.addWidget(self.exportSelected_btn)
        self.export_btn = QtGui.QPushButton(self.centralwidget)
        self.export_btn.setObjectName(_fromUtf8("export_btn"))
        self.verticalLayout_3.addWidget(self.export_btn)
        self.cancel_btn = QtGui.QPushButton(self.centralwidget)
        self.cancel_btn.setObjectName(_fromUtf8("cancel_btn"))
        self.verticalLayout_3.addWidget(self.cancel_btn)
        self.exit_btn = QtGui.QPushButton(self.centralwidget)
        self.exit_btn.setObjectName(_fromUtf8("exit_btn"))
        self.verticalLayout_3.addWidget(self.exit_btn)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.label_boxArtWork = QtGui.QLabel(self.centralwidget)
        self.label_boxArtWork.setAlignment(QtCore.Qt.AlignCenter)
        self.label_boxArtWork.setObjectName(_fromUtf8("label_boxArtWork"))
        self.horizontalLayout.addWidget(self.label_boxArtWork)
        self.label_dicArtWork = QtGui.QLabel(self.centralwidget)
        self.label_dicArtWork.setAlignment(QtCore.Qt.AlignCenter)
        self.label_dicArtWork.setObjectName(_fromUtf8("label_dicArtWork"))
        self.horizontalLayout.addWidget(self.label_dicArtWork)
        self.label_description = QtGui.QLabel(self.centralwidget)
        self.label_description.setObjectName(_fromUtf8("label_description"))
        self.horizontalLayout.addWidget(self.label_description)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.label_source = QtGui.QLabel(self.centralwidget)
        self.label_source.setObjectName(_fromUtf8("label_source"))
        self.horizontalLayout_5.addWidget(self.label_source)
        self.label_destination = QtGui.QLabel(self.centralwidget)
        self.label_destination.setObjectName(_fromUtf8("label_destination"))
        self.horizontalLayout_5.addWidget(self.label_destination)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.listView_source = QtGui.QListView(self.centralwidget)
        self.listView_source.setDragEnabled(True)
        self.listView_source.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self.listView_source.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.listView_source.setModelColumn(0)
        self.listView_source.setObjectName(_fromUtf8("listView_source"))
        self.horizontalLayout_2.addWidget(self.listView_source)
        self.listView_destination = QtGui.QListView(self.centralwidget)
        self.listView_destination.setDragDropMode(QtGui.QAbstractItemView.DropOnly)
        self.listView_destination.setObjectName(_fromUtf8("listView_destination"))
        self.horizontalLayout_2.addWidget(self.listView_destination)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.label_status = QtGui.QLabel(self.centralwidget)
        self.label_status.setText(_fromUtf8(""))
        self.label_status.setObjectName(_fromUtf8("label_status"))
        self.verticalLayout_4.addWidget(self.label_status)
        self.progressBar_destination = QtGui.QProgressBar(self.centralwidget)
        self.progressBar_destination.setMaximumSize(QtCore.QSize(16777215, 15))
        self.progressBar_destination.setProperty("value", 24)
        self.progressBar_destination.setObjectName(_fromUtf8("progressBar_destination"))
        self.verticalLayout_4.addWidget(self.progressBar_destination)
        self.progressBar_fileProgress = QtGui.QProgressBar(self.centralwidget)
        self.progressBar_fileProgress.setMaximumSize(QtCore.QSize(16777215, 15))
        self.progressBar_fileProgress.setProperty("value", 24)
        self.progressBar_fileProgress.setObjectName(_fromUtf8("progressBar_fileProgress"))
        self.verticalLayout_4.addWidget(self.progressBar_fileProgress)
        self.verticalLayout_2.addLayout(self.verticalLayout_4)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.source_btn.setText(_translate("MainWindow", "Source", None))
        self.destination_btn.setText(_translate("MainWindow", "Destination", None))
        self.exportSelected_btn.setText(_translate("MainWindow", "Export Selected", None))
        self.export_btn.setText(_translate("MainWindow", "Export All", None))
        self.cancel_btn.setText(_translate("MainWindow", "Cancel", None))
        self.exit_btn.setText(_translate("MainWindow", "Exit", None))
        self.label_boxArtWork.setText(_translate("MainWindow", "Box", None))
        self.label_dicArtWork.setText(_translate("MainWindow", "Disc", None))
        self.label_description.setText(_translate("MainWindow", "Description", None))
        self.label_source.setText(_translate("MainWindow", "Source:", None))
        self.label_destination.setText(_translate("MainWindow", "Destination:", None))

