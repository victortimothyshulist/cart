#!/usr/bin/python
import ico_compiler
import setupdb
import mysql.connector
import os
import os.path
import re
import logging
from logging.handlers import RotatingFileHandler
import sys
import cart_dump_table
import db_manager
import term_manager
import time


def fetch_sr_code_lines(dn):
    code_lines = dict()
    files_in_sr_code_dir = list()

    if os.path.isdir(dn):
        for entry in os.listdir(dn):
            if entry == "__pycache__": continue

            if entry[-3:] != '.PY':
                raise Exception("The entry '" + entry + "' in '" + dn + "' does not end with '.PY' - please fix.")

            entry_without_py = entry[0:-3]
            
            mo = re.match('.*[a-z].*', entry)
            if bool(mo):
                raise Exception("The entry " + entry + " in '" + dn + r"' contains lowercase letters, that's not allowed, only UPPERCASE - Please correct the name of this file.")

            mo = re.match('.*[^A-Z0-9_].*', entry_without_py)
            if bool(mo):
                raise Exception("The entry " + entry_without_py + " in '" + dn + r"' contains one or more charactors that are -not- 'A' to 'Z' or '0' to '9' or '_'.  Please correct the name of this file.")
        
            if not os.path.isfile(dn + "/" + entry):                
                raise Exception("The entry '" + entry + "' in directory: '" + dn + "' is not a file.  Can only have files in this directory.")

            files_in_sr_code_dir.append(entry_without_py)
            
            all_code_lines = ""
            with open(dn + '/' + entry, 'r') as srfh:
                for codeline in srfh.readlines():
                    all_code_lines += codeline

            code_lines[entry] = all_code_lines

    if os.path.isfile(REG_SR_LIST_FILENAME):
        os.remove(REG_SR_LIST_FILENAME)
        if os.path.isfile(REG_SR_LIST_FILENAME):
            raise Exception("I was not able to delete '" + REG_SR_LIST_FILENAME + "'")

    with open(REG_SR_LIST_FILENAME, 'w') as fh:
        for spec_rep in files_in_sr_code_dir:
            special_replaceble_name = spec_rep.upper()            
            fh.write(special_replaceble_name + "\n")

    return code_lines                


def reload_all_ICOs_from_DB(logging):
    logging.info("*** Reloading all ICOs - from Disk to RAM.")
    # TO DO - write this in the future.
    # TO DO - write this in the future.
    # TO DO - write this in the future.
    # TO DO - write this in the future.
    # TO DO - write this in the future.
    # TO DO - write this in the future.
    # TO DO - write this in the future.
    # TO DO - write this in the future.
    # TO DO - write this in the future.
    # TO DO - write this in the future.
    # TO DO - write this in the future.
    # TO DO - write this in the future.
    pass


