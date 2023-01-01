import os
import os.path
import re
import mysql.connector
import logging
import term_manager


def get_type(linein):
    if linein[0] >= 'a' and linein[0] <= 'z':  
        return 'R'
    elif linein[0] >= 'A' and linein[0] <= 'Z':
        return 'S'
    elif linein[0] == '"':
        return 'L'
    else:
        return '?'


def find_relations(myconn, cidref, catalog_ref, Iref, C1ref, O1ref, O2ref, O3ref):
    # return True if all good, return False if error
    try:
        mycursor = myconn.cursor()

        for rr_catalogue_id in range(len(catalog_ref)):
            rr_name = catalog_ref[rr_catalogue_id]
            
            class_text_lines_type = 'O2'
            lines_ref = O2ref   

            for typeandset in (('I', Iref), ('C1', C1ref), ('O1', O1ref),  ('O2', O2ref), ('O3', O3ref)):
                class_text_lines_type = typeandset[0]
                lines_ref = typeandset[1]

                for class_text_lines_idx in range(len(lines_ref)):

                    if class_text_lines_type == 'I' and class_text_lines_idx > 0: break
                    # We have the above 'break' line because we only need first line of I-lines. Why?
                    # Because all I-lines have to have the same set of RRs.
                     
                    current_line = lines_ref[class_text_lines_idx]
                    vn = -1

                    for current_word in current_line.split():                
                        colon_is_at = current_word.find(':')
                        if colon_is_at== -1: continue
                        start_index = 0
                        # start index is 0 but if starts with '?' or '=' then it's 1.
                        if current_word[0] == '?' or current_word[0] == '=': start_index = 1
                        current_rr_name = current_word[start_index:colon_is_at]
                        vn += 1
                        if current_rr_name[0] >= 'A' and current_rr_name[0] <= 'Z': continue

                        if current_rr_name == rr_name:
                            sql = 'INSERT INTO rr_relations(cidref, rr_catalogue_id, class_text_lines_type, class_text_lines_idx, vn) VALUES('
                            sql += cidref + ', '
                            sql += str(rr_catalogue_id) + ', '
                            sql += '"' + class_text_lines_type + '", '
                            sql += str(class_text_lines_idx) + ', '
                            sql += str(vn)
                            sql += ')'                        
                            mycursor.execute(sql)                    
                    
    except mysql.connector.Error as e:                     
        logging.error("Problem in find_relations(): " + e.msg)
        myconn.rollback()
        return False

    return True
             

def determine_concept_description(inlist, reg_repl):
    newlist = list()
    ec_list_of_lists = list()
    
    for linestr in inlist:
        ec_list = list()
        vn = -1
        desc = ""
        
        for word in linestr.split():
            idx_of_colon = word.find(':')
            idx_of_at = word.find('@')

            if idx_of_colon == -1:
                # It's a constant.
                desc += " " + word            
                continue

            # Ok, not a constant.  It's a replaceable.
            vn += 1

            if idx_of_at == -1:
                grp = word[(idx_of_colon + 1):]
                desc += " :" + grp            
            else:
                grp = word[(idx_of_colon + 1):idx_of_at]
                desc += " :" + grp
                ec_text = word[(idx_of_at + 1):]
                reg_repl_txt = word[0:idx_of_colon]

                # No need to have two or more instances of same regular replaceable and extra conditon:
                if reg_repl_txt not in reg_repl: 
                    reg_repl.add(reg_repl_txt)
                else:
                    #INFO: I already know about [" + reg_repl_txt + "] having: EC [" + ec_text + "]")
                    continue
                                
                if (ec_text[0] >= 'A') and (ec_text[0] <= 'Z'):
                    ec_list.append((vn, 0, ec_text))
                else:
                    ec_list.append((vn, 1, ec_text))
                
        ec_list_of_lists.append(ec_list)            
        desc = desc.strip()
        newlist.append(desc)

    return (newlist, ec_list_of_lists)


def get_symbol_list(inline):
    symbol_list = list()
    cur_const = ""

    for term in inline.split():
        if term[0] == ":":

            if cur_const != "":
                symbol_list.append((0, cur_const[1:]))
                cur_const = ""

            symbol_list.append((1, term[1:]))
        else:
            cur_const += " " + term

    if cur_const != "":
        symbol_list.append((0, cur_const[1:]))
    
    return symbol_list


