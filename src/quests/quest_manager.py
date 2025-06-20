# src/quests/quest_manager.py

import time
import random # For generating IDs and mock data

# Placeholder for actual LLM integration for verification
class LLMQuestVerifier:
    def verify_completion(self, quest_description: str, user_submission: str) -> bool:
        # In a real scenario, this would involve LLM analysis of the submission
        # against the quest requirements.
        # For now, this is a placeholder.
        print(f"LLM Verifier: Checking if '{user_submission}' fulfills '{quest_description}'")
        if not user_submission or len(user_submission) < 10: # Basic check
            return False
        # Simulate LLM verification (e.g. keyword check, sentiment)
        return "complete" in user_submission.lower() or "done" in user_submission.lower()

# Placeholder for integration with a user/rewards system
class UserProfileSystem:
    def __init__(self):
        self.user_profiles = {} # user_id: { "level": 1, "xp": 0, "achievements": [] }

    def get_user_level(self, user_id: str) -> int:
        return self.user_profiles.get(user_id, {}).get("level", 1)

    def add_xp(self, user_id: str, xp_amount: int):
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {"level": 1, "xp": 0, "achievements": []}
        self.user_profiles[user_id]["xp"] += xp_amount
        print(f"User {user_id} gained {xp_amount} XP. Total XP: {self.user_profiles[user_id]['xp']}")
        # Add level up logic if necessary

    def unlock_achievement(self, user_id: str, achievement_id: str):
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {"level": 1, "xp": 0, "achievements": []}
        if achievement_id not in self.user_profiles[user_id]["achievements"]:
            self.user_profiles[user_id]["achievements"].append(achievement_id)
            print(f"User {user_id} unlocked achievement: {achievement_id}")

