#!/usr/bin/python3.7
import os
import re
import sys

INPUT_TAR_GZ = "/home/victor/archive/vcck-cart-testpackages-2021-04-22-seq-1.tar.gz"

print("Hello !\n")
print("TODO_FUTURE: grep through this script for 'TODO_FUTURE':")
print("\nRight now we don't detect any changes in DCID values when direct objects are recompiled.")
print("however, if this changes (CART reports a failed test because of ERAF's DCID value for a given direct object json text differs from what the recompiled version says")
print("then we'll need to complete those sections of code (those marked with 'TODO_FUTURE')")
print("\n")
print("*IF* VCCK code is changed such that the compiled Direct Objects (*.json, *.csv) files become 'stale', and the 'raw' direct object needs to be recompiled, you need to run this")
print("script.   This script (a) decompiles the direct object json files, (b) recompiles the D.O. files, (c) figures out if TID values changed, and if so: (d) changes TID values in all required files, such as FSDB files and ERAF files (*.res file)")
print("again, right now, TID values are managed - but not DCID, since we are not seeing any DCID changes")
print("\n")
print("This will only apply to CART TEST case FSDBs and ERAF for version 1.000 - we will be always using raw text from user for FSDBs...so that FSDB info will always get recompiled")
print("every time CART runs VCCK")
print("\n--- press <RETURN> to continue...")
input()
print("Oh! one other thing! VCCK v1.000 has a feature where ALL L-lines of a direct class must have identical SET of VNAVs.")
print("If the existing FSDBs that this script (revamp.py) recompiles violates that rule, it doesn't care.")
print("\nThat is, this script will allow a 'do' source file to contain L-lines that each have different vnav sets.")
print("This should be okay though since those 'violating direct classes' are only used in the context of running VCCK under CART (and only for those specific FSDBS).")
print("And VCCK only cares about this rule when compiling 'do' files, not when they are already compiled.")
print("\n--- press <RETURN> to continue...")
input()

TEMP = "/home/victor/vcck/temp"
VERSION = "v1.000"

FSDBS = list()

def edit_include_file(infile, converter):
    filename = "./testpackages/files/" + VERSION + "/" + infile
    new_line_list = list()

    with open(filename, 'r') as FH:
        for line in FH:
            line = line.rstrip()
            mo = re.match('^(\s*)(.*)(\d{9})(.*)$', line)

            if bool(mo):
                initial_ws = mo.group(1)
                old_tid_value = mo.group(3)
                new_tid_value = converter[old_tid_value]
                new_line_list.append(initial_ws + mo.group(2) + new_tid_value + mo.group(4))
            else:
                new_line_list.append(line)

    with open(filename, 'w') as FH:
        for line in new_line_list:
            FH.write(line + "\n")


def cleanup_dir(tmpdir):
    # CLEANUP.
    if os.path.isdir(tmpdir):
        cmd = "rm -rf " + tmpdir
        runit(cmd)

        if os.path.isdir(tmpdir):
            print("\n*** cannot remove previous '" + tmpdir + "'\n")
            sys.exit(1)

    return

def normal_apos_2(instr):
    orig = instr

    while True:
        mo = re.match('^(.*?)(\S)\'s\s(.*)$', instr)

        if bool(mo):
            instr = mo.group(1) + mo.group(2) + " 's " + mo.group(3)
        else:
            break

    while True:
        mo = re.match('^(.*?)(\S)\'s"(.*)$', instr)

        if bool(mo):
            instr = mo.group(1) + mo.group(2) + " 's\"" + mo.group(3)
        else:
            break

    while True:

        mo = re.match('^(.*?)(\S)\'s\\\\n(.*)$', instr)

        if bool(mo):
            instr = mo.group(1) + mo.group(2) + " 's\\n" + mo.group(3)
        else:
            break

    return (orig != instr, instr)


def normal_apos_1(instr):
    orig = instr

    while True:
        mo = re.match('^(.*?)\s\'s\s(.*)$', instr)

        if bool(mo):
            instr = mo.group(1) + "'s " + mo.group(2)
        else:
            break

    while True:
        mo = re.match('^(.*?)\s\'s"(.*)$', instr)

        if bool(mo):
            instr = mo.group(1) + "'s\"" + mo.group(2)
        else:
            break

    while True:

        mo = re.match('^(.*?)\s\'s\\\\n(.*)$', instr)

        if bool(mo):
            instr = mo.group(1) + "'s\\n" + mo.group(2)
        else:
            break

    return (orig != instr, instr)


