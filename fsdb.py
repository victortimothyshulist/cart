#!/usr/bin/python3.7
import os
import sys
import re

# Please verify CONFIG variable (in get_files() below) is accurate.

def get_files(VERSION):

    CONFIG = "testpackages"

    STATE_DIRS = ()
    STATE_FILES = ()

    CF = CONFIG + "/" + VERSION + ".conf"
    if not os.path.isfile(CF):
        return("Config file ('"  + CF + "') does not exist.", CONFIG, STATE_DIRS, STATE_FILES)
    
    try:
        
        with open(CF, 'r') as fh:
            for line in fh:
                mo = re.match('^\s*state_(dir|file)s\s*=\s*(.*?)\s*$', line)
                if bool(mo):
                    type = mo.group(1)
                    info = mo.group(2)

                    if type == 'dir':
                        STATE_DIRS = info.split(',')
                    else:
                        STATE_FILES = info.split(',')

    except Exception as ex:
        return("\n*ERR: cannot open file '" + CF + "': " + str(ex), CONFIG, STATE_DIRS, STATE_FILES)

    return ("", CONFIG, STATE_DIRS, STATE_FILES)

def usage():
    print("\nUsage:\n")
    print("\tfsdb <version> [make|clear|install] <name>\n") 
    print("\t\t<version> : a version file in ./testpackages/* (without the '.conf' extension)")
    print("\n\t\tmake : creates a new File State Database file (*.tar.gz)")
    print("\t\tclear : clears out all files and directories for a given version")
    print("\t\tinstall : unzips and untars the <name> file into ./vcck (from testpackages/files/v1.000/<name>.tar.gz)")
    print("\n\t\t<name> : name of file to make.") 
    print("\n")
    sys.exit(0)

def safe_rec_del(thedir: str) -> None:
    thedir_stripped = thedir.strip()
    
    mo = re.match('^[a-zA-Z].*', thedir)
    if not bool(mo):
        return("Refusing to perform rm -rf on dir '" + thedir + "' - directory to delete must start with a alphabetical charactor.")
    
    if (thedir_stripped[0] == '.') or (thedir_stripped[0] == '/'):
        return("Refusing to perform rm -rf on dir '" + thedir + "'")

    rec_del_cmd = "rm -rf " + thedir_stripped
    res = os.system(rec_del_cmd)

    if res != 0:
        return("\nProblem executing '" + rec_del_cmd + "'")

    return ""


def run(OPERATION, VERSION, NAME, OVER_RIDE_DIR = ""):
    (err, CONFIG, STATE_DIRS, STATE_FILES) = get_files(VERSION)

    errors = list()
    warnings = list()

    if err != "":
        errors.append(err)
        return (errors, warnings) 

    if OPERATION == 'clear':

        for dir in STATE_DIRS:
            err = safe_rec_del(dir)
            if err != "":
                errors.append(err)

        for file in STATE_FILES:
            if os.path.isfile(file):
                os.remove(file)
                if os.path.isfile(file):
                    errors.append("Could not remove file '" + file + "'")

        return (errors, warnings) 
    
    elif OPERATION == 'make':
        arcname = ""

        if OVER_RIDE_DIR == "":
            arcname = CONFIG + "/files/" + VERSION + "/" + NAME + ".tar.gz"
        else:
            arcname = OVER_RIDE_DIR + "/" + NAME + ".tar.gz"

        inc_list = ""
  
        for dir in STATE_DIRS:
            if os.path.isdir(dir):
                inc_list += (" " + dir + "/.")
            else:
                warnings.append("dir '" + dir + "' - doesn't exist.")
        for file in STATE_FILES:
            if os.path.isfile(file):
                inc_list += (" " + file)
            else:
                warnings.append("file '" + file + "' - doesn't exist.")
  
        if inc_list == "":
            warnings.append("No files or directories exist for this version right now, so not creating the archive.")
            return (errors, warnings) 

        cmd = "tar czf " + arcname + inc_list
        res = os.system(cmd)
        if res != 0:
            errors.append("Problem running '" + cmd + "' - " + str(res) + "\n")
            return (errors, warnings) 

        return (errors, warnings) 

    elif OPERATION == 'install':
        arcname = CONFIG + "/files/" + VERSION + "/" + NAME + ".tar.gz"
        cmd = "tar zxf " + arcname + " -C ."
        res = os.system(cmd)
        if res != 0:
            errors.append("Problem running '" + cmd + "' - " + str(res))
       
        return (errors, warnings) 

 
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if __name__  == '__main__':
    if (len(sys.argv) != 3) and (len(sys.argv) != 4):
        usage()

    VERSION = sys.argv[1]
    OPERATION = sys.argv[2]
    NAME = ""

    if len(sys.argv) == 4:
        NAME = sys.argv[3]

    print("\nVERSION: " + str(VERSION))
    print("OPERATION: " + str(OPERATION))
    print("NAME: " + str(NAME))

    if OPERATION == "clear" and NAME != "":
        print("\n*ERR: do not provide <name> when operation is 'clear'\n")
        sys.exit(0)

    if OPERATION != 'clear' and OPERATION != 'make' and OPERATION != 'install':
        print("\n*ERR: invalid operation given ('" + str(OPERATION) + "'); It must be 'make', 'clear',  or 'install'\n")
        usage()

    if ((OPERATION == 'make') or (OPERATION == 'install')) and (NAME == "" ):
        print("\n*ERR: for make and install - you must specify a <name>")
        usage()

    (errors, warnings) = run(OPERATION, VERSION, NAME)

    if len(errors) == 0 and len(warnings) == 0:
        print("\nCompleted successfully.\n")
    else:
        if len(errors) > 0: 
            print("\n*ERRORS:\n")
            for err in errors:
                print("\t" + err + "\n")
    
        if len(warnings) > 0:
            print("\n*WARNINGS:\n")
            for warning in warnings: 
                print("\t" + warning + "\n")

        usage()
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------



