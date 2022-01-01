import os
import sys
import time

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QStringListModel, QModelIndex

import GameTDBclient
from GCWiiManager import GCWiiManager
from GCWiiMainWindow import Ui_MainWindow


class GCWii(Ui_MainWindow):

    def __init__(self, source='', destination='', clear_destination=False):
        super(GCWii, self).__init__()
        app = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QtWidgets.QMainWindow()
        self.max_treads = QThread.idealThreadCount()
        self.setupUi(self.MainWindow)
        self.manager = GCWiiManager()
        self.default_box_artwork = str(os.path.join('images', 'blanc-case.png'))
        self.default_disc_artwork = str(os.path.join('images', 'blanc-disc.png'))
        self.source_directory = source
        self.source_game_collection = {}
        self.destination_directory = destination
        self.clear_destination = clear_destination
        self.destination_game_collection = {}
        self.box_artwork_path = os.path.join(os.getcwd(), 'images', 'cover3D')
        self.disc_artwork_path = os.path.join(os.getcwd(), 'images', 'disc')
        self.current_selection = {}
        self.games_to_export = {}
        self.setup_widgets()
        self.MainWindow.show()
        if self.source_directory:
            self.update_source_list()
        if self.destination_directory:
            self.update_destination_list()
        sys.exit(app.exec_())

    def setup_widgets(self):
        self.source_btn.clicked.connect(lambda: self.update_source_list(True))
        self.destination_btn.clicked.connect(lambda: self.update_destination_list(True))
        self.export_btn.clicked.connect(self.export_all)
        self.listView_source.clicked.connect(lambda: self.update_art_work('source'))
        self.listView_destination.clicked.connect(lambda: self.update_art_work('destination'))
        self.listView_destination.addAction(self.action_reload_destination)
        self.listView_destination.addAction(self.action_select_folder_destination)
        self.listView_destination.addAction(self.action_delete_selected_in_destination)
        self.listView_destination.addAction(self.action_delete_all_items_in_destination)
        self.listView_source.addAction(self.action_reload_source)
        self.listView_source.addAction(self.action_select_folder_source)
        self.exit_btn.clicked.connect(self.quit)
        self.exportSelected_btn.clicked.connect(self.export_selection)
        self.cancel_btn.clicked.connect(self.cancel_copy)
        self.label_box.setPixmap(QtGui.QPixmap(self.default_box_artwork))
        self.label_disc.setPixmap(QtGui.QPixmap(self.default_disc_artwork))
        self.progressBar_fileProgress.setVisible(False)
        self.progressBar_destination.setVisible(False)
        self.setup_actions()

    def setup_actions(self):
        # Source
        self.action_reload_source.triggered.connect(self.update_source_list)
        self.action_select_folder_source.triggered.connect(lambda: self.update_source_list(True))

        # Destination
        self.action_reload_destination.triggered.connect(self.update_destination_list)
        self.action_select_folder_destination.triggered.connect(lambda: self.update_destination_list(True))
        self.action_delete_selected_in_destination.triggered.connect(self.delete_selected_in_destination)
        self.action_delete_all_items_in_destination.triggered.connect(self.delete_all_in_destination)

    def delete_all_in_destination(self):
        self.manager.delete_all_files_in_directory(self.destination_directory)
        self.update_destination_list()

    def delete_selected_in_destination(self):
        title = self.listView_destination.currentIndex().data()
        game = self.manager.get_game_from_collection_by_title(title, self.destination_game_collection)
        self.manager.delete_all_files_in_directory(game["path"])
        self.update_destination_list()

    def export_selection(self):
        """ Export games marked on the source list_name """
        results = dict()
        for index in self.listView_source.selectedIndexes():
            title = QModelIndex.data(index)
            for key in self.source_game_collection.keys():
                if self.source_game_collection[key]["title"] == title:
                    results[key] = self.source_game_collection[key]
        self.games_to_export = results
        self.export()

    def get_list_difference(self, source_list, destination_list):
        # return  [source_list for item in source_list if source_list[] not in l2]
        pass

    def export_all(self):
        self.games_to_export = self.source_game_collection
        self.export()

    def update_status_info(self, text=None):
        if not text:
            self.MainWindow.statusBar().clearMessage()
            return self.MainWindow.statusBar().setVisible(False)
        if not self.MainWindow.statusBar().isVisible():
            self.MainWindow.statusBar().setVisible(True)
        self.MainWindow.statusBar().showMessage(text)

    def update_global_progress_bar(self, value):
        self.progressBar_destination.setValue(value)

    def update_file_progress_bar(self, value):
        self.progressBar_fileProgress.setValue(value)

    def reset_progress_bars(self):
        self.progressBar_fileProgress.setValue(0)
        self.progressBar_destination.setValue(0)

    def hide_progress_bars(self):
        self.progressBar_fileProgress.setVisible(False)
        self.progressBar_destination.setVisible(False)

    def show_progress_bars(self):
        self.progressBar_fileProgress.setVisible(True)
        self.progressBar_destination.setVisible(True)

    def update_art_work(self, list_name):
        code = self.get_selection(list_name)
        box = self.default_box_artwork
        disc = self.default_disc_artwork
        if code != '0000':
            region = self.manager.get_game_region(code)
            try:
                if GameTDBclient.get_art_work(region, code, True, None):
                    box = str(os.path.join(self.box_artwork_path, region, code + ".png"))
                if GameTDBclient.get_art_work(region, code, None, True):
                    disc = str(os.path.join(self.disc_artwork_path, region, code + ".png"))
            except GameTDBclient.ErrorFetchingData:
                print("Unable to fetch artwork for game id: '{}' region: '{}'".format(code, region))
        self.label_box.setPixmap(QtGui.QPixmap(box))
        self.label_disc.setPixmap(QtGui.QPixmap(disc))

    def get_selection(self, list_name):
        games_collection = dict()
        model = None
        if list_name == 'source':
            model = self.listView_source.currentIndex()
            games_collection = self.source_game_collection
        elif list_name == 'destination':
            model = self.listView_destination.currentIndex()
            games_collection = self.destination_game_collection
        title = QModelIndex.data(model)
        for identifier in games_collection:
            if games_collection[identifier]["title"] == title:
                return identifier

    def select_directory(self):
        return QtWidgets.QFileDialog.getExistingDirectory(self.MainWindow)

    def update_source_list(self, select=False):
        try:
            if select:
                self.source_directory = self.select_directory()
            if self.source_directory == '':
                return
            list_of_found_files = self.manager.find_supported_files(self.source_directory)
            self.source_game_collection = self.manager.generate_game_collection(list_of_found_files)
            self.label_source.setText('Source: ' + self.source_directory)
            list_of_titles = self.manager.get_sorted_game_titles(self.source_game_collection)
            self.listView_source.setModel(QStringListModel(list_of_titles))
            self.listView_source.selectionModel().selectionChanged.connect(lambda: self.update_art_work('source'))
            self.listView_source.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        except PermissionError as err:
            self.msgBox('You do not have permission to read the source directory selected.', str(err), 'message')

    def update_destination_list(self, select=False):
        try:
            if select:
                self.destination_directory = self.select_directory()
            if self.destination_directory == '':
                return
            list_of_found_files = self.manager.find_supported_files(self.destination_directory)
            self.destination_game_collection = self.manager.generate_game_collection(list_of_found_files)
            self.label_destination.setText('Destination: ' + self.destination_directory)
            self.destination_directory = self.destination_directory
            list_of_titles = self.manager.get_sorted_game_titles(self.destination_game_collection)
            self.listView_destination.setModel(QStringListModel(list_of_titles))
            self.listView_destination.selectionModel().selectionChanged.connect(
                lambda: self.update_art_work('destination'))
            self.listView_source.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        except PermissionError as err:
            self.msgBox('You do not have permission to read the source directory selected.', str(err), 'message')

    def export(self):
        if not self.source_game_collection:
            return self.msgBox("Please select source folder", None, 'message')
        if not self.source_directory:
            return self.msgBox("Please select source folder", None, 'message')
        if not self.destination_directory:
            return self.msgBox("Please select destination folder", None, 'message')
        if self.destination_directory == self.source_directory:
            return self.msgBox("Source and destination should not be the same directory.", None, 'message')
        if not self.games_to_export:
            return self.msgBox("Please select from from source list_name or click \"Export All\"", None, 'message')
        print("Processing task")
        self.show_progress_bars()

        # Create a QThread object
        self.thread = QThread()

        # Create a worker object
        self.worker = CopyWorker(self.games_to_export, self.destination_directory)

        # Move worker to the thread
        self.worker.moveToThread(self.thread)

        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.thread_file_progress.progress.connect(self.update_file_progress_bar)
        self.worker.progress.connect(self.update_global_progress_bar)
        self.worker.processing.connect(self.handle_worker_processing_update)
        self.worker.finished.connect(self.handle_worker_finished)

        self.thread.start()

    def handle_worker_processing_update(self, info=None):
        self.update_status_info(info)
        self.update_destination_list()

    def handle_worker_finished(self):
        print("Finished")
        self.update_destination_list()
        self.reset_progress_bars()
        self.hide_progress_bars()
        self.worker.quit()
        self.thread.quit()

    def quit(self):
        if self.clear_destination:
            self.manager.delete_all_files_in_directory(self.destination_directory)
        sys.exit(0)

    def cancel_copy(self):
        try:
            print("Canceling after completing current transfer\n")
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()
            self.reset_progress_bars()
            self.hide_progress_bars()
        except AttributeError as error:
            print("Nothing to cancel")