class QuestManager:
    def __init__(self, quest_generator, llm_verifier: LLMQuestVerifier, user_profile_system: UserProfileSystem):
        self.quest_generator = quest_generator # From quest_generator.py
        self.llm_verifier = llm_verifier
        self.user_profile_system = user_profile_system
        self.active_quests = {} # quest_id: quest_data
        self.user_quests = {} # user_id: [quest_id1, quest_id2, ...]

    def assign_quest(self, user_id: str, quest_type: str, custom_topic: str = None, season: str = None) -> dict:
        """Assigns a new quest to a user."""
        # In a real system, consider user's current quests, cooldowns, preferences
        user_level_str = self.user_profile_system.user_profiles.get(user_id, {}).get("level_str", "beginner") # Assumes user_profile_system can provide level string

        # This relies on QuestGenerator having user_levels properly populated or accessible
        # For now, we assume QuestGenerator is initialized with the necessary user level data
        quest_data = self.quest_generator.create_quest(
            user_id=user_id,
            quest_type=quest_type,
            custom_topic=custom_topic,
            season=season
        )

        quest_id = quest_data["quest_id"]
        self.active_quests[quest_id] = quest_data

        if user_id not in self.user_quests:
            self.user_quests[user_id] = []
        self.user_quests[user_id].append(quest_id)

        print(f"Quest '{quest_id}' ({quest_data['description']}) assigned to user {user_id}.")
        # TODO: Send milestone notification (e.g., "New quest available!")
        return quest_data

    def get_user_active_quests(self, user_id: str) -> list:
        """Retrieves all active quests for a given user."""
        quest_ids = self.user_quests.get(user_id, [])
        return [self.active_quests[qid] for qid in quest_ids if qid in self.active_quests and self.active_quests[qid]["status"] == "active"]

    def update_quest_progress(self, quest_id: str, progress_increment: int = 1, step_index: int = None) -> bool:
        """Updates the progress of a quest. For multi-step, specify step_index."""
        if quest_id not in self.active_quests:
            print(f"Error: Quest {quest_id} not found.")
            return False

        quest = self.active_quests[quest_id]
        if quest["status"] != "active":
            print(f"Error: Quest {quest_id} is not active.")
            return False

        if quest.get("steps") and step_index is not None and 0 <= step_index < len(quest["steps"]):
            # Multi-step progress
            if not quest["steps"][step_index]["completed"]:
                quest["steps"][step_index]["completed"] = True
                # Check if all steps are completed
                all_steps_done = all(step["completed"] for step in quest["steps"])
                if all_steps_done:
                    # Mark overall quest progress as complete, but don't set to "completed" status yet
                    # Verification should happen first.
                    quest["progress"] = quest.get("target_count", len(quest["steps"])) # Or some max value
                    print(f"All steps for quest {quest_id} completed by user {quest['user_id']}. Ready for verification.")
                    # TODO: Send milestone notification (e.g., "Step X of Y completed!")
                else:
                    # TODO: Send milestone notification
                    print(f"Step {step_index + 1} of quest {quest_id} completed by user {quest['user_id']}.")
            else:
                print(f"Step {step_index + 1} of quest {quest_id} already completed.")
        elif not quest.get("steps"): # Single-step or simple progress count
            # This part might need refinement based on how 'progress' and 'target_count' are defined
            quest["progress"] = quest.get("progress", 0) + progress_increment
            target = quest.get("difficulty_params", {}).get("count_max", 1) # Example target
            print(f"Quest {quest_id} progress for user {quest['user_id']}: {quest['progress']}/{target}")
            # TODO: Send milestone notification
            if quest["progress"] >= target: # Assuming progress meets target
                 print(f"Quest {quest_id} objective met by user {quest['user_id']}. Ready for verification.")
        else:
            print(f"Error: Invalid progress update for quest {quest_id}.")
            return False

        return True

    def submit_for_completion(self, quest_id: str, user_submission: str = None) -> bool:
        """Allows a user to submit a quest for completion verification."""
        if quest_id not in self.active_quests:
            print(f"Error: Quest {quest_id} not found for submission.")
            return False

        quest = self.active_quests[quest_id]
        if quest["status"] != "active":
            print(f"Error: Quest {quest_id} is not active or already processed.")
            return False

        # For some quests, submission might not be text (e.g., auto-detected actions)
        # For others, LLM verification of text/evidence is needed.
        verified = False
        if quest.get("auto_verify", False): # Hypothetical flag for auto-verified quests
            verified = True
        elif user_submission:
            verified = self.llm_verifier.verify_completion(quest["description"], user_submission)
        else:
            # If no submission needed (e.g. progress tracked internally and met)
            # This condition needs to be well-defined. For example, if all steps are complete.
            if quest.get("steps") and all(step["completed"] for step in quest["steps"]):
                verified = True
            elif not quest.get("steps") and quest.get("progress", 0) >= quest.get("difficulty_params", {}).get("count_max", 1) : # Simplified check
                 verified = True


        if verified:
            quest["status"] = "completed"
            print(f"Quest {quest_id} completed by user {quest['user_id']}.")
            self._distribute_rewards(quest["user_id"], quest)
            # TODO: Send milestone notification (e.g., "Quest Complete!")
            # Clean up from active_quests if desired, or move to a completed_quests log
            # For now, just updating status.
        else:
            quest["status"] = "verification_failed" # Or back to 'active' with feedback
            print(f"Quest {quest_id} verification failed for user {quest['user_id']}.")
            # TODO: Send feedback to user
        return verified

    def _distribute_rewards(self, user_id: str, quest_data: dict):
        """Distributes rewards for a completed quest."""
        # Example reward: XP based on difficulty or quest type
        xp_reward = 0
        level_str = self.quest_generator.user_levels.get(user_id, "beginner") # Get level from QuestGenerator's cache for now

        if level_str == "advanced":
            xp_reward = 100
        elif level_str == "intermediate":
            xp_reward = 50
        else:
            xp_reward = 25

        # Quest-type specific bonuses
        if quest_data["type"] == "leadership":
            xp_reward *= 1.5

        self.user_profile_system.add_xp(user_id, int(xp_reward))

        # Unlock achievements (example)
        achievement_id = f"completed_{quest_data['type']}_quest"
        self.user_profile_system.unlock_achievement(user_id, achievement_id)

        if quest_data.get("seasonal_theme"):
             seasonal_achievement = f"completed_seasonal_{quest_data['seasonal_theme'].split(':')[0].lower().replace(' ', '_')}"
             self.user_profile_system.unlock_achievement(user_id, seasonal_achievement)

        print(f"Rewards distributed for quest {quest_data['quest_id']} to user {user_id}.")


