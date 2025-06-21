# tests/unit/quests/test_quest_manager.py
import unittest
from unittest.mock import MagicMock, patch
from src.quests.quest_generator import QuestGenerator # Needed for QuestManager type hint
from src.quests.quest_manager import QuestManager, LLMQuestVerifier, UserProfileSystem

class TestQuestManager(unittest.TestCase):

    def setUp(self):
        self.mock_quest_generator = MagicMock(spec=QuestGenerator)
        self.mock_llm_verifier = MagicMock(spec=LLMQuestVerifier)
        self.mock_user_profile_system = MagicMock(spec=UserProfileSystem)

        # Configure common return values for mocks
        self.generated_quest_data = {
            "quest_id": "quest_123", "user_id": "user1", "type": "social",
            "description": "Welcome 3 new members.", "status": "active", "progress": 0,
            "difficulty_params": {"count_max": 3, "count_min": 3},
            "steps": [
                {"description": "Welcome member 1/3", "completed": False},
                {"description": "Welcome member 2/3", "completed": False},
                {"description": "Welcome member 3/3", "completed": False}
            ],
            "seasonal_theme": None
        }
        self.mock_quest_generator.create_quest.return_value = self.generated_quest_data
        self.mock_quest_generator.user_levels = {"user1": "intermediate"} # For reward calculation

        self.mock_user_profile_system.get_user_level.return_value = 5 # Example level
        self.mock_user_profile_system.user_profiles = {
            "user1": {"level": 5, "xp": 100, "achievements": [], "level_str": "intermediate"}
        }


        self.quest_manager = QuestManager(
            quest_generator=self.mock_quest_generator,
            llm_verifier=self.mock_llm_verifier,
            user_profile_system=self.mock_user_profile_system
        )

    def test_initialization(self):
        self.assertIsNotNone(self.quest_manager)
        self.assertEqual(self.quest_manager.quest_generator, self.mock_quest_generator)

    def test_assign_quest(self):
        user_id = "user1"
        quest_type = "social"
        assigned_quest = self.quest_manager.assign_quest(user_id, quest_type)

        self.mock_quest_generator.create_quest.assert_called_once_with(
            user_id=user_id, quest_type=quest_type, custom_topic=None, season=None
        )
        self.assertIn(assigned_quest["quest_id"], self.quest_manager.active_quests)
        self.assertIn(assigned_quest["quest_id"], self.quest_manager.user_quests[user_id])
        self.assertEqual(assigned_quest, self.generated_quest_data)

    def test_get_user_active_quests(self):
        user_id = "user1"
        self.quest_manager.assign_quest(user_id, "social")

        active_quests = self.quest_manager.get_user_active_quests(user_id)
        self.assertEqual(len(active_quests), 1)
        self.assertEqual(active_quests[0]["quest_id"], self.generated_quest_data["quest_id"])

        # Test for user with no quests
        self.assertEqual(self.quest_manager.get_user_active_quests("user_new"), [])

    def test_update_quest_progress_single_step_quest(self):
        # Setup a non-stepped quest
        single_step_quest_data = {
            "quest_id": "quest_single", "user_id": "user1", "type": "knowledge",
            "description": "Answer 1 question.", "status": "active", "progress": 0,
            "difficulty_params": {"count_max": 1, "count_min": 1}, "steps": None
        }
        self.mock_quest_generator.create_quest.return_value = single_step_quest_data
        quest = self.quest_manager.assign_quest("user1", "knowledge")

        updated = self.quest_manager.update_quest_progress(quest["quest_id"], progress_increment=1)
        self.assertTrue(updated)
        self.assertEqual(self.quest_manager.active_quests[quest["quest_id"]]["progress"], 1)

    def test_update_quest_progress_multi_step_quest(self):
        quest = self.quest_manager.assign_quest("user1", "social") # Uses self.generated_quest_data
        quest_id = quest["quest_id"]

        updated = self.quest_manager.update_quest_progress(quest_id, step_index=0)
        self.assertTrue(updated)
        self.assertTrue(self.quest_manager.active_quests[quest_id]["steps"][0]["completed"])

        # Complete all steps
        for i in range(len(self.generated_quest_data["steps"])):
            self.quest_manager.update_quest_progress(quest_id, step_index=i)

        all_steps_done = all(s["completed"] for s in self.quest_manager.active_quests[quest_id]["steps"])
        self.assertTrue(all_steps_done)
        # Check if overall progress reflects completion (e.g., progress equals target count)
        self.assertEqual(self.quest_manager.active_quests[quest_id]["progress"], len(self.generated_quest_data["steps"]))


    def test_update_quest_progress_invalid_quest(self):
        self.assertFalse(self.quest_manager.update_quest_progress("invalid_id", 1))

    def test_submit_for_completion_verified_by_llm(self):
        quest = self.quest_manager.assign_quest("user1", "social")
        quest_id = quest["quest_id"]
        submission_text = "I did it, it's complete!"

        self.mock_llm_verifier.verify_completion.return_value = True

        completed = self.quest_manager.submit_for_completion(quest_id, submission_text)

        self.assertTrue(completed)
        self.assertEqual(self.quest_manager.active_quests[quest_id]["status"], "completed")
        self.mock_llm_verifier.verify_completion.assert_called_once_with(quest["description"], submission_text)
        self.mock_user_profile_system.add_xp.assert_called_once()
        self.mock_user_profile_system.unlock_achievement.assert_called_once()

    def test_submit_for_completion_auto_verify_all_steps_done(self):
        quest = self.quest_manager.assign_quest("user1", "social") # uses multi-step generated_quest_data
        quest_id = quest["quest_id"]

        # Complete all steps first
        for i in range(len(quest["steps"])):
            self.quest_manager.update_quest_progress(quest_id, step_index=i)

        # No submission text, relies on all steps being completed
        completed = self.quest_manager.submit_for_completion(quest_id, user_submission=None)

        self.assertTrue(completed, f"Quest status: {self.quest_manager.active_quests[quest_id]['status']}")
        self.assertEqual(self.quest_manager.active_quests[quest_id]["status"], "completed")
        self.mock_llm_verifier.verify_completion.assert_not_called() # Should not be called if auto-verified by steps
        self.mock_user_profile_system.add_xp.assert_called_once()


    def test_submit_for_completion_verification_failed(self):
        quest = self.quest_manager.assign_quest("user1", "social")
        quest_id = quest["quest_id"]
        self.mock_llm_verifier.verify_completion.return_value = False

        completed = self.quest_manager.submit_for_completion(quest_id, "Failed attempt.")

        self.assertFalse(completed)
        self.assertEqual(self.quest_manager.active_quests[quest_id]["status"], "verification_failed")
        self.mock_user_profile_system.add_xp.assert_not_called()

    def test_distribute_rewards(self):
        user_id = "user1"
        # Quest data needs 'type' and potentially 'seasonal_theme' for full test coverage
        quest_data_for_reward = {
            "quest_id": "reward_quest_1", "user_id": user_id, "type": "leadership",
            "description": "Lead a team.", "status": "completed",
            "seasonal_theme": "Summer Event" # Test seasonal achievement
        }
        # Ensure user_profiles has the user with a level string for reward calculation
        self.mock_user_profile_system.user_profiles[user_id]["level_str"] = "advanced" # For higher base XP
        self.mock_quest_generator.user_levels[user_id] = "advanced" # Ensure generator's view is consistent

        self.quest_manager._distribute_rewards(user_id, quest_data_for_reward)

        self.mock_user_profile_system.add_xp.assert_called_once_with(user_id, 150) # 100 for advanced * 1.5 for leadership
        self.mock_user_profile_system.unlock_achievement.assert_any_call(user_id, "completed_leadership_quest")
        self.mock_user_profile_system.unlock_achievement.assert_any_call(user_id, "completed_seasonal_summer_event")

    def test_submit_for_completion_quest_not_found(self):
        self.assertFalse(self.quest_manager.submit_for_completion("invalid_quest_id", "submission"))

    def test_submit_for_completion_quest_not_active(self):
        quest = self.quest_manager.assign_quest("user1", "social")
        quest_id = quest["quest_id"]
        self.quest_manager.active_quests[quest_id]["status"] = "completed" # Manually set to not active

        completed = self.quest_manager.submit_for_completion(quest_id, "too late")
        self.assertFalse(completed)
        self.assertEqual(self.quest_manager.active_quests[quest_id]["status"], "completed") # Remains completed


if __name__ == '__main__':
    unittest.main()
