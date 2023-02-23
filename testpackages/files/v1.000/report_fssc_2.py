_CART_sqlcommand = dict()

_CART_sqlcommand[" :05"] = "select term_text from global_term_catalogue where termid IN (SELECT term_id FROM char_pos_term_id  where char_pos_map_ref = (SELECT id FROM char_pos_map where char_value = \" \" and position_value=05)) order by term_text asc"
_CART_sqlcommand[" :08"] = "select term_text from global_term_catalogue where termid IN (SELECT term_id FROM char_pos_term_id  where char_pos_map_ref = (SELECT id FROM char_pos_map where char_value = \" \" and position_value=08)) order by term_text asc"
_CART_sqlcommand[" :12"] = "select term_text from global_term_catalogue where termid IN (SELECT term_id FROM char_pos_term_id  where char_pos_map_ref = (SELECT id FROM char_pos_map where char_value = \" \" and position_value=12)) order by term_text asc"
_CART_sqlcommand["':06"] = "select term_text from global_term_catalogue where termid IN (SELECT term_id FROM char_pos_term_id  where char_pos_map_ref = (SELECT id FROM char_pos_map where char_value = \"'\" and position_value=06)) order by term_text asc"
_CART_sqlcommand["a:01"] = "select term_text from global_term_catalogue where termid IN (SELECT term_id FROM char_pos_term_id  where char_pos_map_ref = (SELECT id FROM char_pos_map where char_value = \"a\" and position_value=01)) order by term_text asc"
_CART_sqlcommand["a:10"] = "select term_text from global_term_catalogue where termid IN (SELECT term_id FROM char_pos_term_id  where char_pos_map_ref = (SELECT id FROM char_pos_map where char_value = \"a\" and position_value=10)) order by term_text asc"
_CART_sqlcommand["a:14"] = "select term_text from global_term_catalogue where termid IN (SELECT term_id FROM char_pos_term_id  where char_pos_map_ref = (SELECT id FROM char_pos_map where char_value = \"a\" and position_value=14)) order by term_text asc"
_CART_sqlcommand["b:00"] = "select term_text from global_term_catalogue where termid IN (SELECT term_id FROM char_pos_term_id  where char_pos_map_ref = (SELECT id FROM char_pos_map where char_value = \"b\" and position_value=00)) order by term_text asc"
_CART_sqlcommand["b:09"] = "select term_text from global_term_catalogue where termid IN (SELECT term_id FROM char_pos_term_id  where char_pos_map_ref = (SELECT id FROM char_pos_map where char_value = \"b\" and position_value=09)) order by term_text asc"
_CART_sqlcommand["c:13"] = "select term_text from global_term_catalogue where termid IN (SELECT term_id FROM char_pos_term_id  where char_pos_map_ref = (SELECT id FROM char_pos_map where char_value = \"c\" and position_value=13)) order by term_text asc"
_CART_sqlcommand["d:00"] = "select term_text from global_term_catalogue where termid IN (SELECT term_id FROM char_pos_term_id  where char_pos_map_ref = (SELECT id FROM char_pos_map where char_value = \"d\" and position_value=00)) order by term_text asc"
_CART_sqlcommand["e:16"] = "select term_text from global_term_catalogue where termid IN (SELECT term_id FROM char_pos_term_id  where char_pos_map_ref = (SELECT id FROM char_pos_map where char_value = \"e\" and position_value=16)) order by term_text asc"
_CART_sqlcommand["g:11"] = "select term_text from global_term_catalogue where termid IN (SELECT term_id FROM char_pos_term_id  where char_pos_map_ref = (SELECT id FROM char_pos_map where char_value = \"g\" and position_value=11)) order by term_text asc"
_CART_sqlcommand["i:10"] = "select term_text from global_term_catalogue where termid IN (SELECT term_id FROM char_pos_term_id  where char_pos_map_ref = (SELECT id FROM char_pos_map where char_value = \"i\" and position_value=10)) order by term_text asc"
_CART_sqlcommand["r:02"] = "select term_text from global_term_catalogue where termid IN (SELECT term_id FROM char_pos_term_id  where char_pos_map_ref = (SELECT id FROM char_pos_map where char_value = \"r\" and position_value=02)) order by term_text asc"
_CART_sqlcommand["r:03"] = "select term_text from global_term_catalogue where termid IN (SELECT term_id FROM char_pos_term_id  where char_pos_map_ref = (SELECT id FROM char_pos_map where char_value = \"r\" and position_value=03)) order by term_text asc"
_CART_sqlcommand["s:07"] = "select term_text from global_term_catalogue where termid IN (SELECT term_id FROM char_pos_term_id  where char_pos_map_ref = (SELECT id FROM char_pos_map where char_value = \"s\" and position_value=07)) order by term_text asc"
_CART_sqlcommand["v:15"] = "select term_text from global_term_catalogue where termid IN (SELECT term_id FROM char_pos_term_id  where char_pos_map_ref = (SELECT id FROM char_pos_map where char_value = \"v\" and position_value=15)) order by term_text asc"
_CART_sqlcommand["y:04"] = "select term_text from global_term_catalogue where termid IN (SELECT term_id FROM char_pos_term_id  where char_pos_map_ref = (SELECT id FROM char_pos_map where char_value = \"y\" and position_value=04)) order by term_text asc"
_CART_sqlcommand["y:11"] = "select term_text from global_term_catalogue where termid IN (SELECT term_id FROM char_pos_term_id  where char_pos_map_ref = (SELECT id FROM char_pos_map where char_value = \"y\" and position_value=11)) order by term_text asc"

_CART_str = ''

for _CART_k in sorted(_CART_sqlcommand.keys()):
   _CART_sql = _CART_sqlcommand[_CART_k]
   
   _CART_str += _CART_k + '|'

   _CART_mycursor = myconn.cursor()
   _CART_mycursor.execute(_CART_sql)
   _CART_records = _CART_mycursor.fetchall()   
   
   for _CART_row in _CART_records:
      _CART_str += _CART_row[0] + ','

   _CART_str += "\n"

cartlog('termlist', _CART_str)
