# tests/analysis/test_sentiment_analyzer.py
import unittest
from src.analysis.sentiment_analyzer import SentimentAnalyzer

class TestSentimentAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = SentimentAnalyzer()

    def test_real_time_sentiment_scoring_positive(self):
        result = self.analyzer.real_time_sentiment_scoring("I am so happy and great!")
        self.assertEqual(result["emotion"], "joy")
        self.assertGreater(result["score"], 0)

    def test_real_time_sentiment_scoring_negative(self):
        result = self.analyzer.real_time_sentiment_scoring("This is really bad and sad.")
        self.assertEqual(result["emotion"], "sadness") # Current placeholder logic
        self.assertLess(result["score"], 0)

    def test_real_time_sentiment_scoring_neutral(self):
        result = self.analyzer.real_time_sentiment_scoring("This is a neutral statement.")
        self.assertEqual(result["emotion"], "neutral")
        self.assertEqual(result["score"], 0)

    def test_track_conversation_mood_positive(self):
        messages = ["It's a beautiful day!", "I love this game.", "Everything is great."]
        mood = self.analyzer.track_conversation_mood(messages)
        self.assertEqual(mood, "positive")

    def test_track_conversation_mood_negative(self):
        messages = ["I'm so frustrated.", "This is not working.", "I give up."]
        mood = self.analyzer.track_conversation_mood(messages)
        self.assertEqual(mood, "negative")

    def test_detect_emotional_escalation_true(self):
        messages = ["This is okay.", "Actually, I'm a bit annoyed.", "Now I'm really angry!", "I hate this!"]
        self.assertTrue(self.analyzer.detect_emotional_escalation(messages))

    def test_detect_emotional_escalation_false(self):
        messages = ["I'm happy.", "Still happy.", "Joyful!"]
        self.assertFalse(self.analyzer.detect_emotional_escalation(messages))

    def test_monitor_community_sentiment_health(self):
        convos = [["happy message"], ["sad message", "angry message"]]
        health = self.analyzer.monitor_community_sentiment_health(convos)
        self.assertIn("overall_mood", health)
        self.assertEqual(health["total_conversations"], 2)
        self.assertEqual(health["negative_conversations"], 1) # based on track_conversation_mood logic

if __name__ == '__main__':
    unittest.main()
