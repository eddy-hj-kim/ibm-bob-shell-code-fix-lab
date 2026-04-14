# Hands-on Lab: Code Review & Bug Fix with Bob Shell

In this lab, you will use **Bob Shell** to perform an automated code review on a buggy Data Pipeline MCP Server, identify hidden bugs, fix them, and verify the fixes with self-written tests — all in three simple steps.

---

## Project Structure

```
.
├── pyproject.toml
└── mcp_server/
    ├── server.py        ← MCP tool definitions
    ├── ingestion.py     ← Data ingestion & pagination
    ├── transform.py     ← Data transformation & aggregation
    ├── validation.py    ← Business rule validation
    ├── export.py        ← File export (JSON / CSV)
    └── mock_data.py     ← Sample transaction dataset
```

The server exposes **5 MCP tools**:

| Tool | Description |
|---|---|
| `ingest_transactions` | Fetch paginated transaction records |
| `get_revenue_summary` | Calculate total revenue |
| `enrich_and_group` | Enrich and group records by region or product |
| `validate_transactions` | Validate records against business rules |
| `export_transactions` | Export records to JSON or CSV |

There are bugs hidden across the codebase. Bob Shell will find and fix them all.

---

## Step 1 — Setup

Clone the repository and install dependencies using `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
cd bob_shell_code_fix_lab
uv sync
```

---

## Step 2 — Review Code and Fix Bugs

Run Bob shell to perform a full code review and automatically fix all bugs:

**Using Bob Shell:**
```bash
bob --yolo -p "
  Review all source files in the @mcp_server/ directory including @mock_data.py.
  Pay close attention to the data schema and edge cases in @mock_data.py
  when reviewing the business logic in other files.
  Identify all bugs and potential issues.
  Fix every bug you find directly in the source files.
  Write a summary of each bug and its fix to review.md.
"
```

After the agent finishes, open `review.md` to see what was found and fixed before moving on.

---

## Step 3 — Generate Tests and Verify Fixes

Run Bob Shell to generate test cases for each MCP tool and validate all fixes:

**Using Bob:**
```bash
bob --yolo -p "
  Based on the fixes documented in @review.md,
  create tests/test_pipeline.py with test cases for each MCP tool in @mcp_server/server.py.
  Each test must validate that the fixes in @review.md are working correctly.
  Run the tests using the project virtual environment:
  source .venv/bin/activate && python -m pytest tests/ -v
  Do NOT install any packages directly. All dependencies are managed by uv.
  If any test fails, fix the code and re-run until all tests pass.
"
```

All tests should pass. ✅
