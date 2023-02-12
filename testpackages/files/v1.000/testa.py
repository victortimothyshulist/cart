_CART_poa = "ABSENT" # poa = present or absent?

if cart_dump_table.dumptable(myconn, "char_pos_term_id", "term_id = (select termid from global_term_catalogue where term_text='z' )") != "":
   _CART_poa = "PRESENT"

cartlog("testa", _CART_poa)


