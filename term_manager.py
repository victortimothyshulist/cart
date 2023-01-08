import os
import re

def adjust_for_apos_s(instr):
    # if input (instr), contains any cases of sequence of: (1) non-space (call it 'x), (2) apostrope ('), (3) letter 's', (4) space
    # then change that to: (1) value of 'x', (2) space (3) apostrope ('), (4) letter 's', (5) space
    # example "victor's car" becomes "victor 's car"

    while True:
        x = instr
        y = re.sub("^(.*?)(\S)'s(\s|$)(.*)", r"\1\2 's\3\4", x)

        if x == y: break
        instr = y
 
    return instr


def get_existing_global_term_list(myconn, logging):
    all_existing = dict()

    try:
        mycursor = myconn.cursor()
        mycursor.execute('SELECT termid, term_text FROM global_term_catalogue')
        records = mycursor.fetchall()
        for record in records:
            all_existing[record[1]] = record[0]
    
    except Exception as ex:
        logging.error("Exception thrown: " + str(ex)) 
        raise ex
    finally:
        mycursor.close()

    return all_existing
        

def load_group_contents(logging, grp_dn):
    logging.info("Loading group contents from '" + grp_dn + "'")
    groupinfo = dict()

    try:        
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
                    gr_entry = adjust_for_apos_s(gr_entry)
                    gr_entry = gr_entry.replace(" ", "_")

                    if gr_entry != "": groupinfo[gr_file].add(gr_entry)
                
    except Exception as ex:
        logging.error("Exception thrown in load_group_contents(): " + str(ex))
        raise ex

    logging.info("Successfully loaded group file contents from '" + grp_dn + "' - " + str(len(groupinfo)) + " files read.")
    return groupinfo


def normalize_text(intext):
    intext = intext.lower()
    intext = intext.strip()
    intext = re.sub('\s{2,}', ' ', intext)
    return intext


