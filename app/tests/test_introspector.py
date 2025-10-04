import pytest
from unittest.mock import patch, MagicMock
from app.introspector import get_table_columns, build_context_from_tables

# Mock data for testing
MOCK_TABLE_COLUMNS = {
    "sales": ["id", "customer_id", "price", "order_date"],
    "customer": ["id", "name", "email"],
    "raw_sales": ["id", "amount", "created_at"]
}

# Test get_table_columns with mock
@patch("app.introspector.inspect")
@patch("app.introspector.pg_engine")
def test_get_table_columns_existing_table(mock_pg_engine, mock_inspect):
    # Setup mocks
    mock_engine = MagicMock()
    mock_pg_engine.return_value = mock_engine

    mock_insp = MagicMock()
    mock_inspect.return_value = mock_insp

    # Table exists
    mock_insp.has_table.return_value = True
    mock_insp.get_columns.return_value = [{"name": c} for c in MOCK_TABLE_COLUMNS["sales"]]

    cols = get_table_columns("sales")
    assert cols == MOCK_TABLE_COLUMNS["sales"]
    mock_insp.has_table.assert_called_once_with("sales", schema="public")
    mock_insp.get_columns.assert_called_once_with("sales", schema="public")

@patch("app.introspector.inspect")
@patch("app.introspector.pg_engine")
def test_get_table_columns_nonexistent_table(mock_pg_engine, mock_inspect):
    # Setup mocks
    mock_engine = MagicMock()
    mock_pg_engine.return_value = mock_engine

    mock_insp = MagicMock()
    mock_inspect.return_value = mock_insp

    # Table does not exist
    mock_insp.has_table.return_value = False

    cols = get_table_columns("missing_table")
    assert cols == []

# Test build_context_from_tables with provided tables
def test_build_context_from_tables_with_tables():
    tables = {
        "sales": ["id", "customer_id", "price", "order_date"],
        "customer": ["id", "name", "email"]
    }
    result = build_context_from_tables(tables)
    assert "Table `sales` has columns: id, customer_id, price, order_date" in result
    assert "Table `customer` has columns: id, name, email" in result

# Test build_context_from_tables with no tables (fallback message)
@patch("app.introspector.get_table_columns")
def test_build_context_from_tables_no_tables(mock_get_columns):
    # Return empty for all tables
    mock_get_columns.return_value = []
    result = build_context_from_tables()
    assert "No schema context provided" in result
