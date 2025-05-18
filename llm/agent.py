from typing import List, Dict
from llm_client import LLMClient
from prompt_templates import PromptTemplates


class Agent:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def run_prompt(self, prompt_name: str, variables: Dict[str, str]) -> str:
        """
        Generate a response from the LLM given a prompt template and variables.

        Args:
            prompt_name (str): The key/name of the prompt template to use.
            variables (Dict[str, str]): Variables to fill into the prompt template.

        Returns:
            str: The LLM's generated response.
        """
        prompt_template = PromptTemplates.get_template(prompt_name)
        if not prompt_template:
            raise ValueError(f"Prompt template '{prompt_name}' not found.")
        
        prompt_text = prompt_template.format(**variables)
        
        response = self.llm_client.chat_completion(prompt_text)
        return response

    def run_conversation(self, prompt_name: str, conversation_history: List[Dict[str, str]]) -> str:
        """
        Run a conversation with the LLM, providing a prompt and conversation context.

        Args:
            prompt_name (str): The key/name of the prompt template to use as the system message.
            conversation_history (List[Dict[str, str]]): List of messages in format {"role": "...", "content": "..."}

        Returns:
            str: The LLM's generated response.
        """
        system_prompt = PromptTemplates.get_template(prompt_name)
        if not system_prompt:
            raise ValueError(f"Prompt template '{prompt_name}' not found.")

        # Compose messages with system prompt as first message
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)

        response = self.llm_client.chat_completion_messages(messages)
        return response
