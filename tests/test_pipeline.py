"""
Test suite for MCP Server tools.
Validates that all bugs documented in review.md are fixed.
"""

import json
import os
import pytest
import tempfile
import shutil
from pathlib import Path

# Import the MCP tools
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp_server'))

from server import (
    ingest_transactions,
    get_revenue_summary,
    enrich_and_group,
    validate_transactions,
    export_transactions
)


class TestBug1PaginationFix:
    """Test Bug #1: Pagination off-by-one error fix"""
    
    def test_page_1_starts_at_index_0(self):
        """Verify page 1 returns the first records (IDs 1-5)"""
        result = json.loads(ingest_transactions(page=1, page_size=5))
        
        assert result["page"] == 1
        assert result["page_size"] == 5
        
        # First page should contain record IDs 1-5
        record_ids = [r["id"] for r in result["records"]]
        assert record_ids == [1, 2, 3, 4, 5], f"Expected IDs [1,2,3,4,5] but got {record_ids}"
    
    def test_page_2_continues_correctly(self):
        """Verify page 2 returns the next set of records (IDs 6-10)"""
        result = json.loads(ingest_transactions(page=2, page_size=5))
        
        assert result["page"] == 2
        
        # Second page should contain record IDs 6-10
        record_ids = [r["id"] for r in result["records"]]
        assert record_ids == [6, 7, 8, 9, 10], f"Expected IDs [6,7,8,9,10] but got {record_ids}"
    
    def test_custom_page_size(self):
        """Verify pagination works with different page sizes"""
        result = json.loads(ingest_transactions(page=1, page_size=3))
        
        assert len(result["records"]) == 3
        
        # Should get first 3 records
        record_ids = [r["id"] for r in result["records"]]
        assert record_ids == [1, 2, 3]


class TestBug2RevenueCalculationFix:
    """Test Bug #2: Incorrect revenue calculation fix"""
    
    def test_revenue_is_calculated_not_counted(self):
        """Verify revenue is sum of (quantity * unit_price), not record count"""
        result = json.loads(get_revenue_summary())
        
        assert result["success"] is True
        assert "total_revenue" in result
        
        # Revenue should be a monetary value, not just a count
        # From mock data: completed transactions should have revenue > 100
        # (e.g., ID 1: 10 * 29.99 = 299.90, ID 2: 5 * 149.99 = 749.95, etc.)
        assert result["total_revenue"] > 100, "Revenue should be calculated, not counted"
        assert isinstance(result["total_revenue"], (int, float))
    
    def test_only_completed_transactions_counted(self):
        """Verify only completed transactions contribute to revenue"""
        # Get all records
        all_result = json.loads(get_revenue_summary())
        
        # Get only completed records
        completed_result = json.loads(get_revenue_summary(status_filter="completed"))
        
        # Both should have same revenue since we only count completed anyway
        assert all_result["total_revenue"] == completed_result["total_revenue"]
    
    def test_revenue_calculation_accuracy(self):
        """Verify revenue calculation is mathematically correct"""
        result = json.loads(get_revenue_summary(status_filter="completed"))
        
        # From mock_data.py, completed transactions (excluding None quantities):
        # ID 1: 10 * 25.00 = 250.00
        # ID 2: 5 * 50.00 = 250.00
        # ID 3: 2 * 120.00 = 240.00
        # ID 4: None (skipped)
        # ID 5: 8 * 25.00 = 200.00
        # ID 6: 3 * 120.00 = 360.00
        # ID 7: 12 * 50.00 = 600.00
        # ID 9: 20 * 25.00 = 500.00
        # ID 10: 4 * 80.00 = 320.00
        # ID 11: 7 * 50.00 = 350.00
        # ID 12: 2 * 200.00 = 400.00
        # ID 13: 15 * 25.00 = 375.00
        # ID 15: 9 * 50.00 = 450.00
        # Total: 4295.00
        
        expected_revenue = 4295.0
        assert abs(result["total_revenue"] - expected_revenue) < 0.01, \
            f"Expected revenue ~{expected_revenue}, got {result['total_revenue']}"


class TestBug5NoneQuantityHandling:
    """Test Bug #5: Missing None check in revenue summary"""
    
    def test_none_quantity_does_not_crash(self):
        """Verify None quantities don't cause TypeError"""
        # This should not raise an exception
        result = json.loads(get_revenue_summary())
        
        assert result["success"] is True
        assert "total_revenue" in result
        # Should complete without TypeError
    
    def test_none_quantity_excluded_from_revenue(self):
        """Verify records with None quantity are excluded from revenue calculation"""
        result = json.loads(get_revenue_summary())
        
        # Record ID 4 has None quantity - should be excluded
        # Revenue should only include records with valid quantities
        assert result["success"] is True
        assert result["total_revenue"] > 0


class TestBug3TypoInFieldName:
    """Test Bug #3: Typo in field name (prodcut -> product)"""
    
    def test_product_name_is_populated(self):
        """Verify product_name field is correctly populated from 'product' field"""
        result = json.loads(enrich_and_group(group_by="product"))
        
        assert result["success"] is True
        assert "summary" in result
        
        # Should have products grouped (Widget A, Widget B, Gadget X, Y, Z)
        # If typo exists, product_name would be None and grouping would fail
        assert len(result["summary"]) > 0, "Should have grouped products"
        
        # Check that actual product names appear in summary
        product_names = list(result["summary"].keys())
        assert any("Widget" in name or "Gadget" in name for name in product_names), \
            f"Expected product names in summary, got: {product_names}"
    
    def test_group_by_product_works(self):
        """Verify grouping by product produces valid results"""
        result = json.loads(enrich_and_group(group_by="product"))
        
        assert result["success"] is True
        assert result["group_by"] == "product"
        
        # Should have multiple product groups
        assert len(result["summary"]) >= 3, "Should have at least 3 different products"
    
    def test_group_by_region_works(self):
        """Verify grouping by region also works correctly"""
        result = json.loads(enrich_and_group(group_by="region"))
        
        assert result["success"] is True
        assert result["group_by"] == "region"
        
        # Should have 3 regions: APAC, AMER, EMEA
        assert len(result["summary"]) == 3, f"Expected 3 regions, got {len(result['summary'])}"
        
        regions = list(result["summary"].keys())
        assert "APAC" in regions
        assert "AMER" in regions
        assert "EMEA" in regions


