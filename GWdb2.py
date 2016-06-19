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
        :param tableName -> string
        :param columns -> tuple
        :param values -> list of tuples
        :return:
        """
        self.tableName = tableName
        self.columns = columns
        self.values = values
        qry = "insert into {}{} values{}".format(self.tableName,self.columns,str(self.values).strip('[]'))
        print(qry)
        self.cur.execute(qry)
        self.con.commit()


    def select(self,tableNAme,args = None):
        """
        :param tableNAme str
        :param args dict
        :return:
        """
        self.tableName = tableNAme
        qry = "select * from {}".format(self.tableName)
        if args:
            arg = " where "
            count = len(args)
            for i in args.keys():
                arg += i + " = '" + args.get(i) + "'"
                if  list(args.keys()).index(i) != count - 1:
                    arg += " and "
            qry = qry + arg
        self.cur.execute(qry)
        print(self.cur.fetchall())


    def delete(self,**kwargs):
        """
        :param kwargs: tableName=table, key1=value, key2=value
         result query = "delete from table where key1='value' and key2='value'"
        :return:
        """
        tableName = kwargs.get('tableName',None)
        count = len(kwargs.keys())
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
                    args += "{} = {}".format(key,kwargs.get(key))
                args += " and "
            args = args[:-4]
            qry = qry + args
        self.cur.execute(qry)
        self.con.commit()
        return 0



    def close(self):
        self.cur.close()
        self.con.close()


test = GWdb()
columns = '(code,title)'
values = [(123,'El mundo'),('123','la vista')]
test.insert('gameTitles',columns,values)
arguments = { 'code' : 'abc',
              'title' : 'test'}
test.select('gameTitles')
test.delete(tableName='gameTitles')
test.select('gameTitles')
test.close()
