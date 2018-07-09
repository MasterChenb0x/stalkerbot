#!/usr/bin/env python
import sys
import os
import re
import random
import time
import getopt
from twython import Twython

#-- Twitter Instance setup
apiKey = 'YOUR_TWITTER_API_KEY'
apiSecret = 'YOUR_API_SECRET'
accessToken = 'YOUR_ACCESS_TOKEN'
accessTokenSecret = 'YOUR_ACCESS_TOKEN_SECRET'

api = Twython(apiKey,apiSecret,accessToken,accessTokenSecret)
#--

'''
This small script just does what the "grabber.rb" script did before. Slightly cleaner? My code I mean; not necessarily the language :-P
'''

myFriends = []
targetFollowers = []
targetFriends = []

# Get baseline friendlist
Friends = api.get_friends_ids(screen_name='ShaolinChenple')
myFriends = Friends['ids']
print(myFriends)

# Get list of followers of target
Followers = api.get_followers_ids(screen_name='chenb0x')
targetFollowers = Followers['ids']
for i in targetFollowers:
	print(str(i))
	try:
		api.create_friendship(user_id=i)
		time.sleep(20)
	except:
		pass

