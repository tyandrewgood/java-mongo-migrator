from typing import List, Dict, Any
from llm.llm_client import LLMClient
from llm.prompt_templates import SCHEMA_SUGGESTION_PROMPT, SCHEMA_REVISION_PROMPT


class SchemaSuggester:
    """
    Generates MongoDB schema suggestions based on parsed Java components using an LLM.
    Also supports revising the schema based on validation feedback.
    """

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def suggest_schema(self, parsed_classes: List[Dict[str, Any]]) -> str:
        if not parsed_classes:
            raise ValueError("No parsed Java classes provided.")

        static_analysis_summary = self._format_parsed_classes(parsed_classes)
        prompt = SCHEMA_SUGGESTION_PROMPT.format(static_analysis=static_analysis_summary)

        response = self.llm_client.generate(prompt)
        return response

    def revise_schema_with_feedback(
        self,
        original_schema: str,
        issues: str,
        parsed_classes: List[Dict[str, Any]]
    ) -> str:
        """
        Use LLM to revise the schema suggestion based on validation issues and parsed classes context.
        """

        static_analysis_summary = self._format_parsed_classes(parsed_classes)
        prompt = SCHEMA_REVISION_PROMPT.format(
            original_schema=original_schema,
            issues=issues,
            static_analysis=static_analysis_summary
        )

        revised_response = self.llm_client.generate(prompt)
        return revised_response

    def _format_parsed_classes(self, parsed_classes: List[Dict[str, Any]]) -> str:
        """
        Helper to create a summary string of parsed classes and their fields.
        """
        lines = []
        for cls in parsed_classes:
            name = cls.get("name", "UnknownClass")
            fields = cls.get("fields", [])
            fields_str = ", ".join(f"{f['name']}:{f.get('type', 'unknown')}" for f in fields) if fields else "No fields"
            lines.append(f"Class: {name}, Fields: {fields_str}")
        return "\n".join(lines)
