"""
Test suite for Apriori Market Basket Analysis
Test-Driven Development: Tests written BEFORE implementation

Apriori Analysis:
- Support: % of transactions containing item(s)
- Confidence: If customer buys A, % chance they buy B
- Lift: How much more likely A and B are bought together vs independently

Example:
- 65% of people who buy Bánh mì (A) also buy Nước (B)
- Support = 12% (12% of all transactions have both A & B)
- Confidence = 65% (if you buy A, 65% chance you buy B)
- Lift = 2.3 (buying A & B together is 2.3x more likely than random)
"""

import pytest
import pandas as pd
import numpy as np
from typing import List, Dict
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestAprioriSupport:
    """Test support calculation - % of transactions containing item(s)"""

    @pytest.mark.apriori
    def test_support_single_item(self):
        """Product A appears in 20 out of 100 transactions → Support = 20%"""
        from apriori_miner import calculate_support

        transactions = [
            {'items': ['A', 'B']},
            {'items': ['A', 'C']},
            {'items': ['B', 'C']},
            # A appears 2 times out of 3 = 66.7%
        ] * 33 + [
            {'items': ['B', 'C']},
        ]  # 100 total, A in 66

        result = calculate_support('A', transactions)
        assert 0.65 < result < 0.70, f"Support should be ~66%, got {result:.2%}"

    @pytest.mark.apriori
    def test_support_item_pair(self):
        """Items A and B together appear in 10 out of 100 → Support = 10%"""
        from apriori_miner import calculate_support

        transactions = [
            {'items': ['A', 'B']},  # 10 times
        ] * 10 + [
            {'items': ['A', 'C']},  # 30 times
        ] * 30 + [
            {'items': ['B', 'C']},  # 60 times
        ] * 60

        result = calculate_support(['A', 'B'], transactions)
        assert result == 0.10, f"Support should be 10%, got {result:.2%}"

    @pytest.mark.apriori
    def test_support_zero(self):
        """Item Z never appears → Support = 0%"""
        from apriori_miner import calculate_support

        transactions = [
            {'items': ['A', 'B']},
            {'items': ['B', 'C']},
            {'items': ['A', 'C']},
        ]

        result = calculate_support('Z', transactions)
        assert result == 0, "Support for non-existent item should be 0"

    @pytest.mark.apriori
    def test_support_all(self):
        """Item appears in all transactions → Support = 100%"""
        from apriori_miner import calculate_support

        transactions = [
            {'items': ['A', 'B']},
            {'items': ['A', 'C']},
            {'items': ['A', 'D']},
        ]

        result = calculate_support('A', transactions)
        assert result == 1.0, "Support for item in all transactions should be 100%"


class TestAprioriConfidence:
    """Test confidence calculation - If A, then what % chance B"""

    @pytest.mark.apriori
    def test_confidence_basic(self):
        """If customer buys Bánh mì, 65% also buy Nước"""
        from apriori_miner import calculate_confidence

        transactions = [
            {'items': ['Bánh mì', 'Nước']},  # 65
        ] * 65 + [
            {'items': ['Bánh mì']},  # 35 (only Bánh, no Nước)
        ] * 35

        result = calculate_confidence('Bánh mì', 'Nước', transactions)
        assert result == 0.65, f"Confidence should be 65%, got {result:.2%}"

    @pytest.mark.apriori
    def test_confidence_zero(self):
        """If customer buys A, 0% chance they buy Z (Z never occurs)"""
        from apriori_miner import calculate_confidence

        transactions = [
            {'items': ['A', 'B']},
            {'items': ['A', 'C']},
        ]

        result = calculate_confidence('A', 'Z', transactions)
        assert result == 0, "Confidence should be 0% if B never appears"

    @pytest.mark.apriori
    def test_confidence_100(self):
        """If customer buys A, 100% buy B (always together)"""
        from apriori_miner import calculate_confidence

        transactions = [
            {'items': ['A', 'B']},
            {'items': ['A', 'B']},
            {'items': ['A', 'B']},
        ]

        result = calculate_confidence('A', 'B', transactions)
        assert result == 1.0, "Confidence should be 100% if always together"

    @pytest.mark.apriori
    def test_confidence_antecedent_missing(self):
        """Confidence for item that never appears → 0"""
        from apriori_miner import calculate_confidence

        transactions = [
            {'items': ['B', 'C']},
            {'items': ['B', 'C']},
        ]

        result = calculate_confidence('Z', 'B', transactions)
        assert result == 0, "Confidence should be 0 if antecedent never appears"


