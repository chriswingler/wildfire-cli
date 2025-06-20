# tests/analysis/test_insights_engine.py
import unittest
from src.analysis.insights_engine import InsightsEngine
from src.analysis.sentiment_analyzer import SentimentAnalyzer # Real one for better testing
from src.analysis.topic_modeler import TopicModeler # Real one

class TestInsightsEngine(unittest.TestCase):
    def setUp(self):
        # Using real (placeholder) analyzers for more integrated testing
        self.sentiment_analyzer = SentimentAnalyzer()
        self.topic_modeler = TopicModeler()
        self.engine = InsightsEngine(
            sentiment_analyzer=self.sentiment_analyzer,
            topic_modeler=self.topic_modeler
        )

    def test_identify_key_participants(self):
        conversation = [
            ("userA", "Hello!"), ("userB", "Hi!"), ("userA", "How are you?"),
            ("userC", "I'm good."), ("userA", "Great!")
        ]
        participants = self.engine.identify_key_participants(conversation, top_n=1)
        self.assertEqual(len(participants), 1)
        if participants:
            self.assertEqual(participants[0][0], "userA")
            self.assertEqual(participants[0][1], 3) # userA sent 3 messages

    def test_score_conversation_quality(self):
        messages = ["This is a great discussion!", "Very informative.", "I learned a lot."]
        # Pass actual participant count
        quality = self.engine.score_conversation_quality(messages, participants=3)
        self.assertIn("overall_quality", quality)
        self.assertGreater(quality["overall_quality_numeric"], 0.5) # Expecting positive/high for this

    def test_detect_knowledge_gaps(self):
        messages = ["How do I deploy troops?", "What is the best strategy?"]
        gaps = self.engine.detect_knowledge_gaps(messages)
        self.assertEqual(len(gaps), 2)
        if gaps:
            self.assertTrue("How do I deploy troops?" in gaps[0])

    def test_map_community_expertise(self):
        user_conversations = {
            "userX": [["Let's talk about fire containment.", "Fire is spreading."]],
            "userY": [["I have a question about the game rules."]]
        }
        expertise = self.engine.map_community_expertise(user_conversations)
        self.assertIn("userX", expertise)
        if "userX" in expertise:
            self.assertIn("firefighting_tactics", expertise["userX"])
        self.assertIn("userY", expertise)
        if "userY" in expertise:
            self.assertIn("user_questions", expertise["userY"])

if __name__ == '__main__':
    unittest.main()
