echo "------- constant?"
grep $1 constant_strings.dat
echo "------ group?"
grep $1 groups/*
echo "------ synsets?"
grep -r $1 alt_text/*

