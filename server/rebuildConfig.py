from common import *
import os, pwd, glob

from string import Template

   
def addAliases(domainname):
    sql = "INSERT INTO " + VIRTUAL_TABLE + " (virtual, alias) VALUES "
    args = []
    for name in ALIASES:
        sql += "(%s, 'root'), "
        args.append(name + "@" + domainname)
    sql = sql[:len(sql)-2]  # Remove the last kommata
    executeSQL(sql,  *args)
    
def getTemplate(file):
    f = open(file, "r")
    templateStr = f.read()
    f.close()
    return Template(templateStr)

def writeTemplate(inputTemplate, outputFile, **templateArgs):
    template = getTemplate(inputTemplate)
    output = template.substitute(templateArgs)
    f = open(outputFile, "w")
    f.write(output)
    f.close()
    
def rebuildAliases():
    """ Deletes all ALIASES and rebuilds them based on the entries from DOMAIN_TABLE. """
    for name in ALIASES:
        sql = "DELETE FROM " + VIRTUAL_TABLE + " WHERE virtual LIKE '" + name + "@%'"
        executeSQL(sql)
    
    sql = "SELECT " + DOMAIN_FIELD + " FROM " + DOMAIN_TABLE + " WHERE mail = TRUE"
    retVal, domains = executeSQL(sql)
    # return should have only n rows with one field each.
    for dom in domains:
        addAliases(dom[0])
        
        
def rebuildApacheConfig():
    retVal, resultSet = executeSQL("SELECT %s, %s FROM %s WHERE http = TRUE" % (DOMAIN_FIELD, "user", DOMAIN_TABLE))
    template = getTemplate("apache-config.template")
    
    output = ""
    for row in resultSet:
        sql = "SELECT %s FROM %s WHERE %s = %s" % ("alias", HTTP_ALIASES, DOMAIN_FIELD, "%s")
        retVal, aliases = executeSQL(sql, row[0])
        configAliases = ""
        for alias in aliases:
            configAliases += alias[0] + " *." + alias[0] + " "
        output += template.substitute(domain = row[0], user = row[1], aliases = configAliases)
        output += "\n\n"
    
    f = open("generated-vhosts", "w")
    f.write(output)
    f.close()
    
def rebuildSSLPRoxy():
    retVal, resultSet = executeSQL("SELECT %s FROM %s WHERE http = TRUE" % (DOMAIN_FIELD, DOMAIN_TABLE))
    template = getTemplate("sslproxy-config.template")
    
    output = ""
    for row in resultSet:
        output += template.substitute(domain = row[0])
        output += "\n"

    f = open("sslproxy.conf", "w")
    f.write(output)
    f.close()
    
def rebuildLogrotateConfig():
    retVal, resultSet = executeSQL("SELECT %s, %s FROM %s WHERE http = TRUE" % (DOMAIN_FIELD, "user", DOMAIN_TABLE))
    logs = ""
    for row in resultSet:
        logs += "/home/%s/%s/log/access.log \n" % (row[1], row[0])
        logs += "/home/%s/%s/log/error.log \n" % (row[1], row[0])

    writeTemplate("logrotate-config.template", "generated-logrotate.conf", logs = logs.rstrip())
    

    
def rebuildAwstatsConfig():
    files = glob.glob("/etc/awstats/awstats.*.*.conf")
    buildCommand = ""
    for f in files: os.remove(f)
    retVal, resultSet = executeSQL("SELECT %s, user FROM %s WHERE http_statistics = TRUE" % (DOMAIN_FIELD, DOMAIN_TABLE))
    for row in resultSet:
        domain, user = row[0], row[1]
        retVal, alResult = executeSQL("SELECT alias FROM %s WHERE %s = %s" % (HTTP_ALIASES, DOMAIN_FIELD, "%s"), domain)
        aliasesList = [n[0] for n in alResult]
        aliases = " ".join(aliasesList)
        writeTemplate("awstats-config.template", "awstats." + domain + ".conf", domain = domain, user = user, aliases = aliases)
        build = '/opt/awstats-6.95/tools/awstats_buildstaticpages.pl -config="%s" -lang="de" -dir="/home/%s/%s/statistics/" -awstatsprog="/opt/awstats-6.95/wwwroot/cgi-bin/awstats.pl"'
        buildCommand += "\n" + build % (domain, user, domain)
        build = 'mv "/home/%s/%s/statistics/awstats.%s.html" "/home/%s/%s/statistics/index.html"' % (user, domain, domain, user, domain)
        buildCommand += "\n" + build
    writeTemplate("rotate_and_report.template", "rotate_and_report", build_command = buildCommand)
        

def test_and_create(path, user):
     """ Tests if a directory exists, if not creates it with 0700. """
     if not os.access(path, os.F_OK):
         os.mkdir(path, 0700)
         uid = pwd.getpwnam(user).pw_uid
         gid = pwd.getpwnam(user).pw_gid
         os.chown(path, uid, gid)
         print "Created:", path
         print "Username, UID, GID:", user, uid, gid
         print ""
 
    
def addDomainDirs():
    retVal, resultSet = executeSQL("SELECT %s, %s, %s FROM %s WHERE http = TRUE" % (DOMAIN_FIELD, "user", "http_statistics", DOMAIN_TABLE))
    for row in resultSet:
        domain = row[0]
        user = row[1]
        stats = row[2]
        path = "/home/%s/%s/" % (user, domain)
        test_and_create(path, user)
        test_and_create(path + "pub/", user)
        test_and_create(path + "log/", user)
        test_and_create(path + "tmp/", user)
        if stats:
            test_and_create(path + "statistics/", user)
   
from shutil import move
 
def moveFiles():
    move("generated-vhosts", "/etc/apache2/sites-available/generated-vhosts")
    move("generated-logrotate.conf", "/etc/logrotate.d/generated-logrotate.conf")
    move("sslproxy.conf", "/etc/apache2/sslproxy.conf")
    move("rotate_and_report", "/etc/cron.daily/rotate_and_report")
    os.chmod("/etc/cron.daily/rotate_and_report", 0755)
    filesToMove = glob.glob("awstats.*.*.conf")
    for f in filesToMove:
        move(f, "/etc/awstats/" + f)

conn = None

def main():
    DBopen()
    rebuildLogrotateConfig()
    rebuildApacheConfig()
    rebuildSSLPRoxy()
    rebuildAliases()
    addDomainDirs()
    rebuildAwstatsConfig()
    moveFiles()
    DBclose()

if __name__ == "__main__":
    main()
