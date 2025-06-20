# tests/analysis/test_topic_modeler.py
import unittest
from src.analysis.topic_modeler import TopicModeler

class TestTopicModeler(unittest.TestCase):
    def setUp(self):
        self.modeler = TopicModeler()

    def test_extract_topics_firefighting(self):
        conversation = ["The fire is spreading fast!", "We need more units for containment."]
        topics = self.modeler.extract_topics(conversation)
        self.assertIn("firefighting_tactics", topics)

    def test_extract_topics_bug_report(self):
        conversation = ["I found a bug when using the helicopter.", "Can someone fix this issue?"]
        topics = self.modeler.extract_topics(conversation)
        self.assertIn("bug_reports", topics)

    def test_identify_trending_discussions(self):
        conversations = [
            ["Fire is spreading!"],
            ["Fire tactics are important."],
            ["I found a bug."]
        ]
        trending = self.modeler.identify_trending_discussions(conversations, top_n=1)
        self.assertEqual(len(trending), 1)
        if trending: # Check if list is not empty
            self.assertEqual(trending[0][0], "firefighting_tactics")

    def test_track_topic_evolution(self):
        conversations_over_time = [
            ("Day1", ["Fire is the main topic today."]),
            ("Day2", ["Bugs are being reported now."])
        ]
        evolution = self.modeler.track_topic_evolution(conversations_over_time)
        self.assertIn("Day1", evolution)
        self.assertIn("firefighting_tactics", evolution["Day1"])
        self.assertIn("Day2", evolution)
        self.assertIn("bug_reports", evolution["Day2"])

    def test_analyze_cross_channel_topics(self):
        channel_data = {
            "general": [["Fire everywhere!"]],
            "feedback": [["New bug found in fire engine."]]
        }
        analysis = self.modeler.analyze_cross_channel_topics(channel_data)
        self.assertIn("general", analysis["per_channel_summary"])
        self.assertIn("firefighting_tactics", analysis["per_channel_summary"]["general"]["topics"])
        # Check based on current placeholder logic for common topics
        self.assertIn("firefighting_tactics", analysis["common_topics_across_channels"])


if __name__ == '__main__':
    unittest.main()
