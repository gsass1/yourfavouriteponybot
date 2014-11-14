import json, re, random

from collections import defaultdict
from log import log

class PonyDB:
    def __init__(self, file, scorewordFile):
        with open(file, "r") as file:
            jsonData = json.loads(file.read())
            self.ponies = jsonData["ponies"]

        with open(scorewordFile, "r") as file:
            jsonData = json.loads(file.read())
            self.scorewords = jsonData

    def GetRandomPony(self):
        return self.ponies[random.choice(self.ponies.keys())]["name"]

    def GetNameForKey(self, key):
        return self.ponies[key]["name"]

    def GenInitialsForName(self, name):
        part = name.partition(' ')
        return part[0][0] + part[2][0]

    def GetAllPonyNameRefsForKey(self, key):
        list = []
        list.append(self.ponies[key]["name"])
        # No "initials" field means that we should just
        # generate the initials here or else we would
        # waste space
        if not self.ponies[key].has_key("initials"):
            # Has whitespace in name
            if (' ' in self.ponies[key]["name"]) == True:
                list.append(self.GenInitialsForName(self.ponies[key]["name"]))
        else:
                list.append(self.ponies[key]["initials"])

        # Add the short name if exists
        # Fluttershy FALSE FALSE
        if ((' ' in self.ponies[key]["name"]) == True) and not self.ponies[key].has_key("shortname"):
            list.append(self.ponies[key]["name"].partition(' ')[0])
        else:
            if self.ponies[key].has_key("shortname"):
                list.append(self.ponies[key]["shortname"])

        # Append nicknames
        if self.ponies[key].has_key("nicknames"):
            list.extend(self.ponies[key]["nicknames"])
        return list

    def FindWholeWord(self, w):
        return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

    def FindReferences(self, string):
        refs = dict()
        for key in self.ponies:
            names = self.GetAllPonyNameRefsForKey(key)
            for ref in names:
                if self.FindWholeWord(ref.lower())(string.lower()):
                    log.info("Key '{0}' with ref '{1}' found in string '{2}'".format(key, ref, string))
                    if refs.has_key(key):
                        refs[key] += 1
                    else:
                        refs[key] = 1

                    # Find scorewords
                    for sw in self.scorewords:
                        if sw.lower() in string.lower():
                            log.info("Found scoreword '{0}'".format(sw))
                            refs[key] += self.scorewords[sw]
        return refs