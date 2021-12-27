import urllib.request, urllib.parse, urllib.error
import os

BASE_URL = 'http://www.gametdb.com'
DISC_PATH = os.path.join(os.getcwd(), 'wii', 'disc')
COVER3D_PATH = os.path.join(os.getcwd(), 'wii', 'cover3D')
ART_URL = 'http://art.gametdb.com/wii'


class GameTDB():
    def __init__(self):
        self.gameList = 'wiitdb.txt'

    def getGameList(self, language='EN'):
        gamesDict = dict()
        params = {'LANG': language}
        try:
            data = urllib.parse.urlencode(params)
            data = data.encode('utf-8')
            result = urllib.request.urlopen(BASE_URL + '/' + self.gameList, data)
        except urllib.error.URLError as e:
            # TODO: Update label to provide error connecting to server.
            return 0
        for i in result:
            line = i.decode('utf-8')
            code, title = line.rstrip('\r\n').split(' = ')
            gamesDict[code] = title
        return gamesDict

    def getArtWork(self, language=None, code=None, cover3D=True, disc=True):
        """
        Sample url request http://art.gametdb.com/wii/cover/US/S72E01.png
        :param language: EN, JA, FR, DE, ES, IT, NL, PT, ZHTW, ZHCN, KO
        :param code: Game id (e.g. S72E01)
        :param cover3D: Boolean
        :param disc: Boolean
        :return: either nothing or 0.
        """
        if language == None or code == None:
            return 0
        else:
            try:
                status = 0
                if disc:
                    outputDir = os.path.join(DISC_PATH, language)
                    if not os.path.exists(outputDir):
                        os.mkdir(outputDir)
                    outputFile = os.path.join(outputDir, code + '.png')
                    if not os.path.exists(outputFile):
                        urllib.request.urlretrieve(ART_URL + '/disc/' + language + '/' + code + '.png', outputFile)
                    status = 1
                if cover3D:
                    outputDir = os.path.join(COVER3D_PATH, language)
                    if not os.path.exists(outputDir):
                        os.mkdir(outputDir)
                    outputFile = os.path.join(outputDir, code + '.png')
                    if not os.path.exists(outputFile):
                        urllib.request.urlretrieve(ART_URL + '/cover3D/' + language + '/' + code + '.png', outputFile)
                    status = 1
                return status
            # Report error if there is no connection to the internet.
            except urllib.error.URLError as e:
                # TODO: Update label to inform internet connection problems
                return 0

# gametdb = GameTDB()
# gamelist = gametdb.getArtWork('US','S72E01')