def process_ico_file_if_it_exists(CLASS_FILE_NAME, ico_last_mod, REG_SR_LIST_FILENAME, myconn, groupinfo, CON_LIST_FILE, logging, GROUP_DIR_NAME, ALT_TEXT_DIR):
    # Return True if reload is necessary (if successfully processed an ICO), otherwise false.
    # So Return False if there was no ICO file waiting to be processed, or we failed to process it.  True if ICO file was there and we successfully processed.
    
    if os.path.isfile(CLASS_FILE_NAME):
        
        if (ico_last_mod == 0) or (os.path.getmtime(CLASS_FILE_NAME) > ico_last_mod):
            group_members_to_add = dict()

            if ico_compiler.process_class_file(REG_SR_LIST_FILENAME, CLASS_FILE_NAME, myconn, groupinfo, group_members_to_add, CON_LIST_FILE):

                # Updating groups, if there are required changes.
                try:                            
                
                    for grp in group_members_to_add:
                        with open(GROUP_DIR_NAME + "/" + grp + ".txt", 'a') as GF:            
                            for val in group_members_to_add[grp]: 
                                val = val.replace("_", " ")
                                GF.write(val + "\n")                                
                                logging.info("Added '" + val + "' to group '" + grp + "'.")                                                                

                except Exception as ex:                    
                    logging.error("Problem with updating group memberships.  Error was: " + str(ex))
                    myconn.rollback()
                    return (False, ico_last_mod, groupinfo)
                    
                myconn.commit()
                os.remove(CLASS_FILE_NAME)
                ico_last_mod = 0
                logging.info("Successfully processed an ICO file.")

                try:
                    term_manager.update_fast_string_scan_cache(myconn, logging, CON_LIST_FILE, GROUP_DIR_NAME, ALT_TEXT_DIR)
                except Exception:
                    logging.error("There was an exception thrown in term_manager.update_fast_string_scan_cache() - program terminating.") 
                    exit(0)

                if len(group_members_to_add.keys()) > 0: 
                    logging.info("Some members added to groups, thus reloading all group members for all groups.")
                    try:
                        groupinfo = term_manager.load_group_contents(logging, GROUP_DIR_NAME)
                    except Exception:
                        exit(0)

                return (True, ico_last_mod, groupinfo)
            else:
                ico_last_mod = os.path.getmtime(CLASS_FILE_NAME)
                return (False, ico_last_mod, groupinfo)
        else:            
            logging.info("I won't bother trying to reprocess the ICO.  The last time I tried, it failed, and you haven't changed the file yet.")
            return (False, ico_last_mod, groupinfo)
    else:
        return (False, ico_last_mod, groupinfo)


def cartlog(area, message):
    #__CART_REPLACED_LINE_02_DO_NOT_REMOVE_THIS_LINE

    known_area = False
    ref = None

    cartlogdirandfile = _CART_RESULTS_DIR + "/" + str(_CART_FILEDB) + "/" + str(_CART_INPUT_LINE_NUMBER) + "/" + area + ".res"
   
    #__CART_REPLACED_LINE_03_DO_NOT_REMOVE_THIS_LINE
    #__CART_REPLACED_LINE_07_DO_NOT_REMOVE_THIS_LINE

    if not known_area:
        print("\n*ERR: called cartlog() with unknown area ('" + area + "').  Check your config file for valid areas.\n")
        exit(1)

    if ref == None:
        try:
            ref = open(cartlogdirandfile, "a")

            #__CART_REPLACED_LINE_04_DO_NOT_REMOVE_THIS_LINE

        except Exception as ex:
            print("\n\n*ERR: cannot open file '" + cartlogdirandfile + "' for writing.\n")
            print("You probably called cartlog() in the wrong place, such as after _CART_INPUT_LINE_NUMBER was incremented past its maximum value.\n")
            exit(1)

    ref.write(message + "\n")
    

def notes():
    print("\nTAKE care of the comment: #TO DO  TO DO TO DO --  Go and check that all \"return\" statements in this function return False for error and only when get to end of function do we return True")
    print("\nVIP: very important: for E.R. diagram explanation doc -- smol_variables table - for RR there is no entry, instead 'rr_relations' must be consulted.  *NO* rr_relations entry for O-4 (TOL) lines though. not needed")
    print("\nAlso note for ER explanation -- if the 'smol_variables' table has NULL for 'sr_name', then that variable is an RR, and the 'rr_relations' table should be consulted.")
    print("\nA concept may have ZERO constants - simply a single vnov:group ! Test that Conalaun accepts this and creates an interpretation (this is later, i know - Stage '2')")
    print("\n[Note (done)] - System will maintain a file 'constant_strings.dat' - distinct set of constant substrings found across all I-lines of all ICOs.  To be used as 'type-0' symbols for NovaGLI style LUI-2-interpretation creation.")
    print("\ncidref and tidref should be FOREIGN KEYS -- or indexes.. figure out the syntax for that!")
    print("\n** NOTE: when rendering database entries for an ICO into 'textbox' for editing.. have to know where all places to convert spaces to underscores. (this is done, table 'class_text_lines' retains the underscores - but in other tables, the underscores are replaced by spaces)")
    print("\n*We should re-use the function in vcck.py ('replace_with_actual_date' - 187 lines) to have 'auto-created' group 'date'.  System will not add any values to 'date' group.  It is auto created if deleted and created on start of program.  Also 'number' is auto created and matches \d+(\.\d*)?")
    print("\nShould go through all functions of ico_compiler.py and see if we are doing a 'close' on the cursor before ending the function.")
    print("\n***** UPDATE ER diagram - new tables:  [ 'global_term_catalogue', 'char_pos_map' and 'char_pos_term_id' ]")
    print("\nCYBER-SECURITY NOTE: in term_manager.build_lexicon() - text from groups and alt_text - gauard against SQL injection - replace all charactors that are -NOT- A-Z,a-z and 0-9 and dot --- with empty stirng")
    print("\n** Need a new table, called 'self_info'.  And it will have the fields : (a) name (b) date_and_time_of_birth, and (c) soul.   Soul is the huge text blob.   'name' is your CE (conversational agent)'s name.. but that name can be in a syn-set (alt_text) so your CE can know all its nicknames")
    print("\n")


