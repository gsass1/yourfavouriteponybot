from log import log
import tweepy

class Twitter:
    def __init__(self, config, noUpdateStatus):
        self.botConfig = config
        self.auth = tweepy.OAuthHandler(self.botConfig.consumerKey, self.botConfig.consumerSecret)
        self.auth.set_access_token(self.botConfig.accessKey, self.botConfig.accessSecret)
        self.api = tweepy.API(self.auth)
        self.noUpdateStatus = noUpdateStatus

    def UpdateStatus(self, status, id):
        log.info("Mentioned: {0}".format(status))
        if not self.noUpdateStatus:
            self.api.update_status(status, id)

    def GetMentionsTimeline(self):
        return self.api.mentions_timeline(count=200)

    def DownloadAllTweets(self, name):
        tweets = []

        newTweets = self.api.user_timeline(screen_name=name, count=200)

        tweets.extend(newTweets)

        oldest = tweets[-1].id - 1

        while len(newTweets) > 0:
            log.info("Getting tweets before %s" % (oldest))
            newTweets = self.api.user_timeline(screen_name=name, count=200, max_id=oldest)
            tweets.extend(newTweets)
            oldest = tweets[-1].id - 1
            log.info("%s tweets downloaded so far" % (len(tweets)))
        return tweets

    def GetUser(self, name):
        # If the user does not exists, tweepy will throw an exception
        try:
            user = self.api.get_user(screen_name=name)
            return user
        except tweepy.TweepError as e:
            return None
