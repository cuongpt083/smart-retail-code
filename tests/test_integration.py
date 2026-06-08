"""
Integration Tests for Phase 4B - Kiotviet API & Zalo Messaging

Comprehensive test suite for:
- Kiotviet API client initialization and configuration
- Zalo messenger message templates and segmentation
- Campaign tracking and analytics
- End-to-end data flow validation
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import tempfile
import os
import sqlite3

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kiotviet_client import KiotvietClient, create_kiotviet_client
from zalo_messenger import ZaloMessenger, SegmentType, create_zalo_messenger


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def kiotviet_client():
    """Create Kiotviet client for testing"""
    return KiotvietClient(
        retail_id="test_retail_123",
        api_key="test_api_key_xyz",
        db_path=":memory:"
    )


@pytest.fixture
def zalo_messenger():
    """Create Zalo messenger for testing"""
    return ZaloMessenger(
        access_token="test_zalo_token_abc",
        db_path=":memory:"
    )


@pytest.fixture
def sample_customers_native():
    """Sample customers in native SQLite format"""
    return [
        {
            "ma_khach_hang": "cust_001",
            "ten_khach_hang": "Nguyễn Văn A",
            "dien_thoai": "0912345678",
            "dia_chi": "123 Main St",
            "email": "a@example.com"
        },
        {
            "ma_khach_hang": "cust_002",
            "ten_khach_hang": "Trần Thị B",
            "dien_thoai": "0987654321",
            "dia_chi": "456 Side St",
            "email": "b@example.com"
        },
    ]


# ============================================================================
# KIOTVIET CLIENT TESTS
# ============================================================================

class TestKiotvietClientSetup:
    """Test Kiotviet client initialization"""

    def test_client_initialization(self, kiotviet_client):
        """Test client initialization with credentials"""
        assert kiotviet_client.retail_id == "test_retail_123"
        assert kiotviet_client.api_key == "test_api_key_xyz"
        assert kiotviet_client.db_path == ":memory:"

    def test_session_creation(self, kiotviet_client):
        """Test HTTP session is properly configured"""
        assert kiotviet_client.session is not None
        assert kiotviet_client.headers["Retailer"] == "test_retail_123"
        assert kiotviet_client.headers["Authorization"] == "test_api_key_xyz"
        assert kiotviet_client.headers["Content-Type"] == "application/json"

    def test_base_url_configured(self, kiotviet_client):
        """Test API base URL is set"""
        assert kiotviet_client.BASE_URL == "https://api.kiotviet.vn"

    def test_factory_function(self):
        """Test factory function creates proper client"""
        client = create_kiotviet_client(
            "test_id",
            "test_key",
            ":memory:"
        )

        assert isinstance(client, KiotvietClient)
        assert client.retail_id == "test_id"
        assert client.api_key == "test_key"

    @patch('requests.Session.get')
    def test_get_customers_error_handling(self, mock_get, kiotviet_client):
        """Test error handling when fetching customers"""
        mock_get.side_effect = Exception("Connection error")

        customers = kiotviet_client.get_customers()

        assert customers == []


# ============================================================================
# ZALO MESSENGER TESTS
# ============================================================================

class TestZaloMessengerSetup:
    """Test Zalo messenger initialization and templates"""

    def test_messenger_initialization(self, zalo_messenger):
        """Test messenger initialization"""
        assert zalo_messenger.access_token == "test_zalo_token_abc"
        assert zalo_messenger.db_path == ":memory:"

    def test_base_url_configured(self, zalo_messenger):
        """Test Zalo API base URL"""
        assert zalo_messenger.BASE_URL == "https://openapi.zalo.me/v2.0"

    def test_templates_for_all_segments(self, zalo_messenger):
        """Test message templates exist for all RFM segments"""
        templates = zalo_messenger.templates

        assert SegmentType.CHAMPIONS.value in templates
        assert SegmentType.POTENTIAL.value in templates
        assert SegmentType.LOYAL.value in templates
        assert SegmentType.LOST.value in templates

    def test_template_structure(self, zalo_messenger):
        """Test each template has required fields"""
        for segment_name, template in zalo_messenger.templates.items():
            assert "subject" in template, f"Missing subject in {segment_name}"
            assert "body" in template, f"Missing body in {segment_name}"
            assert "button_text" in template, f"Missing button_text in {segment_name}"

    def test_factory_function(self):
        """Test factory function creates proper messenger"""
        messenger = create_zalo_messenger(
            "test_token",
            ":memory:"
        )

        assert isinstance(messenger, ZaloMessenger)
        assert messenger.access_token == "test_token"


# ============================================================================
# MESSAGE SENDING TESTS
# ============================================================================

class TestZaloMessaging:
    """Test Zalo message sending functionality"""

    @patch('requests.post')
    def test_send_single_message(self, mock_post, zalo_messenger):
        """Test sending a single message"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": 0,
            "data": {"message_id": "msg_123"}
        }
        mock_post.return_value = mock_response

        result = zalo_messenger.send_message(
            customer_id="cust_001",
            customer_phone="0912345678",
            message="Test message"
        )

        assert result["success"] is True
        assert result["message_id"] == "msg_123"
        assert result["customer_id"] == "cust_001"
        assert "sent_at" in result

    @patch('requests.post')
    def test_send_message_failure(self, mock_post, zalo_messenger):
        """Test handling of message send failures"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": 1,
            "message": "Invalid phone"
        }
        mock_post.return_value = mock_response

        result = zalo_messenger.send_message(
            customer_id="cust_001",
            customer_phone="invalid",
            message="Test"
        )

        assert result["success"] is False
        assert result["error"] == "Invalid phone"

    def test_format_recommendations_valid(self, zalo_messenger):
        """Test formatting product recommendations"""
        products = ["Bánh mì", "Nước", "Gia vị"]
        formatted = zalo_messenger._format_recommendations(products)

        assert "Bánh mì" in formatted
        assert "Nước" in formatted
        assert "•" in formatted
        assert formatted.count("•") == 3

    def test_format_recommendations_default(self, zalo_messenger):
        """Test default recommendations when none provided"""
        formatted = zalo_messenger._format_recommendations(None)

        assert formatted  # Not empty
        assert "•" in formatted

    @patch('requests.post')
    def test_send_product_recommendation(self, mock_post, zalo_messenger):
        """Test sending personalized product recommendations"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": 0,
            "data": {"message_id": "msg_456"}
        }
        mock_post.return_value = mock_response

        products = [
            {"ten_hang": "Bánh mì", "gia_ban": 15000},
            {"ten_hang": "Nước", "gia_ban": 5000},
        ]

        result = zalo_messenger.send_product_recommendation(
            customer_id="cust_001",
            customer_phone="0912345678",
            customer_name="Nguyễn Văn A",
            products=products
        )

        assert result["success"] is True


