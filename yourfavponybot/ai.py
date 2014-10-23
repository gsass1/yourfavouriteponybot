import bot, tweepy

class AI:
    api = None
    ponyLiked = []

    def __init__(self, api):
        self.api = api 
 
    def begin_search_process(self, ponyList, mention):
        self.ponyLiked = dict() 
        tweets = self.api.user_timeline(id=mention.user.id, count=30)
        logger.info(tweets)
        for t in tweets:
            for p in ponyList:
                if p in t.text:
                    logger.info(p)
                    if ponyLiked.has_key(p):
                        self.ponyLiked[p] += 1 
                    else:
                        # Key has to be initialized first
                        self.ponyLiked[p] = 1
        return "None?"