if __name__ != "__main__": exit

LOGGING_DIR = "logs"
if not os.path.isdir(LOGGING_DIR):
    os.mkdir(LOGGING_DIR)
    if not os.path.isdir(LOGGING_DIR):
        print("\n*ERR: Terminating: I cannot seem to create the directory '" + LOGGING_DIR + "'")
        exit(0)

logging.basicConfig(encoding='utf-8', format='%(asctime)s %(levelname)s in function %(funcName)s(), (Line# %(lineno)d) %(message)s', level=logging.DEBUG, handlers=[RotatingFileHandler(LOGGING_DIR + '/conalaun.log', maxBytes=110*1024, backupCount=15, mode='a')],)
logging.info("Program starting.")

#notes()
#print("--------- press enter -----")
#input()
print("\n--- Control-C to exit ---(User Guide Later)---")

##################  INTERFACE CODE TO CART ##################
TESTING = False
_CART_FILEDB = ""
_CART_INPUT_FILE = ""
_CART_INPUT_LINE_NUMBER = -1
_CART_RESULTS_DIR = "results_cart_tests" # must be same as in cart.py
#__CART_REPLACED_LINE_10_DO_NOT_REMOVE_THIS_LINE
#__CART_REPLACED_LINE_01_DO_NOT_REMOVE_THIS_LINE

CON_LIST_FILE = "constant_strings.dat"
ALT_TEXT_DIR = "./alt_text"
REG_SR_LIST_FILENAME = "sr_list.inf"
CLASS_FILE_NAME = 'ico'  # ICO file - [I]nput, [C]ontext, [O]utput
GROUP_DIR_NAME = 'groups'
REG_SR_CODE_DIR = "./sr_code"
SR_VARIABLES = dict()
groupinfo = dict()

db_manager.parse_conf()

myconn = None

try:    
    myconn = mysql.connector.connect(host = db_manager.configuration['DB_HOST'], user = db_manager.configuration["DB_USER"], passwd = db_manager.configuration['DB_PASSWORD'], database = db_manager.configuration['DB_NAME'], autocommit = False)

except mysql.connector.Error as e:
    logging.critical("There was a problem connecting to the database '" + db_manager.configuration['DB_NAME'] + "' : " + e.msg + " - Have you ran the ./setupdb.py script to create the database?")    
    if myconn != None:
        if myconn.is_connected():
            myconn.close()
    exit(0)

logging.info("Succesfully connected to database '" + db_manager.configuration['DB_NAME'] + "'")
if not os.path.isdir(GROUP_DIR_NAME):
    os.mkdir(GROUP_DIR_NAME)
    if not os.path.isdir(GROUP_DIR_NAME):        
        logging.critical("Directory '" + GROUP_DIR_NAME + "' does not exist.  I tried to create it but failed!")
        exit(0)
    else:
        logging.info("Succesfully created group directory: '" + GROUP_DIR_NAME + "'")

