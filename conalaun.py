#!/usr/bin/python
import ico_compiler
import setupdb
import mysql.connector
import os
import re
import logging
from logging.handlers import RotatingFileHandler
import sys


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

def process_ico_file_if_it_exists(CLASS_FILE_NAME, ico_last_mod, REG_SR_LIST_FILENAME, myconn, groupinfo, CON_LIST_FILE, logging, GROUP_DIR_NAME):
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
                    return (False, ico_last_mod)
                    
                myconn.commit()
                os.remove(CLASS_FILE_NAME)
                ico_last_mod = 0
                logging.info("Successfully processed an ICO file.")                

                if len(group_members_to_add.keys()) > 0: 
                    logging.info("Some members added to groups, thus reloading all group members for all groups.")
                    groupinfo = load_group_contents(GROUP_DIR_NAME)

                return (True, ico_last_mod)
            else:
                ico_last_mod = os.path.getmtime(CLASS_FILE_NAME)
                return (False, ico_last_mod)
        else:            
            logging.info("I won't bother trying to reprocess the ICO.  The last time I tried, it failed, and you haven't changed the file yet.")
            return (False, ico_last_mod)
    else:
        return (False, ico_last_mod)


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


def load_group_contents(grp_dn):    
    groupinfo = dict()

    for gr_file in os.listdir(grp_dn):
        orig_gr_file = gr_file
        if not os.path.isfile(grp_dn + "/" + gr_file): continue
        mo = re.match('^(.+)\.txt$', gr_file)
        if not bool(mo): continue
        gr_file = mo.group(1)
        groupinfo[gr_file] = set()

        with open(grp_dn + "/" + orig_gr_file, 'r') as GF:
            for gr_entry in GF.readlines():
                gr_entry = gr_entry.strip()
                gr_entry = gr_entry.replace(" ", "_")
                if gr_entry != "": groupinfo[gr_file].add(gr_entry)

    return groupinfo
    

def notes():
    print("\nThe \"apostrope-s\" thing is NOT an issue for OUTPUT SIDE! just replace bob:'s with value of 'bob' - substring search/replace, without needing to split up line by spaces. Apostrope only allowed in TOLs anyway.")
    print("\nFor apostrope-s on INPUT SIDE - very simple, just do a REGEX search [(\S)'s] and replace with:  [\\1 's] - square brackets not part of search/replace.  Once the LUI has a space inserted before all apostrope-s instance, it will match with ICO:I")    
    print("\nfor user-guide: underscore -can- be part of an RR identifier.  Also group name can have underscore.")    
    print("\nTAKE care of the comment: #TO DO  TO DO TO DO --  Go and check that all \"return\" statements in this function return False for error and only when get to end of function do we return True")
    print("\nTEST the encoding of star ('*') in a O-3 type line.  and put in user guide.")
    print("\nVIP: very important: for E.R. diagram explanation doc -- smol_variables table - for RR there is no entry, instead 'rr_relations' must be consulted.  *NO* rr_relations entry for O-4 (TOL) lines though. not needed")
    print("\nAlso note for ER explanation -- if the 'smol_variables' table has NULL for 'sr_name', then that variable is an RR, and the 'rr_relations' table should be consulted.")
    print("\n*** ER diagram - 'o2_variables' now called 'smol_variables'")
    print("\nA concept may have ZERO constants - simply a single vnov:group ! Test that Conalaun accepts this and creates an interpretation (this is later, i know - Stage '2')")
    print("\n>>>>>>>>>> LUI to be matched *ONLY* with 'I' line- *NOT* context lines. Context ONLY created/edited/deleted by SMOLs.")
    print("\n[Note (done)] - System will maintain a file 'constant_strings.dat' - distinct set of constant substrings found across all I-lines of all ICOs.  To be used as 'type-0' symbols for NovaGLI style LUI-2-interpretation creation.")
    print("\n--NO hierarchical matching!! using novagli to create interpretations though!!!! and *NO* matching LUI with context -ONLY I-lines.")    
    print("\n[Put in User Guide]: Literals inside quotes in SMOLs -- are auto converted to spaces)")
    print("\ncidref and tidref should be FOREIGN KEYS -- or indexes.. figure out the syntax for that!")
    print("\n** [ DOCS reminder ] : remember, for a given RR, in relations table, only index:0 for I-line. [ b/c all I-lines must have same set of replaceables")
    print("\n** [ DOCS reminder ] : for C2 lines - the 'exist' field (**IN class_text_lines'**) *IS NOT* used- instead the 'exist' field in *_group_member_conditions is used")    
    print("\n** NOTE: when rendering database entries for an ICO into 'textbox' for editing.. have to know where all places to convert spaces to underscores. (this is done, table 'class_text_lines' retains the underscores - but in other tables, the underscores are replaced by spaces)")
    print("\nFor user-guide: what if you want a substring of LUI to match an SR? like 'SHE' ?  you can't have SRs (variable or literal) in I-lines, only C1, C2, and SMOLs.  So how to match? easy just use an RR then an 'is syn'.   victor:person (on your I-line), then a C2 line with 'victor is syn HE")
    print("\n*We should re-use the function in vcck.py ('replace_with_actual_date' - 187 lines) to have 'auto-created' group 'date'.  System will not add any values to 'date' group.  It is auto created if deleted and created on start of program.  Also 'number' is auto created and matches \d+(\.\d*)?")    


