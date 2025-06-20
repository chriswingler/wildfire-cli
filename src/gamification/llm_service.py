"""
This module defines a placeholder LLMService for simulating LLM API interactions.
"""
import random
import re
import asyncio # For potential async sleep if simulating network latency

class LLMService:
    """
    A placeholder service to simulate interactions with a Language Model API.
    This service provides dummy analysis based on simple rules and random values.
    """
    def __init__(self, api_key: str = None):
        """
        Initializes the LLMService.

        Args:
            api_key: A placeholder for an LLM API key.
        """
        self.api_key = api_key
        if self.api_key and self.api_key.startswith("DUMMY"):
            print(f"LLMService initialized with a DUMMY API key: {self.api_key}")
        elif self.api_key:
            print("LLMService initialized with an API key.") # Avoid printing the actual key
        else:
            print("LLMService initialized WITHOUT an API key (placeholder mode).")

    async def analyze_message_content(self, message_content: str, analysis_types: list[str]) -> dict:
        """
        Simulates an LLM call to analyze message content based on requested types.

        Args:
            message_content: The text content of the message to analyze.
            analysis_types: A list of strings indicating the types of analysis requested
                              (e.g., "helpfulness", "sentiment", "spam").

        Returns:
            A dictionary containing the simulated LLM analysis results.
        """
        # Simulate network latency if desired
        # await asyncio.sleep(random.uniform(0.1, 0.3))

        simulated_response = {}
        message_lower = message_content.lower()

        if "helpfulness" in analysis_types:
            if re.search(r'\b(help|assist|guide|explain|question|how to|why does)\b', message_lower, re.IGNORECASE):
                simulated_response['helpfulness_score'] = random.uniform(0.5, 0.95)
            elif len(message_content.split()) > 8: # Longer messages might be more helpful
                simulated_response['helpfulness_score'] = random.uniform(0.3, 0.7)
            else:
                simulated_response['helpfulness_score'] = random.uniform(0.0, 0.4)

        if "problem_solving" in analysis_types:
            is_solution_related = bool(re.search(r'\b(solution|solved|fixed|issue|problem|error|bug)\b', message_lower, re.IGNORECASE))
            simulated_response['is_problem_solution'] = is_solution_related and random.random() > 0.3

        if "quality" in analysis_types:
            # Base quality on length, presence of questions/exclamations, word variety
            length_score = min(1.0, len(message_content) / 150.0)
            punctuation_score = 0.1 if '?' in message_content or '!' in message_content else 0.0
            word_variety_score = min(1.0, len(set(message_lower.split())) / (len(message_lower.split()) + 1e-5))

            base_quality = (length_score * 0.5) + (punctuation_score * 0.2) + (word_variety_score * 0.3)
            simulated_response['quality_score'] = min(1.0, base_quality * random.uniform(0.7, 1.3))


        if "sentiment" in analysis_types:
            positive_words = ['thanks', 'great', 'good', 'awesome', 'love', 'excellent', 'helpful', 'nice']
            negative_words = ['stupid', 'bad', 'hate', 'terrible', 'awful', 'problem', 'error']
            sentiment = 0.0
            words = message_lower.split()
            for word in positive_words:
                if word in words:
                    sentiment += 0.25
            for word in negative_words:
                if word in words:
                    sentiment -= 0.35
            # Add some randomness and clamp
            sentiment += random.uniform(-0.1, 0.1)
            simulated_response['sentiment_score'] = max(-1.0, min(1.0, sentiment))

        if "spam" in analysis_types:
            spam_keywords = ['buy now', 'free money', 'subscribe click', 'limited time offer', 'win prize']
            is_spam = False
            for keyword in spam_keywords:
                if keyword in message_lower:
                    is_spam = True
                    break
            simulated_response['is_spam'] = is_spam

        if "keywords" in analysis_types:
            # Extract words that are 4+ chars long, not common short words.
            words = re.findall(r'\b([a-zA-Z]{4,})\b', message_lower)
            # A very simple stopword list
            stopwords = set(["this", "that", "with", "your", "then", "what", "they", "them", "will", "have", "from", "does", "like", "just", "about"])
            filtered_keywords = [word for word in words if word not in stopwords]
            simulated_response['identified_keywords'] = list(set(filtered_keywords))[:5] # Top 5 unique keywords

        if "topic" in analysis_types:
            if re.search(r'\b(question|help|how to|why)\b', message_lower):
                simulated_response['primary_topic'] = "technical question"
            elif re.search(r'\b(idea|suggest|feature|improve)\b', message_lower):
                simulated_response['primary_topic'] = "feedback"
            elif len(message_content.split()) < 5 :
                 simulated_response['primary_topic'] = "chitchat"
            else:
                simulated_response['primary_topic'] = random.choice(["general query", "discussion point", "off-topic"])

        print(f"LLMService simulated response for '{message_content[:30]}...': {simulated_response}")
        return simulated_response
