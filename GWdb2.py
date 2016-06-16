import sqlite3
import os


class GWdb(object):
    def __init__(self):
        self.con = sqlite3.connect("::memory::")
        self.cur = self.con.cursor()
        qry = "CREATE TABLE IF NOT EXISTS gameTitles('id' INTEGER PRIMARY KEY,'code' TEXT,'title' TEXT)"
        self.con.execute(qry)
        qry = "CREATE TABLE IF NOT EXISTS gamesFound('id' INTEGER PRIMARY KEY,'code' TEXT,'path' TEXT, 'fileType' TEXT, 'listName' TEXT)"
        self.con.execute(qry)

    # def delete():
    #     ''' Delete database file '''
    #     if os.path.exists(database):
    #         os.remove(database)
    
    def select(self,*args):
        """
        :param args: Table name followed by dictionary with arguments for the where clause
        :return:
        """
        self.tableName = args[0] or None
        self.arguments = args[1] or None
        if self.tableName == None:
            return 0
        qry = "select * from {}".format(self.tableName)
        if self.arguments:
            arg = " where "
            count = len(self.arguments)
            for i in self.arguments.keys():
                arg += i + " = '" + self.arguments.get(i) + "'"
                if  list(self.arguments.keys()).index(i) != count -1:
                    arg += " and "
            qry = qry + arg
        self.con.execute(qry)
        print(self.cur.fetchall())


    def delete(self,**kwargs):
        self.tableName = kwargs.get('table',None)
        if self.tableName == None:
            return 0


    def close(self):
        self.cur.close()
        self.con.close()


test = GWdb()
arguments = { 'code' : 'abc'}#,
              #'title' : 'test'}
test.select('gameTitles',arguments)
test.close()