def compile_concept(conn, cidref, expanded_list, reg_repl, typestr, ref, line_operators, cisa):
    # cisa = concept-is-a
    cisa_for_c = dict() # This can be defined here because all C lines are done in one invocation of this function.
    sql_dup_detection = set()
    sql_dup_removal = set()

    mycursor = conn.cursor()
    (desc, extra_conditions) = determine_concept_description(expanded_list, reg_repl)

    try:
        tids = 0
        for idx in range(len(extra_conditions)):            
            all_ec = extra_conditions[idx]
            
            for ec_entry in all_ec:                
                (vn, is_cons, name) = (str(ec_entry[0]), str(ec_entry[1]), ec_entry[2])
                if is_cons: name = name.replace('_',' ')
                sql = 'INSERT INTO class_extra_conditions(cidref, type, idx, vn, name, is_cons) VALUES(' + cidref + ', "' + typestr + '", ' + str(idx) + ', ' + vn + ', "' + name + '", ' + is_cons + ')'                
                mycursor.execute(sql)
        
        line_idx_adr = -1 # line_idx_adr : same as 'line_idx' variable below, but after duplicate removal.

        for line_idx in range(len(desc)):
    
            if cisa != None:
                concept_str = expanded_list[line_idx]
                concept_str = concept_str.replace('?', '')
                concept_str = concept_str.replace('=', '')

                setting_now = typestr + ' ' + line_operators[line_idx]

                if concept_str not in cisa: 
                    cisa[concept_str] = setting_now
                elif cisa[concept_str] != setting_now:                    
                    logging.error("The concept: [" + concept_str + "] is on two different O-lines with two different operators! Please fix.  One line has this concept with operator: [" + setting_now + "] and the other with operator: [" + cisa[concept_str] + "]")                    
                    return False                        

            if typestr == 'C':
                concept_str = expanded_list[line_idx]
                setting_now = line_operators[line_idx]
                
                if concept_str not in cisa_for_c:
                    cisa_for_c[concept_str] = setting_now
                elif cisa_for_c[concept_str] != setting_now:                    
                    logging.error("The concept [" + concept_str + "] is on two different C1-lines with two different operators! Please fix.  One line has this concept with operator: [" + setting_now + "] and the other with oeprator: [" + cisa_for_c[concept_str] + "]")
                    return False

            new_or_existing_tid = None
            desc_line = desc[line_idx]
            symbol_seq = get_symbol_list(desc_line)

            sql = 'SELECT tid FROM concepts WHERE description = "' + desc_line + '"'            
            mycursor.execute(sql)
            records = mycursor.fetchall()

            if len(records) > 1:
                logging.error("More than one row returned when checking if a concept exists.  This shouldn't happen! Please check database sanity! Template is: [" + desc_line + "]")                
                conn.rollback()
                return False
            
            if len(records) == 1:               
                tids +=1
                new_or_existing_tid = str(records[0][0])
            else:
                sql = 'INSERT INTO concepts(description) VALUES("' + desc_line + '")'                     
                mycursor.execute(sql)
                new_or_existing_tid = mycursor.lastrowid
                tids += 1
                
                for symbol_num in range(len(symbol_seq)):
                    symbol_data = symbol_seq[symbol_num]
                    sql = 'INSERT INTO concept_symbols(tidref, idx, type, name) VALUES('  + str(new_or_existing_tid) + ', ' + str(symbol_num) + ', ' + str(symbol_data[0]) + ',"' + str(symbol_data[1]) + '")'                     
                    mycursor.execute(sql)

            domain_value = "NULL"
            exist_value = "NULL"
            type_col = typestr
            
            if (typestr == "C"):
                domain_value = '"E"'
                exist_value = '"Y"'
                type_col = 'C1'

                if (line_operators[line_idx]).count('>') == 0:
                    if len(line_operators[line_idx]) == 2: 
                        domain_value = '"I"'
                    if line_operators[line_idx][0] == "-":
                        exist_value = '"N"'
            elif (typestr == "O1" or typestr == "O3"):
                domain_value = '"E"'
                if len(line_operators[line_idx]) == 2: 
                    domain_value = '"I"'                
            elif (typestr == "O2"):
                    # O21 - update only. *no create* if not there.
                    # O22 - update, but if no row was updated, create a row.
                    type_col = 'O21'
                    domain_value = '"E"'

                    if (line_operators[line_idx]).count('+') > 0: type_col = 'O22'
                    if line_operators[line_idx] == '>>': domain_value = '"I"'
                    if line_operators[line_idx] == '++>': domain_value = '"I"'
                               
            line_operator_sql = ''
            if line_operators != None: line_operator_sql = (line_operators[line_idx] + ' ')
            
            if typestr == "I" or typestr == "C":                    
                line_without_ec = line_operator_sql + re.sub('@\S+', '', expanded_list[line_idx])
                
                if line_without_ec in sql_dup_detection:
                    # Note - we cannot remove duplicates for I-line and C1-lines while at the same time keeping the original line text.
                    # Example: if you had three lines:
                    #
                    #     a:w qqqqqqq  b:   rrrrrrrrrr  c:
                    #     a:  qqqqqqq  b:x  rrrrrrrrrr  c:
                    #     a:  qqqqqqq  b:   rrrrrrrrrr  c:y
                    #
                    # There is no way to satsify both requirements of: (a) keep original line text --AND-- (b) remove duplicate lines.
                    # The only way to do that would be of course to expand all lines so they are like:
                    #
                    #     a:w qqqqqqq  b:x  rrrrrrrrrr  c:y
                    #     a:w qqqqqqq  b:x  rrrrrrrrrr  c:y
                    #     a:w qqqqqqq  b:x  rrrrrrrrrr  c:y
                    #
                    # But we don't want to do this.  It is less 'noisy' if we declare for example 'a' to be in group 'w' in only one place.
                    # Thus, if duplicates exist for I-line or C1-lines, we will FTC (fail to compile).
                    # For O1,O2,O3,O4 lines we can remove the duplicates automatically.  Why? because for SMOL types, ALL RRs must -NOT- have a group given, and ALL SRs -MUST HAVE- a group given.
                    # Thus any duplicate lines will be identical, thus auto-de-duplication is simple.
                    #
                    logging.error("There is a duplication of " + typestr + "-line: [" + line_without_ec + "].  *Note: This is the expanded version of the line - so you may not be able to just 'copy' and 'find' the exact text in your ICO.")                    
                    return False                

                sql_dup_detection.add(line_without_ec)
                line_idx_adr += 1                
                sql = 'INSERT INTO class_text_lines(cidref, type, idx, tidref, domain, exist, text) VALUES(' + cidref + ', "' + type_col + '", ' + str(line_idx_adr) + ', ' + str(new_or_existing_tid)  + ', ' + domain_value + ', ' + exist_value + ', "' + line_operator_sql + ref[line_idx] + '")'
                mycursor.execute(sql)

            else:
                line_with_operator = line_operator_sql + expanded_list[line_idx]
                # Okay, we're dealing with an "O" line. Either O1,O2,O3.
                if line_with_operator not in sql_dup_removal:
                    sql_dup_removal.add(line_with_operator)
                    line_idx_adr += 1
                    text_sql = ref[line_idx]
                    text_sql = text_sql.replace('"', '""')                    
                    sql = 'INSERT INTO class_text_lines(cidref, type, idx, tidref, domain, exist, text) VALUES(' + cidref + ', "' + type_col + '", ' + str(line_idx_adr) + ', ' + str(new_or_existing_tid)  + ', ' + domain_value + ', ' + exist_value + ', "' + line_operator_sql + text_sql + '")'
                    mycursor.execute(sql)                    
                    
                    class_text_lines_id_ref = mycursor.lastrowid
                    vn = -1

                    for term in (expanded_list[line_idx]).split():
                        colon_at = term.find(':')
                        if colon_at == -1: continue

                        term_wo_operator = term # 'wo' = without
                        vtype = 'NULL'
                        
                        if term[0] == '=' or term[0] == '?':
                            term_wo_operator = term[1:]
                            colon_at -= 1

                        if term[0] == '?': vtype = "'I'"
                        if term[0] == '=': vtype = "'T'" 

                        term_wo_operator_and_group = term_wo_operator[0:colon_at]
                        vn += 1

                        sr_name = 'NULL'
                        is_cons = 'NULL'
                        
                        if term_wo_operator_and_group == '*':
                            sr_name = '"*"'
                        elif (term_wo_operator_and_group[0] >= 'A' and term_wo_operator_and_group[0] <= 'Z') or (term_wo_operator_and_group[0] == '"'):
                            # It's an SR, not RR. But is it a literal SR? or a variable SR?

                            sr_name = term_wo_operator_and_group
                            is_cons = '"N"'

                            if sr_name[0] == '"':                                
                                is_cons = '"Y"'
                            else:
                                sr_name = '"' + sr_name + '"'

                        sql_sr_name = sr_name.replace('_', ' ')
                        sql = 'INSERT INTO smol_variables(class_text_lines_id_ref, vn, vtype, sr_name, is_cons) VALUES(' + str(class_text_lines_id_ref) + ', ' + str(vn) + ', ' + vtype + ', ' + sql_sr_name + ', ' + is_cons + ')'                            
                        mycursor.execute(sql)
                                                                                                                                                                                            
    except Exception as ex:    
        logging.error("Error attempting to add records for ICO.  Error was: " + str(ex) + " (during type: " + type_col + " processing). SQL was: [" + sql + "]")
        return False

    if tids != len(desc):
        logging.error("ASSERTION FAILED: len(tids) != len(desc).  I failed to find or create a TID for each concept.  This is for type: " + typestr)        
        conn.rollback()
        return False

    return True


def get_constant_substrings(inlist, cur_cons_list, cons_to_add):
    # This function also ensures that all I-lines have the same set of replaceables.
    # They can be in any order of course, but same set across all I-lines.
    first_set = set()
    latest_line_set = set()
    line_number = 0
    
    for linestr in inlist:
        line_number += 1
        cur_sub_str = ""

        for term in linestr.split():
            if term.count(':') == 0:
                cur_sub_str += " " + term 
            else:
                term_no_ec = term
                mo = re.match('^(.+?)@.*$', term)
                if bool(mo):                    
                    term_no_ec = mo.group(1)
                
                if line_number == 1:
                    first_set.add(term_no_ec)
                else:
                    latest_line_set.add(term_no_ec)

                cur_sub_str = cur_sub_str[1:]
                if cur_sub_str != "":
                    if cur_sub_str not in cur_cons_list: cons_to_add.add(cur_sub_str)
                    cur_sub_str = ""

        if line_number > 1:
            sym_diff = first_set.symmetric_difference(latest_line_set)
            if len(sym_diff) > 0:
                logging.error("There is a difference in the set of replaceables between two or more of your I-lines.  One I-line has the set: [" + str(first_set) + "] and another line has set: [" + str(latest_line_set) + "], please correct.  All I-lines must have exactly the same set of replaceables.  The difference in sets is: [" + str(sym_diff) + "]")                
                return False

        latest_line_set.clear()

        if cur_sub_str != "":
            cur_sub_str = cur_sub_str[1:]
            if cur_sub_str not in cur_cons_list: cons_to_add.add(cur_sub_str)

    return True
    

def expand_all_reg_replaceables(lol, mapa, mapb):
    # lol = list of lines
    newlol = list()

    for linestr in lol:
        newlinestr = ""

        for item_wp in linestr.split():
            prefix = "" # only applies if OL type 2.
            item = item_wp
            # _wp = with prefix (for OL-2s)

            if item_wp[0] == '?' or item_wp[0] == '=':
                # for OL-2 - update or update/create, each RR starts with '?' or '='
                # need to get the RR (which starts of course after that first charactor)                
                item = item_wp[1:]
                prefix = item_wp[0]                                
                            
            if (item.count(':') == 0) or (item.count('@') == 1):
                newlinestr += " " + item
                continue

            if item[-1] != ":":
                newlinestr += " " + prefix + item
                continue

            # discovered group
            disc_grp = mapa.get(item[0:-1])

            if disc_grp == None:
                entry = mapb.get(item[0:-1])
                if entry == None:
                    logging.error("Regular replaceable '" + item[0:-1] + "' does not have a group.")                
                    return []
                disc_grp = entry[0]
                
            newlinestr += " " + prefix + item[0:-1] + ":" + disc_grp        
        newlinestr = newlinestr.strip()
        newlol.append(newlinestr)
    return newlol


def get_all_reg_replaceables(instr, rr_level_1: set, rr_level_2: dict, rr_level_3: dict, gmta: dict, gi: dict):
    for item in instr.split():
        if item.count(':') == 0: continue
        idx_of_at = item.find('@')
        idx_of_colon = item.find(':')

        if idx_of_colon == len(item) - 1:
            valstr =item[0:-1]            
            rr_level_1.add(valstr)            
            continue

        if idx_of_at == -1:
            rr_name = item[0: idx_of_colon]
            rr_group = item[idx_of_colon + 1:]                                    
        else:
            rr_name = item[0: idx_of_colon]
            rr_group = item[idx_of_colon + 1:idx_of_at]
            rr_extra_cond = item[idx_of_at + 1:]                    
            
        prev_group_if_any = rr_level_2.get(rr_name)
        if prev_group_if_any != None and prev_group_if_any != rr_group:
            logging.error("Regular replaceable '" + rr_name + "' has two different groups associated with it.  '" + prev_group_if_any + "' and '" + rr_group + "'.  Please correct.")            
            return False

        prev_group_if_any = rr_level_3.get(rr_name)
        if prev_group_if_any != None and prev_group_if_any[0] != rr_group:
            logging.error("Regular replaceable '" + rr_name + "' has two different groups associated with it.  '" + prev_group_if_any[0] + "' and '" + rr_group + "'.  Please correct.")            
            return False
        
        if rr_group not in gi: 
            gi[rr_group] = set()

        if rr_name not in gi[rr_group]:
            if rr_group not in gmta:
                gmta[rr_group] = set()
            gmta[rr_group].add(rr_name)

        if idx_of_at == -1:
            rr_level_2[rr_name] = rr_group            
        else:            
            rr_level_3[rr_name] = (rr_group, rr_extra_cond)            
            if prev_group_if_any != None and prev_group_if_any[1] != rr_extra_cond:
                logging.error("Regular replaceable '" + rr_name + "' has two different extra conditions.   One is '" + prev_group_if_any[1] + "' and '" + rr_extra_cond + "'")                
                return False            

    return True


