#encoding=utf8
import MySQLdb
import sys,os,math
reload(sys)
sys.setdefaultencoding('UTF8')

class GetFromDB():
    def __init__(self,host,user,passwd,db,port = 3306):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db
        self.port = port
        self.conn = MySQLdb.connect(host=self.host,port=self.port , user=self.user, passwd=self.passwd, db=self.db, charset='utf8')
    
    def __del__(self):
        self.conn.close()

    def getRecords(self,sqlcmd):
        try:
            cur = self.conn.cursor()
            n = cur.execute(sqlcmd)
            records = cur.fetchall()
        except Exception, e:
            print "[Error]:", e
        finally:
            cur.close()
        
        print "input from db:" + str(len(records))
        return records
    
    def ExecuteSQL(self,sqlcmd):
        try:
            cur = self.conn.cursor()
            n = cur.execute(sqlcmd)
        except Exception, e:
            print "[Error]:", e
        finally:
            cur.close()
        
