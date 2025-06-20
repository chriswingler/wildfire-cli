import openai # Using the openai library for DeepSeek
import json # For parsing JSON in analyze method

from src.llm.providers import LLMProvider, LLMProviderError, RateLimitError, APIError

import logging
logger = logging.getLogger(__name__)

class DeepSeekProvider(LLMProvider):
    """
    LLMProvider implementation for DeepSeek models using the OpenAI-compatible API.
    """

    DEFAULT_MODEL_NAME = "deepseek-chat"
    DEFAULT_BASE_URL = "https://api.deepseek.com/v1"

    def __init__(self, config: dict):
        """
        Initializes the DeepSeekProvider.

        Args:
            config: A dictionary containing configuration parameters.
                    Expected keys:
                        - 'api_key': DeepSeek API key.
                        - 'model_name' (optional): The DeepSeek model to use (e.g., "deepseek-chat").
                                                   Defaults to "deepseek-chat".
                        - 'base_url' (optional): The base URL for the DeepSeek API.
                                                 Defaults to "https://api.deepseek.com/v1".
        """
        super().__init__(config)
        if not self.config.get('api_key'):
            raise LLMProviderError("DeepSeek API key not found in config.")

        self.api_key = self.config['api_key']
        self.base_url = self.config.get("base_url", self.DEFAULT_BASE_URL)
        self.model_name = self.config.get("model_name", self.DEFAULT_MODEL_NAME)

        self.client = openai.AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    async def query(self, prompt: str, **kwargs) -> str:
        """
        Sends a query to the DeepSeek LLM and returns the response.

        Args:
            prompt: The prompt to send to the LLM.
            **kwargs: Additional keyword arguments for the OpenAI API's chat completions.
                      (e.g., 'temperature', 'max_tokens', 'top_p').

        Returns:
            The LLM's response text content.

        Raises:
            RateLimitError: If the API rate limit is exceeded.
            APIError: For other API-related errors.
            LLMProviderError: For general errors during the query.
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            if response.choices and response.choices[0].message and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
            else:
                raise LLMProviderError("DeepSeek API returned an empty or unexpected response structure.")
        except openai.RateLimitError as e:
            raise RateLimitError(f"DeepSeek API rate limit exceeded: {e}") from e
        except openai.APIConnectionError as e:
            raise APIError(f"DeepSeek API connection error: {e}") from e
        except openai.APIStatusError as e:
            raise APIError(f"DeepSeek API status error: {e.status_code} - {e.message}") from e
        except openai.APIError as e: # Catch-all for other OpenAI/DeepSeek errors
            raise APIError(f"DeepSeek API error: {e}") from e
        except Exception as e:
            raise LLMProviderError(f"An unexpected error occurred during query: {e}") from e

    async def analyze(self, text: str, **kwargs) -> dict:
        """
        Analyzes the given text using the DeepSeek LLM by asking for JSON output.

        Args:
            text: The text to analyze.
            **kwargs: Additional keyword arguments for the query.
                      'analysis_prompt' (optional): A specific prompt for analysis.
                                                     Defaults to asking for sentiment and keywords.

        Returns:
            A dictionary containing the analysis results (parsed JSON if successful)
            or a raw response if JSON parsing fails.

        Raises:
            RateLimitError, APIError, LLMProviderError from the underlying query.
        """
        default_analysis_prompt = (
            f"Analyze the following text and return a JSON object with keys 'sentiment' (string, e.g., positive, negative, neutral) "
            f"and 'keywords' (list of strings, e.g., [\"keyword1\", \"keyword2\"]):\n\nText: \"{text}\""
            f"\n\nReturn ONLY the JSON object."
        )
        analysis_prompt = kwargs.pop('analysis_prompt', default_analysis_prompt)

        try:
            response_str = await self.query(analysis_prompt, **kwargs)
            try:
                # DeepSeek might sometimes return responses wrapped in ```json ... ```
                if response_str.startswith("```json"):
                    response_str = response_str.split("```json", 1)[1].rsplit("```", 1)[0].strip()
                elif response_str.startswith("```"): # A more generic ``` block
                    response_str = response_str.split("```", 1)[1].rsplit("```", 1)[0].strip()

                analysis_result = json.loads(response_str)
                return analysis_result
            except json.JSONDecodeError:
                logger.warning(f"DeepSeek 'analyze' method did not return valid JSON. Response: {response_str}")
                return {"raw_analysis": response_str}
        except (RateLimitError, APIError, LLMProviderError) as e:
            raise e # Re-raise errors from query
        except Exception as e:
            raise LLMProviderError(f"An unexpected error occurred during analysis: {e}") from e

    async def summarize(self, text: str, **kwargs) -> str:
        """
        Summarizes the given text using the DeepSeek LLM.

        Args:
            text: The text to summarize.
            **kwargs: Additional keyword arguments for the summarization query.

        Returns:
            The summarized text as a string.

        Raises:
            RateLimitError, APIError, LLMProviderError from the underlying query.
        """
        prompt = f"Summarize the following text concisely:\n\n\"{text}\""
        if 'max_length' in kwargs:
            prompt += f"\nEnsure the summary is approximately no more than {kwargs['max_length']} words."

        try:
            summary = await self.query(prompt, **kwargs)
            return summary
        except (RateLimitError, APIError, LLMProviderError) as e:
            raise e # Re-raise errors from query
        except Exception as e:
            raise LLMProviderError(f"An unexpected error occurred during summarization: {e}") from e
