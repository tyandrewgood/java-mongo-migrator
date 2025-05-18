import argparse
import logging
import os
import sys
from datetime import datetime

from analyzer.scanner import find_java_files
from analyzer.java_parser import JavaParser
from migration_plan.plan_generator import MigrationPlanGenerator
from migration_plan.plan_validator import MigrationPlanValidator
from schema_inference.schema_suggester import SchemaSuggester
from schema_inference.schema_validator import SchemaValidator
from llm.llm_client import LLMClient

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def parse_java_source(path: str):
    files = find_java_files(path)
    parser = JavaParser()
    parsed_classes = []
    for file_path in files:
        try:
            parsed = parser.parse_java_file(file_path)
            parsed_classes.extend(parsed)
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
    return parsed_classes


def full_migrate_command(path: str) -> None:
    logger.info(f"Starting full migration pipeline for path: {path}")

    files = find_java_files(path)
    if not files:
        logger.error("No Java files found; aborting.")
        sys.exit(1)
    logger.info(f"Found {len(files)} Java files")

    parsed_classes = parse_java_source(path)
    logger.info(f"Parsed {len(parsed_classes)} Java classes")

    llm_client = LLMClient()

    # Step 1: Suggest schema
    suggester = SchemaSuggester(llm_client)
    schema_suggestion = suggester.suggest_schema(parsed_classes)
    print("\n=== Schema Suggestion ===")
    print(schema_suggestion)

    # Step 2: Validate schema suggestion
    schema_validator = SchemaValidator(llm_client)
    schema_validation_report = schema_validator.validate_schema(schema_suggestion, parsed_classes)
    print("\n=== Schema Validation ===")
    print(schema_validation_report)

    if schema_validation_report["status"] != "PASS":
        logger.info("Schema validation issues found, requesting revision from LLM...")
        schema_suggestion = suggester.revise_schema_with_feedback(
            original_schema=schema_suggestion,
            issues=schema_validation_report.get("issues", "No issues provided."),
            parsed_classes=parsed_classes
        )
        print("\n=== Revised Schema Suggestion ===")
        print(schema_suggestion)

        schema_validation_report = schema_validator.validate_schema(schema_suggestion, parsed_classes)
        print("\n=== Re-Validated Schema Report ===")
        print(schema_validation_report)

    # Step 3: Generate migration plan
    plan_generator = MigrationPlanGenerator(llm_client)
    plan = plan_generator.generate_plan(parsed_classes, schema_suggestion=schema_suggestion)
    print("\n=== Migration Plan ===")
    print(plan)

    # Step 4: Validate migration plan
    plan_validator = MigrationPlanValidator(llm_client)
    validation_report = plan_validator.validate_plan(plan, parsed_classes)
    print("\n=== Plan Validation ===")
    print(validation_report)

    # Retry plan revision up to MAX_RETRIES if needed
    max_retries = int(os.getenv("MAX_RETRIES", 3))
    retries = 0

    while not validation_report.get("valid", False) and retries < max_retries:
        logger.info(f"Migration plan validation failed. Attempting revision (try {retries + 1}/{max_retries})...")

        parsed_info_str = "\n".join(
            f"Class: {cls.get('name', 'Unknown')} ({cls.get('type', 'Unknown')})\n" +
            "\n".join(f"  - {f['name']}: {f.get('type', 'unknown')}" for f in cls.get("fields", []))
            for cls in parsed_classes
        )

        issues_list = validation_report.get("issues", [])
        issues_text = "; ".join(
            f"{issue['issue']}: {issue.get('detail', '')}" for issue in issues_list
        ) if issues_list else "No details provided."

        # Revise the plan
        plan = plan_generator.revise_plan_with_feedback(
            migration_plan=plan,
            issues=issues_text,
            parsed_info=parsed_info_str
        )
        print(f"\n=== Revised Migration Plan (Attempt {retries + 1}) ===")
        print(plan)

        retries += 1

        if retries < max_retries:
            validation_report = plan_validator.validate_plan(plan, parsed_classes)
            print(f"\n=== Re-Validated Plan Report (Attempt {retries}) ===")
            print(validation_report)
        else:
            logger.info("Max retries reached. Skipping final validation.")
            break

    if not validation_report.get("valid", False):
        logger.warning(f"Migration plan could not be validated after {max_retries} attempts. Proceeding with last revision.")

    # Save results
    os.makedirs("results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        with open(f"results/schema_suggestion_{timestamp}.md", "w", encoding="utf-8") as f:
            f.write(schema_suggestion)
        logger.info("Saved schema suggestion.")
    except Exception as e:
        logger.error(f"Failed to save schema suggestion: {e}")

    try:
        with open(f"results/migration_plan_{timestamp}.md", "w", encoding="utf-8") as f:
            f.write(plan)
        logger.info("Saved migration plan.")
    except Exception as e:
        logger.error(f"Failed to save migration plan: {e}")

    logger.info("Full migration pipeline completed.")


def main():
    parser = argparse.ArgumentParser(description="Java to MongoDB Migration CLI")
    parser.add_argument("path", help="Root directory of Java source code")
    args = parser.parse_args()

    full_migrate_command(args.path)


if __name__ == "__main__":
    main()