def build_lexicon(myconn, logging, constantref, groupinforef, alt_textref, existing_terms):    
    new_and_existing_terms = dict() # union set of: (1) data read from database and (2) data read from files.
    lexicon_dict = dict()

    # Stage 1 - scan term in constant ref.

    for term in constantref:
        tl_term = normalize_text(term)

        if tl_term not in lexicon_dict.keys():
            lexicon_dict[tl_term] = {'text': tl_term, 'groups': set(), 'constant_strings.dat': True, 'synsetid': ''}

    # Stage 2 - scan all groups.

    for grp_name in groupinforef.keys():
        for term_in_grp in groupinforef[grp_name]:
            tl_term_in_grp = normalize_text(term_in_grp)

            if tl_term_in_grp not in lexicon_dict.keys():
                
                lexicon_dict[tl_term_in_grp] = {'text': tl_term_in_grp, 'groups': {grp_name}, 'constant_strings.dat': False, 'synsetid': ''}
                continue
                                 
            lexicon_dict[tl_term_in_grp]['groups'].add(grp_name)

    # Stage 3 - Find what "Synonym Set ID" <term> is in.

    for ssid in alt_textref.keys():
        for term_in_ssid in alt_textref[ssid]:
            tl_term_in_ssid = normalize_text(term_in_ssid)

            if tl_term_in_ssid not in lexicon_dict.keys():
                
                lexicon_dict[tl_term_in_ssid] = {'text': tl_term_in_ssid, 'groups': set(), 'constant_strings.dat': False, 'synsetid': ssid}
                continue

            lexicon_dict[tl_term_in_ssid]['synsetid'] = ssid
            
    mycursor = myconn.cursor()
    longest_term_len = 0
    only_new_terms = list()

    char_position_cache = dict()
    id_char_pos = dict()
    
    from_files_set = set(lexicon_dict.keys())
    from_database = set(existing_terms.keys())

    deleted_terms = from_database.difference(from_files_set)

    try:
        if len(deleted_terms) > 0:
            logging.info("Detected that some terms have been deleted.  That is, terms exist in the database table 'global_term_catalogue' but do not exist anywhere in disk files.  Removing unnecesary terms from database...")
            logging.info("The terms in question are as follows: " + str(deleted_terms))
            
            term_id_lst = ''
            
            for term_text in deleted_terms:
                term_id_lst += (str(existing_terms[term_text]) + ',')

            term_id_lst = term_id_lst[0:-1]
            sql = 'select distinct(char_pos_map_ref) from char_pos_term_id where term_id in (' + term_id_lst + ')'
            logging.info("Getting list of 'char_pos_map_ref' values that are associated with these terms, using the query: [" + sql + "]")            
            mycursor.execute(sql)
            fetched_records = list(mycursor.fetchall())

            sql = 'delete from char_pos_term_id where term_id in (' + term_id_lst + ')'
            logging.info("Removing unneeded entries in table 'char_pos_term_id' - using SQL: [" + sql + "]")
            mycursor.execute(sql)

            for record in fetched_records:

                char_pos_map_ref = record[0]
                sql_for_char_pos_term_id = 'select count(*) from char_pos_term_id where char_pos_map_ref = ' + str(char_pos_map_ref)        

                logging.info("Checking if ID of '"  + str(char_pos_map_ref) + "' is still needed or not, using query: [" + sql_for_char_pos_term_id + "]")
                mycursor.execute(sql_for_char_pos_term_id)
                records = mycursor.fetchall()

                if len(records) != 1:
                    logging.error("Problem executing SQL: [" + sql_for_char_pos_term_id + "]: number of rows returned is NOT 1.")
                    raise Exception("Problem executing SQL: [" + sql_for_char_pos_term_id + "]")

                count = records[0][0]
                if count == 0:
                    # Ok, so this ID (char_pos_map_ref) value is not used anymore, may as well remove it from table char_pos_map.
                    sql = 'delete from char_pos_map where id = ' + str(char_pos_map_ref)
                    logging.info("Nope, ID value of " + str(char_pos_map_ref) + " is not used anymore - [" + sql_for_char_pos_term_id + "] returned zero!  Will remove this ID by using query: [" + sql + "]")
                    mycursor.execute(sql)
                else:
                    logging.info("We still need ID value of " + str(char_pos_map_ref) + " - Because query '" + sql_for_char_pos_term_id + "' returned a value of " + str(count) + ".  I will NOT remove this ID.")
            
            sql = 'delete from global_term_catalogue where termid in (' + term_id_lst + ')'
            logging.info("Removing unneeded terms in table 'global_term_catalogue' using SQL: [" + sql + "]")
            mycursor.execute(sql)
                                
        for term_text in lexicon_dict.keys():
            
            if term_text in existing_terms.keys():
                new_and_existing_terms[term_text] = existing_terms[term_text]                
                continue

            only_new_terms.append(term_text)
            if len(term_text) > longest_term_len: longest_term_len = len(term_text)

            mycursor.execute('INSERT INTO global_term_catalogue(term_text) VALUES("' + term_text + '")')
            new_and_existing_terms[term_text] = mycursor.lastrowid

        for i in range(longest_term_len):
            str_i = str(i)

            for new_term in only_new_terms:

                len_new_term = len(new_term)
                if i >= len_new_term: continue
                char_at = new_term[i]

                if char_at not in char_position_cache.keys(): char_position_cache[char_at] = dict()
                if str_i not in char_position_cache[char_at].keys(): char_position_cache[char_at][str_i] = set()

                (char_position_cache[char_at][str_i]).add(new_and_existing_terms[new_term])
        
        mycursor.execute("SELECT id, char_value, position_value FROM char_pos_map")
        for record in mycursor.fetchall():
            (db_id, db_char, db_pos) = (record[0], record[1], record[2])

            if record[1] == '': db_char = ' ' # mySQL does an 'Auto-trim' i think. When saving to a CHAR(1) and pushing just a space, it saves it as an empty string.
            # Thus we are correcting for that above : if we see empty string coming back from the db, make it a space.

            if db_char not in id_char_pos.keys(): id_char_pos[db_char] = dict()            
            id_char_pos[db_char][str(db_pos)] = db_id                    
                
        for ch in char_position_cache.keys():
                                    
            for idx in char_position_cache[ch].keys():

                Need_to_Insert = False

                if ch not in id_char_pos.keys(): 
                    Need_to_Insert = True
                    id_char_pos[ch] = dict()
                elif idx not in id_char_pos[ch].keys():
                    Need_to_Insert = True
                
                if Need_to_Insert:
                    # ASSERTION                    
                    
                    if ch == '':
                        raise Exception("Trying to insert empty string into table 'char_pos_map'")

                    sql = 'INSERT INTO char_pos_map(char_value, position_value) VALUES("' + ch + '",' + idx + ")"
                    logging.info("Executing SQL: [" + sql + "]")
                    mycursor.execute(sql)
                    id_char_pos[ch][idx] = mycursor.lastrowid
                    print("I just added that '" + ch + "' at index: " + idx + ' is ID ' + str(id_char_pos[ch][idx]))                    
                else:
                    print("Cool, I already had that '" + ch + "' at index: " + idx + ' was ID ' + str(id_char_pos[ch][idx]))

                for term_id in char_position_cache[ch][idx]:
                    sql = 'INSERT INTO char_pos_term_id(char_pos_map_ref, term_id) VALUES(' + str(id_char_pos[ch][idx]) + ', ' + str(term_id) + ')'
                    logging.info("Executing SQL: [" + sql + "]")
                    mycursor.execute(sql)
                                                                                        
    except Exception as ex:
        logging.error("Exception thrown in build_lexicon(): Error was: " + str(ex))
        raise ex

    finally:
        mycursor.close()
        myconn.commit()

    return (lexicon_dict, new_and_existing_terms)


