from typing import List, Dict

class SchemaValidator:
    """
    Validates the quality and completeness of the MongoDB schema suggestion.
    """

    REQUIRED_KEYWORDS = ["_id", "type", "fields", "relationships"]

    def __init__(self, llm_client):
        self.llm_client = llm_client

    def validate_schema(self, schema_text: str, parsed_classes: List[Dict]) -> Dict[str, str]:
        """
        Validates the schema suggestion returned by the LLM.

        Args:
            schema_text (str): The suggested schema text from the LLM.
            parsed_classes (List[Dict]): Parsed Java class metadata.

        Returns:
            Dict[str, str]: A dictionary with validation status and any issues found.
        """
        results = {
            "status": "PASS",
            "issues": ""
        }

        if not schema_text or len(schema_text.strip()) == 0:
            results["status"] = "FAIL"
            results["issues"] = "Schema suggestion is empty."
            return results

        missing_keywords = [kw for kw in self.REQUIRED_KEYWORDS if kw not in schema_text.lower()]
        if missing_keywords:
            results["status"] = "WARN"
            results["issues"] += f"Missing keywords: {', '.join(missing_keywords)}. "

        class_names = {cls['name'].lower() for item in parsed_classes for cls in item.get("classes", [])}
        mentioned_classes = {name for name in class_names if name in schema_text.lower()}

        missing_classes = class_names - mentioned_classes
        if missing_classes:
            results["status"] = "WARN"
            results["issues"] += f"Classes not mentioned in schema: {', '.join(missing_classes)}. "

        return results
