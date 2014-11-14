import logging, os, tweepy, time, sys, random, json
from ponydb import PonyDB

bot = None

class Bot:
    def Start(self):
        self.logger = self.CreateLogger()

        if len(sys.argv) < 2:
            print("Usage: %s <configfile>" % sys.argv[0])
            return

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

        # Read banned phrases
        with open("bannedphrases.txt", "r") as file:
            self.bannedPhrases = file.read().splitlines()

        self.ponydb = PonyDB("ponies.json", "scorewords.json")

        # Create mentioned.txt if not exists
        if not os.path.exists("mentioned.txt"):
            open("mentioned.txt", "w").close()

        self.auth = tweepy.OAuthHandler(self.botConfig.consumerKey, self.botConfig.consumerSecret)
        self.auth.set_access_token(self.botConfig.accessKey, self.botConfig.accessSecret)
        self.api = tweepy.API(self.auth)

        try:
             self.MainLoop()
        except KeyboardInterrupt as e:
            self.logger.error("Interrupted")
            exit(0)

    def CreateLogger(self):
            logger = logging.getLogger("yourfavponybot")
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

    def ContainsBannedPhrase(self, text):
        for phrase in self.bannedPhrases:
            if phrase.lower() in text.lower():
                return True
        return False

    def GetStrForEval(self, evaluation):
        with open("answers.json", "r") as file:
            jsonData = json.loads(file.read())
            answers = jsonData[str(evaluation)]
            index = random.randrange(0, len(answers))
            return answers[index]

    def GenStatus(self, mention):
        self.logger.info("Now generating status for User: {0}, TweetID: {1}, in response to: '{2}'".format(mention.user.screen_name, mention.id, mention.text))

        tweets = self.api.user_timeline(id=mention.user.id, count=100)

        totalRefs = dict()

        for t in tweets:
            refs = self.ponydb.FindReferences(t.text)
            totalRefs.update(refs)

        # Get refs in user description, value them more
        refs = self.ponydb.FindReferences(mention.user.description)
        refs.update((x, y * 2) for x, y in refs.items())
        totalRefs.update(refs)

        # If nothing found at all
        eval = 1
        if len(totalRefs) == 0:
            eval = 0

        if eval == 1:
            topPony = self.ponydb.GetNameForKey(max(totalRefs, key=totalRefs.get))
        else:
            # Get a random one if we dont have any pony
            topPony = self.ponydb.GetRandomPony()

        answer = self.GetStrForEval(eval) % topPony
        status = "@%s %s" % (mention.user.screen_name, answer)
        return status

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
            mentions = self.api.mentions_timeline()
        except tweepy.TweepError:
            self.logger.info("Rate limit! Waiting a bit...")
            time.sleep(360)
        for mention in mentions:
            if self.AlreadyMentioned(mention.id):
                continue
            else:
                self.WriteMentioned(mention.id)
                if self.ContainsBannedPhrase(mention.text):
                    self.logger.info("Contained banned phrase! " + mention.text)
                    if not self.noUpdateStatus:
                        self.api.update_status("@%s Please don't be rude :c" % mention.user.screen_name, mention.id)
                    continue
                status = self.GenStatus(mention)
                self.logger.info("Mentioned: " + status)
                if not self.noUpdateStatus:
                    self.api.update_status(status, mention.id)
                time.sleep(60)
        time.sleep(120)

if __name__ == "__main__":
    # Set encoding to UTF8
    reload(sys)
    sys.setdefaultencoding("utf8")

    bot = Bot()
    bot.Start()