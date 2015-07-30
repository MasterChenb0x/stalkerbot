#!/bin/bash

#This script simply resolves the twitter IDs gathered from previous scripts and turns them into actual Twitter usernames.
#Making data collection slightly more human readable.
for a in $( ls /home/chen/target_friends/ );
do
	links -dump "https://twitter.com/intent/user?user_id=$a" | grep "@"
done
