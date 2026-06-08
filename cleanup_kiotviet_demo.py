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
import pandas as pd
import numpy as np

# ============================================================================
# CONFIGURATION
# ============================================================================

from dotenv import load_dotenv
import os

load_dotenv()

# .env phải có 1 trong 2 cách:
# Cách 1: Access Token trực tiếp
KIOTVIET_ACCESS_TOKEN = os.getenv('KIOTVIET_ACCESS_TOKEN')
KIOTVIET_RETAILER_NAME = os.getenv('KIOTVIET_RETAILER_NAME')

# Cách 2: Client ID + Secret (để lấy token)
KIOTVIET_CLIENT_ID = os.getenv('KIOTVIET_CLIENT_ID')
KIOTVIET_CLIENT_SECRET = os.getenv('KIOTVIET_CLIENT_SECRET')

# Kiotviet Public API endpoints (NOT kiotviet.vn, use kiotapi.com)
KIOTVIET_BASE_URL = "https://public.kiotapi.com"
KIOTVIET_AUTH_URL = "https://id.kiotviet.vn/connect/token"

# Headers sẽ được set sau khi có access token
KIOTVIET_HEADERS = None

# Rate limiting (Kiotviet allows ~100 requests/min)
REQUEST_DELAY = 0.7  # 700ms between requests

# Tracking file
TRACKING_FILE = "demo_data_ids.json"

# ============================================================================
# HELPER: GET ACCESS TOKEN
# ============================================================================

def get_access_token():
    """Get access token from Kiotviet. Supports 2 methods:
    1. Direct access token in .env (KIOTVIET_ACCESS_TOKEN)
    2. OAuth client_id + client_secret (lấy token từ Kiotviet)
    """
    global KIOTVIET_HEADERS

    # Method 1: Use direct access token
    if KIOTVIET_ACCESS_TOKEN and KIOTVIET_RETAILER_NAME:
        KIOTVIET_HEADERS = {
            "Retailer": KIOTVIET_RETAILER_NAME,
            "Authorization": f"Bearer {KIOTVIET_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }
        return True

    # Method 2: Use OAuth to get token
    if KIOTVIET_CLIENT_ID and KIOTVIET_CLIENT_SECRET:
        try:
            print("🔐 Lấy access token từ Kiotviet OAuth...")
            payload = {
                "scopes": "PublicApi.Access",
                "grant_type": "client_credentials",
                "client_id": KIOTVIET_CLIENT_ID,
                "client_secret": KIOTVIET_CLIENT_SECRET,
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
            }

            response = requests.post(
                KIOTVIET_AUTH_URL,
                data=payload,
                headers=headers,
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                access_token = data.get('access_token')

                # Tên gian hàng có thể lấy từ .env hoặc mặc định
                retailer_name = KIOTVIET_RETAILER_NAME or "default"

                KIOTVIET_HEADERS = {
                    "Retailer": retailer_name,
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                }
                print("  ✓ Lấy token thành công")
                return True
            else:
                print(f"  ❌ Lỗi OAuth: {response.status_code}")
                print(f"     {response.text}")
                return False
        except Exception as e:
            print(f"  ❌ Lỗi lấy token: {e}")
            return False

    return False

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
        """Load tracking file and prepare API headers"""
        print("📖 Loading tracking file...")

        # Step 1: Get access token
        if not get_access_token():
            print("  ❌ Cannot get access token from .env")
            print("   Please set one of:")
            print("     - KIOTVIET_ACCESS_TOKEN + KIOTVIET_RETAILER_NAME")
            print("     - KIOTVIET_CLIENT_ID + KIOTVIET_CLIENT_SECRET")
            return False

        # Step 2: Load tracking file
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
