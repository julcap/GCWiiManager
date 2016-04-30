import sys,time
from PyQt4 import QtCore, QtGui
from GCWiiManager import *
from GWdb import *
from GCWiiMainWindow import Ui_MainWindow

class GCWii(Ui_MainWindow,QtGui.QMainWindow):
    def __init__(self):
        super(GCWii,self).__init__()
        self.setupUi(self)
        self.box='blanc-case.png'
        self.disc='blanc-disc.png'
        self.boxArtWork = os.path.join(os.getcwd(),'wii','cover3D')
        self.discArtWork = os.path.join(os.getcwd(),'wii','disc')
        self.source_btn.clicked.connect(lambda: self.populateListView('source'))
        self.destination_btn.clicked.connect(lambda: self.populateListView('destination'))
        self.export_btn.clicked.connect(lambda: self.exportAll())
        self.listView_source.clicked.connect(lambda: self.updateArtWork('source'))
        self.listView_destination.clicked.connect(lambda: self.updateArtWork('destination'))
        self.exit_btn.clicked.connect(lambda: self.quit())
        self.cancel_btn.clicked.connect(lambda:  print("Hi There"))
        self.label_boxArtWork.setPixmap(QtGui.QPixmap(str(os.path.join(self.boxArtWork,self.box))))
        self.label_dicArtWork.setPixmap(QtGui.QPixmap(str(os.path.join(self.discArtWork,self.disc))))
        self.threadCopy = ThreadCopy()
        self.threadUpdateList = ThreadUpdateList()
        self.connect(self.threadCopy, QtCore.SIGNAL('updateList'), self.populateListView)
        self.connect(self.threadCopy, QtCore.SIGNAL('updateProgressBar'), self.updateProgressBar)
        self.connect(self.threadCopy, QtCore.SIGNAL('status'), self.updateStatusLabel)
        self.progressBar_source.setVisible(False)
        self.progressBar_destination.setVisible(False)
        self.label_status.setVisible(False)
        self.checkAndPrepareDB()
        self.show()

    def updateStatusLabel(self,text,active = True):
        if text:
            self.label_status.setVisible(True)
            self.label_status.setText(text)
        else:
            self.label_status.setVisible(False)

    def msgBox(self, text, textInfo = None, type ='y/n'):
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


    def checkAndPrepareDB(self):
        msgBox = QtGui.QMessageBox()
        try:
            dbList = gameTitlesCount()
            if dbList:
                action = self.msgBox('Current local game list contains {} titles. Would you like to update it?'.format(dbList))
                if action:
                    deleteDB()
                    initDB()
                    self.threadUpdateList.start()
            else:
                action = self.msgBox('It seems there is no available game data.<br>Would you like to download it?',
                                       'If there is no data this application can not work properly.')
                if action:
                    self.threadUpdateList.start()
                else:
                    sys.exit()

        except sqlite3.OperationalError:
            initDB()
            self.checkAndPrepareDB()


    def updateProgressBar(self,progressBarName,value=0,max=0,active = True):
        if progressBarName == 'destination':
            progressBar = self.progressBar_destination
        elif progressBarName == 'source':
            progressBar = self.progressBar_source
        progressBar.setVisible(active)
        if max == 0:
            value = 0
        else:
            value = (value * 100)/max
        progressBar.setValue(value)

    def updateArtWork(self,list):
        code = self.getSelection(list)
        if code == '0000':
            box = str(os.path.join(self.boxArtWork,self.box))
            disc = str(os.path.join(self.discArtWork,self.disc))
        else:
            region = getGameRegion(code)
            disc = str(os.path.join(self.discArtWork,region,code + ".png"))
            box = str(os.path.join(self.boxArtWork,region,code + ".png"))
        self.label_boxArtWork.setPixmap(QtGui.QPixmap(box))
        self.label_dicArtWork.setPixmap(QtGui.QPixmap(disc))

    def getSelection(self,QlistViewName):
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
        Interactive Dicrectory selection
        :return: valid path
        """
        self.fileDialog = QtGui.QFileDialog.getExistingDirectory(self)
        return self.fileDialog

    def viewData(self,gamesDict):
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

    def updateSourceDBTable(self,listOfFoundFiles,listName):
        """
        Clear table for old items and update with new items
        :param listOfFoundFiles:
        :param listName:
        :return:
        """
        flushTable('gamesFound',listName)
        if listOfFoundFiles:
            for file in listOfFoundFiles:
                code = getGameCode(file)
                extension = (os.path.splitext(file))[1].lstrip('.').upper()
                gamesFoundInsert(code,file,extension,listName)

    def populateListView(self,listName,directory = None):
        """
        Populate list with the items found in a dicrectory. Update global path  and dict of files.
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
                    self.updateSourceDBTable(listOfFoundFiles,'source')
                    self.listView_source.setModel(items)
                    self.listView_source.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
                elif  listName == 'destination':
                    self.label_destination.setText('Destination: ' + directory)
                    global destinationPath
                    destinationPath = directory
                    self.updateSourceDBTable(listOfFoundFiles,'destination')
                    global destinationDict
                    destinationDict = gamesDict
                    self.listView_destination.setModel(items)
                    self.listView_source.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
            except PermissionError as err:
                self.msgBox('You do not have permission to read the source directory selected.', str(err), 'message')

    def getGamesDict(self,listOfFoundFiles = []):
        """
        Return a dictionary "code" : "Game title" for populating the list table and fetching the artworks
        """
        if listOfFoundFiles:
            gamesDict = {}
            for file in listOfFoundFiles:
                code = getGameCode(file)
                gamesDict[code] = getTitle(code)
            return gamesDict
        else:
            gamesDict = { '0000' : 'Empty'}
            return gamesDict

    def exportAll(self,listName='source'):
        """
        Start thread for copy items from one list to the other
        :return:
        """
        if listName == 'source':
            progressBar = self.progressBar_destination
        elif listName == 'destination':
            progressBar = self.progressBar_source
        if sourceDict:
            if sourcePath:
                if destinationDict:
                    self.threadCopy.start()
                else:
                    self.msgBox("Missing destination folder",None,'message')
            else:
                self.msgBox("Missing source folder",None,'message')
        else:
            self.msgBox("Missing games to copy",None,'message')

    def quit(self):
        sys.exit(0)

class ThreadCopy(QtCore.QThread):
    def __init__(self,parent = None):
        super(ThreadCopy,self).__init__(parent)

    def export(self,listName='source'):
        items = len(sourceDict)
        count = 0
        self.emit(QtCore.SIGNAL('updateProgressBar'),'destination')
        for code in sourceDict.keys():
            filePath = getPath(code,listName)
            for file in filePath:
                count += 1
                extension = (os.path.splitext(file))[1].lstrip('.').upper()
                self.emit(QtCore.SIGNAL('status'),"Exporting ../{}".format(os.path.basename(file)))
                copyFile(file,destinationPath,normalizedFolderName(code),extension,code)
                self.emit(QtCore.SIGNAL('updateProgressBar'),'destination',count,items)

        self.emit(QtCore.SIGNAL('updateProgressBar'),'destination',0,0,False)
        self.emit(QtCore.SIGNAL('status'),"")
        self.emit(QtCore.SIGNAL('updateList'),'destination',destinationPath)

    def run(self):
        self.export()

class ThreadUpdateList(QtCore.QThread):
    def __init__(self,parent = None):
        super(ThreadUpdateList,self).__init__(parent)

    def run(self):
        downloadGameList()
        populateTitleTable()

app = QtGui.QApplication(sys.argv)
main = GCWii()
sys.exit(app.exec_())


""" 
TODO:
* Input and output folder validation *
- They can not be the same directory.
- If both are empty there is nothing to do beside providing feedback.
"""




