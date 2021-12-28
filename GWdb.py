import ast
import sqlite3
import gametdb
import os


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class GWdb(object):
    def __init__(self):
        self.database = ':memory:'
        self.gameList = {}
        self.fileName = 'wiitdb.txt'
        self.con = sqlite3.connect(self.database)
        self.cur = self.con.cursor()
        qry = "CREATE TABLE IF NOT EXISTS gameTitles('id' INTEGER PRIMARY KEY,'code' TEXT,'title' TEXT)"
        self.cur.execute(qry)
        qry = "CREATE TABLE IF NOT EXISTS gamesFound('id' INTEGER PRIMARY KEY,'code' TEXT,'path' TEXT, 'fileType' TEXT, 'listName' TEXT)"
        self.cur.execute(qry)
        self.getGameList()
        self.populateDatabase()

    def getGameList(self):
        try:
            with open(self.fileName, 'r') as file:
                self.gameList = ast.literal_eval(file.read())
        except FileNotFoundError:
            self.refreshData()

    def refreshData(self):
        TDB = gametdb.GameTDB()
        self.gameList = TDB.getGameList()
        file = open(self.fileName, 'w')
        file.write(str(self.gameList))
        file.close()

    def populateDatabase(self):
        gameTitlesValues = list()
        for i in self.gameList:
            values = (i, self.gameList.get(i))
            gameTitlesValues.append(values)
        self.insert('gameTitles', ('code', 'title'), gameTitlesValues)
        self.con.commit()

    def insert(self, tableName, columns, values):
        """
        :param args:
        :param tableName -> string
        :param columns -> tuple
        :param values -> list of tuples
        :return:
        """
        qry = "insert into {}{} values{}".format(tableName, columns, str(values).strip('[]'))
        self.cur.execute(qry)
        self.con.commit()

    def select(self, tableName, columns, args=None, ):
        """
        :param tableNAme str
        :param args dict
        :param columns string
        :return:
        """
        qry = "select {} from {}".format(columns, tableName)
        if args:
            arg = " where "
            count = len(args)
            for i in args.keys():
                arg += i + " = '" + args.get(i) + "'"
                if list(args.keys()).index(i) != count - 1:
                    arg += " and "
            qry = qry + arg
        self.cur.execute(qry)
        return self.cur.fetchall()

    def delete(self, **kwargs):
        """
        :param kwargs: tableName=table, key1=value, key2=value
         result query = "delete from table where key1='value' and key2='value'"
        :return:
        """
        tableName = kwargs.get('tableName', None)
        if tableName == None:
            return 1
        qry = "delete from {}".format(tableName)
        if kwargs.__len__() > 1:
            args = " where "
            for key in kwargs.keys():
                if key == 'tableName':
                    continue
                if type(kwargs.get(key)) == type(str()):
                    args += key + " = '" + kwargs.get(key) + "'"
                if type(kwargs.get(key)) == type(int()):
                    args += "{} = {}".format(key, kwargs.get(key))
                args += " and "
            args = args[:-4]
            qry = qry + args
        self.cur.execute(qry)
        self.con.commit()
        return 0

    def close(self):
        self.cur.close()
        self.con.close()
        if os.path.exists(self.database):
            os.remove(self.database)
