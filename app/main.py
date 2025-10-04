from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import gradio as gr
import uvicorn
from app.llm_client import generate_all
from app.introspector import build_context_from_tables
from app.generator import render_pyspark, render_sql, render_dbt
from app.config import settings
import logging

log = logging.getLogger("nl_pipeline")
log.setLevel(logging.INFO)

app = FastAPI(title="NL --> DataPipelineBuilder")

# Redirect root to Gradio UI
@app.get("/", include_in_schema=False)
def redirect_to_gradio():
    return RedirectResponse(url="http://localhost:7895")

# -----------------------------
# FastAPI /generate endpoint
# -----------------------------
class GenerateRequest(BaseModel):
    user_request: str
    target: str = settings.DEFAULT_TARGET
    schema_hint: dict = None
    run: bool = False  # explicit run flag

@app.post("/generate")
async def generate_endpoint(payload: GenerateRequest):
    # 1) build context from schema hint or DB
    context_text = build_context_from_tables(payload.schema_hint)
    # 2) ask LLM to produce code (structured JSON)
    try:
        generated = generate_all(payload.user_request, context_text, payload.target)
    except Exception as e:
        log.exception(f"LLM generation failed: {e}")
        return {"error": str(e)}
    # 3) Render local templates as guardrail alternatives
    pyspark_code = render_pyspark(settings.S3_SALES_PREFIX)
    sql_code = render_sql()
    dbt_code = render_dbt()
    # 4) Return everything
    return {
        "llm_outputs": generated,
        "templates": {
            "pyspark": pyspark_code,
            "sql": sql_code,
            "dbt": dbt_code
        }
    }

# -----------------------------
# Gradio app
# -----------------------------
def gradio_app():
    def on_generate(text, target, schema_text):
        # parse schema_text input lines into table:cols dict
        table_map = {}
        for line in schema_text.splitlines():
            if ":" in line:
                t, cols = line.split(":",1)
                table_map[t.strip()] = [c.strip() for c in cols.split(",") if c.strip()]
        payload = {"user_request": text, "target": target, "schema_hint": table_map}
        import requests, json
        resp = requests.post("http://localhost:8000/generate", json=payload, timeout=60)
        if resp.status_code != 200:
            return resp.text
        j = resp.json()
        llm = j.get("llm_outputs", {})
        templates = j.get("templates", {})
        # show LLM code if present else templates
        code = llm.get(target) or templates.get(target) or llm.get("pyspark") or templates.get("pyspark")
        explanation = llm.get("explanation") or "No explanation returned"
        return code, explanation

    with gr.Blocks() as demo:
        gr.Markdown("# NL → Data Pipeline Builder")
        inp = gr.Textbox(
            lines=2,
            label="Natural language request (Write your request)",
            value="Ingest yesterday's sales data from S3, clean out nulls in price, and join with customer table on id"
        )
        tgt = gr.Dropdown(
            choices=["pyspark","sql","dbt"],
            value=settings.DEFAULT_TARGET,
            label="Target"
        )
        schema = gr.Textbox(
            lines=4,
            label="Schema hint (format 'table:col1,col2')",
            value="sales:id,price,order_date,customer_id\ncustomer:id,name,email"
        )
        out_code = gr.Textbox(label="Generated Code", lines=10, interactive=False, show_copy_button=True)
        out_explain = gr.Textbox(label="Explanation", lines=10, interactive=False, show_copy_button=True)

        btn = gr.Button("Generate")
        btn.click(on_generate, inputs=[inp,tgt,schema], outputs=[out_code, out_explain])
    return demo

# -----------------------------
# Run FastAPI + Gradio
# -----------------------------
if __name__ == "__main__":
    import threading, time

    # Start FastAPI in a separate thread
    def run_api():
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, log_level="info")

    t = threading.Thread(target=run_api, daemon=True)
    t.start()

    time.sleep(1)

    # Launch Gradio
    demo = gradio_app()
    demo.launch(server_name="0.0.0.0", server_port=7895, share=True)
