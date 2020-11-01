#!/usr/bin/python3.7
import os
import sys
import re
import datetime

CURRENT_LIST = list()
CURRENT = False
DIR_STATE = "dir_states"
TEMP_ARCHIVE_UNPACK_DIR = "_temp_arc_unpack"
VCCK_PROGRAM = "./vcck.py"
VCCK_PROGRAM_TEMP = "./vcck-cart-temp.py"

TEST_RESULT_DIR = "results_cart_tests"

TEST_RESULT_DIR = TEST_RESULT_DIR.strip()

if TEST_RESULT_DIR[0] == ".":
    print("*ERR: do not have 'TEST_RESULT_DIR' start with '.'\n")
    exit(0)

if TEST_RESULT_DIR[0] == "/":
    print("*ERR: do not have 'TEST_RESULT_DIR' start with '/'\n")
    exit(0)

rm_prev_outdir = "rm -rf " + TEST_RESULT_DIR
res = os.system(rm_prev_outdir)

if res !=0 :
    print("\n*ERR: error when trying to clean up. Error executing '" + rm_prev_outdir + "'")
    exit(0)

os.mkdir(TEST_RESULT_DIR)

if not os.path.isdir(DIR_STATE):
    os.mkdir(DIR_STATE)
    if not os.path.isdir(DIR_STATE):
        print("\n*ERR: was not able to create directory '" + DIR_STATE + "'")
        exit(1)


def backup_existing():
    epoch = str(datetime.datetime.now())
    epoch = epoch.replace(' ','_')
    epoch = epoch.replace(':','_')
    epoch = epoch.replace('-','_')
    epoch = epoch.replace('.','_')

    dirs_to_inc_in_bu = ''
    any = False

    for backupdir in ('shared-lists', 'conversation-history', 'sessions', 'tls_csv', 'interpretations', 'compiled-classes'):
        if os.path.isdir(backupdir):
            dirs_to_inc_in_bu += backupdir + '/. '
            any = True

    backup_dir_cmd = "tar czf " + DIR_STATE + "/" + epoch + ".tar.gz " + dirs_to_inc_in_bu
    if os.path.isfile("template_words_file.data"):
        backup_dir_cmd += "template_words_file.data"
        any = True

    if not any: return

    re = os.system(backup_dir_cmd)

    print(str(any) + " > " + backup_dir_cmd)

    if re != 0:
        print("\n*ERR: problem backing up directory state")
        exit(1)

def sort_all_files(thedir):
    # sort all files in directory <thedir> recursively.

    for entry in os.listdir(thedir):
        entry_fp = thedir + "/" + entry

        if os.path.isdir(entry_fp):
            sort_all_files(entry_fp)
        else:

            mo = re.match('^(.+)/(.+)$', entry_fp)
            if not bool(mo): continue

            dirpart = mo.group(1)
            filename = mo.group(2)
            temp_sorted_filename = dirpart + "/" + filename + ".ts"
            sort_cmd = "sort " + entry_fp + " > " + temp_sorted_filename
            res = os.system(sort_cmd)

            if res != 0:
                print("*ERR: problem executing '" + sort_cmd + "'")

            try:
                os.remove(entry_fp)

                if os.path.isfile(entry_fp):
                    print("*ERR: error could not remove file '" + entry_fp + "'")
                    exit(0)

            except Exception as ex:
                    print("*ERR: error while trying to remove file '" + entry_fp + "'" + str(ex))

            os.rename(temp_sorted_filename, entry_fp)

            if os.path.isfile(temp_sorted_filename):
                print("*ERR: could not rename file '" + temp_sorted_filename + "' to '" + entry_fp + "'")
                exit(0)


def get_file_list_rec(base, theset, thedir):
    for entry in os.listdir(thedir):
        entry_fp = thedir + "/" + entry

        if os.path.isdir(entry_fp):
            get_file_list_rec(base, theset, entry_fp)
        else:
            mo = re.match('^' + base + '/(.+)$', entry_fp)
            if bool(mo):
                rest = mo.group(1)

            theset.add(rest)


