#!/usr/bin/python
import ico_compiler
import setupdb
import mysql.connector
import os
import re
import logging
from logging.handlers import RotatingFileHandler
import sys
import cart_dump_table
import resetdb


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
                    return (False, ico_last_mod, groupinfo)

                myconn.commit()
                os.remove(CLASS_FILE_NAME)
                ico_last_mod = 0
                logging.info("Successfully processed an ICO file.")

                if len(group_members_to_add.keys()) > 0:
                    logging.info("Some members added to groups, thus reloading all group members for all groups.")
                    groupinfo = load_group_contents(GROUP_DIR_NAME)

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
    global _cart_area_classextraconditions
    global _cart_area_conceptsymbols
    global _cart_area_srgroupmemberconditions
    global _cart_area_synrrtorr
    global _cart_area_class
    global _cart_area_smolvariables
    global _cart_area_synrrtosr
    global _cart_area_rrgroupmemberconditions
    global _cart_area_rrcatalogue
    global _cart_area_synsrtosr
    global _cart_area_rrrelations
    global _cart_area_concepts
    global _cart_area_classtextlines
    global _cart_area_groups

    known_area = False
    ref = None

    cartlogdirandfile = _CART_RESULTS_DIR + "/" + str(_CART_FILEDB) + "/" + str(_CART_INPUT_LINE_NUMBER) + "/" + area + ".res"

    if area == "classextraconditions":
        ref = _cart_area_classextraconditions
        known_area = True
    elif area == "conceptsymbols":
        ref = _cart_area_conceptsymbols
        known_area = True
    elif area == "srgroupmemberconditions":
        ref = _cart_area_srgroupmemberconditions
        known_area = True
    elif area == "synrrtorr":
        ref = _cart_area_synrrtorr
        known_area = True
    elif area == "class":
        ref = _cart_area_class
        known_area = True
    elif area == "smolvariables":
        ref = _cart_area_smolvariables
        known_area = True
    elif area == "synrrtosr":
        ref = _cart_area_synrrtosr
        known_area = True
    elif area == "rrgroupmemberconditions":
        ref = _cart_area_rrgroupmemberconditions
        known_area = True
    elif area == "rrcatalogue":
        ref = _cart_area_rrcatalogue
        known_area = True
    elif area == "synsrtosr":
        ref = _cart_area_synsrtosr
        known_area = True
    elif area == "rrrelations":
        ref = _cart_area_rrrelations
        known_area = True
    elif area == "concepts":
        ref = _cart_area_concepts
        known_area = True
    elif area == "classtextlines":
        ref = _cart_area_classtextlines
        known_area = True
    elif area == "groups":
        ref = _cart_area_groups
        known_area = True
    if((area == 'class') and (_CART_FILEDB not in ('smol'))):
        return
    if((area == 'classtextlines') and (_CART_FILEDB not in ('concepts', 'smol'))):
        return
    if((area == 'smolvariables') and (_CART_FILEDB not in ('smol'))):
        return
    if((area == 'concepts') and (_CART_FILEDB not in ('concepts', 'smol'))):
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

            if area == "classextraconditions": _cart_area_classextraconditions = ref
            if area == "conceptsymbols": _cart_area_conceptsymbols = ref
            if area == "srgroupmemberconditions": _cart_area_srgroupmemberconditions = ref
            if area == "synrrtorr": _cart_area_synrrtorr = ref
            if area == "class": _cart_area_class = ref
            if area == "smolvariables": _cart_area_smolvariables = ref
            if area == "synrrtosr": _cart_area_synrrtosr = ref
            if area == "rrgroupmemberconditions": _cart_area_rrgroupmemberconditions = ref
            if area == "rrcatalogue": _cart_area_rrcatalogue = ref
            if area == "synsrtosr": _cart_area_synsrtosr = ref
            if area == "rrrelations": _cart_area_rrrelations = ref
            if area == "concepts": _cart_area_concepts = ref
            if area == "classtextlines": _cart_area_classtextlines = ref
            if area == "groups": _cart_area_groups = ref

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
CART_RAW_ICO = "cart_raw_ico"
_cart_area_classextraconditions = None
_cart_area_conceptsymbols = None
_cart_area_srgroupmemberconditions = None
_cart_area_synrrtorr = None
_cart_area_class = None
_cart_area_smolvariables = None
_cart_area_synrrtosr = None
_cart_area_rrgroupmemberconditions = None
_cart_area_rrcatalogue = None
_cart_area_synsrtosr = None
_cart_area_rrrelations = None
_cart_area_concepts = None
_cart_area_classtextlines = None
_cart_area_groups = None

CON_LIST_FILE = "constant_strings.dat"
REG_SR_LIST_FILENAME = "sr_list.inf"
CLASS_FILE_NAME = 'ico'  # ICO file - [I]nput, [C]ontext, [O]utput
GROUP_DIR_NAME = 'groups'
groupinfo = dict()

config = resetdb.parse_conf(resetdb.CONF_FN)
myconn = None

# The two includes below '#CART_INCLUDE_v1.000_init_db.py' and '#CART_INCLUDE_v1.000_clear_groups.py' should be for ALL versions of CONALAUN.
#
#!/usr/bin/python

import resetdb

resetdb.create(True)


