#!/usr/bin/python

import sys, os

from common import *

def print_usage_and_exit():
    print "Usage: mreceiver {add | del | list} [email]"
    exit()
    

def get_allowed_domains(username):
    """ Returns a list of domains the local user is allowed to add addresses for. """
    # sql = "SELECT domain FROM domains WHERE mail AND user = %s UNION SELECT alias FROM http_aliases WHERE domain IN (SELECT domain FROM domains WHERE mail AND user = %s)"
    sql = "SELECT {domain} FROM {domains} WHERE mail AND user = %s UNION SELECT alias FROM {http_aliases} WHERE {domain} IN (SELECT {domain} FROM {domains} WHERE mail AND user = %s)".format(
        domain=DOMAIN_FIELD, domains=DOMAIN_TABLE, http_aliases=HTTP_ALIASES)
    result, resultSet = executeSQL(sql, username, username)
    return [ dom[0] for dom in resultSet ]
    


def check_username_match(email, username):
    """ Checks if email has the correct domain. """
    try:
        user, domain = email.split("@")
    except:
        print "Something is wrong with the email you supplied: %s" % email
        exit(-1)

    if domain not in get_allowed_domains(username):
        print "You're not allowed to manage email addresses for that domain"
        exit(-1)
    
    if user in ALIASES:
        # user is a reserved administrative alias.
        print "You're not allowed to manage this alias."
        exit(-1)


def proceed_with_listing(username):
    result, resultSet = executeSQL("SELECT virtual FROM " + VIRTUAL_TABLE + " WHERE alias = %s" , username)
    print "Number of email addresses: " + str(result)
    print ""
    for account in resultSet:
        print account[0]
    exit()
    
  
def main():
    DBopen()
    
    username, uid, gid = get_system_userdata()

    if (len(sys.argv) == 2) and (sys.argv[1] == "list"):
        proceed_with_listing(username)
    
    if not len(sys.argv) == 3:
        print_usage_and_exit()    
   
    action = sys.argv[1]
    email = sys.argv[2]
    
    check_username_match(email, username)
    
    if action == "add":
        sql = "INSERT INTO " + VIRTUAL_TABLE + " (virtual, alias) VALUES (%s, %s)" 
        executeSQL(sql, email, username)
        print email + " added!"
        
    elif action == "del":
        sql = "DELETE FROM " + VIRTUAL_TABLE + " WHERE virtual = %s"
        ret, resultSet = executeSQL(sql, email)
        if ret == 0:
            print "No address has been deleted!"
        else:
            print email + " deleted!"
    
    else:
        print_usage_and_exit()

if __name__ == "__main__":
    main()
