# src/quests/dynamic_quest_adapter.py

import random
import time

# Placeholder for actual Community Analytics Engine integration
class CommunityAnalyticsClient:
    def get_server_health_metrics(self, server_id: str) -> dict:
        # In a real system, this would fetch data like engagement levels,
        # channel activity, new member join rate, message sentiment, etc.
        # Mock data for now:
        return {
            "server_id": server_id,
            "overall_engagement": random.choice(["low", "medium", "high"]),
            "active_channels": ["general", "help", "random"],
            "low_activity_channels": ["event-planning", "feedback"],
            "trending_topics": ["new_game_update", "community_poll_idea"],
            "new_member_count_last_7_days": random.randint(0, 20),
            "needs_attention": ["low engagement in #feedback", "more new member welcomes"]
        }

    def get_trending_topics(self, server_id: str) -> list:
        # Mock data
        return random.sample(["AI ethics discussion", "Feature request: dark mode", "Upcoming server event"], k=2)

class DynamicQuestAdapter:
    def __init__(self, analytics_client: CommunityAnalyticsClient, quest_generator):
        self.analytics_client = analytics_client
        self.quest_generator = quest_generator # From quest_generator.py
        # Cache for server health to avoid frequent calls
        self._server_health_cache = {} # server_id: (timestamp, data)
        self._cache_ttl_seconds = 300 # 5 minutes

    def _get_cached_server_health(self, server_id: str) -> dict:
        current_time = time.time()
        if server_id in self._server_health_cache:
            timestamp, data = self._server_health_cache[server_id]
            if current_time - timestamp < self._cache_ttl_seconds:
                return data

        # Fetch new data and update cache
        fresh_data = self.analytics_client.get_server_health_metrics(server_id)
        self._server_health_cache[server_id] = (current_time, fresh_data)
        return fresh_data

    def suggest_quest_type_and_topic(self, server_id: str, user_id: str) -> tuple[str, str | None, str | None]:
        """
        Suggests a quest type, a custom topic (if applicable), and a season
        based on community needs and trends.
        Returns: (quest_type_str, custom_topic_str_or_None, season_str_or_None)
        """
        health_metrics = self._get_cached_server_health(server_id)
        quest_type = "social" # Default
        custom_topic = None
        season = self._get_current_season() # Example: "summer", "winter"

        # Prioritize based on community health metrics
        # This logic can be much more sophisticated
        if health_metrics["overall_engagement"] == "low":
            if health_metrics["new_member_count_last_7_days"] < 5:
                quest_type = "social" # Focus on welcoming new members
            else:
                quest_type = random.choice(["social", "creative"]) # Icebreakers or simple content sharing
        elif health_metrics["overall_engagement"] == "medium":
            if "low engagement in #help" in health_metrics.get("needs_attention", []) or \
               (health_metrics.get("low_activity_channels") and "help" in health_metrics.get("low_activity_channels", [])): # Added default for get
                quest_type = "knowledge"
                custom_topic = "help" # Hint to focus on the help channel
            else:
                quest_type = random.choice(["knowledge", "community"])
        else: # High engagement
            quest_type = random.choice(["leadership", "creative", "community"])

        # Integrate trending topics for community or creative quests
        if quest_type in ["community", "creative"]:
            trending_topics = self.analytics_client.get_trending_topics(server_id)
            if trending_topics:
                custom_topic = random.choice(trending_topics)

        # Override with seasonal themes if applicable
        # For example, if it's December, 'winter' season might be prioritized for certain quest types.
        # This is a simplified seasonal check.
        # A more robust system would have configurable start/end dates for seasons/events.

        print(f"Adapter suggested: QuestType='{quest_type}', Topic='{custom_topic}', Season='{season}' for server {server_id}")
        return quest_type, custom_topic, season


    def generate_adapted_quest(self, server_id: str, user_id: str) -> dict | None:
        """
        Generates a quest dynamically adapted to the server's needs and user's profile.
        """
        quest_type_str, custom_topic, season = self.suggest_quest_type_and_topic(server_id, user_id)

        if not quest_type_str:
            print(f"Could not determine a suitable quest type for user {user_id} on server {server_id}.")
            return None

        # The QuestGenerator should be initialized with user_levels data that includes the user_id
        # This is a dependency that needs to be handled during QuestGenerator's instantiation.
        try:
            # Assuming quest_generator can handle string quest_type by mapping to its internal types if necessary
            # Or, QuestCategory enum could be used here if QuestGenerator expects it.
            # For now, assume QuestGenerator's create_quest method takes string type.
            quest_data = self.quest_generator.create_quest(
                user_id=user_id,
                quest_type=quest_type_str, # e.g., "social", "knowledge"
                custom_topic=custom_topic,
                season=season
            )
            # Further adapt quest description using LLM if needed, based on more specific server needs
            # For example, if quest_data['description'] is generic, refine it.
            # This would be another call to an LLM, possibly through the quest_generator or a dedicated service.
            # quest_data['description'] = self._refine_quest_with_llm(quest_data, health_metrics)

            return quest_data
        except ValueError as e:
            print(f"Error generating adapted quest: {e}")
            return None
        except Exception as e: # Catch other potential errors during quest creation
            print(f"An unexpected error occurred during adapted quest generation: {e}")
            return None

    def _get_current_season(self) -> str | None:
        """Determines the current season. Placeholder logic."""
        month = time.localtime().tm_mon
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "autumn"
        return None

    # def _refine_quest_with_llm(self, quest_data: dict, health_metrics: dict) -> str:
    # This would be a more advanced feature:
    # llm_prompt = (f"Refine this quest: '{quest_data['description']}'. "
    # f"The community ({health_metrics['server_id']}) currently needs: {health_metrics.get('needs_attention', [])}. "
    # f"Make it more engaging and relevant to these needs, while keeping the core objective.")
    # refined_description = self.quest_generator.llm_provider.generate_quest_text(llm_prompt)
    # return refined_description


