import urllib.request
import urllib.parse
import os,re

BASE_URL = 'http://www.gametdb.com'
DISC_PATH =  os.path.join(os.getcwd(),'wii','disc')
COVER3D_PATH = os.path.join(os.getcwd(),'wii','cover3D')

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

    def getArtWorks(self,language = None, cover3D = False, disc = False):
        if language == None:
            return 0
        else:
            params = { 'LANG' : language }
            data = urllib.parse.urlencode(params)
            data = data.encode('utf-8')
            webData = urllib.request.urlopen(BASE_URL + '/' + self.downloads,data)
            if disc:
                self.getDiscArtWork(language,self.getURL('disc',language,webData))
            if cover3D:
                self.getCover3DArtWork(language,self.getURL('cover3D',language,webData))
            else:
                return 0

    def getURL(self,item,language,webData):
        for i in webData:
            result = re.findall('.+GameTDB-wii_' + item + '-' + language ,i.decode('utf-8'))
            for i in str(result).split('href=')[1:]:
                match = re.findall('.+GameTDB-wii_' + item +'-' + language +'.+', str(i.split(' ')[:1]))
                if match:
                    return str(match).strip('[\'\\]\"')

    def getDiscArtWork(self,language,URL):
        print(URL)

    def getCover3DArtWork(self,language,URL):
        print(URL)

gametdb = GameTDB()
gamelist = gametdb.getArtWorks('EN',True,True)

