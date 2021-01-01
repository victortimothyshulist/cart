#!/usr/bin/python3.7
import os
import sys
import re

UPDATE_DIR = "./updates"

# Please verify CONFIG variable (in get_files() below) is accurate.

def get_files(VERSION):
    state_seen = set()
    CONFIG = "testpackages"

    STATE_DIRS = ()
    STATE_FILES = ()

    CF = CONFIG + "/" + VERSION + ".conf"

    if not os.path.isfile(CF):
        return("Config file ('"  + CF + "') does not exist.", CONFIG, STATE_DIRS, STATE_FILES, set(), set())
    
    try:
        
        with open(CF, 'r') as fh:
            for line in fh:
                mo = re.match('^\s*state_(dir|file)s\s*=\s*(.*?)\s*$', line)
                if bool(mo):
                    type = mo.group(1)
                    info = mo.group(2)
                    info = info.strip()
                    info = info.replace(' ', '')

                    if info == '':
                        return("No values given for 'state_" + type + "s' in config file.", CONFIG, STATE_DIRS, STATE_FILES, set(), set())
                    state_seen.add(type)

                    if type == 'dir':
                        STATE_DIRS = info.split(',')
                    else:
                        STATE_FILES = info.split(',')

    except Exception as ex:
        return("\n*ERR: cannot open file '" + CF + "': " + str(ex), CONFIG, STATE_DIRS, STATE_FILES , set(), set())

    DIRSET = set(STATE_DIRS)
    FILESET = set(STATE_FILES)

    if ('dir' not in state_seen) or ('file' not in state_seen):
        return("Either 'state_dirs' and/or 'state_files' not mentioned in your config file.", CONFIG, STATE_DIRS, STATE_FILES, DIRSET, FILESET)

    return ("", CONFIG, STATE_DIRS, STATE_FILES, DIRSET, FILESET)

def usage():
    print("\nUsage:\n")
    print("\t./tcm.py <version> [create|clear|verify|install|edit] <name> [path/to/myfile]\n") 
    print("\t\t<version> : a version file in ./testpackages/* (without the '.conf' extension)")
    print("\n\t\tcreate : creates a new File State Database file (*.tar.gz)")
    print("\t\tclear : clears out all files and directories for a given version")
    print("\t\tverify : Checks if a given File State database tar.gz file contains all files and directories it supposed to.)")
    print("\t\tedit : extracts <name>.tar.gz and replaces 'path/to/myfile' (inside the tar.gz) with file 'myfile' in current directory.")
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


