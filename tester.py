#!/usr/bin/python3.7

import fsdb
import os
import sys

DIR_STATES = "dir_states"

if __name__  == '__main__':
    if (len(sys.argv) != 3) and (len(sys.argv) != 4):
        print("baaaaaaaaaaaaaaaad usage !") 

    VERSION = sys.argv[1]
    OPERATION = sys.argv[2]
    NAME = ""

    if len(sys.argv) == 4:
        NAME = sys.argv[3]

    if OPERATION == "clear" and NAME != "":
        print("\n*ERR: do not provide <name> when operation is 'clear'\n")
        sys.exit(0)

    if OPERATION != 'clear' and OPERATION != 'make' and OPERATION != 'install':
        print("\n*ERR: invalid operation given ('" + str(OPERATION) + "'); It must be 'make', 'clear',  or 'install'\n")

    if ((OPERATION == 'make') or (OPERATION == 'install')) and (NAME == "" ):
        print("\n*ERR: for make and install - you must specify a <name>")

    (errors, warnings) = fsdb.run(OPERATION, VERSION, NAME, DIR_STATES)

    if len(errors) == 0:
        print("\nCompleted successfully.\n")
    else:
        if len(errors) > 0:
            print("\n*ERRORS:\n")
            for err in errors:
                print("\t" + err + "\n")


