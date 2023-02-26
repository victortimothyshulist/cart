#!/usr/bin/python
import db_manager
import os
import sys

ARG_CONFRIM = False
ALT_TEXT = "alt_text"
GRP_DIR = "groups"
CONS_FILE = "constant_strings.dat"
SR_FILE = "sr_list.inf"
SR_CODE = "sr_code"


def del_all_files(gdir):

    if not os.path.isdir(gdir): return

    for entry in os.listdir(gdir):
        if not os.path.isfile(gdir + "/" + entry):
            # There should never be anything but files in the groups or sr_code directory.
            print("\n*ERR: There is an entry in directory '" + gdir + "' that is NOT a file!  That's an issue.  Please manually remove it !")
            exit(1)

        os.remove(gdir + "/" + entry)

    os.rmdir(gdir)


def remove_alt_files(dir1, dir2):

    # Please keep, for safety, the line below - dir1 != 'alt_text':
    if dir1 != 'alt_text':
        # Keep this in here for safety! 
        # Please do not recursively delete all files on entire drive
        # deleting files recursively is dangerous!
        return

    if dir2 == "": dir2 = dir1

    for entry in os.listdir(dir2):
        fullpath = dir2 + "/" + entry
        print(fullpath)

        if os.path.isdir(fullpath):
            remove_alt_files(dir1, fullpath)

            found_at = fullpath.find(dir1)
            if found_at != 0:
                print("REFUSE TO DELETE! FOR SAFETY ! " + fullpath)
                exit(0)

            os.rmdir(fullpath)
            #print("Delete directory " + fullpath)
        else:
            #print("Delete file " + fullpath)
            os.remove(fullpath)


if len(sys.argv) == 2:
    if sys.argv[1] == "-YES":
            ARG_CONFRIM = True

if not ARG_CONFRIM:
    print("\n\n\n---------------------------------- ATTENTION ----------------------------------\n\n")
    print("\t\t\tYOU ARE ABOUT TO DESTROY AN ENTIRE CE DATABASE.\n\n")
    print("\t\t\tENTIRE DATABASE WILL BE DELETED WITH NO RESTORE OPTION !! ALSO ALL FILES WILL BE DELETED\n\n\n")

    print("\t\t\tContinue? (to continue and delete please enter YES - all 3 letters all in uppercase.\n\n")
    confirm = input()

    if confirm != 'YES':
        print("\t\t\tSince you did not enter exactly 'YES' (without quotes), I am NOT going to delete.\n\n")
        exit(0)

# Clear ALL knowledge - both database and files.

# Step 1 - Database.

db_manager.parse_conf()
db_manager.connect_to_db()
db_manager.drop_database()

# Step 2 - Files
if os.path.isfile(SR_FILE): 
    os.remove(SR_FILE)
    if os.path.isfile(SR_FILE):
        print("*ERR: could not delete file '" + SR_FILE + "'")
        exit(1)

if os.path.isdir(ALT_TEXT): 
    remove_alt_files("alt_text", "")
    os.rmdir(ALT_TEXT)

del_all_files(GRP_DIR)
del_all_files(SR_CODE)

if os.path.isfile(CONS_FILE): 
    os.remove(CONS_FILE)
    if os.path.isfile(CONS_FILE): 
        print("\n*ERR: could not remove '" + CONS_FILE + "'")
        exit(1)

