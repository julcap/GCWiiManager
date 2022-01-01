from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSizePolicy


class MessageBox:
    def __init__(self):
        self.msg = QtWidgets.QMessageBox()

    def message(self, message, additional_info='', details=None):
        self.msg.setText(message + '\n\n' + additional_info)
        if details:
            self.msg.setDetailedText(details)

    def critical(self, message, additional_info='', details=None):
        self.message(message, additional_info, details)
        self.msg.setIcon(QtWidgets.QMessageBox.Critical)
        self.msg.setWindowTitle("Critical Error")
        self.msg.show()

    def warning(self, message, additional_info=''):
        self.message(message, additional_info)
        self.msg.setIcon(QtWidgets.QMessageBox.Warning)
        self.msg.setWindowTitle("Warning")
        self.msg.show()

    def info(self, message):
        self.message(message)
        self.msg.setIcon(QtWidgets.QMessageBox.Information)
        self.msg.setWindowTitle("Information")
        self.msg.show()

    def question(self, message):
        self.message(message)
        self.msg.setIcon(QtWidgets.QMessageBox.Question)
        self.msg.setWindowTitle("Question")
        self.msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        self.msg.show()