def problem_in_ol_3_line(strin):
    # basic rule that is specific for O-3 lines is: A star ('*') must be proceeded by either: (a) start of line (^), -OR- (b) space
    # and must be immediately followed by a colon. Else FTC.
    # cannot end a line with asterisk.
    if strin[-1] == '*':
        logging.error("Delete line cannot end with asterisk.  Please correct.  Line is [" + strin + "]")        
        return True

    if strin[-1:-3:-1] == ':*':    
        logging.error("Delete line ends with *: but does not have group name after the colon.  Please correct.")        
        return True

    for i in range(0, len(strin) - 2):
        if strin[i] == '*' and (strin[i + 1] != ':' or strin[i + 2] == ' '):
            logging.error("Delete line contains an asterisk, which is fine, but the asterisk is not followed by a colon and group name. It must be.  Please fix.  Line is [" + strin + "]")        
            return True
    
    for i in range(1, len(strin)):
        if strin[i] == '*' and strin[i - 1] != ' ':
            logging.error("Delete line contains an asterisk, which is fine, but it is proceeded by a charactor that is NOT a space.  Please fix.  All asterisks need a space right before them (or be first charactor on thre line).  Line is [" + strin + "]")
            return True        


def problem_in_ol_2_line(strin):
    num_equals = 0
    num_question = 0

    if strin[-1] == '?' or strin[-1] == '=':
        logging.error("For Update or Update/Create line - line ends with '?' or '='.  No line can end with '?' or '='.  Please correct.  Line is [" + strin + "]")
        return True

    for termtxt in strin.split():
        if termtxt[0] == '?':
            num_question += 1
        elif termtxt[0] == '=':
            num_equals += 1

        if termtxt[0] == '?' or termtxt[0] == '=':
            # OK.. better contain \S+\S+ after the '?'
            mo = re.match('^.\S+:.*$', termtxt)
            if not bool(mo):
                logging.error("Replaceable '" + termtxt + "' needs VNOV and colon (and group if VNOV is not an RR).")
                return True

        if (termtxt.count(':') > 0) and (termtxt[0] != '?' and termtxt[0] != '='):
            logging.error("Replaceable " + termtxt + " does not start with '?' nor '='.  All replaceables for update lines (or update/create lines) must start with '?' or '='.  LIne is [" + strin + "]")
            return True

    if num_equals == 0:        
        logging.error("For Update or Update/Create line - There are no replaceables with '=' prefix.  Please fix. Line with issue is: [" + strin + "]")
        return True

    if num_question == 0:
        logging.error("For Update or Update/Create line - There are no replaceables with '?' prefix.  Please fix. Line with issue is: [" + strin + "]")
        return True

    for i in range(1, len(strin)):
        if (strin[i] == '?' or strin[i] == '=') and strin[i - 1] != ' ':
            logging.error("For Update or Update/Create line - The '?' or '=' is not preceeded by a space.  All '?' or '=' must be preceeded by a space (or start of line).  Line is [" + strin + "]")
            return True

    return False


def problem_Oline(linestr, raw, REG_SR, allow_star=False):

    mo_group_after_rr = re.match('^.*[a-z]:\S.*$', linestr)
    if bool(mo_group_after_rr):
        logging.error("An O-line contains an RR (regular replaceable) followed by a colon, but after the colon is a NON-space.  For Regular Replaceables please just put a colon after and do NOT specify group.  It will be found from a C-line or I-line.  Line is [" + raw + "]")
        return True

    if get_items_before_colon(linestr, raw, REG_SR, allow_star) == False: 
        logging.error("Problem with line '" + linestr + "'")
        return True

    if linestr[0] == ':':
        logging.error("Line starts with a colon (':') - invalid syntax.  Line is [" + raw + "]")
        return True
    
    mo_double_colon = re.match('^.*::.*$', linestr)
    if bool(mo_double_colon):
        logging.error("Two consecutive colons (':') are not allowed.  Bad line is [" + raw + "].  Please correct.")
        return True

    mo_empty = re.match('^.*"".*$', linestr)
    if bool(mo_empty):
        logging.error("No empty literals allowed. Line is: [" + raw + "]")
        return True

    lst_qm_indices = get_ind_list('"', linestr)

    if (len(lst_qm_indices) % 2) != 0:
        logging.error("You have an odd number of quote marks in your line.  Line is [" + raw + "].  You have " + str(len(lst_qm_indices)) + " quote marks.  That's an odd number. Must be even.")
        return True

    if len(lst_qm_indices) > 0:
        for i in range(int(len(lst_qm_indices) / 2)):
            st_idx = lst_qm_indices[i * 2]
            en_idx = lst_qm_indices[(i * 2) + 1]

            sub_str_is = linestr[st_idx + 1:en_idx]               
            mo_only_lower_case = ''

            mo_only_lower_case = re.match('^.*[^a-z0-9_].*$', sub_str_is)
            
            if bool(mo_only_lower_case):
                logging.error("Invalid charactors inside your literal.  Can only have 'a'-'z', '0'-'9' or underscore.  Literal is [" + sub_str_is + "], on line: [" + raw + "].  You must encode spaces inside literals as underscore.  They will be converted.")
                return True

    cnt_qm = -1
    for i in range(len(lst_qm_indices)):
        cnt_qm += 1
        is_odd = i % 2
        idx = lst_qm_indices[i]
        
        if not is_odd:
            # even
            if idx == 0: continue
            if linestr[idx - 1] != ' ':
                logging.error("The opening quote mark is not preceeded by either space or start of line.  All opening quote marks must be preceeded by either (start-of-line -or- space).  Line is [" + raw + "].  Talking about quote mark number " + str(cnt_qm + 1) + " in the line.")
                return True                     

        else:
            # odd..
            if (idx + 2) > (len(linestr) - 1):
                logging.error("The closing quote mark (quote mark number " + str(cnt_qm + 1) + " of the line), is not followed by a colon and a group name. Line is [" + raw + "]")
                return True
            elif linestr[idx + 1] != ':' or ord(linestr[idx + 2]) < 97 or ord(linestr[idx + 2]) > 122:
                logging.error("The closing quote mark (quote mark number " + str(cnt_qm + 1) + " of the line), is not followed by a colon and a group name. Line is [" + raw + "].  Note- Group name must be all in lowercase.")
                return True             

    for term_txt in linestr.split(" "):
        if term_txt.count(':') == 0:
            mo_has_uc = re.match('^.*[A-Z].*$', term_txt)
            if bool(mo_has_uc):
                logging.error("O-line contains a term that has UPPERCASE, but there is no colon and group name given.  Please correct.  Line is [" + raw + "].  Term I'm talking about is [" + term_txt + "]")
                return True

    return False


def get_ind_list(char2find, inputstr):
    last_idx = 0
    lst_indices = list()

    while True:
        last_idx = inputstr.find(char2find, last_idx)            
        if last_idx == -1: break
        lst_indices.append(last_idx)
        last_idx += 1
 
    return lst_indices


def get_items_before_colon(inputstr, raw, regsr, allow_star=False):
    # return True if no errors.
    # return False if error.
    items = list()
    items_aft = list()
    
    for index in get_ind_list(':', inputstr):                

        if inputstr[index - 1] == ' ': 
            logging.error("Charactor before ':' is a space.  That's invalid syntax.  Line is [" + raw + "]")
            return False

        # first find all items before each ':'.            
        cur_item = ""    
        for i in range(index - 1, -1, -1):                    
            if i == 0:
                cur_item += inputstr[0] # due to strip() earlier, we know [0] will not be a space, so we know we need to capture.
                items.append(cur_item[::-1])
                cur_item = ''                
            if inputstr[i] != ' ': 
                cur_item += inputstr[i]                
            elif cur_item != '':
                items.append(cur_item[::-1])
                cur_item = ''
                break

        # now find all items after each ':'
        # note- lowercase text before ':' will have no text after the ':'.
        cur_item = ''

        for i in range(index, len(inputstr), 1):

            if i == len(inputstr) - 1:
                if inputstr[i] != ':': cur_item += inputstr[i]
                items_aft.append(cur_item)
                break

            if inputstr[i] == ':': continue

            if inputstr[i] != ' ':
                cur_item += inputstr[i]
            elif cur_item != '':
                items_aft.append(cur_item)
                cur_item = ''
                break
            else:
                items_aft.append(cur_item)
                break
    
    if len(items) != len(items_aft):
        logging.error("*ASSERTION FAILED: len(items) != len(items_aft) in get_items_before_colon().")
        return False

    for i in range(len(items)):

        if items_aft[i] != '':
            mo_invalid_chars = re.match('^[a-z0-9_]+$', items_aft[i])
            if not bool(mo_invalid_chars):
                logging.error("Group given has invalid charactors.  Group names can only be 'a'-'z', '0'-'9' and underscore.  Group given is: [" + items_aft[i] + "], of line: [" + raw + "]")
                return False

        if items[i][0] >= 'A' and items[i][0] <= 'Z' and len(items_aft[i]) == 0:
            logging.error("No group name given for the special replaceable '" + items[i] + "' - please add group name.  Line is [" + raw + "]")
            return False
                            
    for item in items:
        mo_invalid = re.match('^[a-zA-Z0-9_"]+$', item)
        if not bool(mo_invalid):
            if (item == '*' and not allow_star) or (item != '*'):
                logging.error("VNOV has invalid charactors.  VNOV is [" + item + "], on line: [" + raw + "]")
                return False

        mo_lower = re.match('^.*[a-z].*$', item)  
        mo_upper = re.match('^.*[A-Z].*$', item)

        if bool(mo_upper) and bool(mo_lower):
            logging.error("Line has a VNOV that is mixed case.  The VNOV is [" + item + "], of line: [" + raw + "]")
            return False

        if bool(mo_upper) and (item not in regsr) and item[0] != '"':
            logging.error("Line has an SR that is not registered.  The unregistered SR is [" + item + "], of line: [" + raw + "]")
            return False
    
    return True


