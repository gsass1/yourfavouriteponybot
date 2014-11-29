import unittest
import ponydb
from ai import AI
from main import Bot
import sys

class Mention:
    pass

class Tweet:
    def __init__(self, text):
        self.text = text

class User:
    pass

class AITest(unittest.TestCase):
    def test_ref_query(self):
        db = ponydb.PonyDB("ponies.json", "scorewords.json")
        refs = db.FindReferences("Twilight Sparkle, Rainbow Dash")
        self.assertEqual(len(refs), 2, "Must had found Twilight Sparkle and Rainbow Dash in the string.")

    def test_ref_query_with_scorewords(self):
        db = ponydb.PonyDB("ponies.json", "scorewords.json")
        refs = db.FindReferences("Derpy Cute")
        self.assertGreater(len(refs), 0)
        self.assertGreater(refs["derpy_hooves"], 0)
        self.assertEqual(refs["derpy_hooves"], 3, "Score was evaluated wrongly (1 + 2)")

    def test_response_ai(self):
        ai = AI("responses.json", "statement_indicators.json")
        self.assertEqual(ai.GetStringStatementType("Yes :D"), "positive")
        self.assertEqual(ai.GetStringStatementType("No :("), "negative")
        self.assertEqual(ai.GetStringStatementType("Why you think so dude?"), "question")
        self.assertEqual(ai.GetStringStatementType("Okay"), None)

    def test_User_Donald(self):
        bot = Bot(testMode=True)

        mention = Mention()
        mention.user = User()
        mention.user.screen_name = "Donald"
        mention.user.description = "I live in Alaska"

        tweets = []
        tweets.append(Tweet("Hello"))
        tweets.append(Tweet("Yolo"))
        tweets.append(Tweet("Twilight Sparkle is gud"))

        status, evalType, refs = bot.GenStatusForEvidence(mention, tweets)
        self.assertEqual(evalType, "sure", "Should have found that he likes some pony")
        self.assertEqual(len(refs), 1, "Could have only found Twilight Sparkle!")

    def test_User_Thomas(self):
        bot = Bot(testMode=True)

        mention = Mention()
        mention.user = User()
        mention.user.screen_name = "Thomas"
        mention.user.description = "I live in Germany. Twilight Sparkle is best pony!"

        tweets = []
        tweets.append(Tweet("BlahBlahBlah"))
        tweets.append(Tweet(":D:D:DD"))
        tweets.append(Tweet("This picture of Fluttershy is super cute! https://derpibooru.org/774059"))

        status, evalType, refs = bot.GenStatusForEvidence(mention, tweets)
        self.assertEqual(evalType, "sure", "Should have found that he likes some pony")
        self.assertEqual(len(refs), 2, "Should find Fluttershy and Twilight!")
        self.assert_(refs["twilight_sparkle"] > refs["fluttershy"], "Twilight should have been evaluated higher then Fluttershy!")

    def test_User_Bernd(self):
        bot = Bot(testMode=True)

        mention = Mention()
        mention.user = User()
        mention.user.screen_name = "Bernd"
        mention.user.description = "Bernd? Bernd!"

        tweets = []
        tweets.append(Tweet("Install Gentoo"))
        tweets.append(Tweet("Seems like I did find destiny!"))
        tweets.append(Tweet("I voted for Obama!"))

        status, evalType, refs = bot.GenStatusForEvidence(mention, tweets)
        self.assertEqual(evalType, "guess", "Can only be guess, since no pony data at all")

    def test_User_Harry(self):
        bot = Bot(testMode=True)

        mention = Mention()
        mention.user = User()
        mention.user.screen_name = "Harry"
        mention.user.description = "Rainbow Dash is best pony!"

        tweets = []
        tweets.append(Tweet("Rarity is best pony!"))

        status, evalType, refs = bot.GenStatusForEvidence(mention, tweets)
        self.assertEqual(evalType, "sure", "Should have found that he likes some pony")
        self.assertEqual(len(refs), 2, "Should find Rainbow Dash and Rarity!")
        self.assert_(refs["rainbow_dash"] > refs["rarity"], "RB's score is higher, since she is in the user description!")

    def test_SingleAnswer(self):
        bot = Bot(testMode=True)

        mention = Mention()
        mention.user = User()
        mention.user.screen_name = "Jessica"
        mention.user.description = "Dunno"

        tweets = []
        tweets.append(Tweet("Applejack is nice. She is the best background pony!"))

        status, evalType, refs = bot.GenStatusForEvidence(mention, tweets)
        self.assertEqual(evalType, "sure", "Should have found that she likes some pony")
        self.assertEqual(len(refs), 1, "Should find only find Applejack!")

    def test_Nicknames(self):
        bot = Bot(testMode=True)

        mention = Mention()
        mention.user = User()
        mention.user.screen_name = "Anonymous"
        mention.user.description = "is legion"

        tweets = []
        tweets.append(Tweet("RD TS AJ FS PP. Bet you can't encrypt this!"))

        status, evalType, refs = bot.GenStatusForEvidence(mention, tweets)
        self.assertEqual(evalType, "sure", "Should have found that he likes some pony")
        self.assertEqual(len(refs), 5, "Should have found 5 ponies")

    def test_IsPing(self):
        bot = Bot(testMode=True)

        mention = Mention()
        mention.text = "@YourFavouritePonyBot Ping @Nuke928"

        isPing, user = bot.IsMentionPingRequest(mention)
        self.assert_(isPing, "Should have been evaluated as Ping")
        self.assertEqual(user, "Nuke928", "Should have evaluated Nuke928 as the ping target")

    def test_IsNotPing(self):
        bot = Bot(testMode=True)

        mention = Mention()
        mention.text = "@YourFavouritePonyBot Ding @Nuke928"

        isPing, user = bot.IsMentionPingRequest(mention)
        self.assertEqual(isPing, False, "Should have not been evaluated as Ping")
        self.assertEqual(user, None, "Should have not returned any user")

if __name__ == '__main__':
    unittest.main()
