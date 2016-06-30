# A Gamecube/Wii backup manager
# Just for fun
#
# Julian Capilla-krumbak
# lyhan_jr@hotmail.com

import sys, os
import re
import gametdb
import shutil
import filecmp
from GWcli import *
import GWdb


# Some globals
gameList = 'wiitdb.txt'
URL = 'http://www.gametdb.com/wiitdb.txt?LANG=EN'
supportedFileExtensions = ('ISO','WBFS')
sourcePath = ''
sourceDict = {}
destinationPath = ''
destinationDict = {}
sourceFiles = {}

READ = 'r'
BINARY = 'b'
WRITE = 'w'


def getGameRegion(code):
    """
    A 	41 	All regions. System channels like the Mii channel use it.
    B 	42 	Used by some WiiWare / Virtual Console titles.
    D 	44 	German-speaking regions. Only if separate versions exist, e.g. Zelda: A Link to the Past
    E 	45 	USA and other NTSC regions except Japan
    F 	46 	French-speaking regions. Only if separate versions exist, e.g. Zelda: A Link to the Past.
    I 	49 	Italian-speaking regions. Only if separate versions exist, e.g. Pokemon Snap. Unofficially used by The Homebrew Channel 1.0.5 and newer.
    J 	4A 	Japan
    K 	4B 	Korea. Unofficially used by DVDX 2.0.
    L 	4C 	Japanese Import to Europe, Australia and other PAL regions
    M 	4D 	American Import to Europe, Australia and other PAL regions
    N 	4E 	Japanese Import to USA and other NTSC regions
    P 	50 	Europe, Australia and other PAL regions
    Q 	51 	Korea with Japanese language.
    S 	53 	Spanish-speaking regions. Only if separate versions exist, e.g. Pokemon Snap
    T 	54 	Korea with English language.
    U 	55 	Used by some WiiWare / Virtual Console titles.
    X 	58 	Used by some WiiWare / Virtual Console titles. Also used by DVDX 1.0 and The Homebrew Channel versions 1.0.4 and earlier.
    """
    region = { 'A' : '',
                'B' : '',
                'D' : 'DE',
                'E' : 'US',
                'F' : 'FR',
                'I' : 'IT',
                'J' : 'JA',
                'K' : 'KO',
                'L' : '',
                'M' : '',
                'N' : '',
                'P' : '',
                'Q' : '',
                'S' : 'ES',
                'T' : '',
                'U' : '',
                'X' : ''
                 }
    if region.get(list(code)[3]):
        return region.get(list(code)[3])
    else: return 'EN'

#def populateTitlesTable(titlesDict):
#    flushTable('gameTitles',None)
#    for code in titlesDict:
#        gameTitlesInsert(code,titlesDict[code])

# Check supported file extensions
def supportedExtension(filename):
    """ @filename: absolute path to file
        @extension: list of extensions """
    for extension in supportedFileExtensions:
        if filename.lower().endswith(extension.lower()):
            return 1
    return 0

# def getTitle(code):
#     conn = connectDB()
#     qry = 'SELECT title FROM gameTitles WHERE code="{}"'.format(code)
#     conn.execute(qry)
#     results = conn.fetchall()
#     conn.close()
#     return results[0][0]

def getGameCode(file):
    f = open(file, READ + BINARY)
    data = f.read(1024)
    f.close()
    code = re.search(b'[A-Z0-9]{6}',data)
    if code:
        return code.group(0).decode('ascii')
    else:
        return 0

def findSupportedFiles(path):
    """@path: directory where to search"""
    files = []
    directories = []
    for item in os.listdir(path):
        file = os.path.join(path,item)
        if os.path.isdir(file):
            directories.append(item)
        if os.path.isfile(file) and supportedExtension(file):
            if getGameCode(file):
                files.append(file)
    for directory in directories:
        directory = os.path.join(path,directory)
        for file in os.listdir(directory):
            file = os.path.join(directory,file)
            if os.path.isfile(file) and supportedExtension(file):
                if getGameCode(file):
                    files.append(file)
    if files:
        return files
    else:
        return 0



def checkDuplicate(file1,file2):
    if filecmp.cmp(file1,file2):
        return 1
    else:
        return 0

def getFileName(source):
    return os.path.split(source)[1].split('.')[0].lower()


