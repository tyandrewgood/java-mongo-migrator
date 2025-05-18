import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
import openai
import logging

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class LLMClient:
    """
    A simple OpenAI LLM client wrapper for chat completions.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the LLM client.

        Args:
            api_key (Optional[str]): OpenAI API key. If None, reads from environment variable OPENAI_API_KEY.
            model (Optional[str]): The OpenAI model to use. If None, reads from environment variable OPENAI_MODEL or defaults to "gpt-4-turbo".
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable or pass api_key.")

        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4-turbo")

        openai.api_key = self.api_key
        logger.info(f"Initialized LLMClient with model '{self.model}'")

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,  # Lower for more focused and consistent output
        max_tokens: Optional[int] = 4096,  # Allow detailed multi-step responses
        top_p: float = 1.0,  # Default nucleus sampling
        frequency_penalty: float = 0.2,  # Light penalty to reduce repetition
        presence_penalty: float = 0.0,  # No penalty for introducing new topics
        stop: Optional[List[str]] = None,  # Add if you need clean truncation
    ) -> str:
        """
        Send a chat completion request to OpenAI API.

        Args:
            messages (List[Dict[str, str]]): List of message dicts with "role" and "content".
            temperature (float): Sampling temperature.
            max_tokens (Optional[int]): Max tokens to generate.
            top_p (float): Nucleus sampling parameter.
            frequency_penalty (float): Frequency penalty.
            presence_penalty (float): Presence penalty.
            stop (Optional[List[str]]): List of stop sequences.

        Returns:
            str: The assistant's reply.
        """
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=stop,
            )
            assistant_message = response.choices[0].message.content.strip()
            logger.debug(f"OpenAI response: {assistant_message}")
            return assistant_message

        except openai.error.OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error in LLMClient: {e}")
            raise

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Convenience method to generate a completion from a single prompt string.

        Args:
            prompt (str): The prompt to send to the LLM.
            **kwargs: Additional parameters to pass to chat_completion.

        Returns:
            str: The assistant's reply.
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat_completion(messages, **kwargs)