def compare_dirs(emsg, dir_a, dir_b):
    files_a = set()
    files_b = set()

    get_file_list_rec(dir_a, files_a, dir_a)
    get_file_list_rec(dir_b, files_b, dir_b)

    issues = list()

    for file_in_a in files_a:
        if not file_in_a in files_b:
            issues.append("\n*ERR: " + emsg + ", File: '" + file_in_a + "' is in '" + dir_a + "', but not in '" + dir_b + "'")

    for file_in_b in files_b:
        if not file_in_b in files_a:
            issues.append("\n**ERR: " + emsg + ", File: '" + file_in_b + "' is in '" + dir_b + "', but not in '" + dir_a + "'")

    if len(issues):
        for issue in issues:
            print(issue)
        exit(0)

    DIFF_FN = "diff.txt"

    for afile in files_a:

        if os.path.isfile(DIFF_FN):
            os.remove(DIFF_FN)
            if os.path.isfile(DIFF_FN):
                print("\n*ERR: cannot remove '" + DIFF_FN + "'")
                exit(0)

        diff_cmd = "diff " + dir_a + "/" + afile + " " + dir_b + "/" + afile + " > " + DIFF_FN
        res = os.system(diff_cmd)

        if (res != 0) and (res != 256):
            print("\n*ERR: " + emsg + " problems running the command '" + diff_cmd + "'\n")
            exit(0)

        diffs = list()

        try:
            with open(DIFF_FN, 'r') as dfh:
                diffs = dfh.readlines()

        except Exception as ex:
            print("\n*ERR: problem loading file '" + DIFF_FN + "'")
            exit(0)

        if len(diffs):
            print("\n*ERR: " + emsg + " - different results for file '" + dir_a + "/" + afile + "' -VERSUS- '" + dir_b + "/" + afile + "'")
            print("-----------------------------------------------------------")
            print("                 DIFF  OUTPUT                              ")
            print("-----------------------------------------------------------")
            print(diff_cmd)
            print("-----------------------------------------------------------")

            for line in diffs:
                print(line, end="")
            print("-----------------------------------------------------------")
            print("> : latest test run")
            print("< :  in expected results archive.\n") 
            exit(0)



def validate(emsg, fp_archive, temp_dir, resdir):
    temp_unarc_cmd = "tar -xzf " + fp_archive  + " -C " + temp_dir
    #print("about to execute : " + temp_unarc_cmd)
    #print("press enter")
    #input()
    print(temp_unarc_cmd)
    print('enter...')
    input()

    res = os.system(temp_unarc_cmd)

    #print('hit enter')
    #input()

    if res != 0:
        print("\n*ERR: problem unpacking the archive '" + fp_archive + "'")
        exit(0)
    
    compare_dirs(emsg, temp_dir, resdir)
    safe_rec_del(temp_dir)
    

def create_dir_if_not_exist(thedir):
    try:
        if not os.path.exists(thedir):
            os.mkdir(thedir)
            if not os.path.exists(thedir):
                print("*ERR: Cannot create directory: " + thedir)
                exit(0)
    except Exception as ex:
        print("*ERR: problem creating directory - " + str(ex))
    return


def safe_rec_del(thedir: str) -> None:
    thedir_stripped = thedir.strip()
    if (thedir_stripped[0] == '.') or (thedir_stripped[0] == '/'):
        print("\n*ERR: refusing to perform rm -rf on dir '" + thedir + "'")
        exit(0)

    rec_del_cmd = "rm -rf " + thedir_stripped
    res = os.system(rec_del_cmd)

    #print(rec_del_cmd)
    if res != 0:
        print("\n*ERR: problem executing '" + rec_del_cmd + "'")
        exit(0)


