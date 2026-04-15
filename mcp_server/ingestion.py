"""
Data ingestion module for the Data Pipeline MCP Server.
Responsible for fetching and paginating raw transaction records.
"""

from typing import Optional
from mock_data import MOCK_TRANSACTIONS


def fetch_transactions(
    page: int = 1,
    page_size: int = 5,
    status_filter: Optional[str] = None
) -> dict:
    """
    Fetch paginated transaction records from the data source.

    Args:
        page: Page number to retrieve (1-indexed)
        page_size: Number of records per page
        status_filter: Optional filter by transaction status

    Returns:
        dict containing records, pagination metadata
    """
    records = MOCK_TRANSACTIONS

    if status_filter:
        records = [r for r in records if r["status"] == status_filter]

    total = len(records)

    start = (page - 1) * page_size
    end = start + page_size
    page_records = records[start:end]

    return {
        "records": page_records,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size,
    }


def fetch_all_transactions(status_filter: Optional[str] = None) -> list:
    """
    Fetch all transaction records without pagination.

    Args:
        status_filter: Optional filter by transaction status

    Returns:
        List of all matching transaction records
    """
    records = MOCK_TRANSACTIONS
    if status_filter:
        records = [r for r in records if r["status"] == status_filter]
    return records