if __name__ != "__main__": exit

LOGGING_DIR = "logs"
if not os.path.isdir(LOGGING_DIR):
    os.mkdir(LOGGING_DIR)
    if not os.path.isdir(LOGGING_DIR):
        print("\n*ERR: Terminating: I cannot seem to create the directory '" + LOGGING_DIR + "'")
        exit(0)

logging.basicConfig(encoding='utf-8', format='%(asctime)s %(levelname)s in function %(funcName)s(), (Line# %(lineno)d) %(message)s', level=logging.DEBUG, handlers=[RotatingFileHandler(LOGGING_DIR + '/conalaun.log', maxBytes=200*1024, backupCount=10, mode='a')],)
logging.info("Program starting.")

#notes()
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
REG_SR_LIST_FILENAME = "sr_list.inf"
CLASS_FILE_NAME = 'ico'  # ICO file - [I]nput, [C]ontext, [O]utput
GROUP_DIR_NAME = 'groups'
groupinfo = dict()

config = setupdb.parse_conf(setupdb.CONF_FN)
myconn = None

try:
    myconn = mysql.connector.connect(host = config['DB_HOST'], user = config["DB_USER"], passwd = config['DB_PASSWORD'], database = config['DB_NAME'], autocommit = False)

except mysql.connector.Error as e:
    logging.critical("There was a problem connecting to the database '" + config['DB_NAME'] + "' : " + e.msg + " - Have you ran the ./setupdb.py script to create the database?")    
    if myconn != None:
        if myconn.is_connected():
            myconn.close()
    exit(0)

logging.info("Succesfully connected to database '" + config['DB_NAME'] + "'")
if not os.path.isdir(GROUP_DIR_NAME):
    os.mkdir(GROUP_DIR_NAME)
    if not os.path.isdir(GROUP_DIR_NAME):        
        logging.critical("Directory '" + GROUP_DIR_NAME + "' does not exist.  I tried to create it but failed!")
        exit(0)
    else:
        logging.info("Succesfully created group directory: '" + GROUP_DIR_NAME + "'")

groupinfo = load_group_contents(GROUP_DIR_NAME)
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
cart_input_lines = None
icoFile = 'ico'

if TESTING:
    print("_CART_FILEDB = " + str(_CART_FILEDB))
    print("_CART_INPUT_FILE = " + _CART_INPUT_FILE)

    with open(_CART_INPUT_FILE, 'r') as cart_input_fh:
        cart_input_lines = cart_input_fh.readlines()

while True:    
    lui = None
    print("\n]", end="")
    
    if TESTING:
        _CART_INPUT_LINE_NUMBER += 1
        #__CART_REPLACED_LINE_05_DO_NOT_REMOVE_THIS_LINE

        if _CART_INPUT_LINE_NUMBER == len(cart_input_lines):
            break

        #__CART_REPLACED_LINE_09_DO_NOT_REMOVE_THIS_LINE

        lui = cart_input_lines[_CART_INPUT_LINE_NUMBER].strip()
        #__CART_REPLACED_LINE_08_DO_NOT_REMOVE_THIS_LINE 

    else:    
        try:
            lui = input()

        except KeyboardInterrupt as ex:
            break

    (parsed_ico_okay, ico_last_mod) = process_ico_file_if_it_exists(CLASS_FILE_NAME, ico_last_mod, REG_SR_LIST_FILENAME, myconn, groupinfo, CON_LIST_FILE, logging, GROUP_DIR_NAME)
    if parsed_ico_okay: reload_all_ICOs_from_DB(logging)
             
myconn.close()
myconn = None
#__CART_REPLACED_LINE_06_DO_NOT_REMOVE_THIS_LINE
logging.info("Program terminating.")
print("BYE!!  --delete this later")