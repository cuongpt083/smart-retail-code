#!/usr/bin/env python3
"""Debug test script - directly test RFM functions"""

import sys
sys.path.insert(0, 'src')

from rfm_calculator import score_recency, score_frequency, score_monetary

print("=" * 60)
print("RECENCY TESTS")
print("=" * 60)

test_cases_r = [
    (0, 5, "0 days = very recent"),
    (15, 5, "15 days = recent"),
    (18, 5, "18 days = recent boundary"),
    (19, 4, "19 days = less recent"),
    (36, 4, "36 days = 21-40%"),
    (45, 3, "45 days = medium"),
    (72, 2, "72 days = 61-80%"),
    (80, 1, "80 days = old"),
]

for days, expected, description in test_cases_r:
    result = score_recency(days)
    status = "✅" if result == expected else "❌"
    print(f"{status} score_recency({days}) = {result} (expected {expected}) - {description}")

print("\n" + "=" * 60)
print("FREQUENCY TESTS")
print("=" * 60)

test_cases_f = [
    (0, 1, "0 purchases"),
    (5, 1, "5 purchases"),
    (6, 2, "6 purchases"),
    (12, 3, "12 purchases"),
    (18, 4, "18 purchases"),
    (24, 5, "24 purchases"),
    (30, 5, "30 purchases"),
]

for freq, expected, description in test_cases_f:
    result = score_frequency(freq)
    status = "✅" if result == expected else "❌"
    print(f"{status} score_frequency({freq}) = {result} (expected {expected}) - {description}")

print("\n" + "=" * 60)
print("MONETARY TESTS")
print("=" * 60)

test_cases_m = [
    (0, 1, "0 VND"),
    (1000000, 1, "1M VND"),
    (2000000, 2, "2M VND"),
    (4000000, 3, "4M VND"),
    (6000000, 4, "6M VND"),
    (8000000, 5, "8M VND"),
    (10000000, 5, "10M VND"),
]

for amount, expected, description in test_cases_m:
    result = score_monetary(amount)
    status = "✅" if result == expected else "❌"
    print(f"{status} score_monetary({amount:,.0f}) = {result} (expected {expected}) - {description}")