def getOutputFilePath(inputFile, destination, folderName, fileExtension, gameCode):
    fileName = getFileName(inputFile)
    if fileExtension == 'ISO':
        if fileName != 'disc2':
            fileName = 'game'
    elif fileExtension == 'WBFS':
        fileName = gameCode
    outputFile = os.path.join(destination,folderName,fileName + '.' + fileExtension.lower())
    if not os.path.exists(destination):
        os.mkdir(destination)
    if not os.path.exists(os.path.join(destination,folderName)):
        os.mkdir(os.path.join(destination,folderName))
        #print(outputFile)
    if not os.path.exists(outputFile):
        # print("Copying {} to {}".format(inputFile,outputFile))
        #shutil.copy2(inputFile, outputFile)
        return outputFile
    else:
        if not checkDuplicate(inputFile, outputFile) and fileExtension == 'ISO':
            fileName = 'disc2'
            outputFile = os.path.join(destination,folderName,fileName + '.' + fileExtension.lower())
            #print("Output File: {}".format(outputFile))
            if os.path.exists(outputFile):
                if checkDuplicate(inputFile, outputFile):
                    return 0
            else:
                print("Copying {} to {}".format(inputFile, outputFile))
                #shutil.copy2(inputFile, outputFile)
                return outputFile
        else:
            #print("Skipping {}".format(inputFile))
            return 0
    
def normalizedFolderName(name, code):
    name = re.findall('[A-Za-z0-9 \'\-!?\(\)\.é]',name)
    name = ''.join(name)
    return name + " [" + code + "]"

def main():
    connectionTDB = gametdb.GameTDB()
    db = GWdb.GWdb()
    titles = len(db.select('gameTitles'))

    # Get location for source where to search for games
    global sourcePath
    sourcePath = getGamesPath()
    print("Analyzing [{}]  ...  \n\n".format(sourcePath), end = '')
    try:
        files = findSupportedFiles(sourcePath)
    except PermissionError as err:
        print(err)
        sys.exit(1)

    if not files:
        print("No supported files found")
        sys.exit(0)
        
    # Check games and put the data in the table
    found = 0
    counter = {}
    for extension in supportedFileExtensions:
        counter[extension] = 0
    counter['found'] = 0
    for file in files:
        code = getGameCode(file)
        if code:
            counter['found'] += 1
            filesplit = os.path.splitext(file)
            extension = filesplit[1].lstrip('.').upper()
            counter[extension] += 1
            db.insert('gamesFound',('code','path','fileType','listName'),(code,file,extension,'source'))
            #print("{} {} {} {}".format(counter.get('found'),code,file,extension))   

    for extension in supportedFileExtensions:
        if counter.get(extension):
            print("{} {} files.".format(counter.get(extension),extension))
    print("Found {} supported files".format(counter.get('found')))
    
    # Export files
    global destinationPath
    destinationPath = getDestPath()
    for extension in supportedFileExtensions:
        kvext = {'fileType' : extension }
        if len(db.select('gamesFound',kvext)):
            count = 0
            counter[extension + '-copied'] = 0
            print("Exporting games... ")
            for row in db.select('gamesFound',kvext):
                #print(row)
                count += 1
                code = row[1]
                inputFile = row[2]
                kvcode = {'code' : code }
                title = db.select('gameTitles',kvcode)[0][2]
                folderName = normalizedFolderName(title,code)
                outputFile = getOutputFilePath(inputFile, destinationPath, folderName, extension, code)
                if outputFile:
                    shutil.copy2(inputFile, outputFile)
                    print("[{}/{}] '{}' '{}' '{}' exported successfully.".format(count,counter.get('found'),inputFile,title,code))
                    counter[extension + '-copied'] += 1
                else:
                    print("[{}/{}] Skipping '{}' '{}'".format(count,counter.get('found'),inputFile,title))
                                               
    for extension in supportedFileExtensions:
        if counter.get(extension):
            kvext = {'fileType' : extension }
            print("Exported {} {} files".format(counter.get(extension + '-copied'),extension))
            print("{} unique {} games found".format(len(db.select('gamesFound',kvext)),extension))

    print("All exported files are in '{}'".format(os.path.abspath(destinationPath)))

if __name__ == "__main__":
    main()