# Example Usage (requires QuestGenerator and its dependencies)
if __name__ == "__main__":
    # Mocking dependencies for standalone testing
    class MockLLMProvider:
        def generate_quest_text(self, prompt: str) -> str: return f"LLM: {prompt}"

    class MockQuestGenerator:
        def __init__(self, user_levels_data):
            self.llm_provider = MockLLMProvider()
            self.user_levels = user_levels_data
            self.quest_templates = { # Ensure this matches what DynamicQuestAdapter might request
                "social": "Welcome {count} new members.",
                "knowledge": "Answer {count} questions in #help.",
                "creative": "Share {count} original content in #showcase.",
                "community": "Discuss {topic}.",
                "leadership": "Moderate for {duration}."
            }
        def create_quest(self, user_id, quest_type, custom_topic=None, season=None):
            level = self.user_levels.get(user_id, "beginner")
            count = 1 if level == "beginner" else 3
            duration = "1 day" if level == "beginner" else "3 days"

            if quest_type not in self.quest_templates:
                raise ValueError(f"MockQuestGenerator does not have template for type: {quest_type}")

            desc_template = self.quest_templates[quest_type]

            if "{count}" in desc_template:
                desc = desc_template.format(count=count)
            elif "{topic}" in desc_template:
                desc = desc_template.format(topic=custom_topic or "a generated topic")
            elif "{duration}" in desc_template:
                desc = desc_template.format(duration=duration)
            else:
                desc = desc_template # Should not happen with current templates

            if season:
                desc = f"{season.capitalize()} Special: {desc}"

            return {
                "quest_id": f"q_dyn_{random.randint(1000,9999)}", "user_id": user_id,
                "type": quest_type, "description": desc, "status": "active",
                "custom_topic": custom_topic, "season": season
            }

    mock_user_data = {"user_alpha": "intermediate", "user_beta": "beginner"}
    q_gen = MockQuestGenerator(user_levels_data=mock_user_data)
    analytics = CommunityAnalyticsClient() # Using the placeholder defined above

    adapter = DynamicQuestAdapter(analytics_client=analytics, quest_generator=q_gen)

    server_id_example = "server789"
    user_id_example = "user_alpha"

    print(f"--- Generating adapted quest for User: {user_id_example} on Server: {server_id_example} ---")
    # Simulate a few times to see variation from mock analytics
    for i in range(3):
        print(f"\nAttempt {i+1}:")
        adapted_quest = adapter.generate_adapted_quest(server_id_example, user_id_example)
        if adapted_quest:
            print(f"Generated Quest: {adapted_quest['description']}")
            print(f"Type: {adapted_quest['type']}, Topic: {adapted_quest.get('custom_topic')}, Season: {adapted_quest.get('season')}")
        else:
            print("Failed to generate an adapted quest.")
        time.sleep(0.1) # To ensure random choices might differ if based on time (not strictly necessary here)

    print(f"\n--- Testing with another user (potential for different difficulty via QuestGenerator) ---")
    user_id_example_2 = "user_beta" # Beginner
    adapted_quest_beginner = adapter.generate_adapted_quest(server_id_example, user_id_example_2)
    if adapted_quest_beginner:
        print(f"Generated Quest for {user_id_example_2}: {adapted_quest_beginner['description']}")
    else:
        print(f"Failed to generate an adapted quest for {user_id_example_2}.")