def load_config(file: str, dir: str) -> None:
    oncurrent = False

    data = list() 
    filedb = None
    areas = set()
    
    with open(file, 'r') as fh:

        for line in fh.readlines():
            sline = line.strip()

            if sline == '[]':
                oncurrent = True
                continue

            if sline == "": continue
            if sline[0] == '#': continue

            mo = re.match('^areas\s*=\s*(.+?)\s*$', sline)

            if bool(mo):
                areas_str = mo.group(1).strip()
                listareas = areas_str.split(",")

                for rarea in listareas:
                    rarea = rarea.strip()
                    rarea = rarea.lower()
                    if rarea == "": continue

                    mo2 = re.match('^[a-z]+$', rarea)

                    if not bool(mo2):
                        print("\n*ERR: one of the areas given is invalid ('" + rarea + "') - must be only alphabetical charactors.\n")
                        exit(0)

                    if rarea in areas:
                        print("\n*ERR: area '" + rarea + "' - mentioned more than once.  please correct.\n")
                        exit(0)

                    areas.add(rarea)

                continue

            type = None
            mo = re.match('^\s*([\["])\s*(.+?)\s*[\]"]\s*$', sline)
            if not bool(mo):
                print("\n*ERR: syntax error with line '" + sline + " - must be inside square brackets OR inside quotes -- square brackets to specify a file state database and quotes for LUI to process.\n")
                exit(0)

            type = mo.group(1)
            item = mo.group(2)

            if type == "[":
                oncurrent = False 
                if filedb != None:
                    data.append(filedb)

                filedb = dict()
                filedb['filename'] = item 

                file_in_fp = dir + "/" + item
                if not os.path.isfile(file_in_fp):
                    print("\n*ERR: file does not exist: '" + file_in_fp + "'\n")
                    exit(0)

                filedb['input_set'] = set()
                filedb['input_ordered_list'] = list()

            else:
                if oncurrent:
                    CURRENT_LIST.append(item)
                    continue

                if filedb == None:
                    print("\n*ERR: input specified but no state file given - line is '" + sline + "\n")
                    exit(0)
                else:
                    if item in filedb['input_set']:
                        print("\n*ERR: same input repeated for filedb (" + filedb['filename'] + ")! line is '" + sline + "'.\n")
                        exit(0)
                    else:
                        filedb['input_set'].add(item)
                        filedb['input_ordered_list'].append(item)

    if filedb != None:
        data.append(filedb)

    return (areas, data)


def usage():
    print("\n*Usage: cart.py <config_file> <operation>")
    print("\n<operation> is either 'create' or 'test' (no apostrope, case is insensitive).")
    print("<config_file> - a file inside '" + CONF_DIR + "' (The '.conf' suffix is optional)\n\n") 
    exit(0)


CONF_DIR = "./testpackages"
FILES_IN = CONF_DIR + "/" + "files"

create_dir_if_not_exist(CONF_DIR)
create_dir_if_not_exist(FILES_IN)

CART_INPUT_FILE = "temp_cart_input.txt"

if len(sys.argv) != 3:
    usage()

OPERATION = sys.argv[2]
OPERATION = OPERATION.lower()

if (OPERATION == "current"):
    CURRENT = True

if (OPERATION != "create") and (OPERATION != "test") and (OPERATION != "current"):
    print("\n*ERR: the operation you specified ('" + OPERATION + "') is not valid. Must be either 'create', 'test', or 'current'")
    usage()

TEST_PKG = sys.argv[1]
TEST_PKG_NO_EXT = ""

if TEST_PKG[-5::] != '.conf':
    TEST_PKG_FP = CONF_DIR + "/" + TEST_PKG + ".conf"
    TEST_PKG_NO_EXT = TEST_PKG
else:
    TEST_PKG_FP = CONF_DIR + "/" + TEST_PKG
    len_minus_ext = len(TEST_PKG) - 5
    TEST_PKG_NO_EXT = TEST_PKG[0:len_minus_ext:1] 

if not os.path.isdir(FILES_IN + "/" + TEST_PKG_NO_EXT):
    print("\n*ERR: directory does not exist - '" + FILES_IN + "/" + TEST_PKG_NO_EXT + ".  Please create.\n")
    exit(0)

if os.path.isfile(TEST_PKG_FP) == False:
    print("\n*ERR: file does not exist: '" + TEST_PKG_FP + "'.\n")
    exit(0)

if not CURRENT:
    backup_existing()
    if os.path.isfile('template_words_file.data'):
        os.remove('template_words_file.data')

    for dirtoclear in ("shared-lists", "conversation-history",  "sessions", "tls_csv", "interpretations", "compiled-classes"):
        safe_rec_del(dirtoclear)

print('\n--------------- RUNNING TEST PACKAGE: ' + TEST_PKG_NO_EXT + " ---------------\n")
print("OPERATION: " + OPERATION + "\n")