def run(OPERATION, VERSION, NAME, PATH_AND_FILE, OVER_RIDE_DIR = ""):
    (err, CONFIG, STATE_DIRS, STATE_FILES, DIRSET, FILESET) = get_files(VERSION)

    errors = list()
    warnings = list()

    if not os.path.isdir(UPDATE_DIR):
        os.mkdir(UPDATE_DIR)
        if not os.path.isdir(UPDATE_DIR):
            errors.append("Cannot create directory: '" + UPDATE_DIR + "'")
            return (errors, warnings)

    if err != "":
        errors.append(err)
        return (errors, warnings) 

    if OPERATION == 'edit':
        mo = re.match('^/(.+)$', PATH_AND_FILE)
        _PATH = ""
        _FILE = ""

        if bool(mo):
            PATH_AND_FILE = mo.group(1)
        else:
            errors.append("Path passed in for 'edit' does not start with '/'")
            return (errors, warnings)

        mo = re.match('^(.+)/(.+)$', PATH_AND_FILE)
        if not bool(mo):
            # ok, it is a single filename at root.
            _FILE = PATH_AND_FILE
            _PATH = ''
        else:
            # there is a path and a filename...
            _PATH = '/' + mo.group(1)
            _FILE = mo.group(2)

        _SRC_FILE = UPDATE_DIR + "/" + _FILE

        #print(_PATH + " :: " + _FILE + "::" + _SRC_FILE)

        if not os.path.isfile(_SRC_FILE):
            errors.append("Filename given ('" + _FILE + "') of path ('" + PATH_AND_FILE + "') does not exist in '" + UPDATE_DIR + "' directory.  Please create it.")
            return (errors, warnings)

        TEMPDIR = "temp_dir_for_edit"
       
        err = safe_rec_del(TEMPDIR)
        if err != "":
            errors.append(err)

        os.mkdir(TEMPDIR)
        if not os.path.isdir(TEMPDIR):
            errors.append("Was not able to create directory '" + TEMPDIR + "'")
          
        arcname = CONFIG + "/files/" + VERSION + "/" + NAME + ".tar.gz"

        if not os.path.isfile(arcname):
            errors.append(arcname + " does not exist.")
            return (errors, warnings)

        cmd = "tar zxf " + arcname + " -C " + TEMPDIR
        res = os.system(cmd)

        if res != 0:
            errors.append("Problem running '" + cmd + "' - " + str(res))
            return (errors, warnings)

        print("_PATH = [" + _PATH + "]")
        print("_FILE = [" + _FILE + "]")

        editdst = TEMPDIR + _PATH 
        copy_cmd = "cp " + _SRC_FILE + " ./" + editdst + "/" + _FILE
   
        print(copy_cmd)

        if not os.path.isdir(editdst):
            errors.append("'" + _PATH + "' does not exist in archive '" + NAME + "'")
            return (errors, warnings)
     
        res = os.system(copy_cmd)

        if res != 0:
            errors.append("Problem running command '" + copy_cmd + "'")
            return (errors, warnings)

        cmd = "tar czf " + arcname + " -C " + TEMPDIR + " ."
        res = os.system(cmd)

        if res != 0:
            errors.append("Problem running command '" + cmd + "': " + str(res))
            return (errors, warnings)

        return (errors, warnings)

    elif OPERATION == 'clear':

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
    
    elif OPERATION == 'create':
 
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

        if not os.path.isfile(arcname):
            errors.append(arcname + " does not exist.")
            return (errors, warnings)

        cmd = "tar zxf " + arcname + " -C ."

        res = os.system(cmd)
        if res != 0:
            errors.append("Problem running '" + cmd + "' - " + str(res))
            return (errors, warnings)

        return run('verify', VERSION, NAME, PATH_AND_FILE, OVER_RIDE_DIR)

    elif OPERATION == 'verify':
        arcname = CONFIG + "/files/" + VERSION + "/" + NAME + ".tar.gz"

        if not os.path.isfile(arcname):
            errors.append(arcname + " does not exist.")
            return (errors, warnings)

        outfile = '_temp_out.txt'

        if os.path.isfile(outfile):
            os.remove(outfile)
            if os.path.isfile(outfile):
                errors.append("Cannot remove file '" + outfile + "'")
                return (errors, warnings)

        cmd = "tar ztf " + arcname + " > " + outfile
        res = os.system(cmd)

        if res != 0:
            errors.append("Problem running '" + cmd + "' - " + str(res))
            return (errors, warnings)
        
        if not os.path.isfile(outfile):
            errors.append("Ran command '" + cmd + "' but yet file '" + outfile + " doesn't exist!")
            return (errors, warnings)

        top_level_dirs_seen = set()
        top_level_files_seen = set()

        try:
            
            with open(outfile, 'r') as fh:
                for line in fh:
                    line = line.strip()

                    mo = re.match('^(\.\/)(.*)', line)
                    if bool(mo):
                        line = mo.group(2)

                    # if no '/' in it at all, then it is a top level file.
                    # otherwise, get the top level directory.
                    mo = re.match('^(.+?)/.*', line)
                    if not bool(mo):
                        top_level_files_seen.add(line)
                    else:
                        top_level_dirs_seen.add(mo.group(1))

        except Exception as ex:
            errors.append("Can't open file '" + outfile + "'; " + str(ex))
            return (errors, warnings)

        dir_diff = DIRSET.difference(top_level_dirs_seen)
        file_diff = FILESET.difference(top_level_files_seen)

        for missing in dir_diff:
            warnings.append("Directory: '" + missing + "' missing from archive.")

        for missing in file_diff:
            warnings.append("File: '" + missing + "' missing from archive.")

        return (errors, warnings) 

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if __name__  == '__main__':

    VERSION = sys.argv[1]
    OPERATION = sys.argv[2]
    NAME = ""
    PATH_AND_FILE = ""

    print("\nVERSION: " + str(VERSION))
    print("OPERATION: " + str(OPERATION))

    if OPERATION != 'clear' and len(sys.argv) != 4:
        print("\n*ERR: wrong number of arguments for '" + OPERATION + "' operation.\n")
        sys.exit(0)

    if OPERATION == 'clear' and len(sys.argv) != 3:
        print("\n*ERR: wrong number of arguments for 'clear' operation.\n")
        sys.exit(0)

    if OPERATION == 'edit':
        PATH_AND_FILE = sys.argv[3]
        NAME = VERSION
        print("PATH_AND_FILE: " + PATH_AND_FILE)
        print("NAME: " + NAME + "\n")
    
    (errors, warnings) = run(OPERATION, VERSION, NAME, PATH_AND_FILE)

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

