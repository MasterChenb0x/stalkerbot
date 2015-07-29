#!/bin/bash
search=$1
filename='TARGETTWEETS.txt'
filelines=`cat $filename`
for line in $filelines ; 
do
	links -dump "https://twitter.com/TARGET/status/$line" | grep --after-context=1 --before-context=3 "$1"
done
