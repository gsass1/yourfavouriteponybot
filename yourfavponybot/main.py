import logging, os, tweepy, time, sys, random, json
from ponydb import PonyDB
from ai import AI
from collections import Counter
import heapq
from operator import itemgetter
from twitter import Twitter

bot = None

class Bot:
    def __init__(self, testMode=False):
        self.testMode = testMode
        self.logger = self.CreateLogger()

        if not self.testMode:
            if len(sys.argv) < 2:
                print("Usage: %s <configfile>" % sys.argv[0])
                exit(0)

            self.noUpdateStatus = False

            if len(sys.argv) > 2:
                if sys.argv[2] == "--noupdate":
                    self.noUpdateStatus = True


            # Read in config file
            try:
                import config
                self.botConfig = config.Config("config.json");
            except Exception as e:
                print("Error while parsing config file! %s" % e.message)
                raise

            self.twitter = Twitter(self.botConfig, self.noUpdateStatus)

        self.ai = AI("responses.json", "statement_indicators.json")

        # Read banned phrases
        with open("bannedphrases.txt", "r") as file:
            self.bannedPhrases = file.read().splitlines()

        self.ponydb = PonyDB("ponies.json", "scorewords.json")

        # Create mentioned.txt if not exists
        if not os.path.exists("mentioned.txt"):
            open("mentioned.txt", "w").close()

    def Start(self):
        while True:
            try:
                 self.MainLoop()
            except KeyboardInterrupt as e:
                self.logger.error("Interrupted")
                exit(0)

    def CreateLogger(self):
            logger = logging.getLogger("yourfavponybot")
            logger.setLevel(logging.INFO)

            if self.testMode:
                logFilename = "log_test.txt"
            else:
                logFilename = "log.txt"

            handler = logging.FileHandler(logFilename)
            handler.setLevel(logging.INFO)

            formatter = logging.Formatter("%(asctime)s - %(message)s");

            handler.setFormatter(formatter)

            con = logging.StreamHandler(sys.stdout)
            con.setLevel(logging.INFO)
            con.setFormatter(formatter)

            logger.addHandler(con)
            logger.addHandler(handler)
            return logger

    def ContainsBannedPhrase(self, text):
        for phrase in self.bannedPhrases:
            if phrase.lower() in text.lower():
                return True
        return False

    def GetStrForEval(self, type, evaluation):
        with open("answers.json", "r") as file:
            jsonData = json.loads(file.read())
            if evaluation == "guess":
                answers = jsonData[evaluation]
            else:
                answers = jsonData[evaluation][type]
            index = random.randrange(0, len(answers))
            return answers[index]

    def GenStatusForEvidence(self, mention, tweets):
        totalRefs = dict()

        for t in tweets:
            refs = self.ponydb.FindReferences(t.text)
            if len(refs) > 0:
                totalRefs = dict(Counter(totalRefs)+Counter(refs))

        # Get refs in user description, value them more
        refs = self.ponydb.FindReferences(mention.user.description)
        refs.update((x, y * 2) for x, y in refs.items())
        totalRefs = dict(Counter(totalRefs)+Counter(refs))

        self.logger.info("Refs:")
        self.logger.info(str(totalRefs))

        answerStr = ""

        if len(totalRefs) is not 0:
            # Build a string that goes like this: "A, B or C"
            if len(totalRefs) > 1:
                highest = heapq.nlargest(max(0, min(3, len(totalRefs))), totalRefs, key=totalRefs.get)
                for i in range(0, len(highest)):
                    answerStr += self.ponydb.GetNameForKey(highest[i])
                    if i == len(highest) - 2:
                        answerStr += " or "
                    elif i != len(highest) - 1:
                        answerStr += ", "
            else:
                # Just one pony to process
                answerStr = self.ponydb.GetNameForKey(max(totalRefs, key=totalRefs.get))
        else:
            # Get a random one if we dont have any pony
            answerStr = self.ponydb.GetRandomPony()

        if(len(totalRefs) != 0):
            evalType = "sure"
        else:
            evalType = "guess"

        if(len(totalRefs) == 1):
            type = "single"
        else:
            type = "multi"

        answer = self.GetStrForEval(type, evalType) % answerStr
        status = "@%s %s" % (mention.user.screen_name, answer)
        return status, evalType, totalRefs

    def GenStatusForMention(self, mention):
        self.logger.info("Status is mention")
        tweets = self.twitter.DownloadAllTweets(mention.user.screen_name)
        status, evalType, refs = self.GenStatusForEvidence(mention, tweets)
        return status

    def GenStatusForReply(self, mention):
        self.logger.info("Status is reply")
        reply = self.ai.GetReplyToStatus(mention)
        if reply is not None:
            return "@{0} {1}".format(mention.user.screen_name, reply)
        else:
            return None

    def GenStatus(self, mention):
        self.logger.info("Now generating status for User: {0}, TweetID: {1}, in response to: '{2}'".format(mention.user.screen_name, mention.id, mention.text))
        if mention.in_reply_to_status_id_str is None:
            return self.GenStatusForMention(mention)
        else:
            return self.GenStatusForReply(mention)


    def AlreadyMentioned(self, tweetID):
        with open("mentioned.txt", "r+") as file:
            for line in file.readlines():
                if str(tweetID) in line:
                    return True
        return False

    def WriteMentioned(self, tweetID):
        with open("mentioned.txt", "a") as file:
            file.write(str(tweetID) + "\n")

    def MainLoop(self):
        mentions = []
        try:
            mentions = self.twitter.GetMentionsTimeline()
        except tweepy.TweepError:
            self.logger.info("Rate limit! Waiting a bit...")
            time.sleep(self.botConfig.rateLimitWaitInterval)
        for mention in mentions:
            if self.AlreadyMentioned(mention.id):
                continue
            else:
                if self.ContainsBannedPhrase(mention.text):
                    self.logger.info("Contained banned phrase! " + mention.text)
                    self.twitter.UpdateStatus("@%s Please don't be rude :c" % mention.user.screen_name, mention.id)
                status = self.GenStatus(mention)
                if status is not None:
                    self.twitter.UpdateStatus(status, mention.id)
                else:
                    self.logger.info("No mention")
                self.WriteMentioned(mention.id)
                time.sleep(self.botConfig.tweetInterval)
        time.sleep(self.botConfig.tweetGrabInterval)

if __name__ == "__main__":
    # Set encoding to UTF8
    reload(sys)
    sys.setdefaultencoding("utf8")

    bot = Bot()
    bot.Start()