# Example Usage (requires QuestGenerator from quest_generator.py)
if __name__ == "__main__":
    # This example requires QuestGenerator to be importable and setup
    # For simplicity, we'll mock parts of it if direct import isn't straightforward in this subtask context

    # Mocking QuestGenerator and its dependencies for standalone testing of QuestManager
    class MockLLMProvider:
        def generate_quest_text(self, prompt: str) -> str:
            return f"Mock LLM says: {prompt}"

    class MockQuestGenerator:
        def __init__(self, user_levels_data):
            self.llm_provider = MockLLMProvider()
            self.user_levels = user_levels_data # Store user levels directly
            self.quest_templates = {"social": "Welcome {count} new members."} # simplified

        def create_quest(self, user_id, quest_type, custom_topic=None, season=None):
            level = self.user_levels.get(user_id, "beginner")
            count = 1 if level == "beginner" else 3 if level == "intermediate" else 5
            desc = self.quest_templates[quest_type].format(count=count)
            if season:
                desc = f"{season.capitalize()} Event: {desc}"
            return {
                "quest_id": f"quest_{random.randint(1000,9999)}", "user_id": user_id, "type": quest_type,
                "description": desc, "status": "active", "progress": 0,
                "difficulty_params": {"count_max": count}, # simplified for reward calc
                "steps": [{"description": f"Welcome member {i+1}/{count}", "completed": False} for i in range(count)] if quest_type == "social" else [],
                "seasonal_theme": season.capitalize() + " Event" if season else None
            }

    mock_user_levels_data = {"user1": "beginner", "user2": "intermediate", "user3": "advanced"}
    q_generator = MockQuestGenerator(user_levels_data=mock_user_levels_data)

    llm_verifier = LLMQuestVerifier()
    user_profiles = UserProfileSystem()
    # Initialize user profiles for testing rewards
    user_profiles.user_profiles = {
        "user1": {"level": 1, "xp": 0, "achievements": [], "level_str": "beginner"},
        "user2": {"level": 5, "xp": 500, "achievements": [], "level_str": "intermediate"},
        "user3": {"level": 10, "xp": 1000, "achievements": [], "level_str": "advanced"}
    }

    manager = QuestManager(quest_generator=q_generator, llm_verifier=llm_verifier, user_profile_system=user_profiles)

    # Assign a quest
    print("\n--- Assigning Quest ---")
    assigned_quest = manager.assign_quest(user_id="user1", quest_type="social", season="spring")
    if assigned_quest:
        quest_id = assigned_quest["quest_id"]
        print(f"Assigned Quest ID: {quest_id}")

        # Get active quests for user
        print("\n--- Active Quests ---")
        active_quests = manager.get_user_active_quests("user1")
        print(f"User1 active quests: {active_quests}")

        # Update progress (multi-step example for social quest)
        print("\n--- Updating Progress ---")
        if assigned_quest.get("steps"):
            manager.update_quest_progress(quest_id, step_index=0) # Complete first step
            # Simulate completing all steps for verification
            for i in range(len(assigned_quest["steps"])):
                 manager.update_quest_progress(quest_id, step_index=i)


        # Submit for completion
        print("\n--- Submitting for Completion ---")
        # For multi-step, if all steps are done, it might auto-verify or require a final submission.
        # Current logic: if steps exist and all are done, 'verified' can be true without submission text.
        submission_text = "I've welcomed everyone, it is complete!" # Example submission
        completed_successfully = manager.submit_for_completion(quest_id, user_submission=submission_text)
        print(f"Quest completion status: {completed_successfully}")

        if completed_successfully:
            print(f"User1 profile after quest: {user_profiles.user_profiles['user1']}")

        # Test another user and quest type for reward variation
        print("\n--- Assigning Leadership Quest to Advanced User ---")
        # Note: The MockQuestGenerator needs 'leadership' quest type to be defined for this to work.
        # Adding it here for the sake of the example running.
        q_generator.quest_templates["leadership"] = "Moderate effectively for {duration}." # Example template
        assigned_leadership_quest = manager.assign_quest(user_id="user3", quest_type="leadership")
        if assigned_leadership_quest:
             l_quest_id = assigned_leadership_quest["quest_id"]
             print(f"Assigned Leadership Quest ID: {l_quest_id}")
             # Simulate progress for leadership (non-stepped, assuming direct completion)
             # For a duration-based quest, 'progress' might be time-based or event-based.
             # Here, we'll mock that the condition for completion is met.
             manager.active_quests[l_quest_id]["difficulty_params"]["count_max"] = 1 # Ensure target is met by progress
             manager.active_quests[l_quest_id]["progress"] = 1
             manager.submit_for_completion(l_quest_id, "Leadership tasks done, all complete.")
             print(f"User3 profile after leadership quest: {user_profiles.user_profiles['user3']}")
    else:
        print("Failed to assign quest in example.")
