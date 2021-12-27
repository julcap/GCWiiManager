# Library for CLI functions
import os, sys, shutil

import GWdb
import gametdb
import GCWiiManager as GCWii


class GWcli:
    def __init__(self):
        self.gc_wii_manager = GCWii.GCWiiManager()

    # Validate user input [y/n]
    def validateYN(self, message):
        a = ''
        while True:
            a = input(message + "[y/n]: ").lower()
            if a == "y" or a == "yes":
                return 1
            elif a == "n" or a == "no":
                return 0
            elif a == "e" or a == "exit":
                sys.exit(0)
            else:
                print("""Not a valid option, type "e" or "exit" to quit.""")

    # Get game path from user input
    def getGamesPath(self):
        path = ''
        while not os.path.exists(path):
            path = input("Enter games location: ")
            if not os.path.exists(path):
                print("ERROR: {} not found.".format(path))
        return path

    # Get destination folder
    def getDestPath(self):
        while True:
            path = input("Enter destination folder: ")
            if os.path.exists(path):
                return path
            else:
                a = self.validateYN("The destination folder does not exist. Would you like to create it?")
                if a:
                    os.mkdir(path)
                    return path

    def main(self):
        # Initialize DB and populate data
        gametdb.GameTDB()
        GWdb.GWdb()

        # Get location for source where to search for games
        global sourcePath
        sourcePath = self.getGamesPath()
        print("Analyzing [{}]  ...  \n\n".format(sourcePath), end='')
        try:
            files = self.gc_wii_manager.findSupportedFiles(sourcePath)
        except PermissionError as err:
            print(err)
            sys.exit(1)

        if not files:
            print("No supported files found")
            sys.exit(0)

        # Check games and put the data in the table
        counter = {}
        for extension in self.gc_wii_manager.supportedFileExtensions:
            counter[extension] = 0
        counter['found'] = 0
        for file in files:
            code = self.gc_wii_manager.getGameCode(file)
            if code:
                counter['found'] += 1
                filesplit = os.path.splitext(file)
                extension = filesplit[1].lstrip('.').upper()
                counter[extension] += 1
                db.insert('gamesFound', ('code', 'path', 'fileType', 'listName'), (code, file, extension, 'source'))
                # print("{} {} {} {}".format(counter.get('found'),code,file,extension))

        for extension in self.gc_wii_manager.supportedFileExtensions:
            if counter.get(extension):
                print("{} {} files.".format(counter.get(extension), extension))
        print("Found {} supported files".format(counter.get('found')))

        # Export files
        global destinationPath
        destinationPath = self.getDestPath()
        for extension in self.gc_wii_manager.supportedFileExtensions:
            kvext = {'fileType': extension}
            if len(db.select('gamesFound', '*', kvext)):
                count = 0
                counter[extension + '-copied'] = 0
                print("Exporting games... ")
                for row in db.select('gamesFound', '*', kvext):
                    # print(row)
                    count += 1
                    code = row[1]
                    inputFile = row[2]
                    kvcode = {'code': code}
                    title = db.select('gameTitles', '*', kvcode)[0][2]
                    folderName = self.gc_wii_manager.normalizedFolderName(title, code)
                    outputFile = self.gc_wii_manager.getOutputFilePath(inputFile, destinationPath, folderName,
                                                                       extension, code)
                    if outputFile:
                        shutil.copy2(inputFile, outputFile)
                        print("[{}/{}] '{}' '{}' '{}' exported successfully.".format(count, counter.get('found'),
                                                                                     inputFile,
                                                                                     title, code))
                        counter[extension + '-copied'] += 1
                    else:
                        print("[{}/{}] Skipping '{}' '{}'".format(count, counter.get('found'), inputFile, title))

        for extension in supportedFileExtensions:
            if counter.get(extension):
                kvext = {'fileType': extension}
                print("Exported {} {} files".format(counter.get(extension + '-copied'), extension))
                print("{} unique {} games found".format(len(db.select('gamesFound', kvext)), extension))

        print("All exported files are in '{}'".format(os.path.abspath(destinationPath)))


if __name__ == "__main__":
    cli = GWcli()
    cli.main()