if os.path.isdir("./groups"):
   for _CART_entry in os.listdir("./groups"):
      os.remove("./groups/" + _CART_entry)
   os.rmdir("./groups")

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

    if TESTING:
        _CART_INPUT_LINE_NUMBER += 1
        if bool(_cart_area_classextraconditions):
            _cart_area_classextraconditions.close()
            _cart_area_classextraconditions = None
        if bool(_cart_area_conceptsymbols):
            _cart_area_conceptsymbols.close()
            _cart_area_conceptsymbols = None
        if bool(_cart_area_srgroupmemberconditions):
            _cart_area_srgroupmemberconditions.close()
            _cart_area_srgroupmemberconditions = None
        if bool(_cart_area_synrrtorr):
            _cart_area_synrrtorr.close()
            _cart_area_synrrtorr = None
        if bool(_cart_area_class):
            _cart_area_class.close()
            _cart_area_class = None
        if bool(_cart_area_smolvariables):
            _cart_area_smolvariables.close()
            _cart_area_smolvariables = None
        if bool(_cart_area_synrrtosr):
            _cart_area_synrrtosr.close()
            _cart_area_synrrtosr = None
        if bool(_cart_area_rrgroupmemberconditions):
            _cart_area_rrgroupmemberconditions.close()
            _cart_area_rrgroupmemberconditions = None
        if bool(_cart_area_rrcatalogue):
            _cart_area_rrcatalogue.close()
            _cart_area_rrcatalogue = None
        if bool(_cart_area_synsrtosr):
            _cart_area_synsrtosr.close()
            _cart_area_synsrtosr = None
        if bool(_cart_area_rrrelations):
            _cart_area_rrrelations.close()
            _cart_area_rrrelations = None
        if bool(_cart_area_concepts):
            _cart_area_concepts.close()
            _cart_area_concepts = None
        if bool(_cart_area_classtextlines):
            _cart_area_classtextlines.close()
            _cart_area_classtextlines = None
        if bool(_cart_area_groups):
            _cart_area_groups.close()
            _cart_area_groups = None

        if _CART_INPUT_LINE_NUMBER == len(cart_input_lines):
            break

        if os.path.exists(CART_RAW_ICO):
           for file in sorted(os.listdir(CART_RAW_ICO)):
              _src_file = "\"" + CART_RAW_ICO + "/" + file + "\""
              _cart_do_file_cur_line = re.match('^ico' + str(_CART_INPUT_LINE_NUMBER) + '-.*$', file)
              if bool(_cart_do_file_cur_line):
                 os.system("mv " + _src_file + " " + icoFile)
                 (parsed_ico_okay, ico_last_mod) = process_ico_file_if_it_exists(CLASS_FILE_NAME, ico_last_mod, REG_SR_LIST_FILENAME, myconn, groupinfo, CON_LIST_FILE, logging, GROUP_DIR_NAME)
                 if parsed_ico_okay: reload_all_ICOs_from_DB(logging)

        lui = cart_input_lines[_CART_INPUT_LINE_NUMBER].strip()
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

        except KeyboardInterrupt as ex:
            break

    (parsed_ico_okay, ico_last_mod, groupinfo) = process_ico_file_if_it_exists(CLASS_FILE_NAME, ico_last_mod, REG_SR_LIST_FILENAME, myconn, groupinfo, CON_LIST_FILE, logging, GROUP_DIR_NAME)
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

myconn.close()
myconn = None
if TESTING:
    if bool(_cart_area_classextraconditions):
        _cart_area_classextraconditions.close()
        _cart_area_classextraconditions = None
    if bool(_cart_area_conceptsymbols):
        _cart_area_conceptsymbols.close()
        _cart_area_conceptsymbols = None
    if bool(_cart_area_srgroupmemberconditions):
        _cart_area_srgroupmemberconditions.close()
        _cart_area_srgroupmemberconditions = None
    if bool(_cart_area_synrrtorr):
        _cart_area_synrrtorr.close()
        _cart_area_synrrtorr = None
    if bool(_cart_area_class):
        _cart_area_class.close()
        _cart_area_class = None
    if bool(_cart_area_smolvariables):
        _cart_area_smolvariables.close()
        _cart_area_smolvariables = None
    if bool(_cart_area_synrrtosr):
        _cart_area_synrrtosr.close()
        _cart_area_synrrtosr = None
    if bool(_cart_area_rrgroupmemberconditions):
        _cart_area_rrgroupmemberconditions.close()
        _cart_area_rrgroupmemberconditions = None
    if bool(_cart_area_rrcatalogue):
        _cart_area_rrcatalogue.close()
        _cart_area_rrcatalogue = None
    if bool(_cart_area_synsrtosr):
        _cart_area_synsrtosr.close()
        _cart_area_synsrtosr = None
    if bool(_cart_area_rrrelations):
        _cart_area_rrrelations.close()
        _cart_area_rrrelations = None
    if bool(_cart_area_concepts):
        _cart_area_concepts.close()
        _cart_area_concepts = None
    if bool(_cart_area_classtextlines):
        _cart_area_classtextlines.close()
        _cart_area_classtextlines = None
    if bool(_cart_area_groups):
        _cart_area_groups.close()
        _cart_area_groups = None
logging.info("Program terminating.")
