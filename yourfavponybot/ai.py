import json, random
from log import log

class AI:
    def __init__(self, responsesFile, statIndicatorsFile):
        with open(responsesFile, "r") as file:
            self.responses = json.loads(file.read())

        with open(statIndicatorsFile, "r") as file:
            self.statIndicators = json.loads(file.read())

    def IsStringQuestion(self, string):
        return string.endswith("?")

    def GetStringStatementType(self, string):
        if self.IsStringQuestion(string):
            return "question"

        stats = dict()

        stats["positive"] = 0
        stats["negative"] = 0
        stats["question"] = 0

        anyStat = 0

        if any(word in string for word in self.statIndicators["positive"]):
            anyStat += 1
            stats["positive"] += 1

        if any(word in string for word in self.statIndicators["negative"]):
            anyStat += 1
            stats["negative"] += 1

        if any(word in string for word in self.statIndicators["question"]):
            anyStat += 1
            stats["question"] += 1

        if anyStat == 0:
            return None
        else:
            return max(stats, key=stats.get)

    def GetRandResponseToStatement(self, stat):
            return random.choice(self.responses[stat])

    def GetReplyToStatus(self, mention):
        howHeFeels = self.GetStringStatementType(mention.text.lower())
        log.info("Statement Type: {0}".format(howHeFeels))
        if howHeFeels is None:  # he does not feel
            return None         # dont reply at all
        else:
            return self.GetRandResponseToStatement(howHeFeels)