
if variable_fetch("_CART_FILEDB") == 'fssc' and variable_fetch("_CART_INPUT_LINE_NUMBER") == 0:

   _CART_PREV_only_new_terms = only_new_terms
   _CART_PREV_longest_term_len = longest_term_len
   _CART_PREV_new_and_existing_terms = new_and_existing_terms

   longest_term_len = 5 # make SURE that this really is longest of below terms...

   only_new_terms = list()
   only_new_terms.append('ab') 
   only_new_terms.append('amnop') # longest is 5.  ** if you change this list, make sure to adjust variable 'longest_term_len' above.	 
   only_new_terms.append('xayz') 
   only_new_terms.append('bayz') 

   new_and_existing_terms = dict() 

   new_and_existing_terms['ab'] = 1970
   new_and_existing_terms['amnop'] = 1973
   new_and_existing_terms['xayz'] = 14
   new_and_existing_terms['bayz'] = 82

   # the above tests the code below, in conalaun.py

   # if char_at not in char_position_cache.keys(): char_position_cache[char_at] = dict()  # case 1
   # if str_i not in char_position_cache[char_at].keys(): char_position_cache[char_at][str_i] = set() # case 2
   # (char_position_cache[char_at][str_i]).add(new_and_existing_terms[new_term]) # case 3


