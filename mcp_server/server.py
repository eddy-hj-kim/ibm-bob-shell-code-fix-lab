"""
Data Pipeline MCP Server using FastMCP.
Provides tools to ingest, transform, validate, and export transaction data.
"""

import json
import os
from typing import Optional

from fastmcp import FastMCP

from ingestion import fetch_transactions, fetch_all_transactions
from transform import calculate_total_revenue, enrich_records, group_by_region, group_by_product
from validation import validate_batch
from export import export_to_json, export_to_csv

mcp = FastMCP("Data Pipeline MCP Server")

BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_EXPORT_PATH = os.path.join(BASE_DIR, "export", "transactions")


@mcp.tool()
def ingest_transactions(
    page: int = 1,
    page_size: int = 5,
    status_filter: Optional[str] = None
) -> str:
    """
    Fetch paginated transaction records from the data source.

    Args:
        page: Page number to retrieve (1-indexed)
        page_size: Number of records per page
        status_filter: Optional filter by status (completed, pending, failed)

    Returns:
        JSON string with records and pagination metadata
    """
    try:
        result = fetch_transactions(page=page, page_size=page_size, status_filter=status_filter)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "error_type": type(e).__name__})


@mcp.tool()
def get_revenue_summary(status_filter: Optional[str] = None) -> str:
    """
    Calculate total revenue from completed transactions.

    Args:
        status_filter: Optional filter by status before calculating

    Returns:
        JSON string with revenue summary
    """
    try:
        records = fetch_all_transactions(status_filter=status_filter)
        total_revenue = sum(
            r["quantity"] * r["unit_price"]
            for r in records
            if r.get("status") == "completed"
        )
        return json.dumps({
            "success": True,
            "total_revenue": total_revenue,
            "record_count": len(records),
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "error_type": type(e).__name__})


@mcp.tool()
def enrich_and_group(group_by: str = "region") -> str:
    """
    Enrich all transactions and group them by region or product.

    Args:
        group_by: Grouping key — either 'region' or 'product'

    Returns:
        JSON string with grouped and enriched records
    """
    try:
        records = fetch_all_transactions()
        enriched = enrich_records(records)

        if group_by == "region":
            grouped = group_by_region(enriched)
        elif group_by == "product":
            grouped = group_by_product(enriched)
        else:
            return json.dumps({"success": False, "error": f"Invalid group_by value: '{group_by}'. Use 'region' or 'product'."})

        summary = {k: len(v) for k, v in grouped.items()}
        return json.dumps({"success": True, "group_by": group_by, "summary": summary}, indent=2, default=str)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "error_type": type(e).__name__})


@mcp.tool()
def validate_transactions(status_filter: Optional[str] = None) -> str:
    """
    Validate all transactions against business rules.

    Args:
        status_filter: Optional filter by status before validating

    Returns:
        JSON string with validation summary and list of invalid records
    """
    try:
        records = fetch_all_transactions(status_filter=status_filter)
        result = validate_batch(records)
        return json.dumps({
            "success": True,
            "summary": result["summary"],
            "invalid_records": result["invalid"],
        }, indent=2, default=str)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "error_type": type(e).__name__})


@mcp.tool()
def export_transactions(format: str = "json", filepath: str = DEFAULT_EXPORT_PATH) -> str:
    """
    Export all transactions to a file.

    Args:
        format: Export format — either 'json' or 'csv'
        filepath: Destination file path (without extension, defaults to export/transactions)

    Returns:
        JSON string with export metadata
    """
    try:
        records = fetch_all_transactions()
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        if format == "json":
            result = export_to_json(records, f"{filepath}.json")
        elif format == "csv":
            result = export_to_csv(records, f"{filepath}.csv")
        else:
            return json.dumps({"success": False, "error": f"Unsupported format: '{format}'. Use 'json' or 'csv'."})

        return json.dumps({"success": True, **result}, indent=2, default=str)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "error_type": type(e).__name__})


if __name__ == "__main__":
    mcp.run()
