# remove terms. why? so we can detect when a term 'x' is not used, to remove it from the database table 'global_term_catalogue'
# but do NOT remove it if it exists in at least one of these 3 places:
# (1) as part of 'constant in any previously processed ICO file.
# (2) in any group file
# (3) in a synonym set

if _CART_INPUT_LINE_NUMBER == 1 and _CART_FILEDB == 'no_delete_term_if_used':
   # Test 1 - keep 'abc', it's removed from two places, but still exists in ICO (constant)
   #
   os.remove("alt_text/aa/test1.txt")
   os.remove("groups/aa.txt")

   # Test 2 - keep 'def', it's removed from two places, but still exists in group 'bb'
   #
   os.remove("alt_text/aa/test2.txt")
   os.system("grep -v def constant_strings.dat > constant_strings.dat2")
   os.remove("constant_strings.dat")
   os.rename("constant_strings.dat2", "constant_strings.dat")

   print("HERE WE ARE_CART_FILEDB = " + _CART_FILEDB)

   # Test 3 - keep 'ghi', it's removed from two places, but still exists in syn-set 'aa/test3'
   #
   os.system("grep -v ghi constant_strings.dat > constant_strings.dat2")
   os.remove("constant_strings.dat")
   os.rename("constant_strings.dat2", "constant_strings.dat")
   os.remove("groups/cc.txt")

   # Test 4 - we can for sure remove 'z' - because we're deleting it in all three places:
   os.remove("alt_text/aa/test4.txt")
   os.remove("groups/dd.txt")
   os.system("grep -v z constant_strings.dat > constant_strings.dat2")
   os.remove("constant_strings.dat")
   os.rename("constant_strings.dat2", "constant_strings.dat")
   
