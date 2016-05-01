import urllib.request
import urllib.parse

BASE_URL = 'http://www.gametdb.com/wiitdb.txt'

class GameTDB():
    def __init__(self):
        self.gameList = 'wiitdb.txt'

    def getGameList(self,language = 'EN'):
        gamesDict = dict()
        params =  { 'LANG' : language}
        data = urllib.parse.urlencode(params)
        data = data.encode('utf-8')
        result = urllib.request.urlopen(BASE_URL,data)
        for i in result:
            line = i.decode('utf-8')
            code, title = line.rstrip('\r\n').split(' = ')
            gamesDict[code] = title
        return gamesDict




gametdb = GameTDB()
gamelist = gametdb.getGameList()
print(len(gamelist.items()))
