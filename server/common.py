import MySQLdb
import sys

DOMAIN_TABLE = "domains"
DOMAIN_FIELD = "domain"
VIRTUAL_TABLE = "virtual_aliases"
HTTP_ALIASES = "http_aliases"
ALIASES = ["hostmaster", "postmaster", "newsmaster", "mailmaster", "abuse"]

conn = None


def DBopen():
    DB_USER = "system"
    DB_PASSWD = "XXX"
    DATABASE = "system"
    
    global conn
    conn = MySQLdb.connect(host="localhost", user=DB_USER, passwd = DB_PASSWD, db= DATABASE)
    
def DBclose():
    conn.close()
    
def executeSQL(sql, *paras):
    try:
        cursor = conn.cursor()
        if len(paras):
            # print sql, paras
            ret = cursor.execute(sql, paras)
        else:
            # print sql
            ret = cursor.execute(sql)
        resultSet = cursor.fetchall()
        cursor.close()
        return ret, resultSet        
        
    except MySQLdb.IntegrityError, error:
        print "A database integrity error has occured. Maybe you try to add an already existing entry?"
        print "The exception message is:", error[1]
        sys.exit(-1)
    except Exception, error:
        print "Some unhandled error has occured. Please contact root and describe what you were trying to do and add the following message."
        print error
        sys.exit(-1)
  
def exit(retVal = 0):
     try:
        DBclose()
     except:
         pass
     sys.exit(retVal)

def get_system_userdata():
    """ Returns a tuple consisting of username, UID and GID of the user that called sudo."""
    import os
    username = os.environ['SUDO_USER']
    uid = os.environ['SUDO_UID']
    gid = os.environ['SUDO_GID']
    return username, uid, gid

