from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"
env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape()
)

def render_pyspark(s3_prefix: str, partition_date_expr: str = "yesterday"):
    tmpl = env.get_template("pyspark_ingest.j2")
    return tmpl.render(s3_prefix=s3_prefix, partition_date_expr=partition_date_expr)

def render_sql(schema: str = "public", date_col: str = "order_date"):
    tmpl = env.get_template("sql_ingest.j2")
    return tmpl.render(schema=schema, date_col=date_col)

def render_dbt():
    tmpl = env.get_template("dbt_stg_sales.j2")
    return tmpl.render()