def fetchTID(mapp, key):
    
    if key not in mapp.keys():
        print("\n*** ERROR: cannot find TID '" + key + "' in TID map!\n")
        sys.exit(1)
    return mapp[key]


def process_file_for_dcid(FileName, FileInstance, dcid_map):
    # listdirectobjects.res - DCID
    # matchclassdcc.res - DCID
    # matchclassdcl.res - DCID

    applicable = False

    if FileName == 'listdirectobjects.res': applicable = True
    if FileName == 'matchclassdcc.res': applicable = True
    if FileName == 'matchclassdcl.res': applicable = True
     
    if not applicable: return
   
    # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # TODO_FUTURE: 
    # TODO_FUTURE: 
    # TODO_FUTURE: 
    # We are currently not seeing any difference between the DCIDs that are inside the April 22/2021's compiled-classes/direct directory and the DCID values that are produced
    # when recompiling the DO files.
    # This is the case right now, so we are not affected by it, thus we are not completing the code for this routine right now.
    # IF in the future, CART test fails because of a diffference in DCID values, then we will revisit this function and complete it - that is, to have the functionality of
    # converting DCID values from previoius version of ERAF.

    # USE THE CODE in process_file_for_tid() as a reference.. you're doing the same thing here (editing *.res files) but for DCID values (not TID values).
    # USE THE CODE in process_file_for_tid() as a reference.. you're doing the same thing here (editing *.res files) but for DCID values (not TID values).
    # USE THE CODE in process_file_for_tid() as a reference.. you're doing the same thing here (editing *.res files) but for DCID values (not TID values).
    # USE THE CODE in process_file_for_tid() as a reference.. you're doing the same thing here (editing *.res files) but for DCID values (not TID values).

    # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO

    return