SPECIFIC_FILES_IN = FILES_IN + "/" + TEST_PKG_NO_EXT

(areas, tp) = load_config(TEST_PKG_FP, SPECIFIC_FILES_IN)
if len(areas) == 0:
    print("\n*ERR: config file does not specify any areas.   Please add 'areas=' line.\n")
    exit(0)

# CREATE CART-runnable version of vcck
# OH = output handle

if os.path.isfile(VCCK_PROGRAM_TEMP):
    os.remove(VCCK_PROGRAM_TEMP)
    if os.path.isfile(VCCK_PROGRAM_TEMP):
        print("\n*ERR: I cannot seem to remove the file '" + VCCK_PROGRAM_TEMP + "'.\n")
        exit(0)

code_lines = list()
test_code_lines = list()

try:
    with open(VCCK_PROGRAM, 'r') as IH:
        code_lines = IH.readlines()

except Exception as ex:
    print("\n*ERR: cannot read in the VCCK program code in '" + VCCK_PROGRAM + "' - " + str(ex))
    exit(0)


cart_includes = dict()

line_number_of_id_01 = None
line_number_of_id_02 = None
line_number_of_id_03 = None
line_number_of_id_04 = None
line_number_of_id_05 = None
line_number_of_id_06 = None

leading_space_id_01 = ''
leading_space_id_02 = ''
leading_space_id_03 = ''
leading_space_id_04 = ''
leading_space_id_05 = ''
leading_space_id_06 = ''

find_include_regex  = r"^(\s*)#\s*CART_INCLUDE_" + TEST_PKG_NO_EXT + "_(\w+\.py)$"

for linenum in range(len(code_lines)):
    stline = code_lines[linenum].rstrip()
   
    mo = re.match(find_include_regex, stline)
    if bool(mo):
        ws_for_inc_line = mo.group(1)
        inc_fn = mo.group(2)
        inc_fn_fp = CONF_DIR + "/files/" + TEST_PKG_NO_EXT + "/" + inc_fn

        if not os.path.isfile(inc_fn_fp):
            print("\n*ERR: include file mentioned in line '" + stline + "' does not exist.  - " + inc_fn_fp + " does not exist!\n")
            exit(0)

        try:
            with open(inc_fn_fp, 'r') as fh:
                include_file_lines = fh.readlines()
                cart_includes[linenum] = (ws_for_inc_line, include_file_lines)

        except Exception as ex:
            print("\n*ERR: could not load file '" + inc_fn_fp + "' - check if I have permission to open it.\n")
            exit(0)

    mo = re.match('^(\s*)#\s*__CART_REPLACED_LINE_01_DO_NOT_REMOVE_THIS_LINE\s*$', stline)
    if bool(mo):
        line_number_of_id_01 = linenum
        leading_space_id_01 = mo.group(1)

    mo = re.match('^(\s*)#\s*__CART_REPLACED_LINE_02_DO_NOT_REMOVE_THIS_LINE\s*$', stline)
    if bool(mo):
        line_number_of_id_02 = linenum
        leading_space_id_02 = mo.group(1)

    mo = re.match('^(\s*)#\s*__CART_REPLACED_LINE_03_DO_NOT_REMOVE_THIS_LINE\s*$', stline)
    if bool(mo):
        line_number_of_id_03 = linenum
        leading_space_id_03 = mo.group(1)

    mo = re.match('^(\s*)#\s*__CART_REPLACED_LINE_04_DO_NOT_REMOVE_THIS_LINE\s*$', stline)
    if bool(mo):
        line_number_of_id_04 = linenum
        leading_space_id_04 = mo.group(1)

    mo = re.match('^(\s*)#\s*__CART_REPLACED_LINE_05_DO_NOT_REMOVE_THIS_LINE\s*$', stline)
    if bool(mo):
        line_number_of_id_05 = linenum
        leading_space_id_05 = mo.group(1)

    mo = re.match('^(\s*)#\s*__CART_REPLACED_LINE_06_DO_NOT_REMOVE_THIS_LINE\s*$', stline)
    if bool(mo):
        line_number_of_id_06 = linenum
        leading_space_id_06 = mo.group(1)

