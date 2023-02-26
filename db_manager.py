#!/usr/bin/python
import os.path
import re
import mysql.connector
import time


CONF_FN = "conalaun.conf"
conalaun_db_conn = None
conalaun_db_cursor = None
sql_program = ''
configuration = dict()


def parse_conf():

    if not os.path.isfile(CONF_FN):
        print("\n*ERR: config file '" + CONF_FN + "' does not exist.")
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

            configuration[mo.group(1)] = mo.group(2)

    for req_item in ('DB_HOST', 'DB_USER', 'DB_PASSWORD', 'CREATE_SQL_FILE_NAME', 'DB_NAME'):
        if req_item not in configuration:
            print("\n*ERR: '" + req_item + "' is not given in configuration file '"  + CONF_FN + "'. Please provide a value for it.")  
            exit(1)


def drop_database():
    print("Dropping database...")
    conalaun_db_cursor.execute("DROP DATABASE IF EXISTS " +  configuration['DB_NAME'])
    time.sleep(15)


def connect_to_db():
    global conalaun_db_conn
    global conalaun_db_cursor

    try:        
        conalaun_db_conn = mysql.connector.connect(host = configuration['DB_HOST'], user = configuration["DB_USER"], passwd = configuration['DB_PASSWORD'])
        conalaun_db_cursor = conalaun_db_conn.cursor()
        
    except mysql.connector.Error as e:
        print("\n*ERR: There was a problem connecting to database '" + configuration['DB_NAME'] + "' : " + e.msg)
        exit(1)
        

def create(firstdrop):
    global conalaun_db_conn
    global conalaun_db_cursor

    lot = list() # list of tables

    if not os.path.isfile(configuration['CREATE_SQL_FILE_NAME']):
        print("\n*ERR: SQL script file '" + configuration['CREATE_SQL_FILE_NAME']  + "' which is specified in '" + CONF_FN + "', does not exist.")
        exit(0)

    sql_program = ""

    with open(configuration['CREATE_SQL_FILE_NAME'], 'r') as SFH:
        for sql_line in SFH.readlines():
            sql_program += sql_line
            mo = re.match('CREATE TABLE `<DB_NAME>`.`(.+?)`.*$', sql_line)
            if bool(mo):
                lot.append(mo.group(1))

    sql_program = re.sub('<DB_NAME>', configuration['DB_NAME'], sql_program)

    if firstdrop: drop_database()

    print("Creating database...")
    conalaun_db_cursor.execute(sql_program)

    conalaun_db_cursor.close()
    conalaun_db_conn.close()
    conalaun_db_conn = None
        
    # Check if all tables exist.
    attempts_left = 120
    any_fail = None

    while(attempts_left > 0):
        attempts_left -= 1
        any_fail = False
        time.sleep(1)

        try:
            conalaun_db_conn = mysql.connector.connect(host = configuration['DB_HOST'], user = configuration["DB_USER"], passwd = configuration['DB_PASSWORD'], database = configuration['DB_NAME'], autocommit = False)
            conalaun_db_cursor = conalaun_db_conn.cursor()

        except Exception as ex:
            any_fail = True
            continue

        for table in lot:
            sql = "select * from " + table;

            try:
                conalaun_db_cursor.execute(sql)
                dummy_result = conalaun_db_cursor.fetchall()

            except Exception as ex:                
                any_fail = True
                break
                                
        if not any_fail: break

        conalaun_db_cursor.close()
        conalaun_db_conn.close()
        conalaun_db_conn = None
    
    if not any_fail:
        print("\n* Successfully created CONALAUN database '" + configuration['DB_NAME'] + " '!")
    else:
        print("\n* Timed out waiting for CONALAUN database '" + configuration['DB_NAME'] + " to be ready!")