def not_allowed_char(ltype, cc):
    
    not_allowed = True

    ALLOW_UPPERCASE = False
    ALLOW_LOWERCASE = False
    ALLOW_COLON = False
    ALLOW_SPACE = False
    ALLOW_APOSTROPE = False
    ALLOW_AT_SIGN = False
    ALLOW_DIGITS = False
    ALLOW_QUOTE_MARK = False
    ALLOW_QUESTION_MARK = False
    ALLOW_EQUAL_SIGN = False
    ALLOW_STAR = False
    ALLOW_UNDERSCORE = False

    if ltype == "I":        
        ALLOW_UPPERCASE = True
        ALLOW_LOWERCASE = True
        ALLOW_COLON = True
        ALLOW_SPACE = True
        ALLOW_APOSTROPE = True
        ALLOW_AT_SIGN = True
        ALLOW_DIGITS = True
        ALLOW_UNDERSCORE = True

    if ltype == "C1":               
        ALLOW_UPPERCASE = True
        ALLOW_LOWERCASE = True
        ALLOW_COLON = True
        ALLOW_SPACE = True        
        ALLOW_AT_SIGN = True
        ALLOW_DIGITS = True
        ALLOW_UNDERSCORE = True

    if ltype == "C2":                       
        ALLOW_UPPERCASE = True
        ALLOW_LOWERCASE = True        
        ALLOW_SPACE = True            
        ALLOW_DIGITS = True
        ALLOW_UNDERSCORE = True
        ALLOW_QUOTE_MARK = True

    if ltype == "O1":             
        ALLOW_UPPERCASE = True
        ALLOW_LOWERCASE = True
        ALLOW_COLON = True
        ALLOW_SPACE = True    
        ALLOW_DIGITS = True
        ALLOW_QUOTE_MARK = True
        ALLOW_UNDERSCORE = True

    if ltype == "O2":               
        ALLOW_UPPERCASE = True
        ALLOW_LOWERCASE = True
        ALLOW_COLON = True
        ALLOW_SPACE = True    
        ALLOW_DIGITS = True
        ALLOW_QUOTE_MARK = True
        ALLOW_QUESTION_MARK = True
        ALLOW_EQUAL_SIGN = True
        ALLOW_UNDERSCORE = True

    if ltype == "O3":                        
        ALLOW_UPPERCASE = True
        ALLOW_LOWERCASE = True
        ALLOW_COLON = True
        ALLOW_SPACE = True    
        ALLOW_DIGITS = True
        ALLOW_QUOTE_MARK = True
        ALLOW_STAR = True
        ALLOW_UNDERSCORE = True

    if ALLOW_UPPERCASE and (cc >= 65 and cc <= 90): return False
    if ALLOW_LOWERCASE and (cc >= 97 and cc <= 122): return False
    if ALLOW_COLON and (cc == 58): return False
    if ALLOW_SPACE and (cc == 32): return False
    if ALLOW_APOSTROPE and (cc == 39): return False
    if ALLOW_AT_SIGN and (cc == 64): return False
    if ALLOW_DIGITS and (cc >= 48 and cc <= 57): return False
    if ALLOW_QUOTE_MARK and (cc == 34): return False
    if ALLOW_QUESTION_MARK and (cc == 63): return False
    if ALLOW_EQUAL_SIGN and (cc == 61 ): return False
    if ALLOW_STAR and (cc == 42): return False
    if ALLOW_UNDERSCORE and (cc == 95): return False

    return not_allowed

    
def any_bad_chars(inputstr, ltype):
    for i in range(len(inputstr)):
        if not_allowed_char(ltype, ord(inputstr[i])):            
            return inputstr[i]
    return ""


def level_2_syntax_check(reg_sr, linfo):

    (line_type_txt, lines_ref) = (linfo)

    for iline in lines_ref:

        mo = re.match('^.*:@.*$', iline)
        if bool(mo):
            logging.error(line_type_txt + "-line contains the at-sign ('@') directly after the colon (':') - invalid syntax.  Please specify group after colon and before '@'.  Line is [" + iline + "]")
            return False
            
        for term_txt in iline.split():
            if term_txt.count('@') == 0:                
                mo_any_uc = re.match('^.*[A-Z]+.*$', term_txt)
                if bool(mo_any_uc):
                    logging.error(line_type_txt + "-line contains UPPERCASE letters in a section of the line that is not allowed to have them.  That's invalid syntax.  Line in question is [" + iline + "].  The section I'm talking about is [" + term_txt + "]" )
                    return False

        if ord(iline[0]) >= 65 and ord(iline[0]) <= 90:
            logging.error(line_type_txt + "-line starts with an UPPERCASE charactor.  That's incorrect syntax. Line in brackets is: [" + iline + "]")
            return False         

        if iline[0] == '@' or iline[-1] == '@':
            logging.error(line_type_txt + "-line either starts or ends (or both) with an at sign ('@') - bad syntax.  The bad line in brackets is [" + iline + "]")
            return False

        if iline[0] == ':':
            logging.error(line_type_txt + "-line starts with colon - invalid syntax: Line in square brackets is: [" + iline + "]")
            return False

        if iline[0] == '_':
            logging.error(line_type_txt + "-line starts with an underscore - invalid syntax: Line in square brackets is: [" + iline + "]")
            return False

        if ord(iline[0]) >= 48 and ord(iline[0]) <= 57:
            logging.error(line_type_txt + "-line starts with a digit.  That's incorrect syntax. Line in brackets is: [" + iline + "]")
            return False            

        on_last_char = False

        for chnum in range(1, len(iline)):

            cur_char = iline[chnum]
            prev_char = iline[chnum - 1]        
            ascii_prev_char = ord(prev_char)
            ascii_cur_char = ord(cur_char)
            next_char = ""

            if len(iline) == chnum + 1:
                on_last_char = True
            else:
                next_char = iline[chnum + 1]
                ascii_next_char = ord(next_char)

            if (cur_char == "_" or (ascii_cur_char >= 48 and ascii_cur_char <= 57)) and (prev_char == " "):
                logging.error(line_type_txt + "-line has a term that starts with a digit or underscore.  Bad syntax.  Please correct.  Line is [" + iline + "]")
                return False

            if (ascii_cur_char >= 65 and ascii_cur_char <= 90) and (not on_last_char) and (next_char != " ") and (ascii_next_char < 65 or ascii_next_char > 90) and (ascii_next_char < 48 or ascii_next_char > 57) and (ascii_next_char != 95):
                logging.error(line_type_txt + "-line contains an UPPERCASE charactor which is not followed by another UPPERCASE charactor, a space, a digit, underscore or end of line.  Line in brackets is [" + iline + "]")
                return False

            if (ascii_cur_char >= 65 and ascii_cur_char <= 90) and (ascii_prev_char < 65 or ascii_prev_char > 90) and prev_char != '@' and (ascii_prev_char < 48 or ascii_prev_char > 57) and (ascii_prev_char != 95):
                logging.error(line_type_txt + "-line contains an UPPERCASE charactor which is not preceeded by another UPPERCASE charactor or an 'at sign' (@) or digit or underscore  Line in brackets is: [" + iline + "]")
                return False
                
            if cur_char == ':' and (ascii_prev_char < 97 or ascii_prev_char > 122) and (ascii_prev_char < 48 or ascii_prev_char > 57):
                logging.error(line_type_txt + "-line contains a colon (:) but charactor preceeding it is not 'a' to 'z' and also not '0' to '9'.  Line in brackets is [" + iline + "]")
                return False

            if cur_char == '@' and (ascii_next_char < 97 or ascii_next_char > 122) and (ascii_next_char < 48 or ascii_next_char > 57) and (ascii_next_char < 65 or ascii_next_char > 90):
                logging.error(line_type_txt + "-line contains an 'at sign' (@) but charactor following it is not 'a' to 'z', nor 'A' to 'Z' and also not '0' to '9'. Line in brackets is [" + iline + "]")
                return False

            if cur_char == '@' and (ascii_prev_char < 97 or ascii_prev_char > 122) and (ascii_prev_char < 48 or ascii_prev_char > 57) and (ascii_prev_char != 58):
                logging.error(line_type_txt + "-line contains an 'at sign' (@) but charactor preceeding it is not 'a' to 'z' and also not '0' to '9' and also not colon (:) . Line in brackets is [" + iline + "]")
                return False

        for replaceable_str in re.findall('(\S+?)@(\S+)(?=\s|$)' ,iline):
            # The first part of replaceable (the VNOV - variable name or value) must always be in all lowercase.                  
            mo = re.match('^[a-z:0-9_]+$', replaceable_str[0])
            if not bool(mo):
                logging.error("'" + replaceable_str[0] + "' - this VNOV contains some invalid charactors.  Can only contain 'a'-'z', '0'-'9', colon (:) or underscore (_).  Make sure it has no UPPERCASE letters.  Offending line is [" + iline + "]")
                return False

            if (replaceable_str[0]).count(':') > 1:
                logging.error("'" + replaceable_str[0] + "' - this contains more than one colon (:). It must contain exactly one colon Offending line is [" + iline + "]")
                return False

            if (replaceable_str[0]).count(':') == 0:
                logging.error("'" + replaceable_str[0] + "' - this contains zero colons (:).  It must contain exactly one colon.  Offending line is [" + iline + "]")
                return False

            # the text after the '@' must be either an SR (special replaceable) and be either (a) ALL UPPERCASE or (b) all lowercase.
            # also, if it is all uppercase, it better be one of the known Special Replaceables.
            mo_contains_upper = re.match('.*[A-Z].*', replaceable_str[1])
            mo_contains_lower = re.match('.*[a-z].*', replaceable_str[1])
            
            if bool(mo_contains_upper) and bool(mo_contains_lower):
                logging.error("'" + replaceable_str[1] + "' contains mixed case.  Must be either all uppercase or all lowercase.  *OR* perhaps you have more than one at-sign (@) in a replaceable.")
                return False

            mo = re.match('^[a-zA-Z0-9_]+$', replaceable_str[1]) 
            if not bool(mo):
                logging.error("'" + replaceable_str[1] + "' contains invalid charactors.  Offending line is: [" + iline + "]")
                return False

    for iline in lines_ref:
        for srep in re.findall('@(.+?)(?=\s|$)', iline):
            if ord(srep[0]) >= 65 and ord(srep[0]) <= 90:
                if srep not in reg_sr:
                    logging.error("A line in your ICO file contains an SR that is not registered.  Line is [" + iline + "] and the SR is [" + srep  + "]")
                    return
                    
    return True


