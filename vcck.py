#!/usr/bin/python3.7
import os
import sys
import re

###########################################  INTERFACE CODE TO CART ################################################

DEBUGGING = False
TESTING = False

_CART_FILEDB = ""
_CART_INPUT_FILE = ""
_CART_INPUT_LINE_NUMBER = -1
_CART_RESULTS_DIR = "results_cart_tests" # must be same as in cart.py

#__CART_REPLACED_LINE_01_DO_NOT_REMOVE_THIS_LINE

def cartlog(area, message):
    #__CART_REPLACED_LINE_02_DO_NOT_REMOVE_THIS_LINE

    known_area = False
    ref = None

    cartlogdirandfile = _CART_RESULTS_DIR + "/" + str(_CART_FILEDB) + "/" + str(_CART_INPUT_LINE_NUMBER) + "/" + area + ".res"
   
    #__CART_REPLACED_LINE_03_DO_NOT_REMOVE_THIS_LINE

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

###################################################################################################################

argv_last_index = len(sys.argv) - 1

for argindex in range(len(sys.argv)):

    if sys.argv[argindex] == '-T':
        TESTING = True

        if argindex == argv_last_index:
            print("ERR: command line arguments are invalid: -T specified but no value after it.\n")
            exit(0)

        FILEDB_AND_LUI_FN = sys.argv[argindex + 1]
        mo = re.match('^(\d+|current):(.+)$', FILEDB_AND_LUI_FN)

        if not bool(mo):
            print("ERR: command line arguments are invalid: value for -T argument ('" + FILEDB_AND_LUI_FN + "'), doesn't match the regex (\d+):(.+)\n")
            exit(0)

        _CART_FILEDB = mo.group(1)
        _CART_INPUT_FILE = mo.group(2)

###################################################################################################################
if TESTING:
    print("_CART_FILEDB = " + str(_CART_FILEDB))
    print("_CART_INPUT_FILE = " + _CART_INPUT_FILE)


cart_input_lines = None

if TESTING == True:
    with open(_CART_INPUT_FILE, 'r') as cart_input_fh:
        cart_input_lines = cart_input_fh.readlines()

while True:
    
    if TESTING:
        _CART_INPUT_LINE_NUMBER += 1

        #__CART_REPLACED_LINE_05_DO_NOT_REMOVE_THIS_LINE

        if _CART_INPUT_LINE_NUMBER == len(cart_input_lines):
            break

        lui = cart_input_lines[_CART_INPUT_LINE_NUMBER].strip()
        #CART_INCLUDE_v1.000_file1.py
    else:
        lui = input()

        if lui == ".":
            break

    print("PROCESSING LINE : [" + lui + "]")

#__CART_REPLACED_LINE_06_DO_NOT_REMOVE_THIS_LINE


