import os
import logging

# Assuming providers.py, claude_provider.py, etc., are in the same directory (src/llm)
from .providers import LLMProvider, LLMProviderError
from .claude_provider import ClaudeProvider
from .gemini_provider import GeminiProvider
from .deepseek_provider import DeepSeekProvider
# Import for OpenAIProvider will be added later if it's created in a separate step
# from .openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)

# --- Configuration Loading ---

def load_llm_config() -> dict:
    """
    Loads LLM provider configurations from environment variables.

    Returns:
        A dictionary containing configurations for each provider,
        the default provider name, and fallback provider names.
    """
    config = {
        "claude": {
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "model": os.getenv("CLAUDE_MODEL_NAME", "claude-3-opus-20240229"),
            # Add other Claude-specific configs here if needed
        },
        "gemini": {
            "api_key": os.getenv("GOOGLE_API_KEY"),
            "model_name": os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-pro-latest"),
            "max_input_chars": int(os.getenv("GEMINI_MAX_INPUT_CHARS", "1000000")),
        },
        "deepseek": {
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
            "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            "model_name": os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-chat"),
        },
        # Placeholder for OpenAI provider config
        # "openai": {
        #     "api_key": os.getenv("OPENAI_API_KEY"),
        #     "model_name": os.getenv("OPENAI_MODEL_NAME", "gpt-4-turbo-preview"),
        # },
        "default_provider": os.getenv("DEFAULT_LLM_PROVIDER", "claude").lower(),
        "fallback_providers": [
            p.strip().lower() for p in os.getenv("FALLBACK_LLM_PROVIDERS", "gemini,deepseek").split(',') if p.strip()
        ]
    }

    # Basic validation: Log warnings if default provider's API key is missing
    default_provider_name = config["default_provider"]
    if default_provider_name in config and isinstance(config[default_provider_name], dict):
        if not config[default_provider_name].get("api_key"):
            logger.warning(
                f"Default LLM provider '{default_provider_name}' is configured, "
                "but its API key environment variable is not set."
            )
    elif default_provider_name not in ["claude", "gemini", "deepseek"]: # Add openai when ready
         logger.warning(
            f"Default LLM provider '{default_provider_name}' is not a recognized provider name."
         )


    return config

# --- Provider Instantiation ---

PROVIDER_CLASSES = {
    "claude": ClaudeProvider,
    "gemini": GeminiProvider,
    "deepseek": DeepSeekProvider,
    # "openai": OpenAIProvider, # Add when OpenAIProvider is available
}

def get_llm_provider(config: dict = None) -> LLMProvider:
    """
    Gets an instance of an LLM provider based on the provided or loaded configuration.
    It tries the default provider first, then fallbacks.

    Args:
        config: Optional configuration dictionary. If None, calls load_llm_config().

    Returns:
        An instance of an LLMProvider.

    Raises:
        LLMProviderError: If no LLM provider can be configured (e.g., no API keys).
    """
    if config is None:
        config = load_llm_config()

    default_provider_name = config.get("default_provider")
    provider_order = [default_provider_name] + config.get("fallback_providers", [])

    if not default_provider_name:
        logger.warning("DEFAULT_LLM_PROVIDER environment variable is not set or empty.")
        # If no default, try all known providers that have API keys
        provider_order = [name for name in PROVIDER_CLASSES.keys() if config.get(name, {}).get('api_key')]


    for provider_name in provider_order:
        if not provider_name: # Skip if provider name is empty string from split
            continue

        provider_config = config.get(provider_name)
        ProviderClass = PROVIDER_CLASSES.get(provider_name)

        if ProviderClass and provider_config and provider_config.get("api_key"):
            try:
                logger.info(f"Attempting to initialize LLM provider: {provider_name}")
                return ProviderClass(provider_config)
            except Exception as e:
                logger.error(f"Failed to initialize provider {provider_name}: {e}", exc_info=True)
        elif ProviderClass and provider_config and not provider_config.get("api_key"):
            logger.warning(
                f"Skipping provider {provider_name} because its API key is not configured."
            )
        elif not ProviderClass :
             logger.warning(
                f"Provider '{provider_name}' mentioned in default/fallback list is not recognized/implemented."
            )


    raise LLMProviderError(
        "No LLM provider could be configured. "
        "Check API key environment variables (e.g., ANTHROPIC_API_KEY, GOOGLE_API_KEY, DEEPSEEK_API_KEY) "
        "and DEFAULT_LLM_PROVIDER/FALLBACK_LLM_PROVIDERS settings."
    )

# --- Optional Global Config and Test ---

# Load config once globally for easy access from other modules, if desired.
# However, it's often cleaner to pass config explicitly or use a dependency injection pattern.
# For simplicity in this context, a global config can be acceptable.
LLM_CONFIG = load_llm_config()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("--- Testing LLM Provider Configuration ---")
    logger.info(f"Loaded configuration: {LLM_CONFIG}")

    print("\nAttempting to get LLM provider...")
    try:
        # Example: Set environment variables before running this test
        # export ANTHROPIC_API_KEY="your_claude_key"
        # export GOOGLE_API_KEY="your_gemini_key"
        # export DEEPSEEK_API_KEY="your_deepseek_key"
        # export DEFAULT_LLM_PROVIDER="claude"
        # export FALLBACK_LLM_PROVIDERS="gemini,deepseek"

        # To test fallback, you might unset the default provider's key
        # unset ANTHROPIC_API_KEY

        provider = get_llm_provider(LLM_CONFIG)
        print(f"\nSuccessfully loaded provider: {type(provider).__name__}")
        print(f"Provider config: {provider.config}")

        # Basic test of a provider method (requires async context or a sync wrapper if testing here)
        # import asyncio
        # async def test_query():
        #     try:
        #         response = await provider.query("Hello, who are you?")
        #         print(f"\nTest query response: {response}")
        #     except Exception as e:
        #         print(f"\nError during test query: {e}")
        # asyncio.run(test_query())

    except LLMProviderError as e:
        print(f"\nError getting LLM provider: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

    print("\n--- LLM Configuration Test Complete ---")
