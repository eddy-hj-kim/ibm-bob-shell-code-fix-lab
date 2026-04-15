"""
Mock data generator for the Data Pipeline MCP Server.
Provides sample sales transaction data for testing and development.
"""

MOCK_TRANSACTIONS = [
    {"id": 1,  "timestamp": "2024-01-15T09:23:00+09:00", "product": "Widget A", "quantity": 10,  "unit_price": 25.00,  "region": "APAC",  "status": "completed"},
    {"id": 2,  "timestamp": "2024-01-15T10:05:00+09:00", "product": "Widget B", "quantity": 5,   "unit_price": 50.00,  "region": "APAC",  "status": "completed"},
    {"id": 3,  "timestamp": "2024-01-15T11:30:00-05:00", "product": "Gadget X", "quantity": 2,   "unit_price": 120.00, "region": "AMER",  "status": "completed"},
    {"id": 4,  "timestamp": "2024-01-15T13:45:00-05:00", "product": "Gadget Y", "quantity": None,"unit_price": 80.00,  "region": "AMER",  "status": "completed"},
    {"id": 5,  "timestamp": "2024-01-15T14:00:00+01:00", "product": "Widget A", "quantity": 8,   "unit_price": 25.00,  "region": "EMEA",  "status": "completed"},
    {"id": 6,  "timestamp": "2024-01-15T15:20:00+01:00", "product": "Gadget X", "quantity": 3,   "unit_price": 120.00, "region": "EMEA",  "status": "completed"},
    {"id": 7,  "timestamp": "2024-01-16T08:00:00+09:00", "product": "Widget B", "quantity": 12,  "unit_price": 50.00,  "region": "APAC",  "status": "completed"},
    {"id": 8,  "timestamp": "2024-01-16T09:15:00+09:00", "product": "Gadget Z", "quantity": 1,   "unit_price": 200.00, "region": "APAC",  "status": "failed"},
    {"id": 9,  "timestamp": "2024-01-16T10:30:00-05:00", "product": "Widget A", "quantity": 20,  "unit_price": 25.00,  "region": "AMER",  "status": "completed"},
    {"id": 10, "timestamp": "2024-01-16T11:45:00-05:00", "product": "Gadget Y", "quantity": 4,   "unit_price": 80.00,  "region": "AMER",  "status": "completed"},
    {"id": 11, "timestamp": "2024-01-16T13:00:00+01:00", "product": "Widget B", "quantity": 7,   "unit_price": 50.00,  "region": "EMEA",  "status": "completed"},
    {"id": 12, "timestamp": "2024-01-16T14:30:00+01:00", "product": "Gadget Z", "quantity": 2,   "unit_price": 200.00, "region": "EMEA",  "status": "completed"},
    {"id": 13, "timestamp": "2024-01-17T09:00:00+09:00", "product": "Widget A", "quantity": 15,  "unit_price": 25.00,  "region": "APAC",  "status": "completed"},
    {"id": 14, "timestamp": "2024-01-17T10:20:00+09:00", "product": "Gadget X", "quantity": 5,   "unit_price": 120.00, "region": "APAC",  "status": "pending"},
    {"id": 15, "timestamp": "2024-01-17T11:00:00-05:00", "product": "Widget B", "quantity": 9,   "unit_price": 50.00,  "region": "AMER",  "status": "completed"},
]

VALID_REGIONS = ["APAC", "AMER", "EMEA"]
VALID_STATUSES = ["completed", "pending", "failed"]
VALID_PRODUCTS = ["Widget A", "Widget B", "Gadget X", "Gadget Y", "Gadget Z"]
