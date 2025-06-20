# src/quests/quest_generator.py

import random

# TODO: Integrate with actual LLM provider
class LLMProvider:
    def generate_quest_text(self, prompt: str) -> str:
        # This is a placeholder for LLM integration
        # In a real scenario, this would call an LLM API
        return f"Generated quest text based on prompt: {prompt}"

class QuestGenerator:
    def __init__(self, llm_provider: LLMProvider, community_health_data: dict, user_levels: dict):
        self.llm_provider = llm_provider
        self.community_health_data = community_health_data # e.g., {"engagement": "high", "needs": ["more help channel activity"]}
        self.user_levels = user_levels # e.g., {"user_id_1": "intermediate", "user_id_2": "beginner"}
        self.quest_templates = {
            "social": "Welcome {count} new members warmly to the server.",
            "knowledge": "Answer {count} questions in the #help channel.",
            "creative": "Share {count} original content piece(s) in #showcase.",
            "community": "Organize a discussion on {topic}.",
            "leadership": "Help moderate discussions fairly for {duration}."
        }
        self.seasonal_themes = {
            "summer": "Summer Festival Challenge: ",
            "winter": "Winter Wonderland Quest: "
        }

    def _get_difficulty_params(self, user_id: str) -> dict:
        level = self.user_levels.get(user_id, "beginner")
        if level == "advanced":
            return {"count_min": 5, "count_max": 10, "duration": "7 days"}
        elif level == "intermediate":
            return {"count_min": 3, "count_max": 5, "duration": "3-5 days"}
        else: # beginner
            return {"count_min": 1, "count_max": 3, "duration": "1-2 days"}

    def _adapt_quest_to_community_health(self, base_prompt: str) -> str:
        # Example: Modify prompt based on community needs
        needs = self.community_health_data.get("needs", [])
        if "more help channel activity" in needs:
            base_prompt += " Focus on encouraging help channel participation."
        # Add more adaptation logic based on community_health_data
        return base_prompt

    def _apply_seasonal_theme(self, quest_text: str, season: str = None) -> str:
        if season and season in self.seasonal_themes:
            return self.seasonal_themes[season] + quest_text
        return quest_text

    def create_quest(self, user_id: str, quest_type: str, custom_topic: str = None, season: str = None) -> dict:
        if quest_type not in self.quest_templates:
            raise ValueError(f"Invalid quest type: {quest_type}")

        difficulty_params = self._get_difficulty_params(user_id)

        # Basic template filling
        template = self.quest_templates[quest_type]
        quest_text_base = ""
        if "{count}" in template:
            count = random.randint(difficulty_params["count_min"], difficulty_params["count_max"])
            quest_text_base = template.format(count=count)
        elif "{topic}" in template:
            topic = custom_topic or "a relevant community topic"
            quest_text_base = template.format(topic=topic)
        elif "{duration}" in template:
            quest_text_base = template.format(duration=difficulty_params["duration"])
        else:
            quest_text_base = template

        # LLM prompt construction
        llm_prompt = f"Generate an engaging quest for a Discord community. User level: {self.user_levels.get(user_id, 'unknown')}. Quest type: {quest_type}. Base idea: {quest_text_base}."

        # Adapt prompt based on community health
        llm_prompt = self._adapt_quest_to_community_health(llm_prompt)

        # Generate quest text using LLM (placeholder)
        # In a real scenario, the LLM would refine or generate the quest based on the complex prompt
        generated_text = self.llm_provider.generate_quest_text(llm_prompt)

        # For now, we use a simpler combination due to placeholder LLM
        # This part would be more sophisticated with a real LLM
        final_quest_text = quest_text_base # Default to template if LLM is basic
        if "Generated quest text based on prompt" in generated_text: # Check if LLM provided something beyond simple echo
             # This is a mock-up of how an LLM might refine it.
             # A real LLM could provide a fully formed quest description.
            refined_description = f"{quest_text_base}. The LLM suggests focusing on: {llm_prompt.split('Base idea:')[0].strip()}"
            final_quest_text = refined_description


        # Apply seasonal theme
        final_quest_text = self._apply_seasonal_theme(final_quest_text, season)

        quest_id = f"quest_{random.randint(1000, 9999)}"

        # Multi-step quest progression tracking (basic example)
        # A real system would have more complex state and step definitions
        steps = [{"description": "Complete the main objective.", "completed": False}]
        if quest_type == "social": # For social quests, we attempt to make them multi-step by count
            # 'count' for steps is determined here, separate from description count
            step_count = random.randint(difficulty_params["count_min"], difficulty_params["count_max"])
            if step_count > 0:
                steps = [{"description": f"Welcome member {i+1}/{step_count}.", "completed": False} for i in range(step_count)]
                final_quest_text = f"{final_quest_text} (This is a multi-step quest)."
            else: # Fallback if step_count is 0, provide a single generic social step
                steps = [{"description": "Engage in general social activities on the server.", "completed": False}]
                # Optionally, modify final_quest_text to reflect it's not the typical multi-step welcome quest
                final_quest_text = f"{final_quest_text} (Objective: General social engagement)."


        return {
            "quest_id": quest_id,
            "user_id": user_id,
            "type": quest_type,
            "description": final_quest_text,
            "difficulty_params": difficulty_params,
            "status": "active",
            "progress": 0, # e.g., 0 out of 'count' for social quests
            "steps": steps, # For multi-step quests
            "llm_prompt_used": llm_prompt # For debugging/logging
        }

# Example Usage (for testing purposes, not part of the final file usually)
if __name__ == "__main__":
    # Placeholder data for testing
    mock_llm = LLMProvider()
    mock_community_health = {"engagement": "medium", "needs": ["more help channel activity", "content creation"]}
    mock_user_levels = {"user123": "intermediate", "user456": "beginner", "user789": "advanced"}

    generator = QuestGenerator(llm_provider=mock_llm, community_health_data=mock_community_health, user_levels=mock_user_levels)

    # Test social quest for an intermediate user
    social_quest = generator.create_quest(user_id="user123", quest_type="social", season="summer")
    print("Social Quest:", social_quest)

    # Test knowledge quest for a beginner user
    knowledge_quest = generator.create_quest(user_id="user456", quest_type="knowledge")
    print("\nKnowledge Quest:", knowledge_quest)

    # Test creative quest for an advanced user with a winter theme
    creative_quest = generator.create_quest(user_id="user789", quest_type="creative", season="winter")
    print("\nCreative Quest:", creative_quest)

    # Test community quest
    community_quest = generator.create_quest(user_id="user123", quest_type="community", custom_topic="AI in game development")
    print("\nCommunity Quest:", community_quest)

    # Test leadership quest
    leadership_quest = generator.create_quest(user_id="user789", quest_type="leadership")
    print("\nLeadership Quest:", leadership_quest)

    # Test quest adaptation (e.g. if help channel activity is needed)
    # The LLM prompt should reflect this need.
    # In a real system, the generated_text would be more directly influenced.
    # For now, we check the llm_prompt_used field.
    print(f"\nLLM prompt for knowledge quest included: {knowledge_quest['llm_prompt_used']}")

    # Test multi-step (basic example for social quest)
    if social_quest['steps'] and len(social_quest['steps']) > 1:
        print(f"\nSocial quest is multi-step with {len(social_quest['steps'])} steps.")
        print(f"First step: {social_quest['steps'][0]['description']}")
