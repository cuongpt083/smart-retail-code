"""
Apriori Market Basket Analysis Module

Analyzes product purchase patterns to find:
- Frequently bought together items
- Association rules (If A, then B)
- Recommended product bundles
- Cross-sell and up-sell opportunities

Key Metrics:
- Support: % of transactions with item(s)
- Confidence: If A, % chance customer buys B
- Lift: How much more likely A & B together vs random
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Union
from itertools import combinations
from collections import Counter


# ============================================================================
# SUPPORT CALCULATION
# ============================================================================

def calculate_support(
    items: Union[str, List[str]],
    transactions: List[Dict]
) -> float:
    """
    Calculate support: % of transactions containing item(s).

    Args:
        items: Single item (string) or list of items
        transactions: List of dicts with 'items' key

    Returns:
        Support as decimal (0.0 to 1.0)
    """
    if not transactions:
        return 0.0

    if isinstance(items, str):
        items = [items]

    items_set = set(items)
    count = 0

    for transaction in transactions:
        trans_items = set(transaction.get('items', []))
        if items_set.issubset(trans_items):
            count += 1

    return count / len(transactions)


# ============================================================================
# CONFIDENCE CALCULATION
# ============================================================================

def calculate_confidence(
    antecedent: str,
    consequent: str,
    transactions: List[Dict]
) -> float:
    """
    Calculate confidence: If customer buys A, % chance they buy B.

    Formula: Confidence(A→B) = Support(A,B) / Support(A)

    Args:
        antecedent: Item A (the condition)
        consequent: Item B (the result)
        transactions: List of dicts with 'items' key

    Returns:
        Confidence as decimal (0.0 to 1.0)
    """
    support_a = calculate_support(antecedent, transactions)
    if support_a == 0:
        return 0.0

    support_ab = calculate_support([antecedent, consequent], transactions)
    return support_ab / support_a


# ============================================================================
# LIFT CALCULATION
# ============================================================================

def calculate_lift(
    item_a: str,
    item_b: str,
    transactions: List[Dict]
) -> float:
    """
    Calculate lift: How much more likely A & B together vs independent.

    Formula: Lift(A→B) = Confidence(A→B) / Support(B)
                       = Support(A,B) / (Support(A) * Support(B))

    Values:
    - Lift > 1: Positive correlation (buy together)
    - Lift = 1: Independent
    - Lift < 1: Negative correlation (don't buy together)

    Args:
        item_a: First item
        item_b: Second item
        transactions: List of dicts with 'items' key

    Returns:
        Lift ratio (1.0 = independent)
    """
    support_a = calculate_support(item_a, transactions)
    support_b = calculate_support(item_b, transactions)
    support_ab = calculate_support([item_a, item_b], transactions)

    if support_a == 0 or support_b == 0:
        return 0.0

    expected_support = support_a * support_b
    if expected_support == 0:
        return 0.0

    return support_ab / expected_support


# ============================================================================
# FREQUENT ITEMSETS
# ============================================================================

def find_frequent_itemsets(
    transactions: List[Dict],
    min_support: float = 0.05
) -> Dict[Tuple, float]:
    """
    Find frequent itemsets using apriori principle.

    Args:
        transactions: List of dicts with 'items' key
        min_support: Minimum support threshold (0.0 to 1.0)

    Returns:
        Dict mapping itemset tuples to support values
    """
    if not transactions:
        return {}

    # Create list of all items
    all_items = []
    for transaction in transactions:
        all_items.extend(transaction.get('items', []))

    # Count frequent 1-itemsets
    item_counts = Counter(all_items)
    num_transactions = len(transactions)

    frequent_itemsets = {}

    # Add 1-itemsets
    for item, count in item_counts.items():
        support = count / num_transactions
        if support >= min_support:
            frequent_itemsets[(item,)] = support

    # Generate k-itemsets (k > 1)
    current_itemsets = list(frequent_itemsets.keys())

    while current_itemsets:
        # Generate candidate itemsets
        candidates = []
        for i in range(len(current_itemsets)):
            for j in range(i + 1, len(current_itemsets)):
                union = tuple(sorted(set(current_itemsets[i]) | set(current_itemsets[j])))
                if len(union) > len(current_itemsets[0]):
                    candidates.append(union)

        # Remove duplicates
        candidates = list(set(candidates))

        if not candidates:
            break

        # Calculate support for candidates
        next_itemsets = []
        for candidate in candidates:
            candidate_set = set(candidate)
            count = sum(
                1 for transaction in transactions
                if candidate_set.issubset(set(transaction.get('items', [])))
            )
            support = count / num_transactions

            if support >= min_support:
                frequent_itemsets[candidate] = support
                next_itemsets.append(candidate)

        current_itemsets = next_itemsets

    return frequent_itemsets


# ============================================================================
# ASSOCIATION RULES
# ============================================================================

def generate_association_rules(
    transactions: List[Dict],
    min_support: float = 0.05,
    min_confidence: float = 0.50,
    min_lift: float = 1.0
) -> List[Dict]:
    """
    Generate association rules from frequent itemsets.

    Args:
        transactions: List of dicts with 'items' key
        min_support: Minimum support threshold
        min_confidence: Minimum confidence threshold
        min_lift: Minimum lift threshold

    Returns:
        List of rule dicts with antecedent, consequent, support, confidence, lift
    """
    if not transactions:
        return []

    # Find frequent itemsets
    frequent_itemsets = find_frequent_itemsets(transactions, min_support)

    rules = []

    # Generate rules from itemsets with 2+ items
    for itemset, itemset_support in frequent_itemsets.items():
        if len(itemset) < 2:
            continue

        # Generate all possible antecedent/consequent splits
        for r in range(1, len(itemset)):
            for antecedent_items in combinations(itemset, r):
                antecedent = tuple(sorted(antecedent_items))
                consequent = tuple(sorted(set(itemset) - set(antecedent_items)))

                if len(consequent) == 0:
                    continue

                # Calculate metrics
                antecedent_support = calculate_support(list(antecedent), transactions)
                confidence = itemset_support / antecedent_support if antecedent_support > 0 else 0

                if confidence < min_confidence:
                    continue

                # Calculate lift
                consequent_support = calculate_support(list(consequent), transactions)
                lift = itemset_support / (antecedent_support * consequent_support) \
                    if (antecedent_support * consequent_support) > 0 else 0

                if lift < min_lift:
                    continue

                # Add rule
                rules.append({
                    'antecedent': antecedent,
                    'consequent': consequent,
                    'support': itemset_support,
                    'confidence': confidence,
                    'lift': lift,
                })

    # Sort by lift descending
    rules.sort(key=lambda x: x['lift'], reverse=True)

    return rules


# ============================================================================
# BUNDLE RECOMMENDATIONS
# ============================================================================

def recommend_bundles(
    transactions: List[Dict],
    min_confidence: float = 0.50,
    min_lift: float = 1.0,
    top_n: int = 10
) -> List[Dict]:
    """
    Recommend product bundles based on association rules.

    Args:
        transactions: List of dicts with 'items' key
        min_confidence: Minimum confidence for recommendation
        min_lift: Minimum lift for recommendation
        top_n: Number of top bundles to return

    Returns:
        List of bundle recommendations sorted by confidence
    """
    rules = generate_association_rules(
        transactions,
        min_support=0.01,  # Low support for bundles
        min_confidence=min_confidence,
        min_lift=min_lift
    )

    bundles = []
    for rule in rules:
        antecedent = rule['antecedent'][0] if len(rule['antecedent']) == 1 else rule['antecedent']
        consequent = rule['consequent'][0] if len(rule['consequent']) == 1 else rule['consequent']

        # Skip multi-item bundles for simplicity
        if isinstance(antecedent, tuple) or isinstance(consequent, tuple):
            continue

        bundle = {
            'product_a': antecedent,
            'product_b': consequent,
            'confidence': round(rule['confidence'], 4),
            'lift': round(rule['lift'], 2),
            'support': round(rule['support'], 4),
        }
        bundles.append(bundle)

    # Sort by confidence and return top N
    bundles.sort(key=lambda x: x['confidence'], reverse=True)
    return bundles[:top_n]


# ============================================================================
# MARKET BASKET ANALYSIS
# ============================================================================

def analyze_market_basket(
    transactions: List[Dict],
    min_support: float = 0.05,
    min_confidence: float = 0.50,
    min_lift: float = 1.0
) -> Dict:
    """
    Complete market basket analysis.

    Args:
        transactions: List of dicts with 'items' key (from invoice_items)
        min_support: Minimum support threshold
        min_confidence: Minimum confidence threshold
        min_lift: Minimum lift threshold

    Returns:
        Dict with 'rules', 'bundles', and 'summary'
    """
    rules = generate_association_rules(
        transactions,
        min_support=min_support,
        min_confidence=min_confidence,
        min_lift=min_lift
    )

    bundles = recommend_bundles(
        transactions,
        min_confidence=min_confidence,
        min_lift=min_lift,
        top_n=10
    )

    # Summary stats
    summary = {
        'total_transactions': len(transactions),
        'total_rules': len(rules),
        'total_bundles': len(bundles),
        'avg_confidence': np.mean([r['confidence'] for r in rules]) if rules else 0,
        'avg_lift': np.mean([r['lift'] for r in rules]) if rules else 0,
    }

    return {
        'rules': rules,
        'bundles': bundles,
        'summary': summary,
    }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_bundle_recommendation_for_product(
    product: str,
    transactions: List[Dict],
    min_confidence: float = 0.50
) -> List[str]:
    """
    Get recommended products to bundle with given product.

    Args:
        product: Product name
        transactions: List of dicts with 'items' key
        min_confidence: Minimum confidence threshold

    Returns:
        List of recommended products
    """
    rules = generate_association_rules(
        transactions,
        min_support=0.01,
        min_confidence=min_confidence
    )

    recommendations = []
    for rule in rules:
        # If product is in antecedent
        if len(rule['antecedent']) == 1 and rule['antecedent'][0] == product:
            if len(rule['consequent']) == 1:
                recommendations.append(rule['consequent'][0])

    return recommendations
