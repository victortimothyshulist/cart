def dumptable(myconn, tn, conditions = ""):

   _CART_sql = "SELECT * FROM " + tn;
   
   if conditions != "":
      _CART_sql += " WHERE " + conditions

   _CART_sql += ";"

   _CART_mycursor = myconn.cursor()
   _CART_mycursor.execute(_CART_sql)
   _CART_records = _CART_mycursor.fetchall()
   _CART_str = ''
   _CART_row_num = 0

   for _CART_row in _CART_records:
      _CART_row_num += 1
 
      for _CART_col in _CART_row:
         _CART_col_val = ''

         if isinstance(_CART_col, int):
            _CART_col_val = str(_CART_col).zfill(3)
         else:
            _CART_col_val = _CART_col

         _CART_str += str(_CART_col_val) + "|"

      if _CART_row_num != len(_CART_records): 
         _CART_str = _CART_str + "\n"
      
   return _CART_str


