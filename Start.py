import os
import sys
import time

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal

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
        self.source_title_list_hash_map = {}
        self.source_file_list_hash_map = {}
        self.destination_directory = ''
        self.destination_title_list_hash_map = {}
        self.box_artwork_path = os.path.join(os.getcwd(), 'images', 'cover3D')
        self.disc_artwork_path = os.path.join(os.getcwd(), 'images', 'disc')
        self.source_btn.clicked.connect(lambda: self.updateSourceList(True))
        self.destination_btn.clicked.connect(lambda: self.updateDestinationList(True))
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
            self.updateSourceList()
        if self.destination_directory:
            self.updateDestinationList()
        self.show()

    def exportSelection(self):
        """
        :param listName:
        :return:
        Export games marked on the source list
        """
        results = dict()
        for index in self.listView_source.selectedIndexes():
            title = QtCore.QModelIndex.data(index)
            for key in self.source_title_list_hash_map.keys():
                if self.source_title_list_hash_map[key] == title:
                    results[key] = title
        self.games_to_export = results
        self.export()

    def getListDifference(self, sourceList, destinationList):
        # return  [sourceList for item in sourceList if sourceList[] not in l2]
        pass

    def exportAll(self):
        self.games_to_export = self.source_title_list_hash_map
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
        msgBox.setTextFormat(QtCore.Qt.RichText)
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
            titles_dict = self.source_title_list_hash_map
        elif QlistViewName == 'destination':
            model = self.listView_destination.currentIndex()
            titles_dict = self.destination_title_list_hash_map
        title = QtCore.QModelIndex.data(model)
        for code in titles_dict:
            if titles_dict[code] == title:
                return code

    def selectDirectory(self):
        """
        Interactive Directory selection
        :return: valid path
        """
        self.fileDialog = QtWidgets.QFileDialog.getExistingDirectory(self)
        return self.fileDialog

    def getTitleList(self, games):
        """
        Data to pass to the QlistView table
        :param gamesDict:
        :return:
        """
        result = []
        for key in games:
            result.append(games[key])
        result.sort()
        return QtCore.QStringListModel(result)

    def updateSourceList(self, select=False):
        try:
            if select:
                self.source_directory = self.selectDirectory()
            if self.source_directory == '':
                return
            list_of_found_files = GCWiiManager.find_supported_files(self.source_directory)
            self.source_title_list_hash_map = GCWiiManager.generate_identifier_title_dict(list_of_found_files)
            self.label_source.setText('Source: ' + self.source_directory)
            GCWiiManager.refresh_db_source_table(list_of_found_files, 'source')
            self.listView_source.setModel(self.getTitleList(self.source_title_list_hash_map))
            self.listView_source.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
            self.source_file_list_hash_map = GCWiiManager.generate_identifier_absolute_path_dict(list_of_found_files)

        except PermissionError as err:
            self.msgBox('You do not have permission to read the source directory selected.', str(err), 'message')

    def updateDestinationList(self, select=False):
        try:
            if select:
                self.destination_directory = self.selectDirectory()
            if self.destination_directory == '':
                return
            list_of_found_files = GCWiiManager.find_supported_files(self.destination_directory)
            self.destination_title_list_hash_map = GCWiiManager.generate_identifier_title_dict(list_of_found_files)
            self.label_destination.setText('Destination: ' + self.destination_directory)
            self.destination_directory = self.destination_directory
            GCWiiManager.refresh_db_source_table(list_of_found_files, 'destination')
            self.listView_destination.setModel(self.getTitleList(self.destination_title_list_hash_map))
            self.listView_source.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        except PermissionError as err:
            self.msgBox('You do not have permission to read the source directory selected.', str(err), 'message')

    def export(self):
        """
        Start thread for copy items from one list to the other
        :return:
        """
        if not self.source_title_list_hash_map:
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
        self.worker.initialize(self.games_to_export, self.source_file_list_hash_map, self.destination_directory,
                               self.updateFileProgressBar)

        # Move worker to the thread
        self.worker.moveToThread(self.thread)

        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.progress.connect(self.updateGlobalProgressBar)
        self.worker.processing.connect(self.update_status_label)
        self.worker.finished.connect(self.updateDestinationList)
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
        self.source_file_hash_map = {}
        self.destination_directory = ''

    def initialize(self, games_to_export, source_file_hash_map, destination_directory, update_file_progress):
        self.games_to_export = games_to_export
        self.destination_directory = destination_directory
        self.source_file_hash_map = source_file_hash_map
        self.update_file_progress = update_file_progress

    def export(self):
        self._isRunning = True
        count = 0
        total = len(self.games_to_export)
        for code in self.games_to_export.keys():
            if self._isRunning:
                inputFile = self.source_file_hash_map.get(code)
                if isinstance(inputFile, list):
                    for file in inputFile:
                        self.processing.emit(file)
                        self.processFile(file, code, True)
                else:
                    self.processing.emit(inputFile)
                    self.processFile(inputFile, code)
            count += 1
            self.progress.emit(int((count * 100) / total))
            self.finished.emit()
            self.processing.emit('')
            self.threadFileProgress.quit()

    def processFile(self, inputFile, code, multidisc=False):
        extension = (os.path.splitext(inputFile))[1].lstrip('.').upper()
        name = self.games_to_export.get(code)
        folderName = GCWiiManager.get_destination_normalized_folder_name(name, code)
        outputFile = GCWiiManager.get_output_file_absolute_path(inputFile, self.destination_directory, folderName,
                                                                extension, code,
                                                                multidisc)
        GCWiiManager.create_destination_folder(outputFile)

        if outputFile:
            self.threadFileProgress = ThreadUpdateFileProgress(inputFile, outputFile)
            self.threadFileProgress.progress.connect(self.update_file_progress)
            self.threadFileProgress.start()
            GCWiiManager.copy_file(inputFile, outputFile)

    def updateFileProgress(self, progressBarName, value, max, active=True):
        self.emit(QtCore.SIGNAL('updateProgressBar'), progressBarName, value, max, active)

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
