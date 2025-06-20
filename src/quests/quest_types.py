# src/quests/quest_types.py

from enum import Enum

class QuestCategory(Enum):
    SOCIAL = "Social Quests"
    KNOWLEDGE = "Knowledge Quests"
    CREATIVE = "Creative Quests"
    COMMUNITY = "Community Quests"
    LEADERSHIP = "Leadership Quests"

# Quest templates can be more detailed and structured
# For example, they could include not just a format string,
# but also information about how to verify completion,
# default difficulty, or specific parameters they expect.

QUEST_TEMPLATES = {
    QuestCategory.SOCIAL: {
        "description_template": "Welcome {count} new members warmly to the server.",
        "default_target_metric": "new_member_welcomes",
        "example_llm_prompt_modifier": "Focus on genuine and helpful first interactions."
    },
    QuestCategory.KNOWLEDGE: {
        "description_template": "Answer {count} questions accurately in the #{channel} channel.",
        "default_target_metric": "questions_answered",
        "example_llm_prompt_modifier": "Emphasize quality and verifiable answers."
    },
    QuestCategory.CREATIVE: {
        "description_template": "Share {count} original {content_type} in the #{channel} channel.",
        "default_target_metric": "original_content_shared",
        "example_llm_prompt_modifier": "Encourage unique and high-effort contributions."
    },
    QuestCategory.COMMUNITY: {
        "description_template": "Organize or actively participate in a discussion about '{topic}' in #{channel}.",
        "default_target_metric": "discussions_organized_or_participated",
        "example_llm_prompt_modifier": "Promote constructive dialogue and diverse viewpoints."
    },
    QuestCategory.LEADERSHIP: {
        "description_template": "Help moderate discussions fairly in #{channel} for {duration}.", # Or "mediate {count} disagreements"
        "default_target_metric": "moderation_actions_or_time",
        "example_llm_prompt_modifier": "Highlight impartiality, de-escalation, and community guideline enforcement."
    }
}

# Example of how these might be used or extended:
# - Different variations within a category
# - Parameters for LLM generation, like keywords, tone, complexity
# - Link to specific verification logic or metrics

def get_template_for_category(category: QuestCategory) -> dict:
    """
    Retrieves the template for a given quest category.

    Args:
        category: The QuestCategory enum member.

    Returns:
        The quest template dictionary for that category.
    """
    return QUEST_TEMPLATES.get(category, {})

if __name__ == "__main__":
    # Example usage
    social_template = get_template_for_category(QuestCategory.SOCIAL)
    print(f"Social Quest Template: {social_template}")

    knowledge_template = get_template_for_category(QuestCategory.KNOWLEDGE)
    # Example of filling a template (simplified)
    filled_knowledge_quest = knowledge_template["description_template"].format(count=5, channel="help")
    print(f"Filled Knowledge Quest Example: {filled_knowledge_quest}")

    creative_template = get_template_for_category(QuestCategory.CREATIVE)
    filled_creative_quest = creative_template["description_template"].format(count=1, content_type="artwork", channel="showcase")
    print(f"Filled Creative Quest Example: {filled_creative_quest}")

    community_template = get_template_for_category(QuestCategory.COMMUNITY)
    filled_community_quest = community_template["description_template"].format(topic="Sustainable Living", channel="general-chat")
    print(f"Filled Community Quest Example: {filled_community_quest}")

    leadership_template = get_template_for_category(QuestCategory.LEADERSHIP)
    filled_leadership_quest = leadership_template["description_template"].format(channel="town-hall", duration="one week")
    print(f"Filled Leadership Quest Example: {filled_leadership_quest}")
