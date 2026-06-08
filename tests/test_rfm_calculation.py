"""
Test suite for RFM (Recency, Frequency, Monetary) calculation
Test-Driven Development: Tests written BEFORE implementation

RFM Scoring:
- R (Recency): Days since last purchase (0-90 days) → Score 1-5
- F (Frequency): Number of purchases (0-30) → Score 1-5
- M (Monetary): Total spending (0-10M VND) → Score 1-5

Score mapping (inverse for Recency):
- Score 5: Top 20% (Best)
- Score 4: 21-40%
- Score 3: 41-60% (Middle)
- Score 2: 61-80%
- Score 1: 81-100% (Worst)
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestRecencyCalculation:
    """Test Recency (R) calculation - days since last purchase"""

    @pytest.mark.rfm
    def test_recency_today(self):
        """Customer purchased today → Recency = 0 days"""
        from rfm_calculator import calculate_recency

        today = datetime.now().date()
        last_purchase = today

        result = calculate_recency(last_purchase, today)
        assert result == 0, "Same day purchase should have recency of 0"

    @pytest.mark.rfm
    def test_recency_7_days_ago(self):
        """Customer purchased 7 days ago → Recency = 7 days"""
        from rfm_calculator import calculate_recency

        today = datetime.now().date()
        last_purchase = today - timedelta(days=7)

        result = calculate_recency(last_purchase, today)
        assert result == 7, "7 days ago should have recency of 7"

    @pytest.mark.rfm
    def test_recency_90_days_ago(self):
        """Customer purchased 90 days ago → Recency = 90 days"""
        from rfm_calculator import calculate_recency

        today = datetime.now().date()
        last_purchase = today - timedelta(days=90)

        result = calculate_recency(last_purchase, today)
        assert result == 90, "90 days ago should have recency of 90"

    @pytest.mark.rfm
    def test_recency_none(self):
        """Customer never purchased → Recency = None or max days"""
        from rfm_calculator import calculate_recency

        today = datetime.now().date()
        last_purchase = None

        result = calculate_recency(last_purchase, today)
        assert result is None or result > 100, "Never purchased should be None or very high"


class TestFrequencyCalculation:
    """Test Frequency (F) calculation - number of purchases"""

    @pytest.mark.rfm
    def test_frequency_single_purchase(self):
        """Customer with 1 purchase → Frequency = 1"""
        from rfm_calculator import calculate_frequency

        # One invoice
        invoices = pd.DataFrame({
            'ma_hoa_don': ['HD001'],
            'ma_khach_hang': ['KH001']
        })

        result = calculate_frequency('KH001', invoices)
        assert result == 1, "Single purchase should have frequency of 1"

    @pytest.mark.rfm
    def test_frequency_multiple_purchases(self):
        """Customer with 10 purchases → Frequency = 10"""
        from rfm_calculator import calculate_frequency

        invoices = pd.DataFrame({
            'ma_hoa_don': [f'HD{i:03d}' for i in range(10)],
            'ma_khach_hang': ['KH001'] * 10
        })

        result = calculate_frequency('KH001', invoices)
        assert result == 10, "10 purchases should have frequency of 10"

    @pytest.mark.rfm
    def test_frequency_no_purchases(self):
        """Customer with no purchases → Frequency = 0"""
        from rfm_calculator import calculate_frequency

        invoices = pd.DataFrame({
            'ma_hoa_don': ['HD001', 'HD002'],
            'ma_khach_hang': ['KH001', 'KH001']
        })

        result = calculate_frequency('KH999', invoices)
        assert result == 0, "Non-existent customer should have frequency of 0"

    @pytest.mark.rfm
    def test_frequency_empty_invoices(self):
        """Empty invoice list → Frequency = 0"""
        from rfm_calculator import calculate_frequency

        invoices = pd.DataFrame({
            'ma_hoa_don': [],
            'ma_khach_hang': []
        })

        result = calculate_frequency('KH001', invoices)
        assert result == 0, "Empty invoices should return 0"


class TestMonetaryCalculation:
    """Test Monetary (M) calculation - total spending"""

    @pytest.mark.rfm
    def test_monetary_single_purchase(self):
        """Customer with 1 purchase (1M VND) → Monetary = 1M"""
        from rfm_calculator import calculate_monetary

        invoices = pd.DataFrame({
            'ma_hoa_don': ['HD001'],
            'ma_khach_hang': ['KH001'],
            'khach_da_tra': [1000000]
        })

        result = calculate_monetary('KH001', invoices)
        assert result == 1000000, "Single 1M purchase should sum to 1M"

    @pytest.mark.rfm
    def test_monetary_multiple_purchases(self):
        """Customer with 3 purchases (1M + 2M + 3M) → Monetary = 6M"""
        from rfm_calculator import calculate_monetary

        invoices = pd.DataFrame({
            'ma_hoa_don': ['HD001', 'HD002', 'HD003'],
            'ma_khach_hang': ['KH001', 'KH001', 'KH001'],
            'khach_da_tra': [1000000, 2000000, 3000000]
        })

        result = calculate_monetary('KH001', invoices)
        assert result == 6000000, "Sum should be 6M VND"

    @pytest.mark.rfm
    def test_monetary_no_purchases(self):
        """Customer with no purchases → Monetary = 0"""
        from rfm_calculator import calculate_monetary

        invoices = pd.DataFrame({
            'ma_hoa_don': ['HD001'],
            'ma_khach_hang': ['KH001'],
            'khach_da_tra': [1000000]
        })

        result = calculate_monetary('KH999', invoices)
        assert result == 0, "Non-existent customer should have monetary of 0"

    @pytest.mark.rfm
    def test_monetary_empty_invoices(self):
        """Empty invoice list → Monetary = 0"""
        from rfm_calculator import calculate_monetary

        invoices = pd.DataFrame({
            'ma_hoa_don': [],
            'ma_khach_hang': [],
            'khach_da_tra': []
        })

        result = calculate_monetary('KH001', invoices)
        assert result == 0, "Empty invoices should return 0"


class TestRFMScoring:
    """Test RFM score conversion (0-90 days/count/amount → 1-5 score)"""

    @pytest.mark.rfm
    def test_recency_scoring_recent(self):
        """Recent purchase (0-18 days) → Score 5"""
        from rfm_calculator import score_recency

        for days in [0, 5, 10, 15, 18]:
            score = score_recency(days)
            assert score == 5, f"{days} days should score 5"

    @pytest.mark.rfm
    def test_recency_scoring_medium(self):
        """Medium recent (37-54 days) → Score 3"""
        from rfm_calculator import score_recency

        for days in [37, 45, 50, 54]:
            score = score_recency(days)
            assert score == 3, f"{days} days should score 3"

    @pytest.mark.rfm
    def test_recency_scoring_old(self):
        """Old purchase (72-90+ days) → Score 1"""
        from rfm_calculator import score_recency

        for days in [72, 80, 90, 120]:
            score = score_recency(days)
            assert score == 1, f"{days} days should score 1"

    @pytest.mark.rfm
    def test_frequency_scoring_high(self):
        """High frequency (24-30 purchases) → Score 5"""
        from rfm_calculator import score_frequency

        for freq in [24, 25, 28, 30, 100]:
            score = score_frequency(freq)
            assert score == 5, f"{freq} purchases should score 5"

    @pytest.mark.rfm
    def test_frequency_scoring_low(self):
        """Low frequency (0-6 purchases) → Score 1"""
        from rfm_calculator import score_frequency

        for freq in [0, 1, 3, 6]:
            score = score_frequency(freq)
            assert score == 1, f"{freq} purchases should score 1"

    @pytest.mark.rfm
    def test_monetary_scoring_high(self):
        """High spending (8M-10M+ VND) → Score 5"""
        from rfm_calculator import score_monetary

        for amount in [8000000, 9000000, 10000000, 15000000]:
            score = score_monetary(amount)
            assert score == 5, f"{amount} VND should score 5"

    @pytest.mark.rfm
    def test_monetary_scoring_low(self):
        """Low spending (0-2M VND) → Score 1"""
        from rfm_calculator import score_monetary

        for amount in [0, 500000, 1000000, 2000000]:
            score = score_monetary(amount)
            assert score == 1, f"{amount} VND should score 1"


class TestRFMSegmentation:
    """Test RFM segmentation logic (Champions, Potential, Loyal, Lost)"""

    @pytest.mark.rfm
    def test_segment_champion(self):
        """R=5, F=5, M=5 → Champion"""
        from rfm_calculator import segment_customer

        result = segment_customer(r_score=5, f_score=5, m_score=5)
        assert result == 'Champions', "5-5-5 should be Champion"

    @pytest.mark.rfm
    def test_segment_potential(self):
        """R=5, F=2, M=1 → Potential"""
        from rfm_calculator import segment_customer

        result = segment_customer(r_score=5, f_score=2, m_score=1)
        assert result == 'Potential', "5-2-1 should be Potential"

    @pytest.mark.rfm
    def test_segment_loyal(self):
        """R=2, F=5, M=5 → Loyal"""
        from rfm_calculator import segment_customer

        result = segment_customer(r_score=2, f_score=5, m_score=5)
        assert result == 'Loyal', "2-5-5 should be Loyal"

    @pytest.mark.rfm
    def test_segment_lost(self):
        """R=1, F=1, M=1 → Lost"""
        from rfm_calculator import segment_customer

        result = segment_customer(r_score=1, f_score=1, m_score=1)
        assert result == 'Lost', "1-1-1 should be Lost"

    @pytest.mark.rfm
    def test_segment_at_risk(self):
        """R=2, F=4, M=4 → At-risk (loyal but not recent)"""
        from rfm_calculator import segment_customer

        result = segment_customer(r_score=2, f_score=4, m_score=4)
        assert result == 'Loyal', "2-4-4 should be Loyal (at-risk)"


class TestRFMEndToEnd:
    """End-to-end RFM calculation test"""

    @pytest.mark.rfm
    def test_rfm_calculation_full_flow(self, rfm_test_customers, rfm_test_invoices):
        """Test complete RFM calculation for all customers"""
        from rfm_calculator import calculate_rfm_for_customers

        today = datetime.now().date()
        result = calculate_rfm_for_customers(rfm_test_customers, rfm_test_invoices, today)

        # Verify output structure
        assert isinstance(result, pd.DataFrame), "Result should be DataFrame"
        assert 'rfm_segment' in result.columns, "Should have rfm_segment column"
        assert 'r_score' in result.columns, "Should have r_score column"
        assert 'f_score' in result.columns, "Should have f_score column"
        assert 'm_score' in result.columns, "Should have m_score column"

        # Verify Champion customer
        champion = result[result['ma_khach_hang'] == 'KH_CHAMPION']
        assert not champion.empty, "Champion customer should exist"
        assert champion.iloc[0]['rfm_segment'] == 'Champions', "KH_CHAMPION should be Champions"

    @pytest.mark.rfm
    def test_rfm_customer_count(self, rfm_test_customers, rfm_test_invoices):
        """Test that RFM result has all customers"""
        from rfm_calculator import calculate_rfm_for_customers

        today = datetime.now().date()
        result = calculate_rfm_for_customers(rfm_test_customers, rfm_test_invoices, today)

        assert len(result) == len(rfm_test_customers), "Result should have all customers"


class TestRFMDataValidation:
    """Test data validation in RFM calculation"""

    @pytest.mark.rfm
    def test_handles_missing_customer(self):
        """Handle customer in invoice but not in customer list"""
        from rfm_calculator import calculate_frequency

        customers = pd.DataFrame({
            'ma_khach_hang': ['KH001']
        })

        invoices = pd.DataFrame({
            'ma_hoa_don': ['HD001', 'HD002'],
            'ma_khach_hang': ['KH001', 'KH999']  # KH999 not in customer list
        })

        result = calculate_frequency('KH001', invoices)
        assert result == 1, "Should only count valid customer invoices"

    @pytest.mark.rfm
    def test_handles_zero_invoices(self):
        """Handle zero total purchase amount"""
        from rfm_calculator import calculate_monetary

        invoices = pd.DataFrame({
            'ma_hoa_don': ['HD001'],
            'ma_khach_hang': ['KH001'],
            'khach_da_tra': [0]
        })

        result = calculate_monetary('KH001', invoices)
        assert result == 0, "Zero purchase should return 0"

    @pytest.mark.rfm
    def test_handles_negative_values(self):
        """Handle potential negative values (refunds)"""
        from rfm_calculator import calculate_monetary

        invoices = pd.DataFrame({
            'ma_hoa_don': ['HD001', 'HD002'],
            'ma_khach_hang': ['KH001', 'KH001'],
            'khach_da_tra': [1000000, -100000]  # Refund
        })

        result = calculate_monetary('KH001', invoices)
        assert result == 900000, "Should handle refunds correctly"
