_CART_grp_str = ''

if os.path.isdir("./groups"):
   for _CART_entry in os.listdir("./groups"):

      with open("./groups/" + _CART_entry) as _CART_GFH:
         for _CART_ln_in in _CART_GFH:
            _CART_grp_str += _CART_entry + ':' + _CART_ln_in;

cartlog("groups", _CART_grp_str)

