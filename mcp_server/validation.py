"""
Data validation module for the Data Pipeline MCP Server.
Validates transaction records against business rules before processing.
"""

from mock_data import VALID_REGIONS, VALID_STATUSES, VALID_PRODUCTS

MIN_QUANTITY = 1
MAX_QUANTITY = 1000
MIN_UNIT_PRICE = 0.01
MAX_UNIT_PRICE = 10000.00


def validate_record(record: dict) -> tuple[bool, list[str]]:
    """
    Validate a single transaction record against all business rules.

    Args:
        record: A transaction record dict

    Returns:
        Tuple of (is_valid: bool, errors: list of error message strings)
    """
    errors = []

    # Validate required fields
    for field in ["id", "timestamp", "product", "unit_price", "region", "status"]:
        if field not in record or record[field] is None:
            errors.append(f"Missing required field: '{field}'")

    # Validate region
    if record.get("region") not in VALID_REGIONS:
        errors.append(f"Invalid region '{record.get('region')}'. Must be one of {VALID_REGIONS}")

    # Validate status
    if record.get("status") not in VALID_STATUSES:
        errors.append(f"Invalid status '{record.get('status')}'. Must be one of {VALID_STATUSES}")

    # Validate product
    if record.get("product") not in VALID_PRODUCTS:
        errors.append(f"Invalid product '{record.get('product')}'. Must be one of {VALID_PRODUCTS}")

    # Validate quantity (only if present)
    qty = record.get("quantity")
    if qty is not None:
        if qty < MIN_QUANTITY or qty > MAX_QUANTITY:
            errors.append(
                f"Quantity {qty} out of valid range [{MIN_QUANTITY}, {MAX_QUANTITY}]"
            )

    # Validate unit_price
    price = record.get("unit_price")
    if price is not None:
        if price < MIN_UNIT_PRICE or price > MAX_UNIT_PRICE:
            errors.append(
                f"Unit price {price} out of valid range [{MIN_UNIT_PRICE}, {MAX_UNIT_PRICE}]"
            )

    return (len(errors) == 0, errors)


def validate_batch(records: list) -> dict:
    """
    Validate a batch of transaction records.

    Args:
        records: List of transaction records

    Returns:
        Dict with keys:
            - valid: list of valid records
            - invalid: list of dicts with 'record' and 'errors' keys
            - summary: dict with counts
    """
    valid = []
    invalid = []

    for record in records:
        is_valid, errors = validate_record(record)
        if is_valid:
            valid.append(record)
        else:
            invalid.append({"record": record, "errors": errors})

    return {
        "valid": valid,
        "invalid": invalid,
        "summary": {
            "total": len(records),
            "valid_count": len(valid),
            "invalid_count": len(invalid),
        },
    }