def load_alt_text(logging, rl, basepath, alt_text_path, ref):
    logging.info("Loading alt_text (synonym sets) from '" + alt_text_path + "'")
    if not os.path.isdir(alt_text_path):
        logging.info("The alt_text directory '" + alt_text_path + "' does not exist yet. That's okay.")
        return

    try:
        for ent in os.listdir(alt_text_path):
            key = alt_text_path + "/" + ent

            if rl > 0 and os.path.isfile(key):
                # rl > 0 : because we want to ignore files in base directory.
                key_wo_base = re.sub('^' + basepath, '', key)
                if key_wo_base[0] == '/': key_wo_base = key_wo_base[1:]

                ref[key_wo_base] = set()
            
                with open(key, 'r') as fh:
                    for term in fh.readlines():
                        term = term.strip()
                        if len(term) == 0: continue

                        # if comment, continue to next (skip)
                        if term[0] == '#': continue
                        term = re.sub('\s{2,}', ' ', term)
                        term = re.sub('\t', '', term)
                        term = adjust_for_apos_s(term)
                                                
                        if term in term in ref[key_wo_base]:                        
                            logging.info("Term '" + term + "' mentioned more than once in file '" + key + "'.  It's okay, I ignored duplicates, but you may want to fix.")
                                                    
                        ref[key_wo_base].add(term)
                        
            if os.path.isdir(key):
                load_alt_text(logging, rl + 1, basepath, key, ref)

    except Exception as ex:
        logging.error("Exception occured in load_alt_text() - " + str(ex))
        raise ex


def get_list_of_synonyms(ref, termin):
    res = set()

    for atid in ref.keys():
        synset = ref[atid]
        if termin in synset:
            for otherterm in synset: res.add(otherterm)

    return res


def is_x_a_synonym_of_y(ref, x, y):

    for atid in ref.keys():
        synonym_set = ref[atid]
        if (x in synonym_set) and (y in synonym_set):
            return True

    return False


def get_constant_file_contents(logging, fn):
    con_file_con = set()

    if not os.path.isfile(fn): return con_file_con
    try:    
    
        with open(fn, 'r') as fh:
            for linestr in fh:
                linestr = linestr.strip()
                linestr = re.sub('\t', ' ', linestr)
                linestr = re.sub('\s{2,}', ' ', linestr)
                if linestr == "": continue
                con_file_con.add(linestr)

    except Exception as ex:
        logging.error("Problem in get_constant_file_contents(): " + str(ex))
        raise ex

    logging.info("Successfully loaded constant file '" + fn + "'")        
    return con_file_con


def update_fast_string_scan_cache(myconn, logging, cons_file, grp_dir, alt_dir):

    alt_text = dict()

    try:

        groupinfo = load_group_contents(logging, grp_dir)        
        constantinfo = get_constant_file_contents(logging, cons_file)
        load_alt_text(logging, 0, alt_dir, alt_dir, alt_text)

        saw_member_in_syn_set = dict()
        for atid in alt_text.keys():
            for term in alt_text[atid]:
                if term in saw_member_in_syn_set.keys():
                    logging.error("In synonym set database - term '" + term + "' came up twice! First in '" + saw_member_in_syn_set[term] + "' and second in '" + atid + "'.  Please fix.")                    
                    raise Exception("Term in two different synonym sets")

                else:
                    saw_member_in_syn_set[term] = atid        
        
        existing_global_terms = get_existing_global_term_list(myconn, logging)

        # naet : new and existing terms.
        (lex, naet) = build_lexicon(myconn, logging, constantinfo, groupinfo, alt_text, existing_global_terms)

        #for TERM in naet.keys():
        #    is_new = False
        #    the_id = naet[TERM]
        #    if TERM not in existing_global_terms.keys(): is_new = True

            #print("VS TERM: [" + TERM + "], NEW:[" + str(is_new) + "], ID:[" + str(the_id) + "]")

        #print("\n--------------- [START] : THIS OUTPUT TO BE PUT IN CART ERAF ----------------------")
        #for v in lex.values():
        #    print(">>> " + str(v))
        #print("\n---------------- [END] : THIS OUTPUT TO BE PUT IN CART ERAF ----------------------")
        #print("~~~~~~~~~~~~~~-------------------")
        #print(str(constantinfo))

        #len_ptr = dict()




    except Exception as ex:
        raise Exception(str(ex))