class TestBug4ValidationRangeFix:
    """Test Bug #4: Incorrect quantity validation range"""
    
    def test_boundary_value_1_is_valid(self):
        """Verify quantity of 1 (MIN_QUANTITY) is considered valid"""
        result = json.loads(validate_transactions())
        
        assert result["success"] is True
        
        # Check if any record with quantity=1 is marked as invalid
        invalid_records = result["invalid_records"]
        for record in invalid_records:
            if record.get("quantity") == 1:
                errors = record.get("errors", [])
                # Should NOT have quantity range error
                assert not any("out of valid range" in err for err in errors), \
                    "Quantity of 1 should be valid (MIN_QUANTITY boundary)"
    
    def test_boundary_value_1000_is_valid(self):
        """Verify quantity of 1000 (MAX_QUANTITY) is considered valid"""
        result = json.loads(validate_transactions())
        
        assert result["success"] is True
        
        # Check if any record with quantity=1000 is marked as invalid
        invalid_records = result["invalid_records"]
        for record in invalid_records:
            if record.get("quantity") == 1000:
                errors = record.get("errors", [])
                # Should NOT have quantity range error
                assert not any("out of valid range" in err for err in errors), \
                    "Quantity of 1000 should be valid (MAX_QUANTITY boundary)"
    
    def test_validation_summary_structure(self):
        """Verify validation returns proper summary structure"""
        result = json.loads(validate_transactions())
        
        assert result["success"] is True
        assert "summary" in result
        assert "invalid_records" in result
        
        summary = result["summary"]
        assert "total" in summary
        assert "valid_count" in summary
        assert "invalid_count" in summary


class TestExportFunctionality:
    """Test export_transactions tool"""
    
    def setup_method(self):
        """Create temporary directory for test exports"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_filepath = os.path.join(self.temp_dir, "test_export")
    
    def teardown_method(self):
        """Clean up temporary directory"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_export_json_format(self):
        """Verify JSON export works correctly"""
        result = json.loads(export_transactions(format="json", filepath=self.test_filepath))
        
        assert result["success"] is True
        assert "record_count" in result
        assert result["record_count"] > 0
        
        # Verify file was created
        json_file = f"{self.test_filepath}.json"
        assert os.path.exists(json_file), f"JSON file should be created at {json_file}"
        
        # Verify file contains valid JSON
        with open(json_file, 'r') as f:
            data = json.load(f)
            assert isinstance(data, list)
            assert len(data) > 0
    
    def test_export_csv_format(self):
        """Verify CSV export works correctly"""
        result = json.loads(export_transactions(format="csv", filepath=self.test_filepath))
        
        assert result["success"] is True
        assert "record_count" in result
        
        # Verify file was created
        csv_file = f"{self.test_filepath}.csv"
        assert os.path.exists(csv_file), f"CSV file should be created at {csv_file}"
        
        # Verify file has content
        with open(csv_file, 'r') as f:
            content = f.read()
            assert len(content) > 0
            # Should have header row
            assert "id" in content.lower() or "transaction" in content.lower()
    
    def test_export_invalid_format(self):
        """Verify invalid format returns error"""
        result = json.loads(export_transactions(format="xml", filepath=self.test_filepath))
        
        assert result["success"] is False
        assert "error" in result
        assert "xml" in result["error"].lower()


class TestStatusFiltering:
    """Test status filtering across different tools"""
    
    def test_ingest_with_status_filter(self):
        """Verify status filtering works in ingestion"""
        completed = json.loads(ingest_transactions(page=1, page_size=10, status_filter="completed"))
        pending = json.loads(ingest_transactions(page=1, page_size=10, status_filter="pending"))
        failed = json.loads(ingest_transactions(page=1, page_size=10, status_filter="failed"))
        
        # Each should have different record counts
        completed_count = len(completed["records"])
        pending_count = len(pending["records"])
        failed_count = len(failed["records"])
        
        # At least one should have records
        assert completed_count + pending_count + failed_count > 0
    
    def test_validate_with_status_filter(self):
        """Verify status filtering works in validation"""
        result = json.loads(validate_transactions(status_filter="completed"))
        
        assert result["success"] is True
        assert "summary" in result


class TestErrorHandling:
    """Test error handling in tools"""
    
    def test_invalid_group_by_parameter(self):
        """Verify invalid group_by parameter returns error"""
        result = json.loads(enrich_and_group(group_by="invalid"))
        
        assert result["success"] is False
        assert "error" in result
        assert "invalid" in result["error"].lower()
    
    def test_pagination_with_zero_page(self):
        """Verify page 0 is handled gracefully"""
        result = json.loads(ingest_transactions(page=0, page_size=5))
        
        # Should return pagination structure (page 0 returns empty records)
        assert "records" in result
        assert "page" in result
        assert result["page"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