try:
    groupinfo = term_manager.load_group_contents(logging, GROUP_DIR_NAME)
except Exception:
    exit(0)

ico_last_mod = 0

argv_last_index = len(sys.argv) - 1

for argindex in range(len(sys.argv)):

    if sys.argv[argindex] == '-T':
        TESTING = True

        if argindex == argv_last_index:
            print("ERR: command line arguments are invalid: -T specified but no value after it.\n")
            exit(0)

        FILEDB_AND_LUI_FN = sys.argv[argindex + 1]
        mo = re.match('^(.+):(.+)$', FILEDB_AND_LUI_FN)

        if not bool(mo):
            print("ERR: command line arguments are invalid: value for -T argument ('" + FILEDB_AND_LUI_FN + "'), doesn't match the regex (.+):(.+)\n")
            exit(0)

        _CART_FILEDB = mo.group(1)
        _CART_INPUT_FILE = mo.group(2)

###################################################################################################################
#
#   START:  IN_DEV

try:
    term_manager.update_fast_string_scan_cache(myconn, logging, CON_LIST_FILE, GROUP_DIR_NAME, ALT_TEXT_DIR)
except Exception:     
    logging.error("There was an exception thrown in term_manager.update_fast_string_scan_cache() - program terminating.")    
    exit(0)

#
##############   END:  IN_DEV


cart_input_lines = None
icoFile = 'ico'

if TESTING:
    print("_CART_FILEDB = " + str(_CART_FILEDB))
    print("_CART_INPUT_FILE = " + _CART_INPUT_FILE)

    with open(_CART_INPUT_FILE, 'r') as cart_input_fh:
        cart_input_lines = cart_input_fh.readlines()

while True:    
    lui = None
        
    if TESTING:
        _CART_INPUT_LINE_NUMBER += 1
        #__CART_REPLACED_LINE_05_DO_NOT_REMOVE_THIS_LINE

        if _CART_INPUT_LINE_NUMBER == len(cart_input_lines):
            break

        #__CART_REPLACED_LINE_09_DO_NOT_REMOVE_THIS_LINE

        lui = cart_input_lines[_CART_INPUT_LINE_NUMBER].strip()
        lui = term_manager.adjust_for_apos_s(lui)
        #__CART_REPLACED_LINE_08_DO_NOT_REMOVE_THIS_LINE 

    else:    
        try:
            print("\n]", end="")
            lui = input()
            lui = term_manager.adjust_for_apos_s(lui)
            
        except KeyboardInterrupt as ex:
            break

    try:
        SR_CODE_LINES = fetch_sr_code_lines(REG_SR_CODE_DIR)

        # Commenting out the next 4 lines--  I anticipate that we'll be passing dict "SR_CODE_LINES" to another function in another module to use.
        #for SR_INFO in SR_CODE_LINES.items():
        #    exec(SR_INFO[1])
        #for K in SR_VARIABLES.keys():
        #    print("Value of SR '" + K + "' = " + str(SR_VARIABLES[K]))
                
    except Exception as ex:
        logging.error("There was an exception thrown while loading the Special Replaceable code modules: " + str(ex))

    (parsed_ico_okay, ico_last_mod, groupinfo) = process_ico_file_if_it_exists(CLASS_FILE_NAME, ico_last_mod, REG_SR_LIST_FILENAME, myconn, groupinfo, CON_LIST_FILE, logging, GROUP_DIR_NAME, ALT_TEXT_DIR)
    #CART_INCLUDE_v1.000_dump_tables.py
    #CART_INCLUDE_v1.000_dump_groups.py
     
    if parsed_ico_okay: reload_all_ICOs_from_DB(logging)
    
myconn.close()
myconn = None
#__CART_REPLACED_LINE_06_DO_NOT_REMOVE_THIS_LINE
logging.info("Program terminating.")