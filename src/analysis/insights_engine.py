# src/analysis/insights_engine.py
from collections import Counter

# Assuming SentimentAnalyzer and TopicModeler might be used by InsightsEngine in a more advanced version.
# For now, their full import isn't strictly necessary for these placeholders.
# from .sentiment_analyzer import SentimentAnalyzer
# from .topic_modeler import TopicModeler

class InsightsEngine:
    def __init__(self, llm_provider=None, sentiment_analyzer=None, topic_modeler=None):
        """
        Initializes the InsightsEngine.

        Args:
            llm_provider: An optional LLM provider for advanced insights.
            sentiment_analyzer: An instance of SentimentAnalyzer.
            topic_modeler: An instance of TopicModeler.
        """
        self.llm_provider = llm_provider
        self.sentiment_analyzer = sentiment_analyzer
        self.topic_modeler = topic_modeler

    def identify_key_participants(self, conversation: list[tuple[str, str]], top_n: int = 3) -> list[tuple[str, int]]:
        """
        Identifies key participants in a conversation based on message count.
        Placeholder implementation.

        Args:
            conversation: A list of tuples, where each tuple is (user_id, message_text).
                          Example: [("user1", "Hello!"), ("user2", "Hi there!"), ("user1", "How are you?")]
            top_n: The number of top participants to return.

        Returns:
            A list of tuples, each containing a user_id and their message count, sorted by count.
            Example: [("user1", 2), ("user2", 1)]
        """
        if not conversation:
            return []

        participant_messages = Counter()
        for user_id, message_text in conversation:
            participant_messages[user_id] += 1

        key_participants = participant_messages.most_common(top_n)
        return key_participants

    def score_conversation_quality(self, conversation_messages: list[str], participants: int) -> dict:
        """
        Scores the quality of a conversation.
        Placeholder: Basic score based on length, participants, and simple sentiment.

        Args:
            conversation_messages: A list of message texts.
            participants: Number of unique participants in the conversation.

        Returns:
            A dictionary containing quality metrics.
            Example: {"engagement_score": 0.7, "information_density": 0.5, "overall_quality": "medium"}
        """
        if not conversation_messages:
            return {"engagement_score": 0.0, "information_density": 0.0, "sentiment_score":0.0, "overall_quality": "low"}

        # Engagement: more messages and participants might mean higher engagement
        engagement_score = min(1.0, (len(conversation_messages) / 20.0) * (participants / 5.0)) # Max score at 20 msgs, 5 ppl

        # Information density: longer messages might imply more info (very rough)
        avg_msg_length = sum(len(msg) for msg in conversation_messages) / len(conversation_messages)
        information_density = min(1.0, avg_msg_length / 100.0) # Max score at 100 chars avg length

        # Simplified sentiment (if analyzer is available, otherwise neutral)
        sentiment_score_value = 0.0
        if self.sentiment_analyzer:
            mood = self.sentiment_analyzer.track_conversation_mood(conversation_messages)
            if mood == "positive": sentiment_score_value = 0.5
            elif mood == "negative": sentiment_score_value = -0.5

        # Overall quality (simple average for placeholder)
        overall_score = (engagement_score + information_density + (sentiment_score_value + 1)/2) / 3 # Normalize sentiment to 0-1

        if overall_score > 0.7:
            quality_label = "high"
        elif overall_score > 0.4:
            quality_label = "medium"
        else:
            quality_label = "low"

        return {
            "engagement_score": round(engagement_score, 2),
            "information_density": round(information_density, 2),
            "sentiment_score": round(sentiment_score_value,2),
            "overall_quality_numeric": round(overall_score,2),
            "overall_quality": quality_label
        }

    def detect_knowledge_gaps(self, conversation_messages: list[str]) -> list[str]:
        """
        Detects potential knowledge gaps based on questions asked.
        Placeholder: Looks for messages with question marks or "how to".

        Args:
            conversation_messages: A list of message texts.

        Returns:
            A list of messages that might indicate knowledge gaps.
        """
        potential_gaps = []
        for msg in conversation_messages:
            if "?" in msg or "how do i" in msg.lower() or "what is" in msg.lower() or "explain" in msg.lower():
                potential_gaps.append(msg[:100]) # Add snippet of the message

        return potential_gaps

    def map_community_expertise(self, user_conversations: dict[str, list[list[str]]]) -> dict[str, list[str]]:
        """
        Maps community expertise based on topics users discuss.
        Placeholder: Associates users with topics they've talked about.
        Requires TopicModeler.

        Args:
            user_conversations: A dictionary where keys are user_ids and values are lists
                                of conversations (each conversation being a list of messages)
                                that the user participated in.
                                Example: {"user1": [["fire topic msg", "another fire msg"], ["gameplay q"]]}
        Returns:
            A dictionary mapping user_ids to a list of topics they are associated with.
            Example: {"user1": ["firefighting_tactics", "user_questions"]}
        """
        if not self.topic_modeler:
            return {"error": "TopicModeler not available for expertise mapping."}

        expertise_map = {}
        for user_id, conversations in user_conversations.items():
            user_topics = []
            for convo in conversations:
                user_topics.extend(self.topic_modeler.extract_topics(convo))
            expertise_map[user_id] = list(set(user_topics)) # Unique topics per user

        return expertise_map

if __name__ == '__main__':
    # Example Usage (for testing purposes)

    # Dummy TopicModeler and SentimentAnalyzer for testing InsightsEngine in isolation
    class DummySentimentAnalyzer:
        def track_conversation_mood(self, messages): return "neutral" if len(messages) < 2 else "positive"
    class DummyTopicModeler:
        def extract_topics(self, conversation):
            if "fire" in " ".join(conversation): return ["fire_tactics"]
            if "bug" in " ".join(conversation): return ["bug_reports"]
            return ["general_chat"]

    engine = InsightsEngine(sentiment_analyzer=DummySentimentAnalyzer(), topic_modeler=DummyTopicModeler())

    convo_data = [
        ("userA", "Hello, this is about fire management."),
        ("userB", "I have a question: how do I use the water tanker?"),
        ("userA", "You need to select it and target the fire."),
        ("userC", "I found a bug with the tanker selection!"),
        ("userA", "Thanks for the report userC. We will look into the fire bug.")
    ]
    messages_only = [msg for _, msg in convo_data]

    # Test key participant identification
    key_participants = engine.identify_key_participants(convo_data)
    print(f"Key participants: {key_participants}")

    # Test conversation quality scoring
    quality = engine.score_conversation_quality(messages_only, len(set(u for u,m in convo_data)))
    print(f"Conversation quality: {quality}")

    # Test knowledge gap detection
    gaps = engine.detect_knowledge_gaps(messages_only)
    print(f"Potential knowledge gaps (questions): {gaps}")

    # Test community expertise mapping
    user_convos_data = {
        "userA": [["Fire is spreading!", "Need containment."], ["Another fire question."]],
        "userB": [["How to use tankers?"], ["Is this a bug or a feature?"]],
        "userC": [["Bug report: tanker selection broken."]]
    }
    expertise = engine.map_community_expertise(user_convos_data)
    print(f"Community expertise map: {expertise}")