if line_number_of_id_01 == None:
    print("\n*ERR: Anchor text missing in VCCK source code!!! Missing line '__CART_REPLACED_LINE_01_DO_NOT_REMOVE_THIS_LINE'\n")
    exit(0)

if line_number_of_id_02 == None:
    print("\n*ERR: Anchor text missing in VCCK source code!!! Missing line '__CART_REPLACED_LINE_02_DO_NOT_REMOVE_THIS_LINE'\n")
    exit(0)

if line_number_of_id_03 == None:
    print("\n*ERR: Anchor text missing in VCCK source code!!! Missing line '__CART_REPLACED_LINE_03_DO_NOT_REMOVE_THIS_LINE'\n")
    exit(0)

if line_number_of_id_04 == None:
    print("\n*ERR: Anchor text missing in VCCK source code!!! Missing line '__CART_REPLACED_LINE_04_DO_NOT_REMOVE_THIS_LINE'\n")
    exit(0)

if line_number_of_id_05 == None:
    print("\n*ERR: Anchor text missing in VCCK source code!!! Missing line '__CART_REPLACED_LINE_05_DO_NOT_REMOVE_THIS_LINE'\n")
    exit(0)

if line_number_of_id_06 == None:
    print("\n*ERR: Anchor text missing in VCCK source code!!! Missing line '__CART_REPLACED_LINE_06_DO_NOT_REMOVE_THIS_LINE'\n")
    exit(0)
# create source code for CART-runnable version of vcck !

for linenum in range(len(code_lines)):
    stline = code_lines[linenum].rstrip()

    if linenum == line_number_of_id_01:
        for area in areas:
            test_code_lines.append(leading_space_id_01 + '_cart_area_' + area + ' = None')

    elif linenum == line_number_of_id_02:
        for area in areas:
            test_code_lines.append(leading_space_id_02 + 'global _cart_area_' + area)

    elif linenum == line_number_of_id_03:
        first = True
        for area in areas:
            if first:
                test_code_lines.append(leading_space_id_03 + 'if area == "' + area + '":')
                first = False
            else:
                test_code_lines.append(leading_space_id_03 + 'elif area == "' + area + '":')

            test_code_lines.append(leading_space_id_03 + '    ref = _cart_area_' + area)
            test_code_lines.append(leading_space_id_03 + '    known_area = True') 

    elif linenum == line_number_of_id_04:
        for area in areas:
            test_code_lines.append(leading_space_id_04 + 'if area == "' + area + '": _cart_area_' + area + ' = ref')

    elif linenum == line_number_of_id_05:
        for area in areas:
            test_code_lines.append(leading_space_id_05 + 'if bool(_cart_area_' + area + '):')
            test_code_lines.append(leading_space_id_05 + '    ' + '_cart_area_' + area + '.close()')
            test_code_lines.append(leading_space_id_05 + '    ' + '_cart_area_' + area + ' = None')

    elif linenum == line_number_of_id_06:
        test_code_lines.append(leading_space_id_06 + 'if TESTING:')
        for area in areas:
            test_code_lines.append(leading_space_id_06 + '    if bool(_cart_area_' + area + '):')
            test_code_lines.append(leading_space_id_06 + '        ' + '_cart_area_' + area + '.close()')
            test_code_lines.append(leading_space_id_06 + '        ' + '_cart_area_' + area + ' = None')

    elif linenum in cart_includes.keys():
        ind_ws = cart_includes[linenum][0]
        for codeline in cart_includes[linenum][1]:
            test_code_lines.append(ind_ws + codeline.rstrip())

    else:
        test_code_lines.append(stline)

try:
    with open(VCCK_PROGRAM_TEMP,'w') as FH:
        for cline in test_code_lines:
            FH.write(cline + "\n")

except Exception as ex:
    print("\n*ERR: issues creating '" + VCCK_PROGRAM_TEMP + "' - " + str(ex))
    exit(0)

# Done - creating cart runnable vcck.

# prev_files = all files from previous tar.gz file. to clean up, so we don't mix up files from 2 different *.tar.gz files.
prev_files = set()
TEMP_CONTENTS_FILE = "state_file_contents.txt"

