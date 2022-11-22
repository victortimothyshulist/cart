#!/usr/bin/python
import os.path
import re
import mysql.connector
import time

CONF_FN = "conalaun.conf"

def parse_conf(fn):
    conf_items = dict()

    if not os.path.isfile(fn):
        print("\n*ERR: config file '" + fn + "' does not exist.")
        exit(0)

    with open(CONF_FN, 'r') as CFH:
        for conf_line in CFH.readlines():
            conf_line = conf_line.strip()      
            if len(conf_line) == 0 : continue
            if conf_line[0] == "#": continue

            mo = re.match('^\s*(.+?)\s*=\s*"(.+?)"\s*$', conf_line)
            if not bool(mo): 
                print("*WARNING: ignored line: \n" + conf_line)
                continue

            conf_items[mo.group(1)] = mo.group(2)

    for req_item in ('DB_HOST', 'DB_USER', 'DB_PASSWORD', 'CREATE_SQL_FILE_NAME', 'DB_NAME'):
        if req_item not in conf_items:
            print("\n*ERR: '" + req_item + "' is not given in configuration file '"  + fn + "'. Please provide a value for it.")  

    return conf_items


def create(firstdrop):
    myconn = None
    print("--- Later: add a feature that verifiies all tables exist before exiting")

    configuration = parse_conf(CONF_FN)

    if not os.path.isfile(configuration['CREATE_SQL_FILE_NAME']):
        print("\n*ERR: SQL script file '" + configuration['CREATE_SQL_FILE_NAME']  + "' which is specified in '" + CONF_FN + "', does not exist.")
        exit(0)

    sql_program = ""
    with open(configuration['CREATE_SQL_FILE_NAME'], 'r') as SFH:
        for sql_line in SFH.readlines():
            sql_program += sql_line

    sql_program = re.sub('<DB_NAME>', configuration['DB_NAME'], sql_program)
    myconn = None

    try:
        myconn = mysql.connector.connect(host = configuration['DB_HOST'], user = configuration["DB_USER"], passwd = configuration['DB_PASSWORD'])
        mycursor = myconn.cursor()

        if firstdrop:
            print("Dropping database...")
            mycursor.execute("DROP DATABASE IF EXISTS " +  configuration['DB_NAME'])
            time.sleep(15)

        print("Creating database...")
        mycursor.execute(sql_program)
        time.sleep(15)

        with open('temp_create.sql', 'w') as OUT:
             OUT.write(sql_program)

        print("\n* Successfully created Vulcan database '" + configuration['DB_NAME'] + " '!")
        
    except mysql.connector.Error as e:
        print("\n*ERR: There was a problem creating database '" + configuration['DB_NAME'] + "' : " + e.msg)
        
    finally:
        if myconn != None:
            if myconn.is_connected():
                myconn.close()
                mycursor.close()

