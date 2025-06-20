# tests/analysis/test_dashboard.py
import unittest
from src.analysis.dashboard import AnalysisDashboard

class TestAnalysisDashboard(unittest.TestCase):
    def setUp(self):
        self.dashboard = AnalysisDashboard() # Basic dashboard, no analyzers needed for direct report tests

    def test_generate_sentiment_report(self):
        health_data = {"overall_mood": "positive", "total_conversations": 5,
                       "positive_conversations": 4, "negative_conversations": 0, "escalation_alerts": 1}
        report = self.dashboard.generate_sentiment_report(health_data)
        self.assertIn("Overall Community Mood: Positive", report)
        self.assertIn("Escalation Alerts Triggered: 1", report)

    def test_generate_topic_trend_summary(self):
        trending_topics = [("gameplay_feedback", 10), ("bug_reports", 5)]
        report = self.dashboard.generate_topic_trend_summary(trending_topics)
        self.assertIn("1. Gameplay Feedback: 10 mentions", report)
        self.assertIn("2. Bug Reports: 5 mentions", report)

    def test_generate_community_health_insights(self):
        s_data = {"overall_mood": "neutral", "escalation_alerts": 0}
        t_data = [("fire_tactics", 20)]
        q_scores = [{"overall_quality_numeric": 0.6}, {"overall_quality_numeric": 0.7}]
        report = self.dashboard.generate_community_health_insights(s_data, t_data, q_scores)
        self.assertIn("Overall Mood: Neutral", report)
        self.assertIn("Top Topic: Fire Tactics (20 mentions)", report)
        self.assertIn("Average Conversation Quality (Numeric): 0.65", report)

    def test_generate_moderator_alert(self):
        alert = self.dashboard.generate_moderator_alert(
            "Toxicity Detected",
            "User 'testuser' used offensive language in #general.",
            "channel_link"
        )
        self.assertIn("MODERATOR ALERT", alert)
        self.assertIn("Type: Toxicity Detected", alert)
        self.assertIn("Reference: channel_link", alert)

if __name__ == '__main__':
    unittest.main()
