# Your Favourite Pony Bot

[![Build Status](https://travis-ci.org/Nuke928/yourfavouriteponybot.svg?branch=master)](https://travis-ci.org/Nuke928/yourfavouriteponybot)

"Your Favourite Pony Bot" is a Twitterbot that will try to find a Twitter users favourite pony by looking at his/her posted Tweets.
  
  [See the bot in action!](https://twitter.com/YourFavPonyBot)

## Requirements
* Python 2.7
* Tweepy
* requests
* DerPyBooru
* sqlite3

## Usage

> python main.py -cf CONFIGFILE [options]


Options are:


* --nu/--noupdate - Do not update Twitter status
  

Look in config.json.example for an example

## Interaction

You can mention the bot in a tweet like this: "@YourFavPonyBot Sup?"


The bot will then respond ASAP with a list of ponies he evaluated as possible candidates for your favorite pony.


Example response: "@Guy Your favourite ponies are Fluttershy, Rainbow Dash or Rarity!"


### Pinging

You can ping another user so the bot will try its Algorithm on that user instead.


Example: "@YourFavPonyBot Ping @Nuke928"


Example response: "@Nuke928 @Guy Your favourite ponies are Fluttershy, Rainbow Dash or Rarity :D"

### Chit-chat

Upon replying on a reply of the bot, he will try to understand the message you are trying to tell him.


Example: "@YourFavPonyBot But thats not my pony :(" - will be evaluated as negative.


The bot will then try to reply in a context appropriate matter.


Example: "@Guy Wasn't me who programmed this!"

## Remarks

Mentioned Tweet-IDs will be written to mentioned.db and the log file is log.txt

## mentioned.txt migration of 19th Dec., 2014

We moved saving data in mentioned.txt to a SQL database. Please use migrate_mentioned.py to migrate your .txt file.

## Help wanted with

We need a bigger list of ponies and more intelligent answers. Take a look at ponies.json, answers.json, responses.json, statement_indicators.json and scorewords.json!
If any confusion just ask.