def process_file_for_tid(FileName, FileInstance, tid_map):

    # listdirectobjects.res - DCID
    # matchclassdcc.res - DCID
    # matchclassdcl.res - DCID
  
    # Some files we don't need to bother with !! (Just raw - direct from user info in *.res file)
    if FileName == 'ca.res': return
    if FileName == 'findin.res': return

    if FileName == 'listdirectobjects.res': return
    if FileName == 'matchclassdcc.res': return
    if FileName == 'matchclassdcl.res': return
    if FileName == 'nononcontemp.res': return
    if FileName == 'multihighestscore.res': return
    if FileName == 'cmmnouc.res': return

    fileLines = list()
    newFileLines = list()

    try:
        print("FileName::: " + FileName + " FileInstance::: " + FileInstance)
        with open(FileInstance, 'r') as FH:
            for Line in FH:
                fileLines.append(Line)

        any_diff = False
        
        for Line in fileLines:
            tid_from_file = None
            newLine = ''

            if FileName == 'vnavsub.res':
                mo = re.match('^(\d{9})(.*)$', Line)
              
                if bool(mo):
                    tid_from_file = mo.group(1)
                    new_tid_for_file = fetchTID(tid_map, tid_from_file)

                    if tid_from_file != new_tid_for_file: any_diff = True

                    newLineForFile = new_tid_for_file + mo.group(2)
                    newFileLines.append(newLineForFile)

            elif FileName == 'totallcc.res':
                mo = re.match('^tid:(\d{9})(.*)$', Line)
              
                if bool(mo):
                    tid_from_file = mo.group(1)
                    new_tid_for_file = fetchTID(tid_map, tid_from_file)

                    if tid_from_file != new_tid_for_file: any_diff = True

                    newLineForFile = "tid:" + new_tid_for_file + mo.group(2)
                    newFileLines.append(newLineForFile)


            elif FileName == 'sumlcccalledfrom.res':
                mo = re.match('^(.+),tid:(\d{9})(.*)$', Line)

                if bool(mo): 
                    tid_from_file = mo.group(2)
                    new_tid_for_file = fetchTID(tid_map, tid_from_file)
 
                    if tid_from_file != new_tid_for_file: any_diff = True

                    newLineForFile = mo.group(1) + ",tid:" + new_tid_for_file + mo.group(3) 
                    newFileLines.append(newLineForFile)

            elif FileName == 'noucps.res':
                mo = re.match('^(\d{9})(.*)$', Line)

                if bool(mo): 
                    tid_from_file = mo.group(1)
                    new_tid_for_file = fetchTID(tid_map, tid_from_file)
 
                    if tid_from_file != new_tid_for_file: any_diff = True

                    newLineForFile = new_tid_for_file + mo.group(2) 
                    newFileLines.append(newLineForFile)

            elif FileName == 'constrength.res':
                mo = re.match('^TID:(\d{9})(.*)$', Line)

                if bool(mo): 
                    tid_from_file = mo.group(1)
                    new_tid_for_file = fetchTID(tid_map, tid_from_file)
 
                    if tid_from_file != new_tid_for_file: any_diff = True

                    newLineForFile = "TID:" + new_tid_for_file + mo.group(2) 
                    newFileLines.append(newLineForFile)

            elif FileName == 'lcc.res':
                mo = re.match('^tid:(\d{9})(.*)$', Line)
              
                if bool(mo):
                    tid_from_file = mo.group(1)
                    new_tid_for_file = fetchTID(tid_map, tid_from_file)

                    if tid_from_file != new_tid_for_file: any_diff = True

                    newLineForFile = "tid:" + new_tid_for_file + mo.group(2)
                    newFileLines.append(newLineForFile)

            elif FileName == 'lmmrsa.res':
                mo = re.match('^TID:(\d{9})(.*)$', Line)

                if bool(mo):
                    tid_from_file = mo.group(1)
                    new_tid_for_file = fetchTID(tid_map, tid_from_file)

                    if tid_from_file != new_tid_for_file: any_diff = True

                    newLineForFile = "TID:" + new_tid_for_file + mo.group(2)
                    newFileLines.append(newLineForFile)

            if tid_from_file == None:
                print("\n**ERROR: I can't find TID in line '" + Line + "'")
                print("Terminating.")
                sys.exit(1)

        if any_diff == False:
            print("\n* INFO: No differences in template string-to-TID for file " + FileInstance)
            return

        print("\n* INFO: Yes, differences in template string-to-TID for file " + FileInstance + ", thus recreating " + FileInstance + "...")
        with open(FileInstance, 'w') as OH:
            newFileLines.sort()

            for Line in newFileLines:
                OH.write(Line + "\n")

        print("--> Done recreating for: " + FileInstance)

    except Exception as ex:
        print("\n**ERR: problem in process_file_for_tid('" + FileName + "','" + FileInstance + "')\n\nIssue is: " + str(ex) + "\n")
        sys.exit(1) 


def build_dcid(path):
    data = dict()

    # DETERMINE  OLD dcid to NEW dcid mapping...
    if os.path.isdir(path + "/compiled-classes/direct"):
        for file in os.listdir(path + "/compiled-classes/direct"):
            mo = re.match('^dc-(\d+)\.json$', file)
            if bool(mo):

                try:
                    with open(path + "/compiled-classes/direct/" + file) as FH:
                        for Line in FH:

                            data[Line] = mo.group(1)
                            (was_changed, ModLine) = normal_apos_1(Line)

                            if was_changed:
                                data[ModLine] = mo.group(1)

                            else:
                                (was_changed, ModLine) = normal_apos_2(Line)
                                if was_changed:
                                    data[ModLine] = mo.group(1)

                except Exception as ex:
                    print("\n** problem creating old-dcid to new-dcid map. - " + str(ex))

    return data 

def build_tid(path):
    data = dict()

    for tid in os.listdir(path):
        with open(path + "/" + tid + "/template.data") as F:
            tstr = F.readline()
            tstr = tstr.strip()

            type = 0
 
            data[tstr] = tid
            otstr = tstr
 
            mo = re.match('^(.*)(\S)\'s$', tstr)

            if bool(mo):
                tstr = mo.group(1) + mo.group(2) + " 's"
                type = 1

            while True:
                pline = tstr 
                mo = re.match('^(.*?)(\S)\'s\s(.*)$', tstr)

                if bool(mo):
                    tstr = mo.group(1) + mo.group(2) + " 's " + mo.group(3)
                    type = 1

                if pline == tstr: break

            if type == 1:
                data[tstr] = tid
            else:
                mo = re.match('^(.*)\s\'s$', otstr)

                if bool(mo):
                    otstr = mo.group(1) + "'s"
                    type = 2

                while True:
                    pline = otstr 
                    mo = re.match('^(.*?)\s\'s\s(.*)$', otstr)

                    if bool(mo):
                        otstr = mo.group(1) + "'s " + mo.group(2)
                        type = 2

                    if pline == otstr: break

                if type == 2:
                    data[otstr] = tid

    return data


