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
    global _cart_area_rrrelations
    global _cart_area_rrgroupmemberconditions
    global _cart_area_synsrtosr
    global _cart_area_smolvariables
    global _cart_area_synrrtorr
    global _cart_area_class
    global _cart_area_rrcatalogue
    global _cart_area_classtextlines
    global _cart_area_srgroupmemberconditions
    global _cart_area_conceptsymbols
    global _cart_area_groups
    global _cart_area_synrrtosr
    global _cart_area_classextraconditions
    global _cart_area_concepts

    known_area = False
    ref = None

    cartlogdirandfile = _CART_RESULTS_DIR + "/" + str(_CART_FILEDB) + "/" + str(_CART_INPUT_LINE_NUMBER) + "/" + area + ".res"

    if area == "rrrelations":
        ref = _cart_area_rrrelations
        known_area = True
    elif area == "rrgroupmemberconditions":
        ref = _cart_area_rrgroupmemberconditions
        known_area = True
    elif area == "synsrtosr":
        ref = _cart_area_synsrtosr
        known_area = True
    elif area == "smolvariables":
        ref = _cart_area_smolvariables
        known_area = True
    elif area == "synrrtorr":
        ref = _cart_area_synrrtorr
        known_area = True
    elif area == "class":
        ref = _cart_area_class
        known_area = True
    elif area == "rrcatalogue":
        ref = _cart_area_rrcatalogue
        known_area = True
    elif area == "classtextlines":
        ref = _cart_area_classtextlines
        known_area = True
    elif area == "srgroupmemberconditions":
        ref = _cart_area_srgroupmemberconditions
        known_area = True
    elif area == "conceptsymbols":
        ref = _cart_area_conceptsymbols
        known_area = True
    elif area == "groups":
        ref = _cart_area_groups
        known_area = True
    elif area == "synrrtosr":
        ref = _cart_area_synrrtosr
        known_area = True
    elif area == "classextraconditions":
        ref = _cart_area_classextraconditions
        known_area = True
    elif area == "concepts":
        ref = _cart_area_concepts
        known_area = True
    if((area == 'class') and (_CART_FILEDB not in ('smol'))):
        return
    if((area == 'classtextlines') and (_CART_FILEDB not in ('smol', 'concepts'))):
        return
    if((area == 'smolvariables') and (_CART_FILEDB not in ('smol'))):
        return
    if((area == 'concepts') and (_CART_FILEDB not in ('smol', 'concepts'))):
        return
    if((area == 'groups') and (_CART_FILEDB not in ('smol'))):
        return
    if((area == 'conceptsymbols') and (_CART_FILEDB not in ('concepts'))):
        return
    if((area == 'rrgroupmemberconditions') and (_CART_FILEDB not in ('synandgroups'))):
        return
    if((area == 'srgroupmemberconditions') and (_CART_FILEDB not in ('synandgroups'))):
        return
    if((area == 'synsrtosr') and (_CART_FILEDB not in ('synandgroups'))):
        return
    if((area == 'synrrtosr') and (_CART_FILEDB not in ('synandgroups'))):
        return
    if((area == 'synrrtorr') and (_CART_FILEDB not in ('synandgroups'))):
        return
    if((area == 'rrcatalogue') and (_CART_FILEDB not in ('synandgroups'))):
        return
    if((area == 'rrrelations') and (_CART_FILEDB not in ('synandgroups'))):
        return

    if not known_area:
        print("\n*ERR: called cartlog() with unknown area ('" + area + "').  Check your config file for valid areas.\n")
        exit(1)

    if ref == None:
        try:
            ref = open(cartlogdirandfile, "a")

            if area == "rrrelations": _cart_area_rrrelations = ref
            if area == "rrgroupmemberconditions": _cart_area_rrgroupmemberconditions = ref
            if area == "synsrtosr": _cart_area_synsrtosr = ref
            if area == "smolvariables": _cart_area_smolvariables = ref
            if area == "synrrtorr": _cart_area_synrrtorr = ref
            if area == "class": _cart_area_class = ref
            if area == "rrcatalogue": _cart_area_rrcatalogue = ref
            if area == "classtextlines": _cart_area_classtextlines = ref
            if area == "srgroupmemberconditions": _cart_area_srgroupmemberconditions = ref
            if area == "conceptsymbols": _cart_area_conceptsymbols = ref
            if area == "groups": _cart_area_groups = ref
            if area == "synrrtosr": _cart_area_synrrtosr = ref
            if area == "classextraconditions": _cart_area_classextraconditions = ref
            if area == "concepts": _cart_area_concepts = ref

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
CART_RAW_ICO = "cart_raw_ico"
_cart_area_rrrelations = None
_cart_area_rrgroupmemberconditions = None
_cart_area_synsrtosr = None
_cart_area_smolvariables = None
_cart_area_synrrtorr = None
_cart_area_class = None
_cart_area_rrcatalogue = None
_cart_area_classtextlines = None
_cart_area_srgroupmemberconditions = None
_cart_area_conceptsymbols = None
_cart_area_groups = None
_cart_area_synrrtosr = None
_cart_area_classextraconditions = None
_cart_area_concepts = None