class TestAprioriLift:
    """Test lift calculation - How much more likely together vs independent"""

    @pytest.mark.apriori
    def test_lift_positive(self):
        """Lift > 1: Items are bought together more than random"""
        from apriori_miner import calculate_lift

        # A in 50 out of 100
        # B in 40 out of 100
        # A and B together in 30 out of 100
        # Lift = (30/100) / ((50/100) * (40/100)) = 0.30 / 0.20 = 1.5

        transactions = [
            {'items': ['A', 'B']},  # 30
        ] * 30 + [
            {'items': ['A']},  # 20 (only A)
        ] * 20 + [
            {'items': ['B']},  # 10 (only B)
        ] * 10 + [
            {'items': ['C']},  # 40 (neither)
        ] * 40

        result = calculate_lift('A', 'B', transactions)
        assert 1.4 < result < 1.6, f"Lift should be ~1.5, got {result:.2f}"

    @pytest.mark.apriori
    def test_lift_one(self):
        """Lift = 1: Items are independent (no correlation)"""
        from apriori_miner import calculate_lift

        # A in 50%, B in 50%, A&B in 25%
        # Lift = 0.25 / (0.50 * 0.50) = 0.25 / 0.25 = 1.0

        transactions = [
            {'items': ['A', 'B']},  # 25
        ] * 25 + [
            {'items': ['A']},  # 25 (only A)
        ] * 25 + [
            {'items': ['B']},  # 25 (only B)
        ] * 25 + [
            {'items': ['C']},  # 25 (neither)
        ] * 25

        result = calculate_lift('A', 'B', transactions)
        assert 0.95 < result < 1.05, f"Lift should be ~1.0, got {result:.2f}"

    @pytest.mark.apriori
    def test_lift_less_than_one(self):
        """Lift < 1: Items are bought together less than random (negative correlation)"""
        from apriori_miner import calculate_lift

        transactions = [
            {'items': ['A', 'B']},  # 5 (rarely together)
        ] * 5 + [
            {'items': ['A']},  # 45
        ] * 45 + [
            {'items': ['B']},  # 45
        ] * 45 + [
            {'items': ['C']},  # 5
        ] * 5

        result = calculate_lift('A', 'B', transactions)
        assert result < 1, f"Lift should be < 1, got {result:.2f}"


class TestAprioriRuleGeneration:
    """Test generation of association rules"""

    @pytest.mark.apriori
    def test_generate_rules_basic(self):
        """Generate rules with min support & confidence"""
        from apriori_miner import generate_association_rules

        transactions = [
            {'items': ['Bánh', 'Nước']},
        ] * 60 + [
            {'items': ['Bánh']},
        ] * 20 + [
            {'items': ['Nước']},
        ] * 15 + [
            {'items': ['Khác']},
        ] * 5

        rules = generate_association_rules(
            transactions,
            min_support=0.10,
            min_confidence=0.50
        )

        assert isinstance(rules, list), "Should return list of rules"
        assert len(rules) > 0, "Should find at least one rule"

    @pytest.mark.apriori
    def test_generate_rules_structure(self):
        """Each rule has correct structure"""
        from apriori_miner import generate_association_rules

        transactions = [
            {'items': ['A', 'B']},
        ] * 70 + [
            {'items': ['A']},
        ] * 30

        rules = generate_association_rules(
            transactions,
            min_support=0.50,
            min_confidence=0.60
        )

        if len(rules) > 0:
            rule = rules[0]
            assert 'antecedent' in rule, "Rule should have antecedent"
            assert 'consequent' in rule, "Rule should have consequent"
            assert 'support' in rule, "Rule should have support"
            assert 'confidence' in rule, "Rule should have confidence"
            assert 'lift' in rule, "Rule should have lift"

    @pytest.mark.apriori
    def test_no_rules_high_threshold(self):
        """No rules when thresholds too high"""
        from apriori_miner import generate_association_rules

        transactions = [
            {'items': ['A', 'B']},
        ] * 30 + [
            {'items': ['A']},
        ] * 70

        rules = generate_association_rules(
            transactions,
            min_support=0.95,  # Very high
            min_confidence=0.95  # Very high
        )

        assert len(rules) == 0, "Should find no rules with high thresholds"


