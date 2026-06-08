"""
RFM (Recency, Frequency, Monetary) Calculation Module

RFM Analysis is a behavioral analysis technique used to segment customers based on:
- Recency (R): Days since last purchase (0-90)
- Frequency (F): Number of purchases (0-30+)
- Monetary (M): Total spending amount (0-10M+ VND)

Output:
- RFM Scores: Each metric scored 1-5
- Segmentation: Champions, Potential, Loyal, Lost
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Optional, List, Tuple


# ============================================================================
# RECENCY CALCULATION
# ============================================================================

def calculate_recency(last_purchase_date: Optional[date], today: date) -> Optional[int]:
    """
    Calculate recency (days since last purchase).

    Args:
        last_purchase_date: Date of customer's last purchase
        today: Reference date (today)

    Returns:
        Number of days since last purchase, or None if never purchased
    """
    if last_purchase_date is None:
        return None

    recency = (today - last_purchase_date).days
    return max(0, recency)  # Ensure non-negative


def score_recency(days: Optional[int], max_days: int = 90) -> int:
    """
    Convert recency days to score (1-5).
    Note: Recency is INVERSE - fewer days = higher score

    Scoring:
    - Score 5: 0-18 days (very recent) - top 20%
    - Score 4: 19-36 days - 21-40%
    - Score 3: 37-54 days (medium) - 41-60%
    - Score 2: 55-72 days - 61-80%
    - Score 1: 73-90+ days (old) - bottom 20%

    Args:
        days: Days since last purchase
        max_days: Maximum days considered (default 90)

    Returns:
        Score 1-5 (higher = more recent)
    """
    if days is None:
        return 1  # Never purchased = lowest score

    # Cap at max_days
    days = min(days, max_days)

    # DEBUG
    import sys
    print(f"DEBUG score_recency: days={days}, type={type(days)}, days<=18={days<=18}", file=sys.stderr)

    if days <= 18:
        return 5
    elif days <= 36:
        return 4
    elif days <= 54:
        return 3
    elif days <= 72:
        return 2
    else:
        return 1


# ============================================================================
# FREQUENCY CALCULATION
# ============================================================================

def calculate_frequency(customer_id: str, invoices: pd.DataFrame) -> int:
    """
    Calculate frequency (number of purchases).

    Args:
        customer_id: Customer ID to analyze
        invoices: DataFrame with columns ['ma_khach_hang', 'ma_hoa_don', ...]

    Returns:
        Number of invoices (purchases) for this customer
    """
    customer_invoices = invoices[invoices['ma_khach_hang'] == customer_id]
    return len(customer_invoices)


def score_frequency(frequency: int, max_frequency: int = 30) -> int:
    """
    Convert purchase frequency to score (1-5).

    Scoring:
    - Score 5: 24-30+ purchases (frequent buyer) - top 20%
    - Score 4: 18-23 purchases - 21-40%
    - Score 3: 12-17 purchases (medium) - 41-60%
    - Score 2: 6-11 purchases - 61-80%
    - Score 1: 0-5 purchases (rare buyer) - bottom 20%

    Args:
        frequency: Number of purchases
        max_frequency: Maximum frequency considered (default 30)

    Returns:
        Score 1-5 (higher = more frequent)
    """
    # Thresholds for 5 equal segments
    thresholds = [6, 12, 18, 24]  # Boundaries at 20% intervals

    if frequency >= thresholds[3]:  # 24+
        return 5
    elif frequency >= thresholds[2]:  # 18-23
        return 4
    elif frequency >= thresholds[1]:  # 12-17
        return 3
    elif frequency >= thresholds[0]:  # 6-11
        return 2
    else:  # 0-5
        return 1


# ============================================================================
# MONETARY CALCULATION
# ============================================================================

def calculate_monetary(customer_id: str, invoices: pd.DataFrame) -> float:
    """
    Calculate monetary value (total spending).

    Args:
        customer_id: Customer ID to analyze
        invoices: DataFrame with columns ['ma_khach_hang', 'khach_da_tra', ...]

    Returns:
        Total amount paid by customer (VND)
    """
    customer_invoices = invoices[invoices['ma_khach_hang'] == customer_id]

    if customer_invoices.empty:
        return 0.0

    total = customer_invoices['khach_da_tra'].sum()
    return max(0, total)  # Ensure non-negative (handle refunds)


def score_monetary(monetary: float, max_monetary: float = 10000000) -> int:
    """
    Convert monetary value to score (1-5).

    Scoring (VND):
    - Score 5: 8M-10M+ VND (high spender) - top 20%
    - Score 4: 6M-7.99M VND - 21-40%
    - Score 3: 4M-5.99M VND (medium) - 41-60%
    - Score 2: 2M-3.99M VND - 61-80%
    - Score 1: 0-1.99M VND (low spender) - bottom 20%

    Args:
        monetary: Total spending amount (VND)
        max_monetary: Maximum amount considered (default 10M VND)

    Returns:
        Score 1-5 (higher = more spending)
    """
    # Thresholds for 5 equal segments (in VND)
    thresholds = [2000000, 4000000, 6000000, 8000000]  # 2M, 4M, 6M, 8M

    if monetary >= thresholds[3]:  # 8M+
        return 5
    elif monetary >= thresholds[2]:  # 6M-7.99M
        return 4
    elif monetary >= thresholds[1]:  # 4M-5.99M
        return 3
    elif monetary >= thresholds[0]:  # 2M-3.99M
        return 2
    else:  # 0-1.99M
        return 1


# ============================================================================
# SEGMENTATION
# ============================================================================

def segment_customer(r_score: int, f_score: int, m_score: int) -> str:
    """
    Segment customer based on RFM scores.

    Segments:
    - Champions: R≥4, F≥4, M≥4 (best customers)
    - Loyal: R<3, F≥4, M≥4 (good but not recent)
    - Potential: R≥4, F<3, M varies (new/occasional but recent)
    - Lost: R<2, F<2, M<2 (worst customers)

    Args:
        r_score: Recency score (1-5)
        f_score: Frequency score (1-5)
        m_score: Monetary score (1-5)

    Returns:
        Segment name: 'Champions', 'Loyal', 'Potential', 'Lost', or 'At-risk'
    """
    # Champions: Recently active, frequent, high value
    if r_score >= 4 and f_score >= 4 and m_score >= 4:
        return 'Champions'

    # Loyal: Low recency but high frequency & monetary
    if r_score < 3 and f_score >= 4 and m_score >= 4:
        return 'Loyal'

    # At-risk: Was good, but not recent (subset of Loyal for detailed view)
    if r_score == 2 and f_score >= 4 and m_score >= 4:
        return 'Loyal'  # More specific: "At-risk Loyal"

    # Potential: Recent and somewhat valuable, but low frequency
    if r_score >= 4 and (f_score < 3 or m_score < 3):
        return 'Potential'

    # Lost: Very old, infrequent, low value
    if r_score <= 2 and f_score <= 2 and m_score <= 2:
        return 'Lost'

    # Default: Other (catch-all for edge cases)
    return 'Other'


# ============================================================================
# END-TO-END RFM CALCULATION
# ============================================================================

def calculate_rfm_for_customers(
    customers: pd.DataFrame,
    invoices: pd.DataFrame,
    today: Optional[date] = None
) -> pd.DataFrame:
    """
    Calculate RFM scores and segments for all customers.

    Args:
        customers: DataFrame with customers data
        invoices: DataFrame with invoices data
        today: Reference date (default: today)

    Returns:
        DataFrame with added columns:
        - recency_days
        - frequency
        - monetary
        - r_score, f_score, m_score (1-5)
        - rfm_segment
    """
    if today is None:
        today = datetime.now().date()

    # Create a copy to avoid modifying original
    result = customers.copy()

    # Calculate RFM metrics
    result['recency_days'] = result['ngay_giao_dich_cuoi'].apply(
        lambda x: calculate_recency(x, today)
    )

    result['frequency'] = result['ma_khach_hang'].apply(
        lambda cid: calculate_frequency(cid, invoices)
    )

    result['monetary'] = result['ma_khach_hang'].apply(
        lambda cid: calculate_monetary(cid, invoices)
    )

    # Calculate RFM scores
    result['r_score'] = result['recency_days'].apply(score_recency)
    result['f_score'] = result['frequency'].apply(score_frequency)
    result['m_score'] = result['monetary'].apply(score_monetary)

    # Segment
    result['rfm_segment'] = result.apply(
        lambda row: segment_customer(row['r_score'], row['f_score'], row['m_score']),
        axis=1
    )

    return result


def calculate_rfm_summary(rfm_data: pd.DataFrame) -> dict:
    """
    Calculate RFM summary statistics.

    Args:
        rfm_data: DataFrame from calculate_rfm_for_customers()

    Returns:
        Dict with segment counts and averages
    """
    summary = {
        'total_customers': len(rfm_data),
        'segments': rfm_data['rfm_segment'].value_counts().to_dict(),
        'avg_recency_days': rfm_data['recency_days'].mean(),
        'avg_frequency': rfm_data['frequency'].mean(),
        'avg_monetary': rfm_data['monetary'].mean(),
        'total_monetary': rfm_data['monetary'].sum(),
    }

    # Calculate percentiles
    summary['recency_percentiles'] = {
        '25': rfm_data['recency_days'].quantile(0.25),
        '50': rfm_data['recency_days'].quantile(0.50),
        '75': rfm_data['recency_days'].quantile(0.75),
    }

    summary['monetary_percentiles'] = {
        '25': rfm_data['monetary'].quantile(0.25),
        '50': rfm_data['monetary'].quantile(0.50),
        '75': rfm_data['monetary'].quantile(0.75),
    }

    return summary


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_segment_description(segment: str) -> str:
    """Get human-readable description of RFM segment"""
    descriptions = {
        'Champions': '💎 Best customers - high value, frequent, recent',
        'Loyal': '⭐ Good customers - high value, frequent, but not recent',
        'Potential': '🌟 New/occasional customers - recent, may become valuable',
        'Lost': '❌ Inactive customers - low value, infrequent, old',
        'At-risk': '⚠️ Loyal but at risk - were good, but not recently active',
        'Other': '❓ Others',
    }
    return descriptions.get(segment, 'Unknown')


def get_segment_color(segment: str) -> str:
    """Get color code for segment visualization"""
    colors = {
        'Champions': '#FF5733',     # Red
        'Loyal': '#FFC300',         # Yellow
        'Potential': '#28A745',     # Green
        'Lost': '#95A5A6',          # Gray
        'At-risk': '#FF9800',       # Orange
    }
    return colors.get(segment, '#000000')
