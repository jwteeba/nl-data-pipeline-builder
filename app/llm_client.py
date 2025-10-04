import json
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from app.config import settings

# Initialize LLM
llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0,
    openai_api_key=settings.OPENAI_API_KEY
)

# Prompt template enforcing strict JSON with escaped strings
json_prompt_template = """
You are a pipeline code generator. 

User request: {user_request}
Context: {context}
Target backend: {target}

Generate a JSON object with exactly the following keys:
- "pyspark": a string containing the PySpark code for the requested pipeline
- "sql": a string containing SQL code for the requested pipeline
- "dbt": dbt model(s) SQL (as single string). 
  For the dbt output:
    - Always use {{ ref() }} for other models and {{ source() }} for raw tables.
    - Do NOT resolve or render these macros yourself. Just output valid dbt SQL.
    - Assume the user will run dbt to resolve them.
- "explanation": a string with a plain English explanation of each step

IMPORTANT REQUIREMENTS:
1. Return ONLY JSON. Do NOT include any text, markdown, or code blocks outside JSON.
2. All strings must be properly escaped: 
   - Newlines as "\\n" 
   - Double quotes inside strings as \\" 
   - Tabs as "\\t"
3. Do not truncate code. Include complete pipeline code for each key.
4. The JSON must be valid and parseable with Python's json.loads().

Example structure of the JSON you should return:

{{
  "pyspark": "spark.read.csv('s3://sales.csv').createOrReplaceTempView('sales')\\n...",
  "sql": "CREATE TABLE ...;\\nINSERT INTO ...;\\nSELECT ...;",
  "explanation": "Step 1: ... Step 2: ..."
}}
"""

prompt_template = PromptTemplate(
    input_variables=["user_request", "context", "target"],
    template=json_prompt_template
)


def safe_parse_json(resp: str) -> dict:
    """
    Safely parse LLM response as JSON.
    Attempts to extract JSON if LLM returned extra text or malformed characters.
    """
    try:
        return json.loads(resp)
    except json.JSONDecodeError:
        start = resp.find("{")
        end = resp.rfind("}") + 1
        if start != -1 and end != -1:
            resp_fixed = resp[start:end].replace("\n", "\\n").replace("\t", "\\t")
            try:
                return json.loads(resp_fixed)
            except json.JSONDecodeError:
                pass
        raise RuntimeError("Failed to parse LLM response as JSON:\n" + resp)


def generate_all(user_request: str, context: str = "", target: str = "pyspark") -> dict:
    """
    Generate pipeline code and explanation from natural language request.
    Returns dictionary with keys: 'pyspark', 'sql', 'dbt', 'explanation'.
    """
    # Format prompt
    formatted_prompt = prompt_template.format(
        user_request=user_request,
        context=context,
        target=target
    )

    # Call LLM
    resp = llm.invoke(formatted_prompt).content

    # Safely parse JSON
    parsed = safe_parse_json(resp)

    # Validate required keys
    required_keys = ["pyspark", "sql", "dbt", "explanation"]
    for key in required_keys:
        if key not in parsed:
            raise RuntimeError(
                f"LLM response JSON missing required key '{key}'. Raw response:\n{resp}"
            )

    return parsed
