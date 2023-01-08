
###  we need to update CART so it can IMPORT include files
###  from not just conalaun.py, but any *.py file

####  after we do that...  put the following line  in "term_manager.py"  at line # 111 .. just before "mycursor = "

##       #CART_INCLUDE_v1.000_dump_tables.py
##

##    then take out the above comment

_CART_lex = ""
for _CART_lex_txt in sorted(lexicon_dict.keys()):
   _CART_lex_grps = ""
   for _CART_lex_grp in sorted(lexicon_dict[_CART_lex_txt]{'groups'}):
      _CART_lex_grps += _CART_lex_grp + ','

   _CART_lex_grps = _CART_lex_grps[0:-1]

   _CART_lex += _CART_lex_txt + ':GROUPS=' + _CART_lex_grps + ':constant_strings=' + str(lexicon_dict[_CART_lex_txt]['constant_strings.dat']) + ':symbolset=' + str(lexicon_dict[_CART_lex_txt]['synsetid']) + "\n"

cartlog("lexicon", _CART_lex)