def process_class_file(SR_FN, CLASS_FILE_NAME, myconn, groupinfo, group_members_to_add, CON_LIST_FILE):
    
    # return False - if problem.
    # return True = if successfully parsed the ICO.
    c2_groups_to_check_later = dict()

    cur_cons_list = set() # currently the stuff in the file <CON_LIST_FILE>.
    cons_to_add = set() # anything we find in processing the new ICO file, that does not already exist (in cur_cons_list - we'll add to the file)

    if os.path.isfile(CON_LIST_FILE):
        try:
            with open(CON_LIST_FILE, 'r') as F:
                for linestr in F:
                    linestr = linestr.strip()
                    linestr = linestr.replace('\t','')
                    if linestr != '': cur_cons_list.add(linestr)
        except Exception as ex:
            logging.error("Problem loading file '" + CON_LIST_FILE + "'.  Exception details are: " + str(ex))
            return False
        
    REG_SR = set()

    if os.path.exists(SR_FN):
        with open(SR_FN, 'r') as F:
            for line in F.readlines():                
                line = line.strip()

                if len(line) == 0:
                    continue

                mo_has_space = re.match('^.*[^A-Z0-9_].*$', line)

                if bool(mo_has_space):
                    logging.error("You have an invalid charactor in one of your Special Replaceables.  The SR is [" + line + "].  All SRs must only contain UPPERCASE 'A' to 'Z' and '0' to '9' and underscore.")
                    return False
                
                REG_SR.add(line)

    if not os.path.exists(CLASS_FILE_NAME):
        logging.error("File '" + CLASS_FILE_NAME + "' does not exist.")
        return False

    with open(CLASS_FILE_NAME, 'r') as F:
        lines = F.readlines()

    I = list()

    CL_1 = list() # Context Line Type 1 (CL-1) deals with Database Table based information.
    CL_2 = list() # Context Line Type 2 (CL-2) deals with File Based information (group files, synonym database)

    OL_1 = list() # Output line Type 1 - Deals with CREATING a new state (regardless of whether one exists already or not).    
    OL_2 = list() # Output line Type 2 - Deals with UPDATING an existing state (OR, if one does not already exist, CREATE).
    OL_3 = list() # Output line Type 3 - Deals with REMOVING (deleting) an existing state. 
    OL_4 = list() # Output line Type 4 - Is meant only for sending to user a textual response to screen (and later, convert to speech).

    operator_for_c1_line = list() # "+", "++", "-", "--" read from external or internal, must exist or must not exist.
    operator_for_c2_line = list() # is in, is not in, is syn, is not syn

    operator_for_o1_line = list() # "+", "++" external or internal
    operator_for_o2_line = list() # "+", "++" external or internal, Also, UPDATE ? or UPDATE/CREATE ?
    operator_for_o3_line = list() # "+", "++" external or internal

    # don't need "operator_for_o4_line". A TOL is a TOL :)

    ltype = 0
    last_was_ws = True

    ln = 0
    for linestr in lines:
        ln += 1                
        linestr_strip = linestr.strip()            
        linestr_strip = re.sub('\t+', ' ', linestr_strip)
        linestr_strip = re.sub('\s{2,}', ' ', linestr_strip)
        if ltype == 0: linestr_strip = term_manager.adjust_for_apos_s(linestr_strip)

        if linestr_strip == "" and not last_was_ws:
            ltype += 1        
            if ltype == 3: break
                    
        last_was_ws = True
        if linestr_strip != "": last_was_ws = False
        if linestr_strip == "": continue
        if linestr_strip[0] == '#': continue    
        
        if ltype == 0:
            # We are in an "I" line.            
            the_bad_char_if_any = any_bad_chars(linestr_strip , "I")

            if the_bad_char_if_any != "":
                logging.error("There is a disallowed charactor in the following line in square brackets: [" + linestr_strip + "].\nThe disallowed charactor inside square brackets is: [" + the_bad_char_if_any + "].  That charactor is not allowed in an 'I' line.")
                return False
            
            I.append(linestr_strip)

        elif ltype == 1:
            mo = re.match('(\w+)\s(is in|is not in|is syn|is not syn)\s("?\w+"?)$', linestr_strip)
            mob = re.match('^([+-]{1,2})(.*)$', linestr_strip)
            c_line_without_operator = ""

            # We are in a "C" line. Determine which type (Type 1 - database table based) or Type 2 - file based (group or synonym subsystem).

            if bool(mob):                
                operator_for_c1_line.append(mob.group(1))
                c_line_without_operator = mob.group(2)
                c_line_without_operator = c_line_without_operator.strip()
                line_sub_type = "C1"       
                if c_line_without_operator == "":
                    logging.error("Context line has an operator but nothing else.  Operator is: " + str(mob.group(1)) + "\nFailed to compile ICO.")
                    return False
                CL_1.append(c_line_without_operator)
                
            elif bool(mo):
                # Type 2 - C - Line
                
                line_sub_type = "C2"
                c_line_without_operator = linestr_strip
                operator_for_c2_line.append(mo.group(2))
                CL_2.append(c_line_without_operator)
            else:
                logging.error("Invalid context line: [" + linestr_strip + "].  Must start with '+' or '-' or be one of: ('is in', 'is not in', 'is syn', 'is not syn').  These operators must be in lowercase! Also, check for invalid charactors.  For example, for Type-2 C-lines you cannot have at sign ('@') or other special charactors.  For file based context lines (Type 2 C-lines), only upper/lower and digits allowed.  *Note - if you are using literal string inside quote marks, then spaces need to be represented as underscore.  They'll be converted to spaces during compiling of the ICO.  Also, note you -CAN- say:  y is syn \"some_literal\" *BUT NOT* \"some_literal\"  is syn y.")
                return False

            the_bad_char_if_any = any_bad_chars(c_line_without_operator , line_sub_type)

            if the_bad_char_if_any != "":
                logging.error("There is a disallowed charactor in the following line in square brackets: [" + c_line_without_operator + "].\nThe disallowed charactor inside square brackets is: [" + the_bad_char_if_any + "]")
                logging.error("That charactor is not allowed in an '" + line_sub_type + "' line.")
                return False

        elif ltype == 2:            
            line_sub_type = ""

            # We are in a "O" line.  Line type 2. Now what sub-type of O line?
            
            if (ord(linestr_strip[0]) == 34 and ord(linestr_strip[-1]) != 34) or  (ord(linestr_strip[0]) != 34 and ord(linestr_strip[-1]) == 34):
                logging.error("O-Line starts with quote mark but does not end with a quote mark (OR vice-versa)  Please correct.")
                logging.error("Offending line is ["+ linestr_strip + "]")
                return False

            if ord(linestr_strip[0]) == 34 and ord(linestr_strip[-1]) == 34:
                # Nice, Line Type 2, Sub-type 4 - TOL.
                OL_4.append(linestr_strip[1:-1])      
                line_sub_type = "O4"

            else:
                op_and_line = linestr_strip.split(" ")
                
                if len(op_and_line) >= 2:
                    op_and_line_a = op_and_line[0]
                    op_and_line_b = " ".join(op_and_line[1:])
                    
                    mob_insert = False
                    mob_delete = False                    
                    mob_update = False
                    mob_insert_update = False

                    if op_and_line_a == '+' or op_and_line_a == '++': mob_insert = True
                    if op_and_line_a == '-' or op_and_line_a == '--': mob_delete = True
                    if op_and_line_a == '>' or op_and_line_a == '>>': mob_update = True
                    if op_and_line_a == '+>' or op_and_line_a == '++>': mob_insert_update = True
                    
                    o_line_without_operator = op_and_line_b.strip()
                    
                    if mob_insert:                
                        line_sub_type = "O1"
                        OL_1.append(o_line_without_operator)
                        operator_for_o1_line.append(op_and_line_a)                
                    elif mob_update:            
                        line_sub_type = "O2"
                        OL_2.append(o_line_without_operator)
                        operator_for_o2_line.append(op_and_line_a)                
                    elif mob_insert_update:                
                        line_sub_type = "O2"
                        OL_2.append(o_line_without_operator)
                        operator_for_o2_line.append(op_and_line_a)                
                    elif mob_delete:                
                        line_sub_type = "O3"
                        OL_3.append(o_line_without_operator)
                        operator_for_o3_line.append(op_and_line_a)                

            if line_sub_type == "":
                logging.error("Invalid output line: [" + linestr_strip + "].  All O-lines must start with either quotation mark (for TOLs), or plus sign (insert state), or negative sign (remove a state), or greator than sign (to update a state).  Note: You will get this error even if you have proper start charactor but no space after it.  I require a space after the operator.  Thanks :)" )
                return False
            
            if line_sub_type != "O4":
                the_bad_char_if_any = any_bad_chars(o_line_without_operator, line_sub_type) 
                
                if the_bad_char_if_any != "":
                    logging.error("There is a disallowed charactor in the following line in square brackets: [" + o_line_without_operator + "].\nThe disallowed charactor inside square brackets is: [" + the_bad_char_if_any + "]")                
                    logging.error("That charactor is not allowed in an '" + line_sub_type + "' line.")     
                    return False            
        
    extra_ignored = list()
    for i in range(ln, len(lines)):
        linestr = lines[i]
        linestr_strip = linestr.strip()
        if linestr_strip != "": extra_ignored.append(linestr_strip)

    if len(extra_ignored) > 0:
        logging.error("Failed to compile ICO file - There are extra lines not in 'I', 'C' or 'O' sections.  The extra lines are:")
        for exline in extra_ignored:
            logging.error(exline)
        return False

    if len(OL_1) + len(OL_2) + len(OL_3) + len(OL_4) == 0: 
        logging.error("No 'O' lines! There must be at least one O-line.") 
        return False    

    # Second-level filtering :)
    # First 'I' lines and 'C-1' lines.

    for lineinfo in (('I', I), ('C', CL_1)):
        if not level_2_syntax_check(REG_SR, lineinfo): return False     

    # Now 'C-2' lines
    for linestr in CL_2:

        mo = re.match('^(.+?)\s(is in|is not in|is syn|is not syn)\s(.+?)$', linestr)
        if not bool(mo):
            logging.error("C-2 line has bad syntax.  Line is [" + linestr + "]")
            return False

        param_operator = mo.group(2)
        param_1 = mo.group(1)
        param_2 = mo.group(3)

        # Enforce proper case for first and second parameters for 'Group membership" -- ('is in' OR 'is not in' operators):
        mo_has_lower = re.match('^.*[a-z].*$', param_1)
        mo_has_upper = re.match('^.*[A-Z].*$', param_1)

        if bool(mo_has_lower) and bool(mo_has_upper):
            logging.error("The first parameter is mixed case.  That's invalid syntax.  Line is [" + linestr + "].  Parameter with issue is [" + param_1 + "]")
            return False

        mo_has_lower2 = re.match('^.*[a-z].*$', param_2)
        mo_has_upper2 = re.match('^.*[A-Z].*$', param_2)

        if bool(mo_has_lower2) and bool(mo_has_upper2):
            logging.error("The second parameter is mixed case.  That's invalid syntax.  Line is [" + linestr + "].  Parameter with issue is [" + param_2 + "]")
            return False

        mo_any_invalid = re.match('^.*[^a-zA-Z0-9_].*$', param_1)
        if bool(mo_any_invalid):
            logging.error("First parameter has an invalid charactor.  Must be only A-Z, a-z, 0-9 or underscore.  Parameter with issue is [" + param_1 + "], of line: [" + linestr + "]")
            return False

        if bool(mo_has_upper) and param_1 not in REG_SR:
            logging.error("The special replaceable '" + param_1 + "' mentioned in line: [" + linestr + "], is not registered.")
            return False

        if param_operator == 'is in' or param_operator == 'is not in':
            
            mo_any_invalid = re.match('^.*[^a-z0-9_].*$', param_2)
            if bool(mo_any_invalid):
                logging.error("The group membership line: [" + linestr + "] contains an invalid charactor for second parameter.  The bad parameter is [" + param_2 + "]. Can only be 'a'-'z', '0'-'9' and underscore.")
                return False
        else:
            # okay, it's a Synonym operator.
            if bool(mo_has_upper) and param_2[0] != '"' and not bool(mo_has_upper2):
                logging.error("For your 'is syn/is not syn' line - your first parameter is an SR and your second parameter is an RR.  Not allowed, please switch their positions.  The line I'm talking about is: [" + linestr + "]")                
                return False

            if (param_2[0] == '"' and param_2[-1] != '"') or (param_2[0] != '"' and param_2[-1] == '"'):
                logging.error("Either your second parameter starts with quote but does not end with quote or vice versa, please correct.  Param is [" + param_2 + "], line is [" + linestr + "]")
                return False

            # if param 2 is enclosed in quotes then it is a literal, and thus must be all lowercase.

            if param_2[0] == '"' and param_2[-1] == '"':

                param_2_without_quotes = param_2[1:-1]
                mo_invalid_chars_in_literal = re.match('^.*[^a-z0-9_].*$', param_2_without_quotes)

                if bool(mo_invalid_chars_in_literal):
                    logging.error("The literal parameter has invalid charactors.  Must be only 'a'-'z', '0'-'9' or underscore (space not allowed - use underscore to encode).  Also UPPERCASE not allowed. Param 2 is a literal parameter (because you have it enclosed in quote marks) and is [" + param_2_without_quotes + "], line is [" + linestr + "]")
                    return False

            elif bool(mo_has_upper2) and param_2 not in REG_SR:
                logging.error("The special replaceable '" + param_2 + "' mentioned in line: [" + linestr + "], is not registered.")
                return False

    # now O-1 lines. This is Create only.
    
    for linestr in OL_1:                
        if problem_Oline(linestr, linestr, REG_SR, False): return False

    for raw in OL_2:
        linestr = raw
        linestr = re.sub('\?', '', linestr)
        linestr = re.sub('=', '', linestr)
        if problem_Oline(linestr, raw, REG_SR, False): return False

    # now O-2 lines. This is (a) Update --OR--- (b) Update-Or-Create (if zero rows were updated)
    for linestr in OL_2:
       if problem_in_ol_2_line(linestr): return False

    for linestr in OL_3:        
        if problem_Oline(linestr, linestr, REG_SR, True): return False
        if problem_in_ol_3_line(linestr): return False

    # During 'Regular Replaceable Unification' process (where 'bob:' is converted to 'bob:person' because being found elsewhere), don't forget to verifiy that 'bob:' does not change groups between lines 
    # or even inside same line!

    for linestr in CL_2:

        mo = re.match('^(\S+)\s(?:is in|is not in)\s(\S+)$', linestr)
        if bool(mo):                    
            grp_name = mo.group(2)

            if grp_name not in groupinfo.keys():
                c2_groups_to_check_later[grp_name] = "CL-2 line [" + linestr + "] references a group name '" + grp_name + "', which does not exist. Please correct."
                
    # Stage 2 of processing. (Stage 1 was doing level 1 and level 2 syntax check)
    # Stage 2 is "RR unifier" (and verifying RRs in C2 lines actually exist)
    # So this is where, as an example, if 'bob:' appears in some line #x and 'bob:person' appears in some other line #y
    # that we change line #y to read 'bob:person' also.  Also consider 'extra conditon' that may exist.
        
    rr_level_1 = set() # level 1 - RR is just name (example 'bob:') - no group or extra condition
    rr_level_2 = dict() # level 2 - RR is name and group (example: 'bob:person') - no extra condition
    rr_level_3 = dict() # level 3 - RR is name, group and extra condition (example: 'bob:person@HE')
        
    for linetxt in I:
        if get_all_reg_replaceables(linetxt, rr_level_1, rr_level_2, rr_level_3, group_members_to_add, groupinfo) == False:
            return False

    for linetxt in CL_1:        
        if get_all_reg_replaceables(linetxt, rr_level_1, rr_level_2, rr_level_3, group_members_to_add, groupinfo) == False:
            return False

    # Create any groups given on SMOL lines - where we have <SR>:<groupname>
    for ref in (OL_1, OL_2, OL_3):        
        for idx in range(len(ref)):
            for term in ref[idx].split():                
                colon_at = term.find(':')

                if colon_at == -1: continue
                if colon_at == len(term) - 1: continue
                    
                sr_grp_name = term[(colon_at + 1):]
                if sr_grp_name not in groupinfo.keys():                                        
                    group_members_to_add[sr_grp_name] = set()

    # Groups mentioned earlier in 'C2' lines, that do not exist in ./groups/* - do they exist now? (after processing this ICO file?)
    # If not, error out. FTC.
    for grp in c2_groups_to_check_later.keys():
        if grp not in group_members_to_add.keys():            
            logging.error(c2_groups_to_check_later[grp])
            return False
            
    for rr_name in rr_level_1:
        if (rr_name not in rr_level_2.keys()) and (rr_name not in rr_level_3.keys()):
            logging.error("Regular replaceable '" + rr_name + "' is never assigned a group name.  Please fix.")
            return False
    
    I_expanded = expand_all_reg_replaceables(I, rr_level_2, rr_level_3)
    if len(I) > 0 and len(I_expanded) == 0:        
        return False

    CL_1_expanded = expand_all_reg_replaceables(CL_1, rr_level_2, rr_level_3)
    if len(CL_1) > 0 and len(CL_1_expanded) == 0:
        return False

    OL_1_expanded = expand_all_reg_replaceables(OL_1, rr_level_2, rr_level_3)
    if len(OL_1) > 0 and len(OL_1_expanded) == 0:
        return False

    OL_2_expanded = expand_all_reg_replaceables(OL_2, rr_level_2, rr_level_3)
    if len(OL_2) and len(OL_2_expanded) == 0:
        return False
        
    OL_3_expanded = expand_all_reg_replaceables(OL_3, rr_level_2, rr_level_3)
    if len(OL_3) > 0 and len(OL_3_expanded) == 0:
        return False

    for i in range(len(CL_2)):
        # For operator 'is in' or 'is not in', only the first parameter can be an RR (if it is lowercase)
        # and 2nd parameter can always only be a group.
        operator =operator_for_c2_line[i]
        linestr = CL_2[i]
        terms = linestr.split()

        if (operator == 'is in' or operator == 'is not in') and (linestr[0] >= 'a' and linestr[0] <= 'z'):            
            # is this a known RR? meaning was it defined in an "I" line or "C1" line?
            if (terms[0] not in rr_level_2.keys()) and (terms[0] not in rr_level_3.keys()):
                logging.error("The regular replaceable: '" + terms[0] + "' mentioned on your [" + operator + "] line, is not defined in any I-line nor Context Type 1 line.  The RR '" + terms[0] + "' needs to be defined on either I-line or Type-1 Context line (table based Context line).  Full line text is: [" + linestr + "]")
                return False

        second_offset_at = 0 # terms[second_offset_at] == 3 if it is 'is syn' operator, else it is = 4. and of course =0 if it is not even an 'is syn' or 'is not syn' operator.

        if operator == 'is syn': 
            second_offset_at = 3
        elif operator == 'is not syn':
            second_offset_at = 4            
        
        if second_offset_at > 0:
            # is first argument an RR? if lowercase, yes. In that case check if it is a declared RR.
            if (terms[0][0] >= 'a') and (terms[0][0] <= 'z') and (terms[0] not in rr_level_2.keys()) and (terms[0] not in rr_level_3.keys()):
                logging.error("The regular replaceable: '" + terms[0] + "' mentioned on your [" + operator + "] line, is not defined in any I-line nor Context Type 1 line.  The RR '" + terms[0] + "' needs to be defined on either I-line or Type-1 Context line (table based Context line).  Full line text is: [" + linestr + "]")
                return False
            
            # now what about the second argument? is second argument an RR? if so, is it known (Declared in I-line or C1-line?)
            second_term_text = terms[second_offset_at]
            if (second_term_text[0] >= 'a') and (second_term_text[0] <= 'z') and (second_term_text not in rr_level_2.keys()) and (second_term_text not in rr_level_3.keys()):
                logging.error("The regular replaceable: '" + second_term_text + "' mentioned on your [" + operator + "] line, is not defined in any I-line nor Context Type 1 line.  The RR '" + second_term_text + "' needs to be defined on either I-line or Type-1 Context line (table based Context line).  Full line text is: [" + linestr + "]")
                return False

    if get_constant_substrings(I_expanded, cur_cons_list, cons_to_add) == False: return False

    try:        
        with open(CON_LIST_FILE, 'a') as F:
            for substr in cons_to_add:
                F.write(substr + "\n")
                
    except Exception as ex:
        logging.error("Problem updating constant substring list file ('" + CON_LIST_FILE + "').")
        logging.error("Exception details are: " + str(ex))
        return False    
    
    reg_repl = set()
        
    # Create class entry.
    cnt_i = len(I_expanded)
    cnt_c1 = len(CL_1_expanded)
    cnt_c2 = len(CL_2)
    cnt_o1 = len(OL_1_expanded)
    cnt_o2 = len(OL_2_expanded)
    cnt_o3 = len(OL_3_expanded)
    cnt_o4 = len(OL_4)

    sql = 'INSERT INTO class(cnt_i, cnt_c1, cnt_c2, cnt_o1, cnt_o2, cnt_o3, cnt_o4) VALUES('
    sql += str(cnt_i) + ', '
    sql += str(cnt_c1) + ', '
    sql += str(cnt_c2) + ', '
    sql += str(cnt_o1) + ', '
    sql += str(cnt_o2) + ', '
    sql += str(cnt_o3) + ', '
    sql += str(cnt_o4)
    sql += ')'
        
    try:        
        mycursor = myconn.cursor()
        mycursor.execute(sql)
        cid = str(mycursor.lastrowid)
        
        if not compile_concept(myconn, cid, I_expanded, reg_repl, "I", I, None, None): return False
        if not compile_concept(myconn, cid, CL_1_expanded, reg_repl, "C", CL_1, operator_for_c1_line, None): return False
        
        # Build the 'RR catalogue' - a distinct list of regular replaceables that appear in the ICO file.
        rr_catalog_set = set()
        rr_catalog_list = list()

        for rr_name in rr_level_2.keys(): rr_catalog_set.add(rr_name)
        for rr_name in rr_level_3.keys(): rr_catalog_set.add(rr_name)

        for name in rr_catalog_set: rr_catalog_list.append(name)
        rr_catalog_list_reverse = dict()

        rr_catalog_list_sorted = sorted(rr_catalog_list)

        for i in range(len(rr_catalog_list_sorted)):
            rr_catalog_list_reverse[rr_catalog_list_sorted[i]] = i
            sql = 'INSERT INTO rr_catalogue(cidref, id, name) VALUES(' + cid + ', ' + str(i) + ', "' + rr_catalog_list_sorted[i] + '")'
            mycursor.execute(sql)

        c2_dup_detect = set()

        i_adr = -1 # i_adr : same as 'i' variable below, but after duplicate removal.
        for i in range(len(CL_2)):
            if CL_2[i] not in c2_dup_detect:
                i_adr += 1
                c2_dup_detect.add(CL_2[i])
                escaped_quotes = (CL_2[i]).replace('"', '""')                        
                sql = 'INSERT INTO class_text_lines(cidref, type, idx, tidref, domain, exist, text) VALUES(' + cid + ', "C2", ' + str(i_adr) + ', NULL, NULL, NULL, "' + escaped_quotes + '")'            
                mycursor.execute(sql)

        if not find_relations(myconn, cid, rr_catalog_list_sorted, I_expanded, CL_1_expanded, OL_1_expanded, OL_2_expanded, OL_3_expanded): return False

        concept_is_a = dict()
        if not compile_concept(myconn, cid, OL_1_expanded, reg_repl, "O1", OL_1, operator_for_o1_line, concept_is_a): return False
        if not compile_concept(myconn, cid, OL_2_expanded, reg_repl, "O2", OL_2, operator_for_o2_line, concept_is_a): return False
        if not compile_concept(myconn, cid, OL_3_expanded, reg_repl, "O3", OL_3, operator_for_o3_line, concept_is_a): return False

        o4_dup_detect = set()

        i_adr = -1 # i_adr : same as 'i' variable below, but after duplicate removal.
        for i in range(len(OL_4)):
            if OL_4[i] not in o4_dup_detect:
                o4_dup_detect.add(OL_4[i])                
                i_adr += 1
                sql = 'INSERT INTO class_text_lines(cidref, type, idx, tidref, domain, exist, text) VALUES(' + cid + ', "O4", ' + str(i_adr) + ', NULL, NULL, NULL, "' + OL_4[i] + '")'                 
                mycursor.execute(sql)
        
        # Now compile 'C2' type lines.
        rr_cat_num_to_group_and_exist = dict()
        syn_dict = dict()        
        
        for i in range(len(CL_2)):
            operator = operator_for_c2_line[i]

            if operator == 'is in' or operator == 'is not in':
                                
                opposite_group = 'is in'
                if operator == 'is in': opposite_group = 'is not in'
                c2_line = CL_2[i]
                
                mo = re.match('^(.+)\s+' + operator + '\s+(.+)$', c2_line)
                if bool(mo):
                    rr_or_sr = mo.group(1) # regular replaceable or special replaceable.
                    group_name_str = mo.group(2) # group name

                    if rr_or_sr not in rr_cat_num_to_group_and_exist.keys():  rr_cat_num_to_group_and_exist[rr_or_sr] = dict()
                    if operator not in (rr_cat_num_to_group_and_exist[rr_or_sr]).keys(): rr_cat_num_to_group_and_exist[rr_or_sr][operator] = set()

                    if opposite_group in (rr_cat_num_to_group_and_exist[rr_or_sr]).keys():
                        if group_name_str in (rr_cat_num_to_group_and_exist[rr_or_sr][opposite_group]):                    
                            logging.error("Wait, you want the replaceable '" + rr_or_sr + "' to be in, AND NOT be in, group '" + group_name_str + "' ?!!  That makes no sense. Please fix ICO file.")
                            return False

                    if group_name_str in (rr_cat_num_to_group_and_exist[rr_or_sr][operator]):
                        # no sense adding duplicates                            
                        continue
                    
                    rr_cat_num_to_group_and_exist[rr_or_sr][operator].add(group_name_str)

                    exist_YN = 'Y'
                    if operator == 'is not in': exist_YN = 'N'

                    if rr_or_sr[0] >= 'A' and rr_or_sr[0] <= 'Z':
                        # Special replaceable...
                        sql = 'INSERT INTO sr_group_member_conditions(cidref, sr_name, group_name, exist) VALUES(' + cid + ', "' + rr_or_sr + '", "' +  group_name_str + '", "' +  exist_YN + '")'
                        mycursor.execute(sql)                    
                    else:
                        # Regular replaceable.
                        cur_rr_catalog_id = rr_catalog_list_reverse[rr_or_sr]
                        sql = 'INSERT INTO rr_group_member_conditions(cidref, rr_catalogue_id, group_name, exist) VALUES(' + cid + ', ' +  str(cur_rr_catalog_id) + ', "' + group_name_str + '", "' + exist_YN + '")'                        
                        mycursor.execute(sql)
                else:
                    logging.error("*WEIRD: This should not happen. C2-Line did not match regex.")
                    return False
            elif operator == 'is syn' or operator == 'is not syn':
                opposite_is = 'is not syn'
                true_or_not = 'true'

                if operator == 'is not syn': 
                    opposite_is = 'is syn'
                    true_or_not = 'false'

                c2_line = CL_2[i]
                mo = re.match('^(.+)\s+' + operator + '\s+(.+)$', c2_line)
                if bool(mo):
                    polarity = 'Y'
                    if operator == 'is not syn': polarity = 'N'
                    param_1_text = mo.group(1)
                    param_2_text = mo.group(2)

                    param_1_id = None
                    param_2_id = None

                    if param_1_text == param_2_text:
                        logging.error("There is no point to the C2 line: [" + c2_line + "].  The result will always be " + true_or_not + ".  Please remove or edit this line.")
                        return False

                    param_1_type = get_type(param_1_text)                    
                    param_2_type = get_type(param_2_text)

                    if param_1_type == '?' or param_2_type == '?':
                        logging.error("Problem with parameters with syn/not syn line.")
                        return False

                    if param_1_type == 'R': param_1_id = rr_catalog_list_reverse[param_1_text]
                    if param_2_type == 'R': param_2_id = rr_catalog_list_reverse[param_2_text]

                    if operator not in syn_dict.keys(): syn_dict[operator] = dict()
                    if opposite_is not in syn_dict.keys(): syn_dict[opposite_is] = dict()

                    if param_1_text not in (syn_dict[operator]).keys(): syn_dict[operator][param_1_text] = set()
                    if param_1_text not in (syn_dict[opposite_is]).keys(): syn_dict[opposite_is][param_1_text] = set()

                    if param_2_text in syn_dict[opposite_is][param_1_text]:
                        logging.error("Wait, you want '" + param_1_text + "' to be a synonym and yet NOT be a synonym of '" + param_2_text + "'?  That makes no sense.  Please correct your ICO.")
                        return False
                                         
                    if param_2_text in (syn_dict[operator][param_1_text]): 
                        # no sense adding duplicate rows!
                        continue 
                    (syn_dict[operator][param_1_text]).add(param_2_text)

                    sql = ''

                    if param_1_type == 'R':
                        # First param is 'R', Regular replaceable.

                        if param_2_type == 'R':
                            sql = 'INSERT INTO syn_rr_to_rr(cidref, rr_catalogue_id_1, rr_catalogue_id_2, polarity) VALUES(' + cid + ', ' + str(param_1_id) + ', ' + str(param_2_id) + ', "' + polarity + '")'
                        elif param_2_type == 'S':
                            sql = 'INSERT INTO syn_rr_to_sr(cidref, rr_catalogue_id, sr_name, is_cons, polarity) VALUES(' + cid + ', ' + str(param_1_id) + ', "' + param_2_text + '", "N", "' + polarity + '")'                            
                        elif param_2_type == 'L':
                            # let's remove the quote marks :)
                            literal_string = param_2_text[1:-1]
                            literal_string = literal_string.replace('_', ' ')
                            sql = 'INSERT INTO syn_rr_to_sr(cidref, rr_catalogue_id, sr_name, is_cons, polarity) VALUES(' + cid + ', ' + str(param_1_id) + ', "' + str(literal_string) + '", "Y", "' + polarity + '")'                              
                    elif param_1_type == 'S':
                        # First param is 'S', Special replaceable.

                        if param_2_type == 'S':
                            sql = 'INSERT INTO syn_sr_to_sr(cidref, sr_name_1, sr_name_2, second_sr_is_cons, polarity) VALUES(' + cid + ', "' + param_1_text + '", "' + param_2_text + '", "N", "' + polarity + '")'                            
                        elif param_2_type == 'L':
                            # let's remove the quote marks :)
                            literal_string = param_2_text[1:-1]
                            literal_string = literal_string.replace('_', ' ')
                            sql = 'INSERT INTO syn_sr_to_sr(cidref, sr_name_1, sr_name_2, second_sr_is_cons, polarity) VALUES(' + cid + ', "' + param_1_text + '", "' + literal_string + '", "Y", "' + polarity + '")'
                            
                    if sql == '': 
                        logging.error("No SQL generated for syn/not syn insert.")
                        return False

                    mycursor.execute(sql)
                else:
                    logging.error("*WEIRD: This should not happen. C2-Line did not match regex.")                    
                    return False                
            else:
                logging.error("*HUH ?!! This should not happen - what operator is '" + operator + "' ?!!")
                return False

    except mysql.connector.Error as e:    
        logging.error("Problem creating class table entry for ICO file: " + e.msg)        
        myconn.rollback()
        return False
  
    # TO DO  TO DO TO DO --  Go and check that all "return" statements in this function return False for error and only when get to end of function do we return True
    # TO DO  TO DO TO DO --  Go and check that all "return" statements in this function return False for error and only when get to end of function do we return True
    # TO DO  TO DO TO DO --  Go and check that all "return" statements in this function return False for error and only when get to end of function do we return True
    # TO DO  TO DO TO DO --  Go and check that all "return" statements in this function return False for error and only when get to end of function do we return True
    # TO DO  TO DO TO DO --  Go and check that all "return" statements in this function return False for error and only when get to end of function do we return True
    # TO DO  TO DO TO DO --  Go and check that all "return" statements in this function return False for error and only when get to end of function do we return True
    # TO DO  TO DO TO DO --  Go and check that all "return" statements in this function return False for error and only when get to end of function do we return True
    # TO DO  TO DO TO DO --  Go and check that all "return" statements in this function return False for error and only when get to end of function do we return True
    # TO DO  TO DO TO DO --  Go and check that all "return" statements in this function return False for error and only when get to end of function do we return True
    # TO DO  TO DO TO DO --  Go and check that all "return" statements in this function return False for error and only when get to end of function do we return True
    # TO DO  TO DO TO DO --  Go and check that all "return" statements in this function return False for error and only when get to end of function do we return True
    # TO DO  TO DO TO DO --  Go and check that all "return" statements in this function return False for error and only when get to end of function do we return True
    # TO DO  TO DO TO DO --  Go and check that all "return" statements in this function return False for error and only when get to end of function do we return True
    
    return True