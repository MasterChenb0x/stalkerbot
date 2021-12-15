#!/usr/bin/env python3
import sys
import os
import re
import random
import time
import getopt
import tweepy

#-- Twitter Instance setup
TWITTER = open("/home/chen/Documents/TwiTokens.txt", "r").read().splitlines()
auth = tweepy.OAuthHandler(TWITTER[0], TWITTER[1])
auth.set_access_token(TWITTER[2], TWITTER[3])

api = tweepy.API(auth, wait_on_rate_limit=True)
#--

'''
This small script just does what the "grabber.rb" script did before. Slightly cleaner? My code I mean; not necessarily the language :-P
'''

myFriends = []
targetFollowers = []
targetFriends = []

# Get baseline friendlist
myFriends = api.friends_ids(screen_name='<YOUR HANDLE')
print("---My Friends---")
print(myFriends)

# Get list of followers of target
targetFollowers = api.followers_ids(screen_name='<YOUR TARGET')
print("---Target Followers---")
print(targetFollowers)

# Get list of friends of target
targetFriends = api.friends_ids(screen_name='<YOUR HANDLE>')
print("---Target Friends---")
print(targetFriends)

print(len(myFriends))
print(len(targetFollowers))
print(len(targetFriends))
target_scope = targetFollowers + targetFriends
print(len(target_scope))


to_follow = list(set(targetFollowers) - set(myFriends)) + list(set(myFriends) - set(targetFollowers))
print(len(to_follow))

for i in targetFollowers:
    try:
        api.create_friendship(user_id=i)
        time.sleep(10) # avoid rate limit
        print(f"Following: {i}")
    except:
        pass

# This is just a quick addition
