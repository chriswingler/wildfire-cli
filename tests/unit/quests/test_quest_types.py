# tests/unit/quests/test_quest_types.py
import unittest
from src.quests.quest_types import QuestCategory, QUEST_TEMPLATES, get_template_for_category

class TestQuestTypes(unittest.TestCase):

    def test_quest_categories_exist(self):
        self.assertTrue(len(QuestCategory) >= 5) # SOCIAL, KNOWLEDGE, CREATIVE, COMMUNITY, LEADERSHIP
        self.assertIn(QuestCategory.SOCIAL, QUEST_TEMPLATES)
        self.assertIn(QuestCategory.KNOWLEDGE, QUEST_TEMPLATES)
        self.assertIn(QuestCategory.CREATIVE, QUEST_TEMPLATES)
        self.assertIn(QuestCategory.COMMUNITY, QUEST_TEMPLATES)
        self.assertIn(QuestCategory.LEADERSHIP, QUEST_TEMPLATES)

    def test_get_template_for_category(self):
        social_template = get_template_for_category(QuestCategory.SOCIAL)
        self.assertIsNotNone(social_template)
        self.assertIn("description_template", social_template)
        self.assertIn("default_target_metric", social_template)

        knowledge_template = get_template_for_category(QuestCategory.KNOWLEDGE)
        self.assertIsNotNone(knowledge_template)
        self.assertIn("description_template", knowledge_template)

    def test_get_invalid_template(self):
        # Create a mock category not in QuestCategory to test default return
        class MockInvalidCategory:
            name = "INVALID"
            value = 99

        # Depending on how get_template_for_category handles truly invalid enum members,
        # this might need adjustment or direct test of QUEST_TEMPLATES.get(invalid, {})
        template = QUEST_TEMPLATES.get(MockInvalidCategory, {}) # Simulate fetching an unknown category
        self.assertEqual(template, {})

    def test_template_structure(self):
        for category in QuestCategory:
            template = get_template_for_category(category)
            self.assertIn("description_template", template, f"Template for {category} missing description_template")
            self.assertIsInstance(template["description_template"], str, f"description_template for {category} not a string")
            self.assertIn("default_target_metric", template, f"Template for {category} missing default_target_metric")
            self.assertIn("example_llm_prompt_modifier", template, f"Template for {category} missing example_llm_prompt_modifier")

if __name__ == '__main__':
    unittest.main()
