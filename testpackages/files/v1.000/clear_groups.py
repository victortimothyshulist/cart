if os.path.isdir("./groups"):      
   for _CART_entry in os.listdir("./groups"):
      os.remove("./groups/" + _CART_entry)
   os.rmdir("./groups")
