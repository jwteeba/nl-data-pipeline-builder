import pytest
from jinja2 import Environment, DictLoader, select_autoescape
from app.generator import render_pyspark, render_sql, render_dbt

@pytest.fixture(autouse=True)
def in_memory_env(monkeypatch):
    """
    Patch the app.generator's Jinja2 environment to use in-memory templates.
    """
    templates = {
        "pyspark_ingest.j2": "S3: {{ s3_prefix }}, Partition: {{ partition_date_expr }}",
        "sql_ingest.j2": "Schema: {{ schema }}, Date column: {{ date_col }}",
        "dbt_stg_sales.j2": "DBT template content"
    }
    
    env = Environment(
        loader=DictLoader(templates),
        autoescape=select_autoescape()
    )

    monkeypatch.setattr("app.generator.env", env)


def test_render_pyspark_defaults():
    result = render_pyspark("s3://bucket/path")
    assert "S3: s3://bucket/path" in result
    assert "Partition: yesterday" in result

def test_render_pyspark_custom_partition():
    result = render_pyspark("s3://bucket/path", "2025-10-04")
    assert "S3: s3://bucket/path" in result
    assert "Partition: 2025-10-04" in result

def test_render_sql_defaults():
    result = render_sql()
    assert "Schema: public" in result
    assert "Date column: order_date" in result

def test_render_sql_custom_values():
    result = render_sql("sales", "created_at")
    assert "Schema: sales" in result
    assert "Date column: created_at" in result

def test_render_dbt():
    result = render_dbt()
    assert "DBT template content" in result
