"""
Data export module for the Data Pipeline MCP Server.
Handles writing processed pipeline results to output files.
"""

import csv
import json
import os
from datetime import datetime, timezone


def export_to_json(records: list, filepath: str) -> dict:
    """
    Export a list of records to a JSON file.

    Args:
        records: List of record dicts to export
        filepath: Destination file path

    Returns:
        Dict with export metadata (filepath, record_count, exported_at)
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, default=str)

    return {
        "filepath": filepath,
        "record_count": len(records),
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }


def export_to_csv(records: list, filepath: str) -> dict:
    """
    Export a list of records to a CSV file.

    Args:
        records: List of record dicts to export
        filepath: Destination file path

    Returns:
        Dict with export metadata (filepath, record_count, exported_at)
    """
    if not records:
        return {
            "filepath": filepath,
            "record_count": 0,
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }

    fieldnames = list(records[0].keys())

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    return {
        "filepath": filepath,
        "record_count": len(records),
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }


def cleanup_export_dir(directory: str, keep_latest: int = 5) -> dict:
    """
    Remove old export files from a directory, keeping only the most recent ones.

    Args:
        directory: Path to the export directory
        keep_latest: Number of most recent files to keep

    Returns:
        Dict with removed file count and kept file count
    """
    if not os.path.exists(directory):
        return {"removed": 0, "kept": 0}

    files = sorted(
        [os.path.join(directory, f) for f in os.listdir(directory)],
        key=os.path.getmtime,
        reverse=True,
    )

    to_keep = files[:keep_latest]
    to_remove = files[keep_latest:]

    for f in to_remove:
        os.remove(f)

    return {"removed": len(to_remove), "kept": len(to_keep)}