if os.path.isfile(TEMP_CONTENTS_FILE):
    os.remove(TEMP_CONTENTS_FILE)
    if os.path.isfile(TEMP_CONTENTS_FILE):
        print("\n*ERR: I cannot seem to remove the file '" + TEMP_CONTENTS_FILE + "'.\n")
        exit(0)

if CURRENT:
    outforcurrent = TEST_RESULT_DIR + "/current"
    os.mkdir(outforcurrent)

    if not os.path.isdir(outforcurrent):
        print("\n*ERR: was not able to create '" + outforcurrent + "'")
        exit(1)

    with open(CART_INPUT_FILE, 'w') as fh:
        lineind = 0

        for line in CURRENT_LIST:
            fh.write(line + "\n")
            dir_filedb_linenum = outforcurrent + "/" + str(lineind)
            os.mkdir(dir_filedb_linenum)
            lineind += 1

    make_exec_cmd = "chmod +x " + VCCK_PROGRAM_TEMP
    res = os.system(make_exec_cmd)

    if res != 0:
        print("\n*ERR: problem executing '" + make_exec_cmd + "'")
        exit(1)

    vcck_start_cmd = VCCK_PROGRAM_TEMP + " -T current:" + CART_INPUT_FILE
    print(vcck_start_cmd)

    res = os.system(vcck_start_cmd)

    if res != 0:
        print("\n*ERR: problem running VCCK ('" + vcck_start_cmd + "')")
        exit(1)

    print("\nDone.  Output from cartlog() calls placed in results_cart_tests/current\n")
    print("Directory state wasn't changed.\n")
    exit(0)


for filedbid in range(len(tp)):
    print("Next filedb.  Hit enter to continue:")
    input()

    for file in prev_files:
        
        file = file.strip()

        if file[0] == '/' or file[0] == '.':
            # directory to remove should not start with / or .
            print("*ERR: ** NO ** refusing to run 'rm -rf " + file + "'")
            exit(0)

        rm_cmd = "rm -rf " + file
        #print(rm_cmd)
        res = os.system(rm_cmd)
        if res != 0:
            print("\n*ERR: trying to execute " + rm_cmd + "'")
            exit(0)

    prev_files = set()

    print("Using State Files in: " + str(filedbid) + ", Db: " + tp[filedbid]['filename']) 
    tar_contents_cmd = "tar tzf " + FILES_IN + "/" + TEST_PKG_NO_EXT + "/" + tp[filedbid]['filename'] + " > " + TEMP_CONTENTS_FILE

    res = os.system(tar_contents_cmd)
 
    if res != 0:
        print("\n*ERR: Problem when executing: '" + tar_contents_cmd + " (make sure you verify cleanup of un-archived files)\n")
        exit(0)

    if not os.path.isfile(TEMP_CONTENTS_FILE):
        print("\n*ERR: The content listing file was not created ('" + TEMP_CONTENTS_FILE + "').\n")
        exit(0)

    with open(TEMP_CONTENTS_FILE, 'r') as fh:
        for line in fh:
            sline = line.strip()

            mo = re.match('^\./(.*)$', sline)
            if bool(mo):
                sline = mo.group(1)

            if sline == '': continue
            if sline[0] == '.': continue

            mo = re.match('^(.+?)/.*$', sline)
            if bool(mo):
                prev_files.add(mo.group(1))
            else:
                prev_files.add(sline)
 
    unarchive_cmd = "tar xzf " + FILES_IN + "/" + TEST_PKG_NO_EXT + "/" + tp[filedbid]['filename']

    res = os.system(unarchive_cmd)
    if res != 0:
        print("\n*ERR: Problem when executing: '" + unarchive_cmd + " (make sure you verify cleanup of un-archived files)\n")
        exit(0)
 
    if os.path.isfile(CART_INPUT_FILE):
        os.remove(CART_INPUT_FILE)
        if os.path.isfile(CART_INPUT_FILE):
            print("\n*ERR: cannot remove file '" + CART_INPUT_FILE + "' from last run.")
            exit(0)

    dir_filedbid = TEST_RESULT_DIR + "/" + str(filedbid)
    os.mkdir(dir_filedbid)

    with open(CART_INPUT_FILE, 'w') as fh:
        lineind = 0
        for line in tp[filedbid]['input_ordered_list']:
            fh.write(line + "\n")
            dir_filedb_linenum = dir_filedbid + "/" + str(lineind)
            os.mkdir(dir_filedb_linenum)
            lineind += 1 


    make_exec_cmd = "chmod +x " + VCCK_PROGRAM_TEMP
    res = os.system(make_exec_cmd)
    if res != 0:
        print("\n*ERR: problem executing '" + make_exec_cmd + "'")
        exit(0)

    vcck_start_cmd = VCCK_PROGRAM_TEMP + " -T " + str(filedbid) + ":" + CART_INPUT_FILE
    print(vcck_start_cmd)
    
    res = os.system(vcck_start_cmd)

    if res != 0:
        print("\n*ERR: problem running VCCK ('" + vcck_start_cmd + "')")
        exit(0)
    
