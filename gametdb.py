import os,sys
import urllib.request
import urllib.parse

BASE_URL = 'http://www.gametdb.com/wiitdb.txt'

gameList = 'wiitdb.txt'
URL = 'http://www.gametdb.com/wiitdb.txt?LANG=EN'


class GameTDB():
    def __init__(self):
        self.gameList = 'wiitdb.txt'
        self.gamesDict = dict()

    def getGameList(self,language = 'EN'):
        if os.path.exists(self.gameList):
            os.unlink(self.gameList)
        params =  { 'LANG' : language}
        data = urllib.parse.urlencode(params)
        data = data.encode('utf-8')
        result = urllib.request.urlopen(BASE_URL,data)
        for i in result:
            line = i.decode('utf-8')
            code, title = line.rstrip('\r\n').split(' = ')
            self.gamesDict[code] = title




gametdb = GameTDB()
gamelist = gametdb.getGameList()

for i in gametdb.gamesDict.items():
    print(i)
