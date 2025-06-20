import unittest
import abc

# Adjust imports based on the project structure and how src is found.
# If tests are run from the root directory, src.llm should work.
from src.llm.providers import LLMProvider, LLMProviderError, RateLimitError, APIError
from src.llm import ClaudeProvider, GeminiProvider, DeepSeekProvider
# OpenAIProvider will be added here when created
# from src.llm import OpenAIProvider


class TestLLMProviderInterface(unittest.TestCase):
    """
    Tests the LLMProvider abstract base class interface.
    """

    def test_is_abstract_base_class(self):
        """Test that LLMProvider is an abstract base class."""
        self.assertTrue(issubclass(LLMProvider, abc.ABC), "LLMProvider should be an ABC.")

    def test_abstract_methods_defined(self):
        """Test that core methods are defined as abstract."""
        # __abstractmethods__ stores a frozenset of abstract method names
        self.assertIn("query", LLMProvider.__abstractmethods__)
        self.assertIn("analyze", LLMProvider.__abstractmethods__)
        self.assertIn("summarize", LLMProvider.__abstractmethods__)

    def test_init_requires_config(self):
        """Test that LLMProvider cannot be instantiated without derived class implementing __init__."""
        # Create a minimal concrete class for testing __init__ indirectly
        class DummyProvider(LLMProvider):
            def __init__(self, config: dict): # Must match expected signature by LLMProvider
                super().__init__(config)
            async def query(self, prompt: str, **kwargs) -> str: return ""
            async def analyze(self, text: str, **kwargs) -> dict: return {}
            async def summarize(self, text: str, **kwargs) -> str: return ""

        with self.assertRaisesRegex(TypeError, "Can't instantiate abstract class LLMProvider with abstract methods"):
            LLMProvider({}) # type: ignore

        # Test DummyProvider instantiation
        try:
            dummy_config = {"key": "value"}
            provider = DummyProvider(config=dummy_config)
            self.assertEqual(provider.config, dummy_config)
        except Exception as e:
            self.fail(f"DummyProvider instantiation failed: {e}")


class TestProviderImplementations(unittest.TestCase):
    """
    Tests basic instantiation of concrete LLMProvider implementations.
    These tests ensure constructors are wired up correctly and classes derive from LLMProvider.
    """

    def test_claude_provider_instantiation(self):
        """Test ClaudeProvider instantiation and type."""
        mock_config_claude = {"api_key": "test_key_claude", "model": "claude-test"}
        try:
            provider = ClaudeProvider(config=mock_config_claude)
            self.assertIsInstance(provider, LLMProvider)
            self.assertIsInstance(provider, ClaudeProvider)
            self.assertEqual(provider.config["api_key"], "test_key_claude")
            self.assertEqual(provider.config["model"], "claude-test")
        except Exception as e:
            self.fail(f"ClaudeProvider instantiation failed: {e}")

    def test_gemini_provider_instantiation(self):
        """Test GeminiProvider instantiation and type."""
        mock_config_gemini = {"api_key": "test_key_gemini", "model_name": "gemini-test"}
        try:
            provider = GeminiProvider(config=mock_config_gemini)
            self.assertIsInstance(provider, LLMProvider)
            self.assertIsInstance(provider, GeminiProvider)
            self.assertEqual(provider.config["api_key"], "test_key_gemini")
            self.assertEqual(provider.config["model_name"], "gemini-test")
        except Exception as e:
            self.fail(f"GeminiProvider instantiation failed: {e}")

    def test_deepseek_provider_instantiation(self):
        """Test DeepSeekProvider instantiation and type."""
        mock_config_deepseek = {
            "api_key": "test_key_deepseek",
            "model_name": "deepseek-custom-model",
            "base_url": "http://localhost:1234/v1"
        }
        try:
            provider = DeepSeekProvider(config=mock_config_deepseek)
            self.assertIsInstance(provider, LLMProvider)
            self.assertIsInstance(provider, DeepSeekProvider)
            self.assertEqual(provider.config["api_key"], "test_key_deepseek")
            self.assertEqual(provider.model_name, "deepseek-custom-model")
            self.assertEqual(provider.base_url, "http://localhost:1234/v1")
        except Exception as e:
            self.fail(f"DeepSeekProvider instantiation failed: {e}")

    # Test for OpenAIProvider will be added here when the provider is created
    # def test_openai_provider_instantiation(self):
    #     """Test OpenAIProvider instantiation and type."""
    #     mock_config_openai = {"api_key": "test_key_openai", "model_name": "gpt-test"}
    #     try:
    #         provider = OpenAIProvider(config=mock_config_openai) # Assuming OpenAIProvider is imported
    #         self.assertIsInstance(provider, LLMProvider)
    #         self.assertIsInstance(provider, OpenAIProvider)
    #         self.assertEqual(provider.config["api_key"], "test_key_openai")
    #         self.assertEqual(provider.model_name, "gpt-test") # Assuming model_name attribute
    #     except Exception as e:
    #         self.fail(f"OpenAIProvider instantiation failed: {e}")

class TestLLMProviderExceptions(unittest.TestCase):
    """
    Tests that the custom exceptions are available and correctly subclassed.
    """
    def test_exception_hierarchy(self):
        self.assertTrue(issubclass(RateLimitError, LLMProviderError))
        self.assertTrue(issubclass(APIError, LLMProviderError))

    def test_exception_instantiation(self):
        try:
            raise LLMProviderError("Test LLMProviderError")
        except LLMProviderError as e:
            self.assertEqual(str(e), "Test LLMProviderError")

        try:
            raise RateLimitError("Test RateLimitError")
        except RateLimitError as e:
            self.assertEqual(str(e), "Test RateLimitError")

        try:
            raise APIError("Test APIError")
        except APIError as e:
            self.assertEqual(str(e), "Test APIError")

if __name__ == "__main__":
    unittest.main()