def runit(cmd, pause = False):
    if pause:
        print("\n * * * About to run command: " + cmd + "\n\nPress enter to continue...")
        input()

    try:
        
        r = os.system(cmd)
        if r != 0:
            print("\n*** Issue executing command '" + cmd + ": " +  str(r) + "\n")
            sys.exit(1)

    except Exception as ex:
            print("\n*** Issue executing command '" + cmd + ": " +  str(ex) + "\n")
            sys.exit(1)


if os.path.isdir(TEMP):
    os.system("rm -rf " + TEMP)
    if os.path.isdir(TEMP):
        print("\n** could not clear out old '" + TEMP + "' dir\n")
        sys.exit(1)

if not os.path.isdir(TEMP):
    os.mkdir(TEMP)
    if not os.path.isdir(TEMP):
        print("\n** could not create '" + TEMP + "'\n")
        sys.exit(1)

r = os.system("tar zxf " + INPUT_TAR_GZ + " -C " + TEMP)

if r != 0:
    print("\n** Issue with unzipping archive!\n")
    sys.exit(1)

LIST_FSDB_FILE = "list_fsdbs.txt"

if os.path.isfile(LIST_FSDB_FILE):
    os.remove(LIST_FSDB_FILE)
    if os.path.isfile(LIST_FSDB_FILE):
        print("\n** cannot remove file " + LIST_FSDB_FILE)
        sys.exit(1)

os.system("grep '\[' " + TEMP + "/vcck/testpackages/v1.000.conf > " + LIST_FSDB_FILE)

try:
    with open(LIST_FSDB_FILE, 'r') as fh:
        for line in fh:
            mo = re.match('^\[(.*?):.*]$', line)
            if bool(mo):
                FSDBS.append(mo.group(1))                  

except Exception as ex: 
    print("\n** issue opening '" + LIST_FSDB_FILE + "' " + str(ex))


ERAF_TEMP_DIR = "eraf_temp_dir"
if os.path.isdir(ERAF_TEMP_DIR):
    runit("rm -rf " + ERAF_TEMP_DIR)
    if os.path.isdir(ERAF_TEMP_DIR):
        print("\n*** ERR: could not clean up (could not remove previous directory: '" + ERAF_TEMP_DIR + "'.\n")
        sys.exit(1)

os.mkdir(ERAF_TEMP_DIR)
if not os.path.isdir(ERAF_TEMP_DIR):
    print("\n*** ERR: could not create directory '" + ERAF_TEMP_DIR + "'.\n")
    sys.exit(1)

cmd = "tar zxf " + TEMP + "/vcck/testpackages/files/" + VERSION + "/" + VERSION + ".tar.gz -C " + ERAF_TEMP_DIR
runit(cmd)

