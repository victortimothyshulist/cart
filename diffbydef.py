#!/usr/bin/perl
#

if(!(-d "diff"))
{
	`mkdir diff`;
}

$cmd = 'ls -la diff/ | grep -v ^total |grep -v "\.$" | wc -l';
$cnt = `$cmd`;

if($cnt > 0)
{
	`rm diff/*`;
}

my $f1n = $ARGV[0];
my $f2n = $ARGV[1];

%f1 = ();
%f2 = ();

$any = 0;

func($f1n, \%f1);
func($f2n, \%f2);

my @files_only_in_1 = ();
my @files_only_in_2 = ();

my @common = ();

for my $F1 (keys %f1)
{
	if(!exists $f2{$F1})
	{
		push @files_only_in_1, $F1;
	}
	else
	{
		push @common, $F1;
	}
}

for my $F2 (keys %f2)
{
	if(!exists $f1{$F2})
	{
		push @files_only_in_2, $F2;
	}
}

open(Z, ">result.html");
print Z "<html><body>";

if(@files_only_in_1 > 0)
{
	$any = 1;
	print("\n\n*Functions in '$f1n' that are not in '$f2n'....\n\n");
	print Z "<h1>Functions in '$f1n' that are not in '$f2n':</h1>";
	foreach my $f (@files_only_in_1)
	{
		print $f."\n";
		print Z $f."<br>";
	}
	print "\n";
}

if(@files_only_in_2 > 0)
{
	$any = 1;
	print("\n\n*Functions in '$f2n' that are not in '$f1n'....\n\n");
	print Z "<h1>Functions in '$f2n' that are not in '$f1n':</h1>";
	foreach my $f (@files_only_in_2)
	{
		print $f."\n";
		print Z $f."<br>";
	}
	print "\n";
}

foreach my $cf (@common)
{
	$s1 = "___temp_1.py";
	$s2 = "___temp_2.py";

	writefile($s1, $f1{$cf});
	writefile($s2, $f2{$cf});

	$diffstrcmd = "diff $s1 $s2 > diff.txt";
	`$diffstrcmd`;

	$diffstr = "";
	$hdiffstr = "";

	if(!open(R, "<diff.txt"))
	{
		print("*ERR: cannot read file 'diff.txt'\n");
		exit;
	}
	foreach my $ln (<R>)
	{
		$diffstr .= $ln;

		if($ln =~ m/^\d/)
		{
			$hdiffstr .= '<BR>'; 
		}

		$hdiffstr .= $ln;
		$hdiffstr .= '<BR>';
	}
	close(R);

	if($diffstr ne '')
	{
		$any = 1;
		$ofile = "./diff/".$cf;

		print Z "<h1>Changes in function '".$cf."'</h1><BR>";

		if(!open(O, ">$ofile"))
		{
			print("*ERR: can't open '$ofile'\n");
			exit;
		}
		print O $diffstr;
		print Z $hdiffstr;
		close(O);
	}

	unlink($s1);
	unlink($s2);
}

if($any == 0)
{
	print("\n* Files are identical.\n");
	print Z "<h1>Files are identical.</h1>";

}

print Z "</body></html>";
close(Z);

sub writefile()
{
	my ($file, $ref) = @_;

	if(!open(H, ">$file"))
	{
		print("*ERR: can't open file '$file'.\n");
		exit;
	}
	
	foreach my $ln (@{$ref})
	{
		print H $ln."\n";
	}
	close(H);
}


sub func()
{
	my $main = '____main____';
	my $current_func = $main;

	my ($f, $r) = @_;

	if(!open(F, "<$f"))
	{
		print "*ERR: can't open '$f'\n";
		exit;
	}

	for my $ln (<F>)
	{
		chomp($ln);
		if($ln =~ m/^\s*$/) { next; }

		if($ln =~ m/^def\s+(.+?)\((.*)\):\s*$/)
		{
			$current_func = $1;
			$sig = $2;
		        push @{$r->{$current_func}}, "<b><i><font color='red'>PARAMETERS</font></i></b>: ".$sig.'<hr>';	
			next;
		}
		elsif($ln =~ m/^\S/)
		{
			$current_func = $main;
			$ln =~ s/^\s*(.+?)\s*$/$1/;
	        	push @{$r->{$current_func}}, $ln;
		}
		else
		{
			$ln =~ s/^\s*(.+?)\s*$/$1/;
	        	push @{$r->{$current_func}}, $ln;
		}
	}

	close(F);
}