class TestBundleRecommendations:
    """Test product bundle recommendations from Apriori"""

    @pytest.mark.apriori
    def test_recommend_bundles(self):
        """Recommend bundles based on confidence"""
        from apriori_miner import recommend_bundles

        transactions = [
            {'items': ['Bánh mì', 'Nước']},
        ] * 65 + [
            {'items': ['Bánh mì']},
        ] * 35 + [
            {'items': ['Thịt', 'Gia vị']},
        ] * 50 + [
            {'items': ['Thịt']},
        ] * 50

        bundles = recommend_bundles(transactions, min_confidence=0.50, top_n=5)

        assert isinstance(bundles, list), "Should return list of bundles"
        assert len(bundles) > 0, "Should recommend at least one bundle"

    @pytest.mark.apriori
    def test_bundle_structure(self):
        """Each bundle has product1, product2, confidence"""
        from apriori_miner import recommend_bundles

        transactions = [
            {'items': ['A', 'B']},
        ] * 80 + [
            {'items': ['A']},
        ] * 20

        bundles = recommend_bundles(transactions, min_confidence=0.75)

        if len(bundles) > 0:
            bundle = bundles[0]
            assert 'product_a' in bundle, "Bundle should have product_a"
            assert 'product_b' in bundle, "Bundle should have product_b"
            assert 'confidence' in bundle, "Bundle should have confidence"

    @pytest.mark.apriori
    def test_bundle_sorting_by_confidence(self):
        """Bundles sorted by confidence descending"""
        from apriori_miner import recommend_bundles

        transactions = [
            {'items': ['A', 'B']},
        ] * 80 + [
            {'items': ['A']},
        ] * 20 + [
            {'items': ['C', 'D']},
        ] * 60 + [
            {'items': ['C']},
        ] * 40

        bundles = recommend_bundles(transactions, min_confidence=0.50, top_n=10)

        # Verify sorted by confidence descending
        if len(bundles) > 1:
            for i in range(len(bundles) - 1):
                assert bundles[i]['confidence'] >= bundles[i+1]['confidence'], \
                    "Bundles should be sorted by confidence descending"


class TestAprioriEndToEnd:
    """End-to-end Apriori analysis"""

    @pytest.mark.apriori
    def test_full_apriori_flow(self, apriori_test_data):
        """Complete Apriori workflow"""
        from apriori_miner import analyze_market_basket

        transactions = apriori_test_data.to_dict('records')

        result = analyze_market_basket(transactions, min_support=0.05, min_confidence=0.30)

        assert 'rules' in result, "Result should have rules"
        assert 'bundles' in result, "Result should have bundles"
        assert 'summary' in result, "Result should have summary"

    @pytest.mark.apriori
    def test_empty_transactions(self):
        """Handle empty transaction list"""
        from apriori_miner import generate_association_rules

        transactions = []
        rules = generate_association_rules(transactions)

        assert isinstance(rules, list), "Should return empty list"
        assert len(rules) == 0, "Should be empty for empty input"


class TestAprioriValidation:
    """Test data validation in Apriori"""

    @pytest.mark.apriori
    def test_handles_duplicate_items(self):
        """Handle transactions with duplicate items"""
        from apriori_miner import calculate_support

        transactions = [
            {'items': ['A', 'A', 'B']},  # Duplicate A
            {'items': ['A', 'B']},
        ]

        result = calculate_support('A', transactions)
        assert result > 0, "Should handle duplicates"

    @pytest.mark.apriori
    def test_handles_case_sensitivity(self):
        """Items should be case-sensitive"""
        from apriori_miner import calculate_support

        transactions = [
            {'items': ['Bánh', 'bánh']},  # Different cases
        ]

        support_upper = calculate_support('Bánh', transactions)
        support_lower = calculate_support('bánh', transactions)

        assert support_upper == support_lower, "Both should be found (same transaction)"

    @pytest.mark.apriori
    def test_handles_empty_items(self):
        """Handle transactions with empty items list"""
        from apriori_miner import calculate_support

        transactions = [
            {'items': []},  # Empty
            {'items': ['A']},
        ]

        result = calculate_support('A', transactions)
        assert 0 < result <= 1, "Should handle empty transactions"