for F in FSDBS:

    tmpdir = "fsdb_temp_" + F
    print("ON: " + tmpdir)

    if os.path.isdir(tmpdir):
        cmd = "rm -rf " + tmpdir
        runit(cmd)

        if os.path.isdir(tmpdir):
            print("\n*** cannot remove previous '" + tmpdir + "'\n")
            sys.exit(1)
        
    os.mkdir(tmpdir)
    if not os.path.isdir(tmpdir):
        print("\n*** could not create " + tmpdir + "\n")
        sys.exit(1)
    
    cmd = "tar zxf " + TEMP + "/vcck/testpackages/files/v1.000/" + F + " -C " + tmpdir
    runit(cmd)
    
    cmd = "tcm clear"
    runit(cmd)

    cmd = "tcm install " + F 
    runit(cmd)

    # if no templates, skip.
    TLSPATH = tmpdir + "/tls_csv"
    
    SOMEFILES = False
 
    for file in os.listdir(TLSPATH):
        mo = re.match('^000.*$', file)
        if bool(mo):
            SOMEFILES = True
            break

    if not SOMEFILES: 
        print("Skipping " + F + ": no Templates.\n")
        cleanup_dir(tmpdir)
        continue

    cmd = "./decompiler.py"
    runit(cmd)

    cmd = "rm -rf tls_csv"
    runit(cmd)

    cmd = "rm -rf compiled-classes"   
    runit(cmd)

    cmd = "./vcck.py -B"
    runit(cmd)
   
    prev_tid_dict = build_tid(tmpdir + "/tls_csv")
    cur_tid_dict = build_tid("./tls_csv")

    # SANITY CHECKS...
    sane = True

    for K in prev_tid_dict.keys():
        if K not in cur_tid_dict.keys():
            print("\n** WHAT?! TID '" + K + "' is in previous but not current!\n")
            sane = False 

    for K in cur_tid_dict.keys():
        if K not in prev_tid_dict.keys():
            print("\n** WHAT?! TID '" + K + "' is in current but not previous!\n")  
            sane = False 
 
    if not sane: sys.exit(1)

    tidmap = dict()
    for tstr in cur_tid_dict.keys():
        tidmap[tstr] = dict()
        tidmap[tstr]['previous'] = prev_tid_dict[tstr]
        tidmap[tstr]['current'] = cur_tid_dict[tstr] 

    already_done = set()

    # Convert all TID values in ./tls_csv
   
    tidconvert = dict()
    dcidconvert = dict()

    for TS in tidmap.keys():
        current_tid = tidmap[TS]['current']
        previous_tid = tidmap[TS]['previous']
 
        if current_tid not in already_done:
            tidconvert[previous_tid] = current_tid

            print(tmpdir + "::" + str(previous_tid) + " TO " + str(current_tid))

            cmd = "cp " + tmpdir + "/tls_csv/" + previous_tid + "/*nav*.data ./tls_csv/" + current_tid
            runit(cmd) 

            cmd = "cp " + tmpdir + "/tls_csv/" + previous_tid + "/*ref*.data ./tls_csv/" + current_tid
            runit(cmd) 

            already_done.add(current_tid)
        else:
            continue

    # Convert all TID values in ./interpretations
    for intfile in os.listdir("./interpretations"):
        mo = re.match('^.+\.data', intfile)
        if not bool(mo): continue

        newfilelines = list()

        with open("./interpretations/" + intfile, 'r') as fh:
            for line in fh:
                line = line.strip()

                mo = re.match('^(\d{21}),"(.+)",(\d{9}),(\d+),\((.*)\)$', line)

                if line == '': 
                    continue

                if not bool(mo):
                    print("**ERROR could not parse the line [" + line + "]")
                    print("Press <RETURN>")
                    input()
                    continue
                
                tid_in_file = mo.group(3)
                new_tid_for_file = tidconvert[tid_in_file]

                line = mo.group(1) + ",\"" + mo.group(2) + "\"" + "," + new_tid_for_file + "," + mo.group(4) + ",(" + mo.group(5) + ")"
                newfilelines.append(line)

        with open("./interpretations/" + intfile, 'w') as fh:
            for line in newfilelines:
                fh.write(line + "\n")

    # Find all *.res files and process (change old TID to new TID)...
    all_res_files = dict()
    F_chop_tar_gz = F
    mo = re.match('^(.*)\.tar\.gz$', F_chop_tar_gz)

    if not bool(mo):
        print("Huh !!!?? no tar.gz at end of '" + F_chop_tar_gz + "' !!??")
        sys.exit(1)
    else:
        F_chop_tar_gz = mo.group(1)

    for _fsdb_ in os.listdir(ERAF_TEMP_DIR):
        for _line_num_ in os.listdir(ERAF_TEMP_DIR + "/" + _fsdb_):
            for _fsdb_file_ in os.listdir(ERAF_TEMP_DIR + "/" + _fsdb_ + "/" + _line_num_):
                #print("FSDB: [" + _fsdb_ + "], LINENUM: [" + _line_num_ + "], FILE = [" + _fsdb_file_ + "]---CUR FSDB IS [" + F_chop_tar_gz + "]")
                if _fsdb_ == F_chop_tar_gz:
                    if _fsdb_file_ not in all_res_files.keys(): all_res_files[_fsdb_file_] = list()
                    all_res_files[_fsdb_file_].append(ERAF_TEMP_DIR + "/" + _fsdb_ + "/" + _line_num_ + "/" + _fsdb_file_)

    #print("---- ABOUT TO UPDATE ALL *.res files ----")
    #print("Press <RETURN>")
 
    for FileName in all_res_files.keys():
        for FileInstance in all_res_files[FileName]:
            process_file_for_tid(FileName, FileInstance, tidconvert)
    
    new_dcid = build_dcid(".") 
    old_dcid = build_dcid(tmpdir)

    sane = True

    for K in old_dcid.keys():
         if K not in new_dcid.keys():
             print("\n** WHAT?! DCID '" + K + "' is in previous but not current!\n")
             sane = False

    for K in new_dcid.keys(): 
        if K not in old_dcid.keys(): 
             print("\n** WHAT?! DCID '" + K + "' is in current but not previous!\n")
             sane = False

    if not sane: sys.exit(1)

    dcidmap = dict()

    for do_str in new_dcid.keys():
        dcidmap[do_str] = dict()
        dcidmap[do_str]['previous'] = old_dcid[do_str]
        dcidmap[do_str]['current'] = new_dcid[do_str]

    already_done = set()

    for DOS in dcidmap.keys():
        current_dcid = dcidmap[DOS]['current']
        previous_dcid = dcidmap[DOS]['previous']

        if previous_dcid not in already_done:
            dcidconvert[previous_dcid] = current_dcid

            if previous_dcid == current_dcid:
                #print("Since previous dcid (" + str(previous_dcid) + ") == current dcid (" + str(current_dcid) + "), no need to copy!")
                continue
           
            print(tmpdir + " :: Since previous dcid (" + str(previous_dcid) + ")  != current dcid (" + str(current_dcid) + "), we -DO- need to copy!!! OK! you have work to do... grep through this script and complete the code areas that have 'TODO_FUTURE' written near them.")
            print("\nScript terminating...")
            sys.exit(0)
            
            # TODO_FUTURE:
            # TODO_FUTURE:
            # TODO_FUTURE:
            # TODO_FUTURE:
            # TODO_FUTURE:
            #
	    # create and test code that... renames....  <OLD CODE> == previous_dcid, and <NEW CODE> == current_dcid
            # 
            # compiled-classes/direct/dc- <OLD CODE>.csv  >>>> compiled-classes/direct/dc- <NEW CODE>.csv 
	    # compiled-classes/direct/dc- <OLD CODE>.json  >>>> compiled-classes/direct/dc- <NEW CODE>.json
            #
            # cmd = "cp ....required copy command"...
            # runit(cmd)
            # cmd = "cp ....required copy command"...
            # runit(cmd)

            already_done.add(previous_dcid)

    for FileName in all_res_files.keys():
        for FileInstance in all_res_files[FileName]:
            process_file_for_dcid(FileName, FileInstance, dcidconvert)


    # rename directories in cached-lcc-factors
    some_cache = False

    if os.path.isdir("./cached-lcc-factors"):
        for tiddir in os.listdir("./cached-lcc-factors"):
            some_cache = True 
            os.rename("./cached-lcc-factors/" + tiddir, "./cached-lcc-factors/" + tiddir + "X")
  
    if some_cache:
        for oldtid in tidconvert.keys():
            newtid = tidconvert[oldtid]
            cmd = "mv " + "./cached-lcc-factors/" + oldtid + "X " + "./cached-lcc-factors/" + newtid
            runit(cmd) 
  
    if F_chop_tar_gz == 'calc_lcc_factors':
        edit_include_file('add_to_tid_csv.py', tidconvert)
        edit_include_file('touch_sls.py', tidconvert)
        edit_include_file('tptc_calc_lcc/remove_if_line_number_index_6_and_slfile_is_file2.txt.py', tidconvert)

    cmd = "tcm create " + F
    runit(cmd)

    print("CLEAN UP FSDB...")
    cleanup_dir(tmpdir)

cmd = "tar czf ./testpackages/files/" + VERSION + "/" + VERSION + ".tar.gz -C " + ERAF_TEMP_DIR + " ."
runit(cmd) 

#print("----------------------")
#print("----------------------")
#print("----------------------")
#print("---Done: " + F)
#print("\nPress <RETURN> to continue")
#input()


