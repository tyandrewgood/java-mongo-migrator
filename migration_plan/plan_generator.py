from typing import List, Dict, Any, Optional
from llm.llm_client import LLMClient
from llm.prompt_templates import MIGRATION_PLAN_PROMPT, PLAN_REVISION_FEEDBACK_PROMPT


class MigrationPlanGenerator:
    """
    Uses an LLM to generate a step-by-step migration plan from Java to MongoDB.
    """

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def generate_plan(self, parsed_classes: List[Dict[str, Any]], schema_suggestion: Optional[str] = None) -> str:
        """
        Generates a migration plan from the parsed Java classes.

        Args:
            parsed_classes (List[Dict[str, Any]]): Parsed class metadata from Java source code.
            schema_suggestion (Optional[str]): Suggested MongoDB schema to inform migration plan.

        Returns:
            str: LLM-generated migration plan text.
        """
        if not parsed_classes:
            raise ValueError("No parsed Java classes provided.")

        static_analysis_summary = "\n".join(
            f"Class: {cls.get('name', 'Unknown')} ({cls.get('type', 'Unknown')})\n" +
            "\n".join(f"  - {f['name']}: {f.get('type', 'unknown')}" for f in cls.get("fields", []))
            for cls in parsed_classes
        )

        # Optionally append schema suggestion to static analysis summary for more context
        if schema_suggestion:
            static_analysis_summary += "\n\nMongoDB Schema Suggestion:\n" + schema_suggestion

        # Construct prompt with the combined summary
        prompt = MIGRATION_PLAN_PROMPT.format(static_analysis=static_analysis_summary)

        # Query the LLM
        response = self.llm_client.generate(prompt)

        return response

    def revise_plan_with_feedback(self, migration_plan: str, issues: str, parsed_info: str) -> str:
        prompt = PLAN_REVISION_FEEDBACK_PROMPT.format(
            migration_plan=migration_plan,
            issues=issues,
            parsed_info=parsed_info
        )
        revised_plan = self.llm_client.generate(prompt)
        return revised_plan
