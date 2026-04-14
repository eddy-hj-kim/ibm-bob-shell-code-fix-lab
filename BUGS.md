# Bug Reference — Instructor Notes

This document is intended for **instructors only**. Do not share with lab participants.

There are **5 bugs** hidden across the codebase, all detectable through code review alone.

---

## Bug 1 — `ingestion.py`: Off-by-one error in pagination

**Location:** `fetch_transactions()`, line computing `start`

**Buggy code:**
```python
start = page * page_size  # page=1, page_size=5 → start=5 (skips first page!)
```

**Fix:**
```python
start = (page - 1) * page_size
```

**Why it's detectable:** The function docstring says `page` is 1-indexed, but the formula treats it as 0-indexed.

---

## Bug 2 — `transform.py`: Wrong return value in `calculate_total_revenue`

**Location:** `calculate_total_revenue()`

**Buggy code:**
```python
completed = [r for r in records if r.get("status") == "completed"]
return len(completed)  # returns count, not revenue!
```

**Fix:**
```python
return sum(r["quantity"] * r["unit_price"] for r in completed if r.get("quantity") is not None)
```

**Why it's detectable:** Function is named `calculate_total_revenue` and docstring says "Returns total revenue as a float", but it returns `len()` — obviously wrong.

---

## Bug 3 — `transform.py`: Typo in dictionary key

**Location:** `enrich_records()`, enriched record assignment

**Buggy code:**
```python
r["product_name"] = r.get("prodcut")  # typo: "prodcut" instead of "product"
```

**Fix:**
```python
r["product_name"] = r.get("product")
```

**Why it's detectable:** `"prodcut"` is a clear typo. `product_name` will always be `None`.

---

## Bug 4 — `validation.py`: Wrong comparison operators in quantity range check

**Location:** `validate_record()`, quantity validation block

**Buggy code:**
```python
if qty <= MIN_QUANTITY or qty >= MAX_QUANTITY:  # rejects boundary values 1 and 1000
```

**Fix:**
```python
if qty < MIN_QUANTITY or qty > MAX_QUANTITY:
```

**Why it's detectable:** Using `<=` and `>=` means boundary values `MIN_QUANTITY=1` and `MAX_QUANTITY=1000` are rejected as invalid, contradicting the range comment `[MIN_QUANTITY, MAX_QUANTITY]`.

---

## Bug 5 — `server.py`: Missing `None` check on `quantity` before multiplication

**Location:** `get_revenue_summary()`, the `sum()` generator expression

**Buggy code:**
```python
total_revenue = sum(
    r["quantity"] * r["unit_price"]
    for r in records
    if r.get("status") == "completed"
)
```

**Fix:**
```python
total_revenue = sum(
    r["quantity"] * r["unit_price"]
    for r in records
    if r.get("status") == "completed" and r.get("quantity") is not None
)
```

**Why it's detectable:** `mock_data.py` contains a record with `quantity: None` and `status: "completed"` (id=4). A reviewer who reads `mock_data.py` alongside `server.py` will spot the missing None guard.

---

## Expected `review.md` from Participants

```
## Bug 1 — ingestion.py: Off-by-one error in pagination
## Bug 2 — transform.py: calculate_total_revenue returns count instead of revenue
## Bug 3 — transform.py: Typo "prodcut" in enrich_records
## Bug 4 — validation.py: Wrong comparison operators in quantity range check
## Bug 5 — server.py: Missing None check on quantity in get_revenue_summary
```
