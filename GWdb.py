# Database related functions
import os
import sqlite3

database = "GWTempDB"

def deleteDB():
    if os.path.exists(database):
        os.remove(database)   

def connectDB():
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    return cursor

def initDB():
    conn = connectDB()
    qry = "CREATE TABLE IF NOT EXISTS gameTitles('id' INTEGER PRIMARY KEY,'code' TEXT,'title' TEXT)"
    conn.execute(qry)
    qry = "CREATE TABLE IF NOT EXISTS gamesFound('id' INTEGER PRIMARY KEY,'code' TEXT,'path' TEXT, 'fileType' TEXT, 'listName' TEXT)"
    conn.execute(qry)
    conn.close()

def flushTable(tableName):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    qry = "DELETE FROM " + tableName
    cursor.execute(qry)
    conn.commit()
    conn.close()

def flushTables():
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    qry = "DELETE FROM gamesFound"
    cursor.execute(qry)
    conn.commit()
    conn.close()

def flushTable(tableName,listName):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    qry = "DELETE FROM {} where listName='{}'".format(tableName,listName)
    cursor.execute(qry)
    conn.commit()
    conn.close()

def gamesFoundInsert(code,fullPath,fileType,listName):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    qry = 'INSERT INTO gamesFound(code,path,fileType,listName) VALUES(?,?,?,?)'
    cursor.execute(qry,(code,fullPath,fileType,listName))
    conn.commit()
    conn.close()

def gameTitlesInsert(code,title):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    qry = 'INSERT INTO gameTitles(code,title) VALUES(?,?)'
    cursor.execute(qry,(code,title))
    conn.commit()
    conn.close()
    
def gameTitlesCount():
    conn = connectDB()
    qry = 'SELECT count(*) FROM gameTitles'
    conn.execute(qry)
    results = conn.fetchall()
    conn.close()
    return results[0][0]

def gamesFoundCount(extension,listName='source'):
    if extension == 'all':
        extension = "fileType like '%'"
    else:
        extension = "fileType='" + extension + "'"
    conn = connectDB()
    qry = 'SELECT count(distinct(code)) FROM gamesFound where {} and listName = "{}"'.format(extension,listName)
    conn.execute(qry)
    results = conn.fetchall()
    conn.close()
    return results[0][0]
    

def getTitle(code):
    conn = connectDB()
    qry = 'SELECT title FROM gameTitles WHERE code="{}"'.format(code)
    conn.execute(qry)
    results = conn.fetchall()
    conn.close()
    return results[0][0]

def getGameFound(extension='all',listName='source'):
    if extension == 'all':
        extension = "fileType like '%'"
    else:
        extension = "fileType='" + extension + "'"
    conn = connectDB()
    qry = 'SELECT code,path FROM gamesFound WHERE {} and listName="{}"'.format(extension,listName)
    conn.execute(qry)
    results = conn.fetchall()
    conn.close()
    return results

def getFoundTitles():
    conn = connectDB()
    qry = """SELECT distinct(gf.code),gt.title FROM gamesFound as gf JOIN gameTitles as gt on gt.code=gf.code"""
    conn.execute(qry)
    results = conn.fetchall()
    conn.close()
    return results

def getPath(code,listName):
    conn = connectDB()
    qry = """ SELECT group_concat(path) from gamesFound where code='{}' and listName='{}'""".format(code,listName)
    conn.execute(qry)
    results = conn.fetchall()
    conn.close()
    results = str(results[0][0]).split(',')
    return results

print(gamesFoundCount('all'))
