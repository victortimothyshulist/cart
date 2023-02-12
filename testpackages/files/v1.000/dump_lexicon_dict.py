_CART_lex = ""
for _CART_lex_txt in sorted(lexicon_dict.keys()):
   _CART_lex_grps = ""

   for _CART_lex_grp in sorted(lexicon_dict[_CART_lex_txt]['groups']):
      _CART_lex_grps += _CART_lex_grp + ','

   _CART_lex_synsets = ""
   for _CART_synset in sorted(lexicon_dict[_CART_lex_txt]['synsetids']):
      _CART_lex_synsets += _CART_synset + ','

   _CART_lex_grps = _CART_lex_grps[0:-1]
   _CART_lex_synsets = _CART_lex_synsets[0:-1]

   _CART_lex += _CART_lex_txt + ':GROUPS=' + _CART_lex_grps + ':constant_strings=' + str(lexicon_dict[_CART_lex_txt]['constant_strings.dat']) + ':symbolsets=' + _CART_lex_synsets + "\n"

cartlog("lexicon", _CART_lex)

