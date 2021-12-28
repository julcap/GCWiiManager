# A Gamecube/Wii backup manager
#
# Julian Capilla
# lyhan_jr@hotmail.com

import re, os
import filecmp

from GWdb import GWdb

supportedFileExtensions = ('ISO', 'WBFS')


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
    region = {'A': '',
              'B': '',
              'D': 'DE',
              'E': 'US',
              'F': 'FR',
              'I': 'IT',
              'J': 'JA',
              'K': 'KO',
              'L': '',
              'M': '',
              'N': '',
              'P': '',
              'Q': '',
              'S': 'ES',
              'T': '',
              'U': '',
              'X': ''
              }
    if region.get(list(code)[3]):
        return region.get(list(code)[3])
    else:
        return 'EN'


# Check supported file extensions
def supportedExtension(filename):
    """ @filename: absolute path to file
        @extension: list of extensions """
    for extension in supportedFileExtensions:
        if filename.lower().endswith(extension.lower()):
            return 1
    return 0


def getBiteChunk(file, size):
    f = open(file, 'rb')
    data = f.read(size)
    f.close()
    return data


def getGameCode(file):
    code = re.search(b'[A-Z0-9]{6}', getBiteChunk(file, 1024))
    if code:
        return code.group(0).decode('ascii')
    else:
        return 0


def getDiskNumber(file):
    data = getBiteChunk(file, 1024)
    match = re.search(b'[A-Z0-9]{6}', data)
    return int(data[match.span()[1]]) + 1


def findSupportedFiles(path):
    """@path: directory where to search"""
    files = []
    directories = []
    for item in os.listdir(path):
        file = os.path.join(path, item)
        if os.path.isdir(file):
            directories.append(item)
        if os.path.isfile(file) and supportedExtension(file):
            if getGameCode(file):
                files.append(file)
    for directory in directories:
        directory = os.path.join(path, directory)
        for file in os.listdir(directory):
            file = os.path.join(directory, file)
            if os.path.isfile(file) and supportedExtension(file):
                if getGameCode(file):
                    files.append(file)
    if files:
        return files
    else:
        return 0


def checkDuplicate(file1, file2):
    if filecmp.cmp(file1, file2):
        return 1
    else:
        return 0


def parseFileList(listOfFoundFiles=[]):
    """
    Return a dictionary "code" : "Game title" for populating the list table and fetching the artworks
    """
    if not listOfFoundFiles:
        return {'0000': 'Folder is empty'}
    result = {}
    for file in listOfFoundFiles:
        key = getGameCode(file)
        db = GWdb()
        kvcode = {'code': key}
        result[key] = db.select('gameTitles', '*', kvcode)[0][2]
    return result


def parseSourceList(listOfFoundFiles=[]):
    """
    Return a dictionary "code" : "/Absolut/file/path"
    """
    if not listOfFoundFiles:
        return {'0000': 'Folder is empty'}

    result = {}
    for file in listOfFoundFiles:
        key = getGameCode(file)
        db = GWdb()
        kvcode = {'code': key}
        data = db.select('gamesFound', '*', kvcode)
        if len(data) > 1:
            result[key] = [data[0][2], data[1][2]]
        else:
            result[key] = data[0][2]
    return result


def updateSourceDBTable(listOfFoundFiles, listName):
    """
    Clear table for old items and update with new items
    :param listOfFoundFiles:
    :param listName:
    :return:
    """
    # flushTable('gamesFound',listName)
    db = GWdb()
    db.delete(tableName='gamesFound', listName=listName)
    if listOfFoundFiles:
        for file in listOfFoundFiles:
            code = getGameCode(file)
            extension = (os.path.splitext(file))[1].lstrip('.').upper()
            # gamesFoundInsert(code,file,extension,listName)
            db.insert('gamesFound', ('code', 'path', 'fileType', 'listName'),
                      (code, file, extension, 'source'))


def get_output_file_absolute_path(input_file, destination, folder_name, file_extension, game_code, multi_disc):
    print("*****************\n"
          "input_file:\t'{}'\n"
          "destination:\t'{}'\n"
          "folder_name:\t'{}'\n"
          "file_extension:\t'{}'\n"
          "game_code:\t'{}'\n"
          "multidisc:\t'{}'\n"
          "*****************\n".format(input_file, destination, folder_name, file_extension, game_code, multi_disc))
    file_name = ''
    if file_extension == 'ISO':
        if multi_disc:
            disc = getDiskNumber(input_file)
            if disc == 1:
                file_name = 'game'
            elif disc == 2:
                file_name = 'disc2'
        else:
            file_name = 'game'
    elif file_extension == 'WBFS':
        file_name = game_code
    return os.path.join(destination, folder_name, file_name + '.' + file_extension.lower())


def create_destination_folder(absolute_path):
    path = os.path.dirname(absolute_path)
    if not os.path.exists(path):
        os.mkdir(path)


def get_destination_normalized_folder_name(game_title, identifier):
    name = re.findall('[A-Za-z0-9 \'\-!?\(\)\.é]', game_title)
    name = ''.join(name)
    return name + " [" + identifier + "]"
