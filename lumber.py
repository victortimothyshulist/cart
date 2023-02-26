if(!open(F, "<term_manager.py"))
{
  print("sucks");
  exit(1);
}

$c = 1;

foreach my $ln (<F>)
{
   chomp($ln);
   $cf = sprintf("%6d", $c);
   print $cf.':'.$ln."\n";
   $c++;
}
close(F);
