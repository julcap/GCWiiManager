# A Gamecube/Wii backup manager
#
# Julian Capilla
# lyhan_jr@hotmail.com

import re, os
import filecmp


class GCWiiManager:
    supportedFileExtensions = ('ISO', 'WBFS')

    @staticmethod
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
    @staticmethod
    def supportedExtension(filename):
        """ @filename: absolute path to file
            @extension: list of extensions """
        for extension in GCWiiManager.supportedFileExtensions:
            if filename.lower().endswith(extension.lower()):
                return 1
        return 0

    @staticmethod
    def getBiteChunk(file, size):
        f = open(file, 'rb')
        data = f.read(size)
        f.close()
        return data

    @staticmethod
    def getGameCode(file):
        code = re.search(b'[A-Z0-9]{6}', GCWiiManager.getBiteChunk(file, 1024))
        if code:
            return code.group(0).decode('ascii')
        else:
            return 0

    @staticmethod
    def getDiskNumber(file):
        data = GCWiiManager.getBiteChunk(file, 1024)
        match = re.search(b'[A-Z0-9]{6}', data)
        return int(data[match.span()[1]]) + 1

    @staticmethod
    def findSupportedFiles(path):
        """@path: directory where to search"""
        files = []
        directories = []
        for item in os.listdir(path):
            file = os.path.join(path, item)
            if os.path.isdir(file):
                directories.append(item)
            if os.path.isfile(file) and GCWiiManager.supportedExtension(file):
                if GCWiiManager.getGameCode(file):
                    files.append(file)
        for directory in directories:
            directory = os.path.join(path, directory)
            for file in os.listdir(directory):
                file = os.path.join(directory, file)
                if os.path.isfile(file) and GCWiiManager.supportedExtension(file):
                    if GCWiiManager.getGameCode(file):
                        files.append(file)
        if files:
            return files
        else:
            return 0

    @staticmethod
    def checkDuplicate(file1, file2):
        if filecmp.cmp(file1, file2):
            return 1
        else:
            return 0

    @staticmethod
    def getFileName(source):
        return os.path.split(source)[1].split('.')[0].lower()

    @staticmethod
    def getOutputFilePath(inputFile, destination, folderName, fileExtension, gameCode, multidisc):
        print("*****************\n"
              "inputFile:\t'{}'\n"
              "destination:\t'{}'\n"
              "folderName:\t'{}'\n"
              "fileExtension:\t'{}'\n"
              "gameCode:\t'{}'\n"
              "multidisc:\t'{}'\n"
              "*****************\n".format(inputFile, destination, folderName, fileExtension, gameCode, multidisc))
        file_name = GCWiiManager.getFileName(inputFile)
        if fileExtension == 'ISO':
            if multidisc:
                disc = GCWiiManager.getDiskNumber(inputFile)
                if disc == 1:
                    file_name = 'game'
                elif disc == 2:
                    file_name = 'disc2'
        elif fileExtension == 'WBFS':
            file_name = gameCode
        output_file = os.path.join(destination, folderName, file_name + '.' + fileExtension.lower())
        if not os.path.exists(destination):
            os.mkdir(destination)
        if not os.path.exists(os.path.join(destination, folderName)):
            os.mkdir(os.path.join(destination, folderName))
        if not os.path.exists(output_file):
            return output_file
        else:
            if not GCWiiManager.checkDuplicate(inputFile, output_file) and fileExtension == 'ISO':
                file_name = 'disc2'
                output_file = os.path.join(destination, folderName, file_name + '.' + fileExtension.lower())
                if os.path.exists(output_file):
                    if GCWiiManager.checkDuplicate(inputFile, output_file):
                        return 0
                else:
                    return output_file
            else:
                return 0

    @staticmethod
    def normalizedFolderName(name, code):
        name = re.findall('[A-Za-z0-9 \'\-!?\(\)\.é]', name)
        name = ''.join(name)
        return name + " [" + code + "]"