class CopyWorker(QThread):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    processing = pyqtSignal(str)

    def __init__(self, games_to_export, destination_directory):
        super(CopyWorker, self).__init__()
        self.thread_file_progress = ThreadUpdateFileProgress()
        self._is_running = False
        self.manager = GCWiiManager()
        self.games_to_export = games_to_export
        self.destination_directory = destination_directory

    def export(self):
        self._is_running = True
        count = 0
        total = len(self.games_to_export)
        for identifier in self.games_to_export.keys():
            if self._is_running:
                if isinstance(self.games_to_export[identifier]["files"], list):
                    for file in self.games_to_export[identifier]["files"]:
                        self.processing.emit(file)
                        self.process_file(file, identifier, True)
                else:
                    self.processing.emit(self.games_to_export[identifier]["files"])
                    self.process_file(self.games_to_export[identifier]["files"], identifier, False)
            count += 1
            self.progress.emit(int((count * 100) / total))
            time.sleep(0.5)
        self.thread_file_progress.quit()
        self.processing.emit('')
        self.finished.emit()

    def process_file(self, input_file, identifier, multidisc=False):
        extension = (os.path.splitext(input_file))[1].lstrip('.').upper()
        game = self.games_to_export.get(identifier)
        folder_name = self.manager.get_destination_normalized_folder_name(game["title"], identifier)
        output_file = self.manager.get_output_file_absolute_path(input_file, self.destination_directory, folder_name,
                                                                 extension, identifier,
                                                                 multidisc)
        self.manager.create_destination_folder(output_file)

        if output_file:
            self.thread_file_progress.initialize(input_file, output_file)
            self.thread_file_progress.start()
            self.manager.copy_file(input_file, output_file)

    def stop(self):
        self._is_running = False

    def run(self):
        self.export()


