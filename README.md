# Natural Language → Data Pipeline Builder (In Development)

## Overview
This repo demonstrates a production-oriented system that converts natural-language pipeline descriptions into runnable artifacts (PySpark, SQL, dbt). It uses LangChain + OpenAI for generation, Jinja templates as safe fallbacks, and has schema introspection to reduce hallucinations.

## Problem it solves
Non-technical users can’t write SQL or Spark code.

## Quickstart
1. set `OPENAI_API_KEY`.
2. Start Postgres locally (optional)
3. Install:
   pip install -r requirements.txt
4. Run:
   python -m app.main
   - opens Gradio UI at http://localhost:7895
   - FastAPI runs at http://localhost:8000
4. Build Docker container:
   - docker build -t llm-pipeline-builder .
   - docker run -it --rm -p 8000:8000 -p 7895:7895 llm-pipeline-builder

## Safety
- Generated code is non-destructive by default (writes to staging tables).
- Execution requires explicit dry-run disablement.
- The system introspects schema and uses template guardrails.