# ============================================================================
# CAMPAIGN MANAGEMENT TESTS
# ============================================================================

class TestCampaignManagement:
    """Test campaign tracking and analytics"""

    def test_track_campaign_success(self, zalo_messenger):
        """Test tracking campaign metrics"""
        result = zalo_messenger.track_campaign(
            campaign_id="camp_001",
            segment="Champions",
            sent_count=100,
            success_count=95
        )

        assert result["success"] is True
        assert result["campaign_id"] == "camp_001"
        assert result["success_rate"] == 0.95

    def test_track_campaign_zero_sent(self, zalo_messenger):
        """Test campaign with zero messages sent"""
        result = zalo_messenger.track_campaign(
            campaign_id="camp_002",
            segment="Lost",
            sent_count=0,
            success_count=0
        )

        assert result["success_rate"] == 0

    def test_campaign_stats_retrieval(self):
        """Test retrieving campaign statistics"""
        fd, db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        try:
            # Create campaigns table
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""CREATE TABLE campaigns (
                campaign_id TEXT PRIMARY KEY,
                segment TEXT,
                sent_at TIMESTAMP,
                sent_count INTEGER,
                success_count INTEGER,
                failure_count INTEGER,
                success_rate REAL
            )""")
            conn.commit()
            conn.close()

            # Create messenger and track campaign
            messenger = ZaloMessenger("test_token", db_path)
            messenger.track_campaign("camp_001", "Champions", 100, 95)

            # Retrieve stats
            stats = messenger.get_campaign_stats()

            assert len(stats) == 1
            assert stats[0]["campaign_id"] == "camp_001"
            assert stats[0]["success_rate"] == 0.95

        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    @patch('requests.post')
    def test_segment_campaign_sending(self, mock_post, zalo_messenger, sample_customers_native):
        """Test sending campaign to entire RFM segment"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": 0,
            "data": {"message_id": "msg_"}
        }
        mock_post.return_value = mock_response

        result = zalo_messenger.send_segment_campaign(
            segment=SegmentType.CHAMPIONS,
            customers=sample_customers_native,
            recommendations=["Bánh mì", "Nước"]
        )

        assert result["segment"] == "Champions"
        assert result["sent"] == 2
        assert result["failed"] == 0
        assert len(result["message_ids"]) == 2


# ============================================================================
# INTEGRATION WORKFLOW TESTS
# ============================================================================

class TestIntegrationWorkflows:
    """Test end-to-end integration workflows"""

    def test_client_configuration_consistency(self):
        """Test Kiotviet and Zalo clients are independently configured"""
        kiotviet = KiotvietClient("retail_123", "key_123", ":memory:")
        zalo = ZaloMessenger("token_123", ":memory:")

        # Verify clients are separate
        assert kiotviet.retail_id != zalo.access_token
        assert kiotviet.api_key != zalo.access_token
        assert isinstance(kiotviet, KiotvietClient)
        assert isinstance(zalo, ZaloMessenger)

    @patch('requests.post')
    def test_kiotviet_to_zalo_message_flow(self, mock_post, sample_customers_native):
        """Test data flow from Kiotviet customers to Zalo messages"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": 0, "data": {"message_id": "msg_001"}}
        mock_post.return_value = mock_response

        # Initialize clients
        kiotviet_client = KiotvietClient("test_id", "test_key", ":memory:")
        zalo_messenger = ZaloMessenger("test_token", ":memory:")

        # Simulate receiving customers from Kiotviet
        customers = sample_customers_native

        # Send campaign via Zalo
        campaign_result = zalo_messenger.send_segment_campaign(
            segment=SegmentType.CHAMPIONS,
            customers=customers,
            recommendations=["Bánh mì", "Nước"]
        )

        # Verify campaign execution
        assert campaign_result["segment"] == "Champions"
        assert campaign_result["sent"] == 2
        assert campaign_result["failed"] == 0

    def test_database_isolation(self):
        """Test database isolation between clients"""
        fd1, db_path1 = tempfile.mkstemp(suffix=".db")
        fd2, db_path2 = tempfile.mkstemp(suffix=".db")
        os.close(fd1)
        os.close(fd2)

        try:
            client1 = KiotvietClient("id1", "key1", db_path1)
            client2 = KiotvietClient("id2", "key2", db_path2)

            # Verify they use different databases
            assert client1.db_path != client2.db_path

        finally:
            if os.path.exists(db_path1):
                os.remove(db_path1)
            if os.path.exists(db_path2):
                os.remove(db_path2)


# ============================================================================
# TEST EXECUTION
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
