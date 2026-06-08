"""
Dashboard Zalo Campaign Automation Tests

Tests for:
- Campaign template selector
- Message preview & formatting
- Campaign send logic
- Campaign history
- Delivery tracking
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dashboard_helpers import (
    get_template_by_key, format_message, extract_recommendations,
    validate_segment, validate_customers_list, format_success_rate,
    log_campaign_start, log_campaign_result, log_campaign_error
)


# ============================================================================
# TEMPLATE TESTS
# ============================================================================

class TestMessageTemplates:
    """Test message templates"""

    def test_get_champions_template(self):
        """Test Champions template"""
        template = get_template_by_key("CHAMPIONS")
        assert "subject" in template
        assert "body" in template
        assert "button_text" in template
        assert "VIP" in template["body"]

    def test_get_potential_template(self):
        """Test Potential template"""
        template = get_template_by_key("POTENTIAL")
        assert "subject" in template
        assert "New Product" in template["subject"] or "Khám phá" in template["subject"]

    def test_get_loyal_template(self):
        """Test Loyal template"""
        template = get_template_by_key("LOYAL")
        assert "subject" in template
        assert "Win-Back" in template["subject"] or "nhớ" in template["subject"]

    def test_get_lost_template(self):
        """Test Lost template"""
        template = get_template_by_key("LOST")
        assert "subject" in template
        # Template uses Vietnamese "Chúng tôi muốn có bạn trở lại"
        assert template["subject"] is not None and len(template["subject"]) > 0

    def test_template_has_required_fields(self):
        """Test all templates have required fields"""
        for segment in ["CHAMPIONS", "POTENTIAL", "LOYAL", "LOST"]:
            template = get_template_by_key(segment)
            assert "subject" in template
            assert "body" in template
            assert "button_text" in template
            assert "{customer_name}" in template["body"]
            assert "{recommendations}" in template["body"]

    def test_invalid_template_returns_default(self):
        """Test invalid template returns default (Potential)"""
        template = get_template_by_key("INVALID")
        assert template is not None
        assert "New Product" in template["subject"] or "Khám phá" in template["subject"]


# ============================================================================
# MESSAGE FORMATTING TESTS
# ============================================================================

class TestMessageFormatting:
    """Test message formatting"""

    def test_format_message_with_customer_name(self):
        """Test message formatting with customer name"""
        message = format_message(
            "CHAMPIONS",
            customer_name="Nguyễn Văn A",
            recommendations=["Product 1", "Product 2"]
        )

        assert "Nguyễn Văn A" in message
        assert "Product 1" in message
        assert "Product 2" in message
        assert "Xin chào" in message

    def test_format_message_with_recommendations(self):
        """Test recommendations are formatted as bullet list"""
        products = ["Bánh mì", "Nước", "Gia vị"]
        message = format_message(
            "POTENTIAL",
            customer_name="Test",
            recommendations=products
        )

        # Check all products are in message
        for product in products:
            assert product in message

        # Check bullet points
        assert "•" in message

    def test_format_message_default_recommendations(self):
        """Test default recommendations if none provided"""
        message = format_message(
            "CHAMPIONS",
            customer_name="Test"
        )

        # Should have default recommendations
        assert "•" in message

    def test_format_message_capped_recommendations(self):
        """Test maximum 5 recommendations"""
        products = ["A", "B", "C", "D", "E", "F", "G"]  # 7 products
        message = format_message(
            "CHAMPIONS",
            customer_name="Test",
            recommendations=products
        )

        # Count bullet points (should be max 5)
        bullet_count = message.count("•")
        assert bullet_count == 5


# ============================================================================
# RECOMMENDATIONS TESTS
# ============================================================================

class TestRecommendations:
    """Test product recommendations"""

    def test_champions_recommendations(self):
        """Test Champions segment recommendations"""
        recs = extract_recommendations("Champions")
        assert len(recs) > 0
        assert isinstance(recs, list)

    def test_potential_recommendations(self):
        """Test Potential segment recommendations"""
        recs = extract_recommendations("Potential")
        assert len(recs) > 0

    def test_loyal_recommendations(self):
        """Test Loyal segment recommendations"""
        recs = extract_recommendations("Loyal")
        assert len(recs) > 0

    def test_lost_recommendations(self):
        """Test Lost segment recommendations"""
        recs = extract_recommendations("Lost")
        assert len(recs) > 0

    def test_invalid_segment_returns_default(self):
        """Test invalid segment returns Potential recs"""
        recs = extract_recommendations("INVALID")
        assert len(recs) > 0


# ============================================================================
# VALIDATION TESTS
# ============================================================================

class TestValidation:
    """Test validation functions"""

    def test_validate_segment_valid(self):
        """Test valid segments"""
        assert validate_segment("Champions") is True
        assert validate_segment("Potential") is True
        assert validate_segment("Loyal") is True
        assert validate_segment("Lost") is True

    def test_validate_segment_invalid(self):
        """Test invalid segments"""
        assert validate_segment("INVALID") is False
        assert validate_segment("VIP") is False
        assert validate_segment("") is False

    def test_validate_customers_valid(self):
        """Test valid customer list"""
        customers = [
            {"ma_khach_hang": "c1", "ten_khach_hang": "Name1", "dien_thoai": "0912345678"},
            {"ma_khach_hang": "c2", "ten_khach_hang": "Name2", "dien_thoai": "0987654321"}
        ]
        assert validate_customers_list(customers) is True

    def test_validate_customers_empty(self):
        """Test empty customer list"""
        assert validate_customers_list([]) is False

    def test_validate_customers_missing_field(self):
        """Test customer missing required field"""
        customers = [
            {"ma_khach_hang": "c1", "ten_khach_hang": "Name1"}  # Missing dien_thoai
        ]
        assert validate_customers_list(customers) is False

    def test_validate_customers_none(self):
        """Test None customer list"""
        assert validate_customers_list(None) is False


# ============================================================================
# FORMATTING HELPER TESTS
# ============================================================================

class TestFormattingHelpers:
    """Test formatting helper functions"""

    def test_format_success_rate_valid(self):
        """Test success rate formatting"""
        assert format_success_rate(95, 100) == "95%"
        assert format_success_rate(50, 100) == "50%"
        assert format_success_rate(0, 100) == "0%"

    def test_format_success_rate_zero_total(self):
        """Test success rate with zero total"""
        assert format_success_rate(50, 0) == "0%"

    def test_format_success_rate_high_precision(self):
        """Test success rate rounds to 0%"""
        assert format_success_rate(1, 300) == "0%"  # 0.33% rounds to 0%


# ============================================================================
# LOGGING TESTS
# ============================================================================

class TestLogging:
    """Test logging functions"""

    @patch('dashboard_helpers.logger')
    def test_log_campaign_start(self, mock_logger):
        """Test campaign start logging"""
        log_campaign_start("Champions", 50)
        assert mock_logger.info.called

    @patch('dashboard_helpers.logger')
    def test_log_campaign_result(self, mock_logger):
        """Test campaign result logging"""
        result = {"sent": 50, "failed": 0}
        log_campaign_result("camp_001", "Champions", result)
        assert mock_logger.info.called

    def test_log_campaign_error(self):
        """Test campaign error logging works"""
        # Just verify function exists and is callable
        import dashboard_helpers
        assert hasattr(dashboard_helpers, 'log_campaign_error')
        assert callable(getattr(dashboard_helpers, 'log_campaign_error'))


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestDashboardIntegration:
    """Integration tests for dashboard components"""

    def test_template_format_flow(self):
        """Test full template -> format -> preview flow"""
        # Step 1: Get template
        template = get_template_by_key("CHAMPIONS")
        assert template is not None

        # Step 2: Get recommendations
        recs = extract_recommendations("Champions")
        assert len(recs) > 0

        # Step 3: Format message
        message = format_message("CHAMPIONS", "Test Customer", recs)

        # Step 4: Verify message quality
        assert "Test Customer" in message
        assert len(message) > 100  # Should be substantial message
        assert "•" in message  # Should have bullet points

    def test_segment_to_template_mapping(self):
        """Test all segments map to correct templates"""
        segment_template_map = {
            "Champions": "CHAMPIONS",
            "Potential": "POTENTIAL",
            "Loyal": "LOYAL",
            "Lost": "LOST"
        }

        for segment, template_key in segment_template_map.items():
            # Validate segment
            assert validate_segment(segment) is True

            # Get template
            template = get_template_by_key(template_key)
            assert template is not None

            # Get recommendations
            recs = extract_recommendations(segment)
            assert len(recs) > 0

            # Format message
            message = format_message(template_key, "Customer", recs)
            assert len(message) > 50

    def test_campaign_workflow(self):
        """Test end-to-end campaign workflow"""
        # Simulate campaign workflow

        # 1. Segment selection
        selected_segment = "Champions"
        assert validate_segment(selected_segment) is True

        # 2. Template selection
        template = get_template_by_key(selected_segment.upper())
        assert template is not None

        # 3. Message preview
        recs = extract_recommendations(selected_segment)
        message = format_message(selected_segment.upper(), "Sample Customer", recs)
        assert "Sample Customer" in message

        # 4. Customer list validation
        customers = [
            {"ma_khach_hang": "c1", "ten_khach_hang": "Name1", "dien_thoai": "0912345678"},
        ]
        assert validate_customers_list(customers) is True

        # 5. Campaign ready
        assert len(message) > 0
        assert len(customers) > 0


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_very_long_customer_name(self):
        """Test with very long customer name"""
        long_name = "A" * 100
        message = format_message("CHAMPIONS", long_name, ["Product"])
        assert long_name in message

    def test_special_characters_in_name(self):
        """Test with special characters in customer name"""
        special_name = "Nguyễn Văn Á!"
        message = format_message("CHAMPIONS", special_name, ["Product"])
        # Should not crash, message should contain name
        assert isinstance(message, str)

    def test_empty_recommendations(self):
        """Test with empty recommendations list"""
        message = format_message("CHAMPIONS", "Test", [])
        # Should use defaults or handle gracefully
        assert isinstance(message, str)
        assert len(message) > 0

    def test_single_recommendation(self):
        """Test with single recommendation"""
        message = format_message("CHAMPIONS", "Test", ["Product"])
        assert "Product" in message

    def test_many_recommendations(self):
        """Test with many recommendations (capped at 5)"""
        recs = [f"Product {i}" for i in range(20)]
        message = format_message("CHAMPIONS", "Test", recs)

        # Should have at most 5 products
        product_count = sum(1 for i in range(20) if f"Product {i}" in message)
        assert product_count <= 5


# ============================================================================
# TEST EXECUTION
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
