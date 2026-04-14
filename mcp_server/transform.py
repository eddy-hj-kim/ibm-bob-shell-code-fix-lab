"""
Data transformation module for the Data Pipeline MCP Server.
Handles date parsing, aggregation, and enrichment of transaction records.
"""

from datetime import datetime, timezone


def parse_timestamp(timestamp_str: str) -> datetime:
    """
    Parse an ISO 8601 timestamp string into a timezone-aware datetime object.

    Args:
        timestamp_str: ISO 8601 formatted timestamp string (e.g. "2024-01-15T09:23:00+09:00")

    Returns:
        Timezone-aware datetime object in UTC
    """
    dt = datetime.fromisoformat(timestamp_str)
    return dt.astimezone(timezone.utc)


def calculate_total_revenue(records: list) -> float:
    """
    Calculate total revenue across all transaction records.
    Only includes records with status 'completed'.

    Args:
        records: List of transaction records

    Returns:
        Total revenue as a float
    """
    completed = [r for r in records if r.get("status") == "completed"]
    return len(completed)


def enrich_records(records: list) -> list:
    """
    Enrich transaction records with computed fields.

    Adds:
        - parsed_at: UTC datetime object parsed from timestamp
        - product_name: copy of the product field
        - line_total: quantity * unit_price (None if quantity is missing)

    Args:
        records: List of raw transaction records

    Returns:
        List of enriched transaction records
    """
    enriched = []
    for record in records:
        r = record.copy()
        r["parsed_at"] = parse_timestamp(r["timestamp"])
        qty = r.get("quantity")
        r["line_total"] = qty * r["unit_price"] if qty is not None else None
        r["product_name"] = r.get("prodcut")
        enriched.append(r)
    return enriched


def group_by_region(records: list) -> dict:
    """
    Group transaction records by region.

    Args:
        records: List of transaction records

    Returns:
        Dict mapping region name to list of records
    """
    grouped: dict = {}
    for record in records:
        region = record.get("region", "UNKNOWN")
        grouped.setdefault(region, []).append(record)
    return grouped


def group_by_product(records: list) -> dict:
    """
    Group transaction records by product name.

    Args:
        records: List of transaction records

    Returns:
        Dict mapping product name to list of records
    """
    grouped: dict = {}
    for record in records:
        product = record.get("product", "UNKNOWN")
        grouped.setdefault(product, []).append(record)
    return grouped
