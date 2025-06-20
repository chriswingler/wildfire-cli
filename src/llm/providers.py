import abc

class LLMProviderError(Exception):
    """Base exception class for LLM provider errors."""
    pass

class RateLimitError(LLMProviderError):
    """Exception raised for rate limiting errors."""
    pass

class APIError(LLMProviderError):
    """Exception raised for API errors."""
    pass

class LLMProvider(abc.ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: dict):
        """
        Initializes the LLMProvider.

        Args:
            config: A dictionary containing configuration parameters
                    such as API keys and model settings.
        """
        self.config = config

    @abc.abstractmethod
    async def query(self, prompt: str, **kwargs) -> str:
        """
        Sends a query to the LLM and returns the response.

        Args:
            prompt: The prompt to send to the LLM.
            **kwargs: Additional keyword arguments for the LLM provider.

        Returns:
            The LLM's response as a string.
        """
        pass

    @abc.abstractmethod
    async def analyze(self, text: str, **kwargs) -> dict:
        """
        Analyzes the given text using the LLM.

        Args:
            text: The text to analyze.
            **kwargs: Additional keyword arguments for the LLM provider.

        Returns:
            A dictionary containing the analysis results.
        """
        pass

    @abc.abstractmethod
    async def summarize(self, text: str, **kwargs) -> str:
        """
        Summarizes the given text using the LLM.

        Args:
            text: The text to summarize.
            **kwargs: Additional keyword arguments for the LLM provider.

        Returns:
            The summarized text as a string.
        """
        pass
