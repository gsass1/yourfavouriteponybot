import os, tweepy, time, sys, random, json
from pprint import pprint

consumerKey=""
consumerSecret=""
accessKey=""
accessSecret=""

ponyList = []
bannedPhrases = []

def containsBannedPhrase(text):
    for phrase in bannedPhrases:
        if phrase.lower().rstrip("\n") in text.lower():
            return True
    return False

def genStatus(mention):
    index = random.randrange(0, len(ponyList))
    favouritePony = ponyList[index].rstrip('\n')
    status = "@%s Your favourite pony is %s!" % (mention.user.screen_name, favouritePony)
    return status 

def wasAlreadyMentioned(tweetID):
    with open("mentioned.txt", "r+") as file:
        for line in file.readlines():
            if str(tweetID) in line:
                print(tweetID)
                return True
    return False

def writeMentioned(tweetID):
    with open("mentioned.txt", "a") as file:
        file.write(str(tweetID) + "\n")

if len(sys.argv) != 2:
    print("Usage: %s <configfile>" % sys.argv[0])
    exit()

# Read in config file
with open(sys.argv[1], "r") as configFile:
    jsonData = json.loads(configFile.read())
    consumerKey = jsonData["consumerKey"]
    consumerSecret = jsonData["consumerSecret"]
    accessKey = jsonData["accessKey"]
    accessSecret = jsonData["accessSecret"]

# Read pony list
with open("ponies.txt", "r") as poniesFile:
    ponyList = poniesFile.readlines()

# Read banned phrases
with open("bannedphrases.txt", "r") as file:
    bannedPhrases = file.readlines()

# Create mentioned.txt if not exists
if not os.path.exists("mentioned.txt"):
    open("mentioned.txt", "w").close()

auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
auth.set_access_token(accessKey, accessSecret)
api = tweepy.API(auth)

while True:
    mentions = []
    try:
        mentions = api.mentions_timeline()
    except tweepy.TweepError:
        print("Rate limit! Waiting a bit...")
        time.sleep(360) 
    for mention in mentions:
        if wasAlreadyMentioned(mention.id):
            print("Already mentioned!")
        else:
            writeMentioned(mention.id)
            if containsBannedPhrase(mention.text):
                print("Contained banned phrase! " + mention.text)
                continue
            status = genStatus(mention)
            print("Mentioned: " + status)
            api.update_status(status)
            continue
        time.sleep(120)
