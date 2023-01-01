#!/usr/bin/python
import os.path
import re
import mysql.connector
import db_manager

try:
    if __name__ == "__main__":
        db_manager.parse_conf()
        db_manager.connect_to_db()
        db_manager.create(False)
        
except Exception as ex:
    print("Problem creating database !!!\n")
    print(str(ex))