class ThreadUpdateFileProgress(QThread):
    count = 0
    progress = pyqtSignal(int)

    def __init__(self):
        super(ThreadUpdateFileProgress, self).__init__()
        ThreadUpdateFileProgress.count += 1
        print("Number of file progress threads ", ThreadUpdateFileProgress.count)
        self.input_file = None
        self.output_file = None

    def __del__(self):
        print("Number of file progress threads ", ThreadUpdateFileProgress.count)
        ThreadUpdateFileProgress.count -= 1

    def initialize(self, input_file=None, output_file=None):
        self.input_file = input_file
        self.output_file = output_file

    def run(self):
        input_size = os.path.getsize(self.input_file)
        while True:
            try:
                output_size = os.path.getsize(self.output_file)
                self.progress.emit(int((output_size * 100) / input_size))
                time.sleep(0.2)
                if input_size == output_size:
                    break
            except FileNotFoundError:
                time.sleep(0.2)
        self.progress.emit(0)


class ThreadDownload(QThread):
    def __init__(self, job=None):
        super(ThreadDownload, self).__init__()
        self.job = job

    def run(self):
        self.job()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        print("WARNING: All items in the destination directory will be deleted on 'Exit'!")
        GCWii('/home/jca/games', '/home/jca/converted', clear_destination=True)
    else:
        GCWii()
