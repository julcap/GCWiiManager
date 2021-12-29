import os
import sys
import time

from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QStringListModel, QModelIndex

import GCWiiManager
import GameTDBclient
from GCWiiMainWindow import Ui_MainWindow


class GCWii(Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self):
        super(GCWii, self).__init__()
        self.setupUi(self)
        self.default_box_artwork = str(os.path.join('images', 'blanc-case.png'))
        self.default_disc_artwork = str(os.path.join('images', 'blanc-disc.png'))
        self.source_directory = ''
        self.source_game_collection = {}
        self.destination_directory = ''
        self.destination_game_collection = {}
        self.box_artwork_path = os.path.join(os.getcwd(), 'images', 'cover3D')
        self.disc_artwork_path = os.path.join(os.getcwd(), 'images', 'disc')
        self.source_btn.clicked.connect(lambda: self.update_source_list(True))
        self.destination_btn.clicked.connect(lambda: self.update_destination_list(True))
        self.export_btn.clicked.connect(lambda: self.exportAll())
        self.listView_source.clicked.connect(lambda: self.updateArtWork('source'))
        self.listView_destination.clicked.connect(lambda: self.updateArtWork('destination'))
        self.exit_btn.clicked.connect(lambda: self.quit())
        self.exportSelected_btn.clicked.connect(lambda: self.exportSelection())
        self.cancel_btn.clicked.connect(lambda: self.cancel_copy())
        self.label_boxArtWork.setPixmap(QtGui.QPixmap(self.default_box_artwork))
        self.label_dicArtWork.setPixmap(QtGui.QPixmap(self.default_disc_artwork))
        self.progressBar_fileProgress.setVisible(False)
        self.progressBar_destination.setVisible(False)
        self.label_status.setVisible(False)
        self.current_selection = {}
        self.games_to_export = {}
        if self.source_directory:
            self.update_source_list()
        if self.destination_directory:
            self.update_destination_list()
        self.show()

    def exportSelection(self):
        """
        :param listName:
        :return:
        Export games marked on the source list
        """
        results = dict()
        for index in self.listView_source.selectedIndexes():
            title = QModelIndex.data(index)
            for key in self.source_game_collection.keys():
                if self.source_game_collection[key]["title"] == title:
                    results[key] = self.source_game_collection[key]
        self.games_to_export = results
        self.export()

    def getListDifference(self, sourceList, destinationList):
        # return  [sourceList for item in sourceList if sourceList[] not in l2]
        pass

    def exportAll(self):
        self.games_to_export = self.source_game_collection
        self.export()

    def update_status_label(self, text=''):
        if text:
            self.label_status.setVisible(True)
            self.label_status.setText(text)
        else:
            self.label_status.setVisible(False)

    def msgBox(self, text, textInfo=None, type='y/n'):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText(text)
        if textInfo:
            msgBox.setInformativeText(textInfo)
        msgBox.setTextFormat(Qt.RichText)
        if type == 'y/n':
            msgBox.setStandardButtons(msgBox.Yes | msgBox.No)
            result = msgBox.exec_()
            if result == msgBox.Yes:
                return 1
            elif result == msgBox.No:
                return 0
        else:
            msgBox.exec_()

    def updateProgressBar(self, progress_bar_name, value=0, max=0, active=True):
        bar = None
        if progress_bar_name == 'destination':
            bar = self.progressBar_destination
        elif progress_bar_name == 'fileProgress':
            bar = self.progressBar_fileProgress
        bar.setVisible(active)
        if max == 0:
            value = 0
        else:
            value = (value * 100) / max
        bar.setValue(value)

    def updateGlobalProgressBar(self, value):
        self.progressBar_destination.setValue(value)

    def updateFileProgressBar(self, value):
        self.progressBar_fileProgress.setValue(value)

    def resetProgressBars(self):
        self.progressBar_fileProgress.setValue(0)
        self.progressBar_destination.setValue(0)

    def hideProgressBars(self):
        self.progressBar_fileProgress.setVisible(False)
        self.progressBar_destination.setVisible(False)

    def showProgressBars(self):
        self.progressBar_fileProgress.setVisible(True)
        self.progressBar_destination.setVisible(True)

    def updateArtWork(self, list):
        code = self.getSelection(list)
        box = self.default_box_artwork
        disc = self.default_disc_artwork
        if code != '0000':
            region = GCWiiManager.get_game_region(code)
            try:
                if GameTDBclient.get_art_work(region, code, True, None):
                    box = str(os.path.join(self.box_artwork_path, region, code + ".png"))
                if GameTDBclient.get_art_work(region, code, None, True):
                    disc = str(os.path.join(self.disc_artwork_path, region, code + ".png"))
            except GameTDBclient.ErrorFetchingData:
                print("Unable to fetch artwork for game id: '{}' region: '{}'".format(code, region))
        self.label_boxArtWork.setPixmap(QtGui.QPixmap(box))
        self.label_dicArtWork.setPixmap(QtGui.QPixmap(disc))

    def getSelection(self, QlistViewName):
        """
        Return the code of the game from the list iterating through dictionary
        :param QlistViewName:
        :return:
        """
        if QlistViewName == 'source':
            model = self.listView_source.currentIndex()
            games_collection = self.source_game_collection
        elif QlistViewName == 'destination':
            model = self.listView_destination.currentIndex()
            games_collection = self.destination_game_collection
        title = QModelIndex.data(model)
        for identifier in games_collection:
            if games_collection[identifier]["title"] == title:
                return identifier

    def selectDirectory(self):
        """
        Interactive Directory selection
        :return: valid path
        """
        self.fileDialog = QtWidgets.QFileDialog.getExistingDirectory(self)
        return self.fileDialog

    def update_source_list(self, select=False):
        try:
            if select:
                self.source_directory = self.selectDirectory()
            if self.source_directory == '':
                return
            list_of_found_files = GCWiiManager.find_supported_files(self.source_directory)
            self.source_game_collection = GCWiiManager.generate_game_collection(list_of_found_files)
            self.label_source.setText('Source: ' + self.source_directory)
            GCWiiManager.refresh_db_source_table(list_of_found_files, 'source')
            list_of_titles = GCWiiManager.get_sorted_game_titles(self.source_game_collection)
            self.listView_source.setModel(QStringListModel(list_of_titles))
            selection_model = self.listView_source.selectionModel()
            selection_model.selectionChanged.connect(lambda: self.updateArtWork('source'))

            self.listView_source.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        except PermissionError as err:
            self.msgBox('You do not have permission to read the source directory selected.', str(err), 'message')

    def update_destination_list(self, select=False):
        try:
            if select:
                self.destination_directory = self.selectDirectory()
            if self.destination_directory == '':
                return
            list_of_found_files = GCWiiManager.find_supported_files(self.destination_directory)
            self.destination_game_collection = GCWiiManager.generate_game_collection(list_of_found_files)
            self.label_destination.setText('Destination: ' + self.destination_directory)
            self.destination_directory = self.destination_directory
            GCWiiManager.refresh_db_source_table(list_of_found_files, 'destination')
            list_of_titles = GCWiiManager.get_sorted_game_titles(self.destination_game_collection)
            self.listView_destination.setModel(QStringListModel(list_of_titles))
            selection_model = self.listView_destination.selectionModel()
            selection_model.selectionChanged.connect(lambda: self.updateArtWork('destination'))
            self.listView_source.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        except PermissionError as err:
            self.msgBox('You do not have permission to read the source directory selected.', str(err), 'message')

    def export(self):
        """
        Start thread for copy items from one list to the other
        :return:
        """
        if not self.source_game_collection:
            return self.msgBox("Please select source folder", None, 'message')
        if not self.source_directory:
            return self.msgBox("Please select source folder", None, 'message')
        if not self.destination_directory:
            return self.msgBox("Please select destination folder", None, 'message')
        if self.destination_directory == self.source_directory:
            return self.msgBox("Source and destination should not be the same directory.", None, 'message')
        if not self.games_to_export:
            return self.msgBox("Please select from from source list or click \"Export All\"", None, 'message')
        self.showProgressBars()

        # Create a QThread object
        self.thread = QThread()

        # Create a worker object
        self.worker = CopyWorker()
        self.worker.initialize(self.games_to_export, self.destination_directory, self.updateFileProgressBar)

        # Move worker to the thread
        self.worker.moveToThread(self.thread)

        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.progress.connect(self.updateGlobalProgressBar)
        self.worker.processing.connect(self.update_status_label)
        self.worker.finished.connect(self.update_destination_list)
        self.thread.finished.connect(self.resetProgressBars)
        self.thread.finished.connect(self.hideProgressBars)

        self.thread.start()

    def quit(self):
        GCWiiManager.quit()
        sys.exit(0)

    def cancel_copy(self):
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()
        self.resetProgressBars()
        self.hideProgressBars()


class CopyWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    processing = pyqtSignal(str)

    def __init__(self, parent=None):
        super(CopyWorker, self).__init__(parent)
        self._isRunning = False
        self.games_to_export = {}
        self.update_global_progress = {}
        self.update_file_progress = {}
        self.destination_directory = ''

    def initialize(self, games_to_export, destination_directory, update_file_progress):
        self.games_to_export = games_to_export
        self.destination_directory = destination_directory
        self.update_file_progress = update_file_progress

    def export(self):
        self._isRunning = True
        count = 0
        total = len(self.games_to_export)
        for identifier in self.games_to_export.keys():
            if self._isRunning:
                if isinstance(self.games_to_export[identifier]["files"], list):
                    for file in self.games_to_export[identifier]["files"]:
                        self.processing.emit(file)
                        self.processFile(file, identifier, True)
                else:
                    self.processing.emit(self.games_to_export[identifier]["files"])
                    self.processFile(self.games_to_export[identifier]["files"], identifier)
            count += 1
            self.progress.emit(int((count * 100) / total))
            self.finished.emit()
            self.processing.emit('')
            self.threadFileProgress.quit()

    def processFile(self, inputFile, identifier, multidisc=False):
        extension = (os.path.splitext(inputFile))[1].lstrip('.').upper()
        game = self.games_to_export.get(identifier)
        folder_name = GCWiiManager.get_destination_normalized_folder_name(game["title"], identifier)
        output_file = GCWiiManager.get_output_file_absolute_path(inputFile, self.destination_directory, folder_name,
                                                                 extension, identifier,
                                                                 multidisc)
        GCWiiManager.create_destination_folder(output_file)

        if output_file:
            self.threadFileProgress = ThreadUpdateFileProgress(inputFile, output_file)
            self.threadFileProgress.progress.connect(self.update_file_progress)
            self.threadFileProgress.start()
            GCWiiManager.copy_file(inputFile, output_file)

    def updateFileProgress(self, progress_bar_name, value, total, active=True):
        self.emit(QtCore.SIGNAL('updateProgressBar'), progress_bar_name, value, total, active)

    def stop(self):
        self._isRunning = False

    def run(self):
        self.export()


class ThreadUpdateFileProgress(QtCore.QThread):
    progress = pyqtSignal(int)

    def __init__(self, inputFile=None, outputFile=None):
        super(ThreadUpdateFileProgress, self).__init__()
        self.inputFile = inputFile
        self.outputFile = outputFile

    def updateProgress(self):
        inputSize = os.path.getsize(self.inputFile)
        while True:
            try:
                outputSize = os.path.getsize(self.outputFile)
                self.progress.emit(int((outputSize * 100) / inputSize))
                time.sleep(0.1)
                if inputSize == outputSize:
                    break
            except FileNotFoundError:
                time.sleep(0.1)
        self.progress.emit(0)

    def run(self):
        self.updateProgress()


app = QtWidgets.QApplication(sys.argv)
main = GCWii()
sys.exit(app.exec_())
