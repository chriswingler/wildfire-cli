# src/analysis/topic_modeler.py
from collections import Counter

class TopicModeler:
    def __init__(self, llm_provider=None):
        """
        Initializes the TopicModeler.

        Args:
            llm_provider: An optional LLM provider for more advanced topic modeling.
        """
        self.llm_provider = llm_provider

    def extract_topics(self, conversation: list[str]) -> list[str]:
        """
        Extracts topics from a single conversation.
        Placeholder implementation using simple keyword spotting.

        Args:
            conversation: A list of message texts.

        Returns:
            A list of identified topics. Example: ["firefighting", "game_mechanics"]
        """
        if not conversation:
            return []

        # Simple keyword spotting for placeholder
        text = " ".join(conversation).lower()
        topics = []
        if "fire" in text or "flames" in text or "containment" in text:
            topics.append("firefighting_tactics")
        if "team" in text or "players" in text or "multiplayer" in text:
            topics.append("team_coordination")
        if "bug" in text or "issue" in text or "fix" in text:
            topics.append("bug_reports")
        if "feature" in text or "idea" in text or "suggestion" in text:
            topics.append("feature_requests")
        if "help" in text or "question" in text or "how to" in text:
            topics.append("user_questions")

        return list(set(topics)) # Return unique topics

    def identify_trending_discussions(self, conversations: list[list[str]], top_n: int = 3) -> list[tuple[str, int]]:
        """
        Identifies trending discussion topics from multiple conversations.
        Placeholder implementation.

        Args:
            conversations: A list of conversations, where each is a list of messages.
            top_n: The number of top trending topics to return.

        Returns:
            A list of tuples, each containing a topic and its frequency, sorted by frequency.
            Example: [("firefighting_tactics", 10), ("bug_reports", 5)]
        """
        if not conversations:
            return []

        all_topics = []
        for convo in conversations:
            all_topics.extend(self.extract_topics(convo))

        topic_counts = Counter(all_topics)
        trending = topic_counts.most_common(top_n)

        return trending

    def track_topic_evolution(self, conversations_over_time: list[tuple[str, list[str]]]) -> dict:
        """
        Tracks how topics evolve over time.
        Placeholder: For now, just show topics per time period.
        A real implementation would compare topic distributions across periods.

        Args:
            conversations_over_time: A list of tuples, where each tuple is (timestamp/period_name, conversation_messages).
                                     Example: [("2023-01-01", ["msg1", "msg2"]), ("2023-01-02", ["msg3"])]

        Returns:
            A dictionary mapping time periods to their identified topics.
            Example: {"2023-01-01": ["topic_A"], "2023-01-02": ["topic_B"]}
        """
        evolution = {}
        for period_name, convo_messages in conversations_over_time:
            topics = self.extract_topics(convo_messages)
            if period_name not in evolution:
                evolution[period_name] = []
            evolution[period_name].extend(topics)
            evolution[period_name] = list(set(evolution[period_name])) # Unique topics per period

        return evolution

    def analyze_cross_channel_topics(self, channel_conversations: dict[str, list[list[str]]]) -> dict:
        """
        Analyzes and correlates topics across different channels.
        Placeholder: For now, just lists topics per channel and common topics.

        Args:
            channel_conversations: A dictionary where keys are channel names and
                                   values are lists of conversations in that channel.
                                   Example: {"general": [[msg1, msg2]], "feedback": [[msg3]]}
        Returns:
            A dictionary summarizing topics per channel and common topics.
        """
        channel_topic_summary = {}
        all_topics_across_channels = []

        for channel_name, conversations in channel_conversations.items():
            channel_topics = []
            for convo in conversations:
                channel_topics.extend(self.extract_topics(convo))

            unique_channel_topics = list(set(channel_topics))
            channel_topic_summary[channel_name] = {
                "topics": unique_channel_topics,
                "topic_counts": Counter(channel_topics).most_common(5) # Top 5 topics for the channel
            }
            all_topics_across_channels.extend(unique_channel_topics)

        # Identify common topics across all channels
        if not all_topics_across_channels:
             common_topics = []
        else:
            topic_counts = Counter(all_topics_across_channels)
            # Common topics are those appearing in more than one channel (or a certain percentage)
            # Simplified: topics appearing in at least 2 channels, or top N overall
            common_topics = [topic for topic, count in topic_counts.items() if count >= min(2, len(channel_conversations))]
            if not common_topics and all_topics_across_channels: # if no topic in >=2 channels, take overall most common
                common_topics = [topic_counts.most_common(1)[0][0]] if topic_counts else []


        return {
            "per_channel_summary": channel_topic_summary,
            "common_topics_across_channels": common_topics
        }

if __name__ == '__main__':
    # Example Usage (for testing purposes)
    modeler = TopicModeler()

    convo1 = ["The fire is spreading fast!", "We need more units for containment."]
    convo2 = ["I found a bug when using the helicopter.", "Can someone fix this issue?"]
    convo3 = ["Maybe we can add a new type of water tanker? It's a feature suggestion."]
    convo4 = ["How do I deploy troops effectively?", "I have a question about game mechanics."]

    # Test topic extraction
    print(f"Topics for convo1: {modeler.extract_topics(convo1)}")
    print(f"Topics for convo2: {modeler.extract_topics(convo2)}")

    # Test trending discussions
    all_conversations = [convo1, convo1, convo2, convo3, convo4, convo4, convo4]
    trending = modeler.identify_trending_discussions(all_conversations, top_n=2)
    print(f"Trending discussions: {trending}")

    # Test topic evolution
    conversations_by_day = [
        ("Day1", ["Fire is the main topic today.", "Lots of talk about tactics."]),
        ("Day2", ["Bugs are being reported now.", "Also some feature ideas."]),
        ("Day3", ["More feature requests and questions about how to play."])
    ]
    evolution = modeler.track_topic_evolution(conversations_by_day)
    print(f"Topic evolution: {evolution}")

    # Test cross-channel topic analysis
    channel_data = {
        "general_chat": [convo1, convo4, ["Just chatting about the game."]],
        "bug_reports": [convo2, ["Another bug with the UI."]],
        "feature_ideas": [convo3, ["New map idea."]]
    }
    cross_channel_analysis = modeler.analyze_cross_channel_topics(channel_data)
    print(f"Cross-channel analysis: {cross_channel_analysis}")
