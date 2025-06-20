import google.generativeai as genai
from google.api_core import exceptions as google_exceptions # For error handling

from src.llm.providers import LLMProvider, LLMProviderError, RateLimitError, APIError

# It's good practice to define a logger for warnings or errors.
import logging
logger = logging.getLogger(__name__)

class GeminiProvider(LLMProvider):
    """
    LLMProvider implementation for Google's Gemini models.
    """

    # Default token limit approximation. Real tokenization is more complex.
    # Gemini 1.5 Pro has 1M tokens, Flash has 1M.
    # This is more of a character limit for a simple check.
    # Actual token counting would require a tokenizer.
    DEFAULT_MAX_INPUT_CHARS = 1000000


    def __init__(self, config: dict):
        """
        Initializes the GeminiProvider.

        Args:
            config: A dictionary containing configuration parameters.
                    Expected keys:
                        - 'api_key': Google Generative AI API key.
                        - 'model_name': The Gemini model to use (e.g., "gemini-1.5-pro-latest").
                        - 'max_input_chars' (optional): Approximate max characters for input text
                                                       to prevent overly large requests.
        """
        super().__init__(config)
        if not self.config.get('api_key'):
            raise LLMProviderError("Google Generative AI API key not found in config.")

        genai.configure(api_key=self.config['api_key'])

        model_name = self.config.get("model_name", "gemini-1.5-pro-latest") # Default to 1.5 Pro
        self.model = genai.GenerativeModel(model_name)

        # Store an approximate max character length for input text management.
        # This is a simplification; true token counting is more accurate.
        self.max_input_chars = config.get("max_input_chars", self.DEFAULT_MAX_INPUT_CHARS)

    def _check_input_length(self, text: str, operation_name: str) -> str:
        """
        Checks if the input text length is within a reasonable limit.
        Truncates and logs a warning if it's too long.
        """
        if len(text) > self.max_input_chars:
            logger.warning(
                f"Input text for {operation_name} is too long ({len(text)} chars). "
                f"Truncating to {self.max_input_chars} chars. "
                "Consider implementing chunking for very large inputs."
            )
            return text[:self.max_input_chars]
        return text

    async def query(self, prompt: str, **kwargs) -> str:
        """
        Sends a query to the Gemini LLM and returns the response.

        Args:
            prompt: The prompt to send to the LLM.
            **kwargs: Additional keyword arguments for the Gemini API.
                      (e.g., 'temperature', 'top_p', 'top_k', 'candidate_count', 'max_output_tokens')
                      Refer to google.generativeai.GenerativeModel.generate_content_async documentation.

        Returns:
            The LLM's response as a string.

        Raises:
            RateLimitError: If the API rate limit is exceeded.
            APIError: For other API-related errors.
            LLMProviderError: For general errors during the query.
        """
        try:
            # generation_config can be passed via kwargs if needed
            generation_config = genai.types.GenerationConfig(**kwargs) if kwargs else None
            response = await self.model.generate_content_async(prompt, generation_config=generation_config)

            if response.parts:
                return "".join(part.text for part in response.parts if hasattr(part, 'text'))
            elif response.candidates and response.candidates[0].content.parts:
                 # Check if text is within candidates (standard structure)
                return "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text'))
            else:
                # If no text parts, it might be a blocked prompt or empty response
                if response.prompt_feedback and response.prompt_feedback.block_reason:
                    raise APIError(f"Gemini API request blocked: {response.prompt_feedback.block_reason_message}")
                raise LLMProviderError("Gemini API returned an empty response or unexpected structure.")

        except google_exceptions.ResourceExhausted as e:
            raise RateLimitError(f"Google API rate limit exceeded: {e}") from e
        except google_exceptions.GoogleAPIError as e: # General Google API error
            raise APIError(f"Google API error: {e}") from e
        except Exception as e:
            raise LLMProviderError(f"An unexpected error occurred during query: {e}") from e

    async def analyze(self, text: str, **kwargs) -> dict:
        """
        Analyzes the given text using the Gemini LLM.
        Uses a structured prompt to ask Gemini for analysis.

        Args:
            text: The text to analyze.
            **kwargs: Additional keyword arguments.
                      'analysis_type': Describes the type of analysis (e.g., "sentiment", "entities").
                                       Defaults to a general analysis.
                      Other kwargs are passed to the query method.

        Returns:
            A dictionary containing the analysis results.

        Raises:
            RateLimitError, APIError, LLMProviderError from the underlying query.
        """
        text_to_analyze = self._check_input_length(text, "analysis")
        analysis_type = kwargs.pop('analysis_type', 'general text properties') # remove from kwargs

        prompt = (
            f"Please analyze the following text for {analysis_type}: \"{text_to_analyze}\". "
            "Provide the output as a structured JSON object. "
            "For example, if analyzing for sentiment, provide: {\"sentiment\": \"positive|negative|neutral\", \"score\": 0.xx}."
            "If analyzing for entities, provide: {\"entities\": [{\"text\": \"...\", \"type\": \"...\"}]}."
        )

        try:
            response_str = await self.query(prompt, **kwargs)
            import json
            try:
                analysis_result = json.loads(response_str)
                return analysis_result
            except json.JSONDecodeError:
                logger.warning(f"Gemini 'analyze' method did not return valid JSON. Response: {response_str}")
                return {"raw_analysis": response_str}
        except (RateLimitError, APIError, LLMProviderError) as e:
            raise e # Re-raise errors from query
        except Exception as e:
            raise LLMProviderError(f"An unexpected error occurred during analysis: {e}") from e

    async def summarize(self, text: str, **kwargs) -> str:
        """
        Summarizes the given text using the Gemini LLM.

        Args:
            text: The text to summarize.
            **kwargs: Additional keyword arguments for the summarization.
                      'max_length': Suggested max length for the summary (guides prompt).
                      'min_length': Suggested min length for the summary (guides prompt).
                      Other kwargs are passed to the query method.

        Returns:
            The summarized text as a string.

        Raises:
            RateLimitError, APIError, LLMProviderError from the underlying query.
        """
        text_to_summarize = self._check_input_length(text, "summarization")

        prompt = f"Please summarize the following text concisely: \"{text_to_summarize}\""
        if 'max_length' in kwargs: # kwargs are passed to query, so don't pop
            prompt += f"\nEnsure the summary is no more than approximately {kwargs['max_length']} words."
        if 'min_length' in kwargs:
            prompt += f"\nEnsure the summary is at least approximately {kwargs['min_length']} words."

        try:
            summary = await self.query(prompt, **kwargs)
            return summary
        except (RateLimitError, APIError, LLMProviderError) as e:
            raise e # Re-raise errors from query
        except Exception as e:
            raise LLMProviderError(f"An unexpected error occurred during summarization: {e}") from e
