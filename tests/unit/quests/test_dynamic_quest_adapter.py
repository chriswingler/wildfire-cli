# tests/unit/quests/test_dynamic_quest_adapter.py
import unittest
from unittest.mock import MagicMock, patch
import time
from src.quests.quest_generator import QuestGenerator # For type hint
from src.quests.dynamic_quest_adapter import DynamicQuestAdapter, CommunityAnalyticsClient

class TestDynamicQuestAdapter(unittest.TestCase):

    def setUp(self):
        self.mock_analytics_client = MagicMock(spec=CommunityAnalyticsClient)
        self.mock_quest_generator = MagicMock(spec=QuestGenerator)

        # Default mock return values
        self.mock_analytics_client.get_server_health_metrics.return_value = {
            "server_id": "server1", "overall_engagement": "medium",
            "active_channels": ["general", "help"], "low_activity_channels": [],
            "trending_topics": ["topic1", "topic2"],
            "new_member_count_last_7_days": 10,
            "needs_attention": []
        }
        self.mock_analytics_client.get_trending_topics.return_value = ["topic1", "topic2"]

        self.generated_quest_data = {"quest_id": "dyn_quest_1", "description": "Adapted quest"}
        self.mock_quest_generator.create_quest.return_value = self.generated_quest_data

        self.adapter = DynamicQuestAdapter(
            analytics_client=self.mock_analytics_client,
            quest_generator=self.mock_quest_generator
        )
        # Clear cache before each test if needed, or manage time
        self.adapter._server_health_cache = {}


    def test_initialization(self):
        self.assertIsNotNone(self.adapter)
        self.assertEqual(self.adapter.analytics_client, self.mock_analytics_client)

    @patch('time.time', return_value=1000) # Mock current time
    def test_get_cached_server_health_fresh_fetch(self, mock_time):
        server_id = "server1"
        self.adapter._get_cached_server_health(server_id)
        self.mock_analytics_client.get_server_health_metrics.assert_called_once_with(server_id)
        self.assertIn(server_id, self.adapter._server_health_cache)

    @patch('time.time')
    def test_get_cached_server_health_uses_cache(self, mock_time):
        server_id = "server1"
        # Prime cache
        mock_time.return_value = 1000
        self.adapter._get_cached_server_health(server_id)
        self.mock_analytics_client.get_server_health_metrics.assert_called_once_with(server_id)

        # Call again within TTL
        mock_time.return_value = 1000 + self.adapter._cache_ttl_seconds - 1
        self.adapter._get_cached_server_health(server_id)
        # Assert mock was still called only once (cache hit)
        self.mock_analytics_client.get_server_health_metrics.assert_called_once_with(server_id)

    @patch('time.time')
    def test_get_cached_server_health_cache_expired(self, mock_time):
        server_id = "server1"
        # Prime cache
        mock_time.return_value = 1000
        self.adapter._get_cached_server_health(server_id)
        self.mock_analytics_client.get_server_health_metrics.assert_called_once_with(server_id)

        # Call again after TTL
        mock_time.return_value = 1000 + self.adapter._cache_ttl_seconds + 1
        self.adapter._get_cached_server_health(server_id)
        # Assert mock was called again (cache miss)
        self.assertEqual(self.mock_analytics_client.get_server_health_metrics.call_count, 2)


    def test_suggest_quest_type_low_engagement_new_members_needed(self):
        self.mock_analytics_client.get_server_health_metrics.return_value["overall_engagement"] = "low"
        self.mock_analytics_client.get_server_health_metrics.return_value["new_member_count_last_7_days"] = 2
        quest_type, _, _ = self.adapter.suggest_quest_type_and_topic("server1", "user1")
        self.assertEqual(quest_type, "social")

    def test_suggest_quest_type_medium_engagement_help_needed(self):
        self.mock_analytics_client.get_server_health_metrics.return_value["overall_engagement"] = "medium"
        self.mock_analytics_client.get_server_health_metrics.return_value["needs_attention"] = ["low engagement in #help"]
        quest_type, topic, _ = self.adapter.suggest_quest_type_and_topic("server1", "user1")
        self.assertEqual(quest_type, "knowledge")
        self.assertEqual(topic, "help")

    def test_suggest_quest_type_high_engagement(self):
        self.mock_analytics_client.get_server_health_metrics.return_value["overall_engagement"] = "high"
        quest_type, _, _ = self.adapter.suggest_quest_type_and_topic("server1", "user1")
        self.assertIn(quest_type, ["leadership", "creative", "community"])

    def test_suggest_quest_type_uses_trending_topic(self):
        self.mock_analytics_client.get_server_health_metrics.return_value["overall_engagement"] = "high" # To make community/creative likely
        trending = ["super_hot_topic"]
        self.mock_analytics_client.get_trending_topics.return_value = trending

        # Run a few times as type selection is random for high engagement
        for _ in range(10): # Increased attempts for higher chance of hitting community/creative
            quest_type, topic, _ = self.adapter.suggest_quest_type_and_topic("server1", "user1")
            if quest_type in ["community", "creative"]:
                self.assertEqual(topic, trending[0])
                return # Test passed
        self.fail("Community or Creative quest type with trending topic not selected after multiple tries.")


    @patch('time.localtime') # To control current month for season
    def test_suggest_quest_type_includes_season(self, mock_localtime):
        # Mock tm_mon: 12=Dec (winter), 6=Jun (summer)
        mock_localtime.return_value = time.struct_time((2023, 12, 15, 0,0,0,0,0,0)) # December
        _, _, season = self.adapter.suggest_quest_type_and_topic("server1", "user1")
        self.assertEqual(season, "winter")

        mock_localtime.return_value = time.struct_time((2023, 6, 15, 0,0,0,0,0,0)) # June
        _, _, season = self.adapter.suggest_quest_type_and_topic("server1", "user1")
        self.assertEqual(season, "summer")


    def test_generate_adapted_quest_successful(self):
        server_id = "server1"
        user_id = "user1"
        # Mock suggest_quest_type_and_topic to return predictable values for this test
        self.adapter.suggest_quest_type_and_topic = MagicMock(return_value=("social", "a_topic", "summer"))

        quest = self.adapter.generate_adapted_quest(server_id, user_id)

        self.adapter.suggest_quest_type_and_topic.assert_called_once_with(server_id, user_id)
        self.mock_quest_generator.create_quest.assert_called_once_with(
            user_id=user_id, quest_type="social", custom_topic="a_topic", season="summer"
        )
        self.assertEqual(quest, self.generated_quest_data)

    def test_generate_adapted_quest_suggestion_fails(self):
        # If suggest_quest_type_and_topic returns None for quest_type
        self.adapter.suggest_quest_type_and_topic = MagicMock(return_value=(None, None, None))
        quest = self.adapter.generate_adapted_quest("server1", "user1")
        self.assertIsNone(quest)
        self.mock_quest_generator.create_quest.assert_not_called()

    def test_generate_adapted_quest_generator_raises_value_error(self):
        self.mock_quest_generator.create_quest.side_effect = ValueError("Invalid quest type in generator")
        # Mock suggest_quest_type_and_topic to ensure it provides valid inputs to create_quest call
        self.adapter.suggest_quest_type_and_topic = MagicMock(return_value=("social", None, None))

        quest = self.adapter.generate_adapted_quest("server1", "user1")
        self.assertIsNone(quest)
        self.mock_quest_generator.create_quest.assert_called_once() # Ensure it was called

    def test_generate_adapted_quest_generator_raises_unexpected_error(self):
        self.mock_quest_generator.create_quest.side_effect = Exception("Unexpected error")
        self.adapter.suggest_quest_type_and_topic = MagicMock(return_value=("social", None, None))

        quest = self.adapter.generate_adapted_quest("server1", "user1")
        self.assertIsNone(quest)
        self.mock_quest_generator.create_quest.assert_called_once()


if __name__ == '__main__':
    unittest.main()
