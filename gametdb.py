import urllib.request
import urllib.parse
import os

BASE_URL = 'http://www.gametdb.com'
DISC_PATH =  os.path.join(os.getcwd(),'wii','disc')
COVER3D_PATH = os.path.join(os.getcwd(),'wii','cover3D')

class GameTDB():
    def __init__(self):
        self.gameList = 'wiitdb.txt'

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

    def getArtWorks(self,language = None, cover3D = False, disc = False):
        if language == None:
            return 0
        else:
            if disc:
                self.getDiscArtWork(language)
            elif cover3D:
                self.getCover3DArtWork(language)
            else:
                return 0

    def getDiscArtWork(self,language):
        pass

    def getCover3DArtWork(self,language):
        pass




gametdb = GameTDB()
gamelist = gametdb.getGameList()
print(len(gamelist.items()))
