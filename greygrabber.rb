#!/usr/local/rvm/rubies/ruby-2.1.2/bin/ruby
require 'twitter'

   rClient = Twitter::REST::Client.new do |config|
   config.consumer_key = "CONSUMER_KEY"
   config.consumer_secret = "CONSUMER_SECRET"
   config.access_token = "ACCESS_TOKEN"
   config.access_token_secret = "ACCESS_TOKEN_SECRET"
   end

#Get a list of your TARGET's followers
follower_ids = []
rClient.follower_ids("TARGET").each do |id|
	folllower_ids.push(id)
end

#Get a list of YOUR followers
friend_ids = []
rClient.friend_ids("YOUR_HANDLE").each do |id|
	friend_ids.push(id)
end

#Follow the followers of your TARGET who are not yet being followed
rClient.follow(follower_ids - friend_ids)

#Get a list of the Tweeters your TARGET is FOLLOWING
friend_idz = []
rClient.friend_ids("TARGET").each do |id|
	friend_idz.push(id)
end

puts friend_idz

#Follow the Tweeters your TARGET is following who you have not yeet followed
rClient.follow(friend_idz - friend_ids)

=begin
At this point in the code, there are two things that have happened. You are following all of the people who follow your TARGET, AND you should now be following everyone whho your TARGET follows; both sides of the follow coin
=end
