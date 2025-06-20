# tests/unit/quests/test_quest_generator.py
import unittest
from unittest.mock import MagicMock, patch
from src.quests.quest_generator import QuestGenerator, LLMProvider

class TestQuestGenerator(unittest.TestCase):

    def setUp(self):
        self.mock_llm_provider = MagicMock(spec=LLMProvider)
        self.mock_llm_provider.generate_quest_text.return_value = "LLM generated quest text"

        self.community_health_data = {"engagement": "medium", "needs": ["more help channel activity"]}
        self.user_levels = {"user_beginner": "beginner", "user_intermediate": "intermediate", "user_advanced": "advanced"}

        self.quest_generator = QuestGenerator(
            llm_provider=self.mock_llm_provider,
            community_health_data=self.community_health_data,
            user_levels=self.user_levels
        )

    def test_initialization(self):
        self.assertIsNotNone(self.quest_generator)
        self.assertEqual(self.quest_generator.llm_provider, self.mock_llm_provider)

    def test_get_difficulty_params(self):
        beginner_params = self.quest_generator._get_difficulty_params("user_beginner")
        self.assertEqual(beginner_params["count_min"], 1)
        self.assertEqual(beginner_params["count_max"], 3)

        intermediate_params = self.quest_generator._get_difficulty_params("user_intermediate")
        self.assertEqual(intermediate_params["count_min"], 3)
        self.assertEqual(intermediate_params["count_max"], 5)

        advanced_params = self.quest_generator._get_difficulty_params("user_advanced")
        self.assertEqual(advanced_params["count_min"], 5)
        self.assertEqual(advanced_params["count_max"], 10)

        unknown_user_params = self.quest_generator._get_difficulty_params("user_unknown") # Should default to beginner
        self.assertEqual(unknown_user_params["count_min"], 1)


    def test_adapt_quest_to_community_health(self):
        base_prompt = "Base quest prompt."
        adapted_prompt = self.quest_generator._adapt_quest_to_community_health(base_prompt)
        self.assertIn("Focus on encouraging help channel participation", adapted_prompt)

    def test_apply_seasonal_theme(self):
        quest_text = "Do a quest."
        summer_quest = self.quest_generator._apply_seasonal_theme(quest_text, "summer")
        self.assertIn("Summer Festival Challenge:", summer_quest)

        no_season_quest = self.quest_generator._apply_seasonal_theme(quest_text, None)
        self.assertEqual(no_season_quest, quest_text)

        invalid_season_quest = self.quest_generator._apply_seasonal_theme(quest_text, "nosuchseason")
        self.assertEqual(invalid_season_quest, quest_text)


    def test_create_social_quest(self):
        user_id = "user_intermediate"
        quest = self.quest_generator.create_quest(user_id, "social", season="winter")

        self.assertEqual(quest["user_id"], user_id)
        self.assertEqual(quest["type"], "social")
        self.assertIn("Winter Wonderland Quest:", quest["description"])
        self.assertTrue(3 <= quest["difficulty_params"]["count_min"] <= quest["difficulty_params"]["count_max"] <= 5) # Intermediate count
        self.mock_llm_provider.generate_quest_text.assert_called_once()
        self.assertIn(f"User level: {self.user_levels[user_id]}", quest["llm_prompt_used"])
        self.assertIn("Base idea: Welcome ", quest["llm_prompt_used"]) # Check base idea part of prompt
        self.assertIn("multi-step quest", quest["description"].lower()) # Check if multi-step hint is there
        self.assertTrue(len(quest["steps"]) >= quest["difficulty_params"]["count_min"])


    def test_create_knowledge_quest(self):
        user_id = "user_beginner"
        quest = self.quest_generator.create_quest(user_id, "knowledge")

        self.assertEqual(quest["type"], "knowledge")
        self.assertTrue(1 <= quest["difficulty_params"]["count_min"] <= quest["difficulty_params"]["count_max"] <= 3) # Beginner count
        self.assertIn("Answer ", quest["description"]) # Check if template is used
        # Check community health adaptation in prompt
        self.assertIn("Focus on encouraging help channel participation.", quest["llm_prompt_used"])

    def test_create_community_quest_with_topic(self):
        user_id = "user_advanced"
        topic = "AI safety"
        quest = self.quest_generator.create_quest(user_id, "community", custom_topic=topic)

        self.assertEqual(quest["type"], "community")
        self.assertIn(topic, quest["description"])
        self.assertTrue(quest["difficulty_params"]["duration"] == "7 days") # Advanced duration

    def test_create_quest_invalid_type(self):
        with self.assertRaises(ValueError):
            self.quest_generator.create_quest("user_beginner", "invalid_quest_type")

    def test_create_quest_llm_refinement_placeholder(self):
        # This test checks the current placeholder behavior where LLM output is appended.
        # It will need to be updated if/when real LLM integration changes this logic.
        user_id = "user_intermediate"
        self.mock_llm_provider.generate_quest_text.return_value = "Generated quest text based on prompt: LLM refined output."
        quest = self.quest_generator.create_quest(user_id, "social")

        self.assertIn("LLM suggests focusing on", quest["description"])
        self.assertIn(f"User level: {self.user_levels[user_id]}", quest["description"])

    # Test multi-step generation logic specifically for social quests
    def test_multi_step_social_quest_generation(self):
        user_id = "user_intermediate" # Expects 3-5 steps
        quest = self.quest_generator.create_quest(user_id, "social")

        self.assertTrue(quest["steps"] is not None)
        self.assertTrue(3 <= len(quest["steps"]) <= 5, f"Expected 3-5 steps, got {len(quest['steps'])}")
        for i, step in enumerate(quest["steps"]):
            self.assertIn(f"Welcome member {i+1}/{len(quest['steps'])}", step["description"])
            self.assertFalse(step["completed"])
        self.assertIn("(This is a multi-step quest)", quest["description"])

    def test_non_social_quest_default_steps(self):
        user_id = "user_intermediate"
        # Knowledge quest is not configured for multi-step in the same way as social
        quest = self.quest_generator.create_quest(user_id, "knowledge")

        self.assertTrue(quest["steps"] is not None)
        self.assertEqual(len(quest["steps"]), 1) # Default single step
        self.assertEqual(quest["steps"][0]["description"], "Complete the main objective.")
        self.assertFalse("(This is a multi-step quest)" in quest["description"])


if __name__ == '__main__':
    unittest.main()
