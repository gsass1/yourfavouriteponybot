import unittest
import ponydb
from ai import AI

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

if __name__ == '__main__':
    unittest.main()
