"""
Cleanup Kiotviet Demo Data

This script removes all demo data that was pushed to Kiotviet.

It reads the tracking file (demo_data_ids.json) and deletes:
1. Invoices
2. Customers
3. Products

Flow:
1. Read demo_data_ids.json
   ↓
2. Delete invoices
   ↓
3. Delete customers
   ↓
4. Delete products
   ↓
5. Remove tracking file
   ↓
6. Done - Demo data cleaned up
"""

import json
import requests
import time
from pathlib import Path
import sys
from typing import List, Dict

# ============================================================================
# CONFIGURATION
# ============================================================================

from dotenv import load_dotenv
import os

load_dotenv()

KIOTVIET_RETAIL_ID = os.getenv('KIOTVIET_RETAIL_ID')
KIOTVIET_API_KEY = os.getenv('KIOTVIET_API_KEY')

# Kiotviet API endpoints
KIOTVIET_BASE_URL = "https://public.kiotviet.vn"
KIOTVIET_HEADERS = {
    "Retail-ID": KIOTVIET_RETAIL_ID,
    "Authorization": f"Bearer {KIOTVIET_API_KEY}",
    "Content-Type": "application/json",
}

# Rate limiting (Kiotviet allows ~100 requests/min)
REQUEST_DELAY = 0.7  # 700ms between requests

# Tracking file
TRACKING_FILE = "demo_data_ids.json"

# ============================================================================
# KIOTVIET API CLIENT FOR CLEANUP
# ============================================================================

class KiotvietDemoCleanup:
    """Clean up demo data from Kiotviet"""

    def __init__(self):
        self.tracking = None
        self.cleanup_stats = {
            "invoices_deleted": 0,
            "invoices_failed": 0,
            "customers_deleted": 0,
            "customers_failed": 0,
            "products_deleted": 0,
            "products_failed": 0,
        }

    def load_tracking_file(self) -> bool:
        """Load tracking file that was created during push"""
        print("📖 Loading tracking file...")

        if not Path(TRACKING_FILE).exists():
            print(f"  ❌ {TRACKING_FILE} not found")
            print("   Did you run: python push_data_to_kiotviet.py ?")
            return False

        try:
            with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
                self.tracking = json.load(f)
            print(f"  ✓ Loaded tracking file")
            print(f"    - Products: {len(self.tracking.get('products', []))}")
            print(f"    - Customers: {len(self.tracking.get('customers', []))}")
            print(f"    - Invoices: {len(self.tracking.get('invoices', []))}")
            return True

        except Exception as e:
            print(f"  ❌ Error loading tracking file: {e}")
            return False

    def delete_invoice(self, kiotviet_id: str) -> bool:
        """Delete an invoice from Kiotviet"""
        try:
            response = requests.delete(
                f"{KIOTVIET_BASE_URL}/invoices/{kiotviet_id}",
                headers=KIOTVIET_HEADERS,
                timeout=10,
            )

            time.sleep(REQUEST_DELAY)

            if response.status_code in [200, 204]:
                return True
            else:
                print(f"  ⚠️  Invoice {kiotviet_id}: {response.status_code}")
                return False

        except Exception as e:
            print(f"  ⚠️  Invoice {kiotviet_id}: {str(e)}")
            return False

    def delete_customer(self, kiotviet_id: str) -> bool:
        """Delete a customer from Kiotviet"""
        try:
            response = requests.delete(
                f"{KIOTVIET_BASE_URL}/customers/{kiotviet_id}",
                headers=KIOTVIET_HEADERS,
                timeout=10,
            )

            time.sleep(REQUEST_DELAY)

            if response.status_code in [200, 204]:
                return True
            else:
                print(f"  ⚠️  Customer {kiotviet_id}: {response.status_code}")
                return False

        except Exception as e:
            print(f"  ⚠️  Customer {kiotviet_id}: {str(e)}")
            return False

    def delete_product(self, kiotviet_id: str) -> bool:
        """Delete a product from Kiotviet"""
        try:
            response = requests.delete(
                f"{KIOTVIET_BASE_URL}/products/{kiotviet_id}",
                headers=KIOTVIET_HEADERS,
                timeout=10,
            )

            time.sleep(REQUEST_DELAY)

            if response.status_code in [200, 204]:
                return True
            else:
                print(f"  ⚠️  Product {kiotviet_id}: {response.status_code}")
                return False

        except Exception as e:
            print(f"  ⚠️  Product {kiotviet_id}: {str(e)}")
            return False

    def cleanup_invoices(self) -> bool:
        """Delete all invoices"""
        print("\n🧾 Deleting invoices...")

        invoices = self.tracking.get('invoices', [])
        if not invoices:
            print("  ℹ️  No invoices to delete")
            return True

        for idx, invoice in enumerate(invoices):
            kiotviet_id = invoice.get('kiotviet_id')
            if kiotviet_id:
                if self.delete_invoice(kiotviet_id):
                    self.cleanup_stats['invoices_deleted'] += 1
                else:
                    self.cleanup_stats['invoices_failed'] += 1

            if (idx + 1) % 10 == 0:
                print(f"  ✓ Deleted {idx + 1}/{len(invoices)} invoices")

        print(f"  ✓ Deleted {self.cleanup_stats['invoices_deleted']}/{len(invoices)} invoices")
        return True

    def cleanup_customers(self) -> bool:
        """Delete all customers"""
        print("\n👥 Deleting customers...")

        customers = self.tracking.get('customers', [])
        if not customers:
            print("  ℹ️  No customers to delete")
            return True

        for idx, customer in enumerate(customers):
            kiotviet_id = customer.get('kiotviet_id')
            if kiotviet_id:
                if self.delete_customer(kiotviet_id):
                    self.cleanup_stats['customers_deleted'] += 1
                else:
                    self.cleanup_stats['customers_failed'] += 1

            if (idx + 1) % 10 == 0:
                print(f"  ✓ Deleted {idx + 1}/{len(customers)} customers")

        print(f"  ✓ Deleted {self.cleanup_stats['customers_deleted']}/{len(customers)} customers")
        return True

    def cleanup_products(self) -> bool:
        """Delete all products"""
        print("\n📦 Deleting products...")

        products = self.tracking.get('products', [])
        if not products:
            print("  ℹ️  No products to delete")
            return True

        for idx, product in enumerate(products):
            kiotviet_id = product.get('kiotviet_id')
            if kiotviet_id:
                if self.delete_product(kiotviet_id):
                    self.cleanup_stats['products_deleted'] += 1
                else:
                    self.cleanup_stats['products_failed'] += 1

            if (idx + 1) % 10 == 0:
                print(f"  ✓ Deleted {idx + 1}/{len(products)} products")

        print(f"  ✓ Deleted {self.cleanup_stats['products_deleted']}/{len(products)} products")
        return True

    def remove_tracking_file(self):
        """Remove tracking file after cleanup"""
        try:
            Path(TRACKING_FILE).unlink()
            print(f"\n🗑️  Removed {TRACKING_FILE}")
        except Exception as e:
            print(f"\n⚠️  Could not remove {TRACKING_FILE}: {e}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main cleanup flow"""
    print("=" * 70)
    print("🧹 CLEANING UP KIOTVIET DEMO DATA")
    print("=" * 70)

    cleanup = KiotvietDemoCleanup()

    # Load tracking file
    if not cleanup.load_tracking_file():
        return False

    print("\n⚠️  WARNING: This will DELETE all demo data from your Kiotviet shop!")
    print("   Press Ctrl+C to cancel, or wait 3 seconds...")

    try:
        time.sleep(3)
    except KeyboardInterrupt:
        print("\n✓ Cleanup cancelled")
        return False

    # Clean up in order: invoices → customers → products
    cleanup.cleanup_invoices()
    cleanup.cleanup_customers()
    cleanup.cleanup_products()

    # Remove tracking file
    cleanup.remove_tracking_file()

    # Summary
    print("\n" + "=" * 70)
    print("✅ DEMO DATA CLEANUP COMPLETE!")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"  • Invoices deleted: {cleanup.cleanup_stats['invoices_deleted']}")
    if cleanup.cleanup_stats['invoices_failed']:
        print(f"    (Failed: {cleanup.cleanup_stats['invoices_failed']})")
    print(f"  • Customers deleted: {cleanup.cleanup_stats['customers_deleted']}")
    if cleanup.cleanup_stats['customers_failed']:
        print(f"    (Failed: {cleanup.cleanup_stats['customers_failed']})")
    print(f"  • Products deleted: {cleanup.cleanup_stats['products_deleted']}")
    if cleanup.cleanup_stats['products_failed']:
        print(f"    (Failed: {cleanup.cleanup_stats['products_failed']})")

    total_deleted = (cleanup.cleanup_stats['invoices_deleted'] +
                    cleanup.cleanup_stats['customers_deleted'] +
                    cleanup.cleanup_stats['products_deleted'])

    print(f"\n🎯 Total deleted: {total_deleted} items")
    print(f"\n✓ Your Kiotviet shop is back to clean state!")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
