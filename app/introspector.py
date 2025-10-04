from sqlalchemy import create_engine, inspect
from app.config import settings
from typing import List, Dict

def pg_engine():
    url = f"postgresql://{settings.PG_USER}:{settings.PG_PASS}@{settings.PG_HOST}:{settings.PG_PORT}/{settings.PG_DB}"
    return create_engine(url, pool_pre_ping=True)

def get_table_columns(table_name: str) -> List[str]:
    engine = pg_engine()
    insp = inspect(engine)
    # assume public schema for demo
    if not insp.has_table(table_name, schema="public"):
        return []
    cols = insp.get_columns(table_name, schema="public")
    return [c["name"] for c in cols]

def build_context_from_tables(tables: Dict[str, List[str]] = None) -> str:
    """
    Build LLM textual context describing available schemas.
    Optionally, introspect live database if `tables` is None.
    """
    lines = []
    if not tables:
        # for demo, introspect sales and customer if present
        for t in ("sales","customer","raw_sales"):
            cols = get_table_columns(t)
            if cols:
                lines.append(f"Table `{t}` has columns: {', '.join(cols)}")
    else:
        for t, cols in tables.items():
            lines.append(f"Table `{t}` has columns: {', '.join(cols)}")
    if not lines:
        lines.append("No schema context provided. Assume standard sales(customer_id,id,price,order_date) and customer(id,name,email).")
    return "\n".join(lines)