CON_LIST_FILE = "constant_strings.dat"
ALT_TEXT_DIR = "./alt_text"
REG_SR_LIST_FILENAME = "sr_list.inf"
CLASS_FILE_NAME = 'ico'  # ICO file - [I]nput, [C]ontext, [O]utput
GROUP_DIR_NAME = 'groups'
REG_SR_CODE_DIR = "./sr_code"
SR_VARIABLES = dict()
groupinfo = dict()

db_manager.parse_conf()

# The two includes below '#CART_INCLUDE_v1.000_init_db.py' and '#CART_INCLUDE_v1.000_clear_groups.py' should be for ALL versions of CONALAUN.
#
os.system("dos2unix ./clearKB.py")
os.system("chmod +x ./clearKB.py")
os.system("./clearKB.py -YES")

os.system("dos2unix setupdb.py")
os.system("chmod +x setupdb.py")
os.system("./setupdb.py")


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
        if bool(_cart_area_rrrelations):
            _cart_area_rrrelations.close()
            _cart_area_rrrelations = None
        if bool(_cart_area_rrgroupmemberconditions):
            _cart_area_rrgroupmemberconditions.close()
            _cart_area_rrgroupmemberconditions = None
        if bool(_cart_area_synsrtosr):
            _cart_area_synsrtosr.close()
            _cart_area_synsrtosr = None
        if bool(_cart_area_smolvariables):
            _cart_area_smolvariables.close()
            _cart_area_smolvariables = None
        if bool(_cart_area_synrrtorr):
            _cart_area_synrrtorr.close()
            _cart_area_synrrtorr = None
        if bool(_cart_area_class):
            _cart_area_class.close()
            _cart_area_class = None
        if bool(_cart_area_rrcatalogue):
            _cart_area_rrcatalogue.close()
            _cart_area_rrcatalogue = None
        if bool(_cart_area_classtextlines):
            _cart_area_classtextlines.close()
            _cart_area_classtextlines = None
        if bool(_cart_area_srgroupmemberconditions):
            _cart_area_srgroupmemberconditions.close()
            _cart_area_srgroupmemberconditions = None
        if bool(_cart_area_conceptsymbols):
            _cart_area_conceptsymbols.close()
            _cart_area_conceptsymbols = None
        if bool(_cart_area_groups):
            _cart_area_groups.close()
            _cart_area_groups = None
        if bool(_cart_area_synrrtosr):
            _cart_area_synrrtosr.close()
            _cart_area_synrrtosr = None
        if bool(_cart_area_classextraconditions):
            _cart_area_classextraconditions.close()
            _cart_area_classextraconditions = None
        if bool(_cart_area_concepts):
            _cart_area_concepts.close()
            _cart_area_concepts = None

        if _CART_INPUT_LINE_NUMBER == len(cart_input_lines):
            break

        if os.path.exists(CART_RAW_ICO):
           for file in sorted(os.listdir(CART_RAW_ICO)):
              _src_file = "\"" + CART_RAW_ICO + "/" + file + "\""
              _cart_do_file_cur_line = re.match('^ico' + str(_CART_INPUT_LINE_NUMBER) + '-.*$', file)
              if bool(_cart_do_file_cur_line):
                 os.system("mv " + _src_file + " " + icoFile)
                 (parsed_ico_okay, ico_last_mod, groupinfo) = process_ico_file_if_it_exists(CLASS_FILE_NAME, ico_last_mod, REG_SR_LIST_FILENAME, myconn, groupinfo, CON_LIST_FILE, logging, GROUP_DIR_NAME, ALT_TEXT_DIR)
                 if parsed_ico_okay: reload_all_ICOs_from_DB(logging)

        lui = cart_input_lines[_CART_INPUT_LINE_NUMBER].strip()
        lui = term_manager.adjust_for_apos_s(lui)
        if(lui == "/PAUSE"):

            print("\n\t\t* * * CART TESTING PAUSED * * *")
            print("\n\t\t - press enter to continue -")
            input()
            continue
        mo_swp = re.match("^/PAUSE:(.+)$", lui)
        if bool(mo_swp):
            print("\n\t\t* * * CART TESTING PAUSED * * *")
            print("\n\t\t - press enter to continue -")
            lui = mo_swp.group(1)
            print("\n\t\tAfter you press enter, CONALAUN will process:")
            print("\n\t\t	" + lui)
            input()

    else:
        try:
            print("\n]", end="")
            lui = input()
            lui = term_manager.adjust_for_apos_s(lui)

        except KeyboardInterrupt as ex:
            break

    (parsed_ico_okay, ico_last_mod, groupinfo) = process_ico_file_if_it_exists(CLASS_FILE_NAME, ico_last_mod, REG_SR_LIST_FILENAME, myconn, groupinfo, CON_LIST_FILE, logging, GROUP_DIR_NAME, ALT_TEXT_DIR)
    cartlog("class", cart_dump_table.dumptable(myconn, "class", ""))
    cartlog("classtextlines", cart_dump_table.dumptable(myconn, "class_text_lines", ""))
    cartlog("smolvariables", cart_dump_table.dumptable(myconn, "smol_variables", ""))
    cartlog("concepts", cart_dump_table.dumptable(myconn, "concepts", ""))
    cartlog("classextraconditions", cart_dump_table.dumptable(myconn, "class_extra_conditions", ""))
    cartlog("conceptsymbols", cart_dump_table.dumptable(myconn, "concept_symbols", ""))
    cartlog("rrgroupmemberconditions", cart_dump_table.dumptable(myconn, "rr_group_member_conditions", ""))
    cartlog("srgroupmemberconditions", cart_dump_table.dumptable(myconn, "sr_group_member_conditions", ""))
    cartlog("synsrtosr", cart_dump_table.dumptable(myconn, "syn_sr_to_sr", ""))
    cartlog("synrrtosr", cart_dump_table.dumptable(myconn, "syn_rr_to_sr", ""))
    cartlog("synrrtorr", cart_dump_table.dumptable(myconn, "syn_rr_to_rr", ""))
    cartlog("rrcatalogue", cart_dump_table.dumptable(myconn, "rr_catalogue", ""))
    cartlog("rrrelations", cart_dump_table.dumptable(myconn, "rr_relations", ""))
    _CART_grp_str = ''
    
    if os.path.isdir("./groups"):
       for _CART_entry in os.listdir("./groups"):
    
          with open("./groups/" + _CART_entry) as _CART_GFH:
             for _CART_ln_in in _CART_GFH:
                _CART_grp_str += _CART_entry + ':' + _CART_ln_in;
    
    cartlog("groups", _CART_grp_str)
    

    if parsed_ico_okay: reload_all_ICOs_from_DB(logging)

    try:
        SR_CODE_LINES = fetch_sr_code_lines(REG_SR_CODE_DIR)

        # Commenting out the next 4 lines--  I anticipate that we'll be passing dict "SR_CODE_LINES" to another function in another module to use.
        #for SR_INFO in SR_CODE_LINES.items():
        #    exec(SR_INFO[1])
        #for K in SR_VARIABLES.keys():
        #    print("Value of SR '" + K + "' = " + str(SR_VARIABLES[K]))

    except Exception as ex:
        logging.error("There was an exception thrown while loading the Special Replaceable code modules: " + str(ex))

