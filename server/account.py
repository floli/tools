#!/usr/bin/python

from optparse import OptionParser
import sys
import MySQLdb
from common import *


def main():
    parser = setup_optparser()
    (options, args) = parser.parse_args()
    
    check_args(args, parser) # Checks if the positional arguements are synatically correct
        
    account_type = args[0]
    action = args[1]
    
    check_options(action, options) # Checks if the options are syntactically correct, depending on action
    
    DBopen()
    
    if action == "list":
        proceed_with_listing(account_type)
        
    check_login(options.login)
    
    prepare_login_data(account_type, options)
    
    if action == "add":
        process_dir(options)
     
    
    execute(action, account_type, options)
    print_success(action, account_type, options)
    
    DBclose()
    
    
    
def setup_optparser():
    """ Setup the parsers help. """
    usage =  "\n"
    usage += "account account_type action [options] \n"
    usage += "  account_type can be either 'ftp' or 'mailbox'\n"
    usage += "  action can be either 'add', 'del' or 'list'.\n"
    usage += "  If action is 'add' all of the options below need to be given.\n"
    usage += "  If action is 'del' only login need to be given.\n"
    usage += "  If action is 'list' no options need to be given.\n"   
    parser = OptionParser(usage=usage)
    parser.add_option("-l", "--login", help="The login for the account. Your username will be appended to this value. In all caes without domain/username suffix.")
    parser.add_option("-d", "--directory", help="The directory on which the account will point (relative to the current directory)")
    parser.add_option("-p", "--password", help="The password for the account")
    return parser
    

def check_args(args, parser):
    """ Checks validity of arguments. """    
    if len(args) <> 2:
        parser.print_help()
        sys.exit(1)

    if args[0] not in ["ftp", "mailbox"]:
        print "First argument must be either 'ftp' or 'mailbox'."
        sys.exit(1)
        
    if args[1] not in ["add", "del", "list"]:
        print "Second argument must be either 'add', 'del' or 'list'."
        sys.exit(1)
        
 
def check_options(action, options):
    """ Check if all required options are giving. Depends on the selected action. """
    if action == "add":
        if not (options.login and options.directory and options.password):
            print "Not all required options have been given!"
            sys.exit(1)
            
    if action == "del":
        if not (options.login):
            print "Not all required options have been given!"
            sys.exit(1)
            
def check_login(login):
    """ login always need to have the form name@domain.tld. domain.tld also need to be in the table of domains for the local user name. Both is checked here. """
    splitted = login.split("@")
    if len(splitted) != 2:
        print "There is something wrong with the login you have supplied. """
        exit(-1)
    else:
        domain = splitted[1]
        
    username = get_system_userdata()[0] 
        
    sql = "SELECT %s FROM %s WHERE user = %s "
    sql += "UNION SELECT alias FROM %s INNER JOIN %s ON %s.%s = %s.%s WHERE %s.user = %s"
    sql = sql % (DOMAIN_FIELD, DOMAIN_TABLE, "%s", HTTP_ALIASES, DOMAIN_TABLE, DOMAIN_TABLE, DOMAIN_FIELD, HTTP_ALIASES, DOMAIN_FIELD, DOMAIN_TABLE, "%s")
    retVal, resultSet = executeSQL(sql, username, username)
    
    if not domain in [i[0] for i in resultSet] :
        print "You are not allowed to manage accounts for the domain " + domain + "!"
        exit(-1)        
              


def prepare_login_data(account_type, options):
    """ Append the userid to the loginname and crypts the password for ftp accounts. """
    import crypt
    options.username, options.uid, options.gid = get_system_userdata()
    options.home =  "/home/" + options.username   
       
    #if account_type == "ftp" and options.password:
    #    options.password = crypt.crypt(options.password, options.login)
    
def execute(action, account_type, options):
    """ Compiles the sql string for creation and deletion of accounts. """
    if account_type == "mailbox":
        tablename = "mailboxes"
    elif account_type == "ftp":
        tablename = "ftp"
    
    if action == "del":
        sql = "DELETE FROM " + tablename + " WHERE `login` = %s"
        if not executeSQL(sql, options.login)[0]:
            print "No account has been deleted!"
            exit(-1)
        
    elif action == "add":
        if account_type == "mailbox":
            sql = "INSERT INTO " + tablename + " (`name`, `login`, `home`, `maildir`, `uid`, `gid`, `password`) "
            sql += "VALUES (%s, %s, %s, %s, %s, %s, %s)" 
            executeSQL(sql, options.username, options.login, options.home, options.directory, options.uid, options.gid, options.password)
            
        elif account_type == "ftp":
            sql = "INSERT INTO " + tablename + " (`name`, `login`, `password`, `uid`, `gid`, `dir`, `shell`) "
            sql += "VALUES (%s, %s, %s, %s, %s, %s, '/bin/bash')"
            executeSQL(sql, options.username, options.login, options.password, options.uid, options.gid, options.directory)
            # print sql % (options.username, options.login, options.password, options.uid, options.gid, options.directory)
    
    
   
def print_success(action, account_type, options):
    """ Prints information after a successfull creation of a account. """    
    print "Success"
    print "action: " + action
    print "account type: " + account_type
    print "login: " + options.login
    if action == "add":
        print "target directory: " + options.directory
        
    
def process_dir(options):
    """ Checks if the given directory is under the homedir of the user and converts a relative path into a absolute one."""
    import os
    options.directory = os.path.realpath(options.directory)
    if options.directory[:len(options.home)] <> options.home:
        print "Directory must be under your home directory!"
        sys.exit(-1)
        
def proceed_with_listing(account_type):
    username, uid, gid = get_system_userdata()
    if account_type == "mailbox":
        sql = "SELECT login,maildir FROM mailboxes WHERE `name` = %s"
    elif account_type == "ftp":
        sql = "SELECT login,dir FROM `ftp` WHERE `name` = %s"
    
    retVal, rows = executeSQL(sql, username)
    
    
    print "Listing type: " + account_type
    print "Number of accounts: " + str(len(rows))
    print ""

    for account in rows:
        print "Login: " + account[0]
        print "Target directory: " + account[1]
        print ""
        
    exit(0)
    
    
if __name__ == "__main__":
    main()