print("-ready to remove files. Press enter.")
input()

for file in prev_files:
    
    file = file.strip()

    if file[0] == '/' or file[0] == '.':
        # directory to remove should not start with / or .
        print("*ERR: ** NO **  refusing to run 'rm -rf " + file + "'")
        exit(0)

    rm_cmd = "rm -rf " + file
    #print(rm_cmd) 
    res = os.system(rm_cmd)
    if res != 0:
        print("\n*ERR: trying to execute '" + rm_cmd + "'")
        exit(0)


temp_file = "vcck-cart-temp.py"
orig_file = "vcck.py"

if os.path.exists(temp_file):
    try:
        os.remove(temp_file)

    except Exception as ex:
        print("*ERR: " + str(ex))

if os.path.exists(temp_file):
    print("*ERR: I was unable to remove previous file '" + temp_file + "' - Stopping the testing.")
    exit()

os.remove(TEMP_CONTENTS_FILE)

if os.path.isfile(CART_INPUT_FILE):
    os.remove(CART_INPUT_FILE)
    if os.path.isfile(CART_INPUT_FILE):
        print("\n*ERR: I was not able to remove file '" + CART_INPUT_FILE + "'")
        exit(0)

#os.remove(VCCK_PROGRAM_TEMP)

safe_rec_del(TEMP_ARCHIVE_UNPACK_DIR)
os.mkdir(TEMP_ARCHIVE_UNPACK_DIR)

if not os.path.isdir(TEMP_ARCHIVE_UNPACK_DIR):
    print("\n*ERR: could not create '" + TEMP_ARCHIVE_UNPACK_DIR + "'")
    exit(0)

if OPERATION == "create":
    new_archive = CONF_DIR + "/files/" + TEST_PKG_NO_EXT + "/" + TEST_PKG_NO_EXT + ".tar.gz"

    if os.path.isfile(new_archive):
        os.remove(new_archive)
        if os.path.isfile(new_archive):
            print("\n*ERR: I was not able to remove the file '" + new_archive + "' from last run!\n")
            exit(0)

    sort_all_files(TEST_RESULT_DIR)

    tar_create_cmd = "tar -C " + TEST_RESULT_DIR + " -czf " + new_archive + " ."
    res = os.system(tar_create_cmd)

    if res != 0:
        print("\n*ERR: problems when trying to create archive.  Error executing: " + tar_create_cmd)
        exit(0)

    if not validate("The archive was not created successfully. ", new_archive, TEMP_ARCHIVE_UNPACK_DIR, TEST_RESULT_DIR):
        pass

    print("\n*Great! Expected test result archive created successfully.: " + new_archive + "\n")

else:
    existing_archive = CONF_DIR + "/files/" + TEST_PKG_NO_EXT + "/" + TEST_PKG_NO_EXT + ".tar.gz"
    if not os.path.isfile(existing_archive):
        print("\n*ERR: Archive '" + existing_archive + "' does not exist.  Did you run a 'create' yet?")
        exit(0)

    sort_all_files(TEST_RESULT_DIR)
    validate("\n* * * Regression testing FAILED !!!! ", existing_archive, TEMP_ARCHIVE_UNPACK_DIR, TEST_RESULT_DIR)    
    print("\n---------------------------------------------------")
    print("* Regression testing *PASSED*")
    print("---------------------------------------------------")


