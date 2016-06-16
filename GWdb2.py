import sqlite3
import os


class GWdb(object):
    def __init__(self):
        self.con = sqlite3.connect(":memory:")
        self.cur = self.con.cursor()
        qry = "CREATE TABLE IF NOT EXISTS gameTitles('id' INTEGER PRIMARY KEY,'code' TEXT,'title' TEXT)"
        self.cur.execute(qry)
        qry = "CREATE TABLE IF NOT EXISTS gamesFound('id' INTEGER PRIMARY KEY,'code' TEXT,'path' TEXT, 'fileType' TEXT, 'listName' TEXT)"
        self.cur.execute(qry)
        self.con.commit()

    # def delete():
    #     ''' Delete database file '''
    #     if os.path.exists(database):
    #         os.remove(database)
    def insert(self,tableName,columns,values):
        """
        :param args:
        :string table name
        :tuple columns
        :list of tuples values
        :return:
        """
        self.tableName = tableName
        self.columns = columns
        self.values = values
        qry = "insert into {}{} values{}".format(self.tableName,self.columns,str(self.values).strip('[]'))
        print(qry)
        self.cur.execute(qry)
        self.con.commit()


    def select(self,tableNAme,arguments = None):
        """
        :param tableNAme str
        :param arguments dict
        :return:
        """
        self.tableName = tableNAme
        self.arguments = arguments
        qry = "select * from {}".format(self.tableName)
        if self.arguments:
            arg = " where "
            count = len(self.arguments)
            for i in self.arguments.keys():
                arg += i + " = '" + self.arguments.get(i) + "'"
                if  list(self.arguments.keys()).index(i) != count -1:
                    arg += " and "
            qry = qry + arg
        self.cur.execute(qry)
        print(self.cur.fetchall())


    def delete(self,**kwargs):
        self.tableName = kwargs.get('table',None)
        if self.tableName == None:
            return 0


    def close(self):
        self.cur.close()
        self.con.close()


test = GWdb()
columns = '(code,title)'
values = [('abc','El mundo'),('123','la vista')]
test.insert('gameTitles',columns,values)
arguments = { 'code' : 'abc',
              'title' : 'test'}
test.select('gameTitles')
test.close()
