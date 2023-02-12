if variable_fetch("_CART_FILEDB") == 'fssc' and variable_fetch("_CART_INPUT_LINE_NUMBER") == 0:

   _CART_res = ''
   for _CART_char in sorted(char_position_cache.keys()):
      for _CART_index in sorted(char_position_cache[_CART_char].keys()):
         for _CART_term in sorted(char_position_cache[_CART_char][_CART_index]):
            _CART_res += str(_CART_char) + ':' + str(_CART_index) + ':' + str(_CART_term) + '|' 

   cartlog("fssc", _CART_res)

   only_new_terms = _CART_PREV_only_new_terms 
   longest_term_len = _CART_PREV_longest_term_len 
   new_and_existing_terms = _CART_PREV_new_and_existing_terms


