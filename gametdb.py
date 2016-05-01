import urllib.request
import urllib.parse
import os,re

BASE_URL = 'http://www.gametdb.com'
DISC_PATH =  os.path.join(os.getcwd(),'wii','disc')
COVER3D_PATH = os.path.join(os.getcwd(),'wii','cover3D')
ART_URL = 'http://art.gametdb.com/wii'

class GameTDB():
    def __init__(self):
        self.gameList = 'wiitdb.txt'
        self.downloads = 'Wii/Downloads'

    def getGameList(self,language = 'EN'):
        gamesDict = dict()
        params =  { 'LANG' : language}
        data = urllib.parse.urlencode(params)
        data = data.encode('utf-8')
        result = urllib.request.urlopen(BASE_URL + '/' + self.gameList,data)
        for i in result:
            line = i.decode('utf-8')
            code, title = line.rstrip('\r\n').split(' = ')
            gamesDict[code] = title
        return gamesDict

    def getArtWork(self,language = None,code = None, cover3D = True, disc = True):
        """
        sample url request http://art.gametdb.com/wii/cover/US/S72E01.png
        :param language: EN, JA, FR, DE, ES, IT, NL, PT, ZHTW, ZHCN, KO
        :param code: e.g. S72E01
        :param cover3D:
        :param disc:
        :return:
        """
        if language == None or code == None:
            return 0
        else:
            try:
                if disc:
                    outputDir = os.path.join(DISC_PATH,language)
                    urllib.request.urlretrieve(ART_URL + '/disc/'+ language + '/' + code +'.png',
                                               os.path.join(outputDir,code + '.png'))
                if cover3D:
                    outputDir = os.path.join(COVER3D_PATH, language)
                    urllib.request.urlretrieve(ART_URL + '/cover3D/' + language + '/' + code + '.png',
                                               os.path.join(outputDir, code + '.png'))
            except FileNotFoundError:
                os.mkdir(outputDir)
                self.getArtWork(language,code,cover3D,disc)
            else:
                return 0


#gametdb = GameTDB()
#gamelist = gametdb.getArtWork('US','S72E01')

