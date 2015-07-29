#!/bin/bash

#Strip ".txt" from the filenames for better data mining later
for x in $( ls ); do
	FRIEND=`basename $x .txt`
	cp $x $FRIEND
done

#For every file, strip any part of the string that is NOT a Tweet ID
for a in $( ls ); do
	cat $a | tr -c [0-9] ' ' | tr -s ' ' | tr ' ' '\n' > $a"_new"
done
