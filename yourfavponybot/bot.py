#!/usr/bin/env python

import logging, os, tweepy, time, sys, random, json

consumerKey=""
consumerSecret=""
accessKey=""
accessSecret=""

ponyList = []
bannedPhrases = []
answers = []

noUpdateStatus = False 

def createLogger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler("log.txt")
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(message)s");

    handler.setFormatter(formatter)

    con = logging.StreamHandler(sys.stdout)
    con.setLevel(logging.INFO)
    con.setFormatter(formatter)

    logger.addHandler(con)
    logger.addHandler(handler)
    return logger

def containsBannedPhrase(text):
    for phrase in bannedPhrases:
        if phrase.lower() in text.lower():
            return True
    return False

def getRandAnswer():
    index = random.randrange(0, len(answers))
    return answers[index]

def getStrForEval(evaluation):
    with open("answers.json", "r") as file:
        jsonData = json.loads(file.read())
        answers = jsonData[str(evaluation)]
        index = random.randrange(0, len(answers))
        return answers[index]

def genStatus(mention):
    from intel import AI, EvaluationType
    ai = AI(api)
    pony, evaluation = ai.begin_search_process(ponyList, mention)
    answer = getStrForEval(evaluation) % pony
    status = "@%s %s" % (mention.user.screen_name, answer)
    return status 

def wasAlreadyMentioned(tweetID):
    with open("mentioned.txt", "r+") as file:
        for line in file.readlines():
            if str(tweetID) in line:
                return True
    return False

def writeMentioned(tweetID):
    with open("mentioned.txt", "a") as file:
        file.write(str(tweetID) + "\n")

if len(sys.argv) < 2:
    print("Usage: %s <configfile>" % sys.argv[0])
    exit()

if len(sys.argv) > 2:
    if sys.argv[2] == "--noupdate":
        noUpdateStatus = True

# Read in config file
with open(sys.argv[1], "r") as configFile:
    jsonData = json.loads(configFile.read())
    consumerKey = jsonData["consumerKey"]
    consumerSecret = jsonData["consumerSecret"]
    accessKey = jsonData["accessKey"]
    accessSecret = jsonData["accessSecret"]

# Read pony list
with open("ponies.txt", "r") as poniesFile:
    ponyList = poniesFile.read().splitlines()

# Read banned phrases
with open("bannedphrases.txt", "r") as file:
    bannedPhrases = file.read().splitlines()

# Read answers
with open("answers.txt", "r") as file:
    answers = file.read().splitlines()

# Create mentioned.txt if not exists
if not os.path.exists("mentioned.txt"):
    open("mentioned.txt", "w").close()

logger = createLogger()

auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
auth.set_access_token(accessKey, accessSecret)
api = tweepy.API(auth)

while True:
    mentions = []
    try:
        mentions = api.mentions_timeline()
    except tweepy.TweepError:
        logger.info("Rate limit! Waiting a bit...")
        time.sleep(360) 
    for mention in mentions:
        if wasAlreadyMentioned(mention.id):
            continue
        else:
            writeMentioned(mention.id)
            if containsBannedPhrase(mention.text):
                logger.info("Contained banned phrase! " + mention.text)
                if not noUpdateStatus:
                    api.update_status("@%s Please don't be rude :c" % mention.user.screen_name, mention.id)
                continue
            status = genStatus(mention)
            logger.info("Mentioned: " + status)
            if not noUpdateStatus:
                api.update_status(status, mention.id)
            time.sleep(60)
    time.sleep(120)
