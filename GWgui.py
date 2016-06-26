import sys, time
from PyQt4 import QtCore, QtGui
from GCWiiManager import *
import GWdb2
import gametdb
from GCWiiMainWindow import Ui_MainWindow


class GCWii(Ui_MainWindow, QtGui.QMainWindow):
    def __init__(self):
        super(GCWii, self).__init__()
        self.setupUi(self)
        self.box = 'blanc-case.png'
        self.disc = 'blanc-disc.png'
        self.boxArtWork = os.path.join(os.getcwd(), 'wii', 'cover3D')
        self.discArtWork = os.path.join(os.getcwd(), 'wii', 'disc')
        self.source_btn.clicked.connect(lambda: self.populateListView('source'))
        self.destination_btn.clicked.connect(lambda: self.populateListView('destination'))
        self.export_btn.clicked.connect(lambda: self.exportAll())
        self.listView_source.clicked.connect(lambda: self.updateArtWork('source'))
        self.listView_destination.clicked.connect(lambda: self.updateArtWork('destination'))
        self.exit_btn.clicked.connect(lambda: self.quit())
        self.exportSelected_btn.clicked.connect(lambda: self.exportSelection())
        self.cancel_btn.clicked.connect(lambda: print("Hi There"))
        self.label_boxArtWork.setPixmap(QtGui.QPixmap(str(os.path.join(self.boxArtWork, self.box))))
        self.label_dicArtWork.setPixmap(QtGui.QPixmap(str(os.path.join(self.discArtWork, self.disc))))
        self.threadUpdateList = ThreadUpdateList()
        self.progressBar_fileProgress.setVisible(False)
        self.progressBar_destination.setVisible(False)
        self.label_status.setVisible(False)
        self.db = GWdb2.GWdb()
        self.gametdb = gametdb.GameTDB()
        self.show()

    def updateSourceFiles(self, filesDict):
        results = dict()
        for key in filesDict.keys():
            args = {'code': key}
            files = self.db.select('gamesFound', args)
            if len(files) > 1:
                f = list()
                f.append(files[0][2])
                f.append(files[1][2])
                results[key] = f
            else:
                results[key] = files[0][2]
        global sourceFiles
        sourceFiles = results

    def exportSelection(self, listName='source'):
        """
        :param listName:
        :return:
        Export games marked on the source list
        """
        results = dict()
        # print(sourceDict)
        for index in self.listView_source.selectedIndexes():
            title = QtCore.QModelIndex.data(index)
            for key in sourceDict.keys():
                if sourceDict[key] == title:
                    results[key] = title
        global currentSelection
        currentSelection = results
        # print(currentSelection)
        self.updateSourceFiles(results)
        self.export()

    def exportAll(self):
        global currentSelection
        currentSelection = None
        self.export()

    def updateStatusLabel(self, text, active=True):
        if text:
            self.label_status.setVisible(True)
            self.label_status.setText(text)
        else:
            self.label_status.setVisible(False)

    def msgBox(self, text, textInfo=None, type='y/n'):
        msgBox = QtGui.QMessageBox()
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

    def updateProgressBar(self, progressBarName, value=0, max=0, active=True):
        # print("DEBUG {} {} {} {} ".format(progressBarName,value,max,active))
        if progressBarName == 'destination':
            progressBar = self.progressBar_destination
        elif progressBarName == 'fileProgress':
            progressBar = self.progressBar_fileProgress
        progressBar.setVisible(active)
        if max == 0:
            value = 0
        else:
            value = (value * 100) / max
        progressBar.setValue(value)

    def updateArtWork(self, list):
        code = self.getSelection(list)
        box = str(os.path.join(self.boxArtWork, self.box))
        disc = str(os.path.join(self.discArtWork, self.disc))
        if code != '0000':
            region = getGameRegion(code)
            if (self.gametdb.getArtWork(region, code, True, None)):
                box = str(os.path.join(self.boxArtWork, region, code + ".png"))
            if (self.gametdb.getArtWork(region, code, None, True)):
                disc = str(os.path.join(self.discArtWork, region, code + ".png"))
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
            dict = sourceDict
        elif QlistViewName == 'destination':
            model = self.listView_destination.currentIndex()
            dict = destinationDict
        title = QtCore.QModelIndex.data(model)
        for code in dict:
            if dict[code] == title:
                return code

    def selectDirectory(self):
        """
        Interactive Directory selection
        :return: valid path
        """
        self.fileDialog = QtGui.QFileDialog.getExistingDirectory(self)
        return self.fileDialog

    def viewData(self, gamesDict):
        """
        Data to pass to the QlistView table
        :param gamesDict:
        :return:
        """
        itemList = []
        for code in gamesDict:
            itemList.append(gamesDict[code])
        itemList.sort()
        data = QtGui.QStringListModel(itemList)
        return data

    def updateSourceDBTable(self, listOfFoundFiles, listName):
        """
        Clear table for old items and update with new items
        :param listOfFoundFiles:
        :param listName:
        :return:
        """
        # flushTable('gamesFound',listName)
        self.db.delete(tableName='gamesFound', listName=listName)
        if listOfFoundFiles:
            for file in listOfFoundFiles:
                code = getGameCode(file)
                extension = (os.path.splitext(file))[1].lstrip('.').upper()
                # gamesFoundInsert(code,file,extension,listName)
                self.db.insert('gamesFound', ('code', 'path', 'fileType', 'listName'),
                               (code, file, extension, 'source'))

    def populateListView(self, listName, directory=None):
        """
        Populate list with the items found in a directory. Update global path  and dict of files.
        :param listName: listWidget name
        :param directory:

        """
        if directory == None:
            directory = self.selectDirectory()
        if directory:
            try:
                listOfFoundFiles = findSupportedFiles(directory)

                gamesDict = self.getGamesDict(listOfFoundFiles)
                items = self.viewData(gamesDict)
                if listName == 'source':
                    self.label_source.setText('Source: ' + directory)
                    global sourcePath
                    sourcePath = directory
                    global sourceDict
                    sourceDict = gamesDict
                    self.updateSourceDBTable(listOfFoundFiles, 'source')
                    self.listView_source.setModel(items)
                    self.listView_source.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
                elif listName == 'destination':
                    self.label_destination.setText('Destination: ' + directory)
                    global destinationPath
                    destinationPath = directory
                    self.updateSourceDBTable(listOfFoundFiles, 'destination')
                    global destinationDict
                    destinationDict = gamesDict
                    self.listView_destination.setModel(items)
                    self.listView_source.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
            except PermissionError as err:
                self.msgBox('You do not have permission to read the source directory selected.', str(err), 'message')

    def ioexchange(self):
        with open(exchange.io, WRITE) as f:
            f.writable()

    def getGamesDict(self, listOfFoundFiles=[]):
        """
        Return a dictionary "code" : "Game title" for populating the list table and fetching the artworks
        """
        if listOfFoundFiles:
            gamesDict = {}
            for file in listOfFoundFiles:
                code = getGameCode(file)
                kvcode = {'code': code}
                gamesDict[code] = self.db.select('gameTitles', kvcode)[0][2]
            return gamesDict
        else:
            gamesDict = {'0000': 'Folder is empty'}
            return gamesDict

    def export(self):
        """
        Start thread for copy items from one list to the other
        :return:
        """
        if sourceDict:
            if sourcePath:
                if destinationDict:
                    if destinationPath == sourcePath:
                        self.msgBox("Source and destination should not be the same directory.", None, 'message')
                    else:
                        self.threadCopy = ThreadCopy()
                        self.connect(self.threadCopy, QtCore.SIGNAL('updateList'), self.populateListView)
                        self.connect(self.threadCopy, QtCore.SIGNAL('updateProgressBar'), self.updateProgressBar)
                        self.connect(self.threadCopy, QtCore.SIGNAL('status'), self.updateStatusLabel)
                        self.threadCopy.start()
                else:
                    self.msgBox("Missing destination folder", None, 'message')
            else:
                self.msgBox("Missing source folder", None, 'message')
        else:
            self.msgBox("Missing games to copy", None, 'message')

    def quit(self):
        self.db.close()
        sys.exit(0)


class ThreadCopy(QtCore.QThread):
    def __init__(self, parent=None):
        super(ThreadCopy, self).__init__(parent)

    def updateFileProgress(self, progressBarName, value, max, active=True):
        # print("DEBUG: {} {} {} {} ".format(progressBarName,value,max,active))
        self.emit(QtCore.SIGNAL('updateProgressBar'), progressBarName, value, max, active)

    def export(self, listName='source'):
        if sourceFiles:
            gamesToExport = sourceFiles
            for i in sourceFiles:
                print("{} {}".format(i, sourceFiles[i]))
        else:
            gamesToExport = sourceDict
        items = len(gamesToExport)
        # print("Items " + str(items))
        count = 0
        self.emit(QtCore.SIGNAL('updateProgressBar'), 'destination')
        for code in gamesToExport.keys():
            # print("Handling {}, ... {}".format(code,gamesToExport[code]))
            # kvargs = {'code' : code,
            #          'listName' : listName}
            # print(sourceDict)
            # print(currentSelection)
            # filePath = self.db.select('gamesFound',kvargs)
            filePath = sourceFiles.get(code)
            # print("FilePATH = {}".format(filePath))
            for inputFile in filePath:
                # print(filePath)
                count += 1
                extension = (os.path.splitext(inputFile))[1].lstrip('.').upper()
                # print(sourceDict.get(code))
                # sys.exit()
                name = sourceDict.get(code)
                folderName = normalizedFolderName(name, code)
                # print(inputFile)
                self.emit(QtCore.SIGNAL('status'), "Exporting ../{}".format(os.path.basename(inputFile)))
                outputFile = getOutputFilePath(inputFile, destinationPath, folderName, extension, code)
                # print(outputFile)
                # print(destinationPath)
                # print(folderName)
                # print(extension)
                # print(code)
                if outputFile:
                    ### DEBUG ###
                    # print(filePath)
                    # print("INPUT: " + inputFile)
                    # print("OUTPUT: " + outputFile)
                    ###
                    self.threadFileProgress = ThreadUpdateFileProgress(inputFile, outputFile)
                    self.connect(self.threadFileProgress, QtCore.SIGNAL('updateFileBar'), self.updateFileProgress)
                    self.threadFileProgress.start()
                    shutil.copy2(inputFile, outputFile)
                self.emit(QtCore.SIGNAL('updateProgressBar'), 'destination', count, items)
                # while self.threadFileProgress.isRunning():
                time.sleep(0.1)

        self.emit(QtCore.SIGNAL('updateProgressBar'), 'destination', 0, 0, False)
        self.emit(QtCore.SIGNAL('status'), "")
        self.emit(QtCore.SIGNAL('updateList'), 'destination', destinationPath)

    def run(self):
        self.export()


class ThreadUpdateList(QtCore.QThread):
    def __init__(self, parent=None):
        super(ThreadUpdateList, self).__init__(parent)

    def run(self):
        titles = gametdb.GameTDB()
        titlesDict = titles.getGameList()
        if titlesDict:
            for code in titlesDict:
                gameTitlesInsert(code, titlesDict[code])


class ThreadUpdateFileProgress(QtCore.QThread):
    def __init__(self, inputFile=None, outputFile=None):
        super(ThreadUpdateFileProgress, self).__init__()
        self.inputFile = inputFile
        self.outputFile = outputFile

    def updateProgress(self):
        inputSize = os.path.getsize(self.inputFile)
        while True:
            try:
                outputSize = os.path.getsize(self.outputFile)
                self.emit(QtCore.SIGNAL('updateFileBar'), 'fileProgress', outputSize, inputSize)
                time.sleep(0.1)
                if inputSize == outputSize:
                    break
            except FileNotFoundError:
                time.sleep(0.1)
        self.emit(QtCore.SIGNAL('updateFileBar'), 'fileProgress', 0, 0, False)

    def run(self):
        self.updateProgress()


app = QtGui.QApplication(sys.argv)
main = GCWii()
sys.exit(app.exec_())