myconn.close()
myconn = None
if TESTING:
    if bool(_cart_area_rrrelations):
        _cart_area_rrrelations.close()
        _cart_area_rrrelations = None
    if bool(_cart_area_rrgroupmemberconditions):
        _cart_area_rrgroupmemberconditions.close()
        _cart_area_rrgroupmemberconditions = None
    if bool(_cart_area_synsrtosr):
        _cart_area_synsrtosr.close()
        _cart_area_synsrtosr = None
    if bool(_cart_area_smolvariables):
        _cart_area_smolvariables.close()
        _cart_area_smolvariables = None
    if bool(_cart_area_synrrtorr):
        _cart_area_synrrtorr.close()
        _cart_area_synrrtorr = None
    if bool(_cart_area_class):
        _cart_area_class.close()
        _cart_area_class = None
    if bool(_cart_area_rrcatalogue):
        _cart_area_rrcatalogue.close()
        _cart_area_rrcatalogue = None
    if bool(_cart_area_classtextlines):
        _cart_area_classtextlines.close()
        _cart_area_classtextlines = None
    if bool(_cart_area_srgroupmemberconditions):
        _cart_area_srgroupmemberconditions.close()
        _cart_area_srgroupmemberconditions = None
    if bool(_cart_area_conceptsymbols):
        _cart_area_conceptsymbols.close()
        _cart_area_conceptsymbols = None
    if bool(_cart_area_groups):
        _cart_area_groups.close()
        _cart_area_groups = None
    if bool(_cart_area_synrrtosr):
        _cart_area_synrrtosr.close()
        _cart_area_synrrtosr = None
    if bool(_cart_area_classextraconditions):
        _cart_area_classextraconditions.close()
        _cart_area_classextraconditions = None
    if bool(_cart_area_concepts):
        _cart_area_concepts.close()
        _cart_area_concepts = None
logging.info("Program terminating.")
