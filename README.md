# ☕ Java Mongo Migrator

A CLI tool that analyzes legacy Java EE applications (like the JBoss Kitchensink app) and generates AI-assisted migration plans to a modern Java 21 stack — specifically **Spring Boot with MongoDB**.

This tool combines static code analysis with large language models (LLMs) to:

- Generate a migration plan from Java EE + relational DB to Spring Boot + MongoDB
- Suggest MongoDB schemas inferred from existing JPA entities and application logic
- Validate and revise outputs in an iterative loop (inspired by corrective RAG patterns)

---

## 🧠 Use Case

Given a legacy JBoss Java application — such as the [`kitchensink`](https://github.com/jboss-developer/jboss-eap-quickstarts/tree/main/kitchensink) quickstart — this tool can:

- Detect frameworks and technologies in use  
- Recommend steps for modernization with Java 21 and MongoDB  
- Suggest equivalent Spring Boot components  
- Propose a document-based schema for MongoDB  
- Validate generated plans and re-run when key requirements are missing

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/java-mongo-migrator.git
cd java-mongo-migrator
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your OpenAI API key

Create a `.env` file:

```bash
echo "OPENAI_API_KEY=sk-..." > .env
```

Or export directly:

```bash
export OPENAI_API_KEY=sk-...
```

### 4. Run the analyzer

```bash
python main.py /path/to/kitchensink
```

The tool will generate:

- `schema_suggestion_<timestamp>.md` — MongoDB schema suggestion
- `migration_plan_<timestamp>.md` — Spring Boot migration plan

---

## 🧱 Project Structure

```
java-mongo-migrator/
├── analyzer/            # Java parser and project inspector
├── migration_plan/      # Plan generator and validator
├── schema_inference/    # Schema inference and validation logic
├── llm/                 # LLM prompt orchestration
├── results/             # Markdown outputs
├── main.py              # CLI entry point
└── README.md
```

## 🔁 Processing Pipeline

```
                ┌──────────────────┐
                │    Java Source   │
                │     Directory    │
                └──────┬───────────┘
                       │
            ┌──────────▼──────────────┐ 
            │ Extract & Parse Classes │
            └──────────┬──────────────┘
                       │
        ┌──────────────▼─────────────────┐
        │     LLM proposes Mongo schema  │
        └──────────────┬─────────────────┘
                       │
        ┌──────────────▼─────────────────┐
        │     Checks schema against code │
        └──────────────┬─────────────────┘
                       │ feedback loop if invalid
        ┌──────────────▼────────────────────┐
        │        Revise and update schema   │
        └──────────────┬────────────────────┘
                       │
        ┌──────────────▼────────────────────┐
        │    Generates migration plan       │
        └──────────────┬────────────────────┘
                       │
        ┌──────────────▼────────────────────┐
        │    Validates LLM-generated plan   │
        └──────────────┬────────────────────┘
                       │ feedback loop if invalid
        ┌──────────────▼────────────────────┐
        │  Revise and Update Migration Plan │
        └──────────────┬────────────────────┘
                       │
        ┌──────────────▼────────────────────┐
        │ Save results (schema & plan .md)  │
        └───────────────────────────────────┘
```

---

## 🔄 Corrective Loop

After initial generation, the tool **validates** both the migration plan and schema using structured prompt-based critiques that check for:

- Coverage of all parsed Java classes and fields  
- Accurate event handling migration (e.g., CDI → Spring events)  
- Proper transaction management strategies for MongoDB  
- Complete and correct validation logic migration  
- Thorough schema modeling (including indexes, embedding vs referencing)  

If any critical gaps, hallucinations, or inconsistencies are found, the system triggers a **corrective prompt chain** that:

- **Identifies specific issues** with structured JSON feedback  
- **Re-prompts the LLM** to regenerate or revise the original output using the feedback and static analysis context  
- Iterates until the output is valid or no significant issues remain  

This approach mimics a **Corrective RAG** (Retrieval-Augmented Generation) pattern — combining validation, retrieval, and iterative refinement to ensure **accuracy, completeness, and consistency** in generated plans.

---

## 📁 Example Output

- [Migration Plan for Kitchensink](results/kitchensink_migration_plan.md)  
- [MongoDB Schema Suggestion for Kitchensink](results/kitchensink_schema_suggestion.md)
