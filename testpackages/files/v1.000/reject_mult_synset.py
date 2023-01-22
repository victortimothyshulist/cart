_CART_lst_synsets = list()
_CART_lst_synsets.append(saw_member_in_syn_set[term])
_CART_lst_synsets.append(atid)
_CART_lst_synsets_sorted = sorted(_CART_lst_synsets)

cartlog("multsynset", "In synonym set database - term '" + term + "' came up twice! All terms can only belong to zero or at most one synonym set. The syn sets it belongs to are: " + str(_CART_lst_synsets_sorted))


