"""
Push Synthetic Data to Kiotviet API

This script uploads generated synthetic data to a real Kiotviet shop
for shop demonstration purposes.

Flow:
1. Read CSV files (products, customers, invoices, items)
   ↓
2. Validate API connectivity
   ↓
3. Create products in Kiotviet
   ↓
4. Create customers in Kiotviet
   ↓
5. Create invoices in Kiotviet
   ↓
6. Save tracking file (demo_data_ids.json) for cleanup
   ↓
7. Shop now displays demo data
"""

import pandas as pd
import requests
import json
import time
from datetime import datetime
from pathlib import Path
import sys
from typing import Dict, List, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

# Đọc từ .env hoặc cấu hình
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
REQUEST_DELAY = 0.7  # 700ms between requests (to stay safe)

# Tracking file to record what was created
TRACKING_FILE = "demo_data_ids.json"

# CSV files to read
CSV_FILES = {
    "products": "products.csv",
    "customers": "customers.csv",
    "invoices": "invoices.csv",
    "invoice_items": "invoice_items.csv",
}

# ============================================================================
# KIOTVIET API CLIENT
# ============================================================================

class KiotvietDemoUploader:
    """Upload synthetic data to Kiotviet"""

    def __init__(self):
        self.tracking = {
            "created_at": datetime.now().isoformat(),
            "products": [],
            "customers": [],
            "invoices": [],
            "errors": [],
        }

    def validate_credentials(self) -> bool:
        """Validate API credentials"""
        print("🔐 Validating Kiotviet API credentials...")

        if not KIOTVIET_RETAIL_ID or not KIOTVIET_API_KEY:
            print("  ❌ Missing KIOTVIET_RETAIL_ID or KIOTVIET_API_KEY in .env")
            return False

        try:
            response = requests.get(
                f"{KIOTVIET_BASE_URL}/customers",
                headers=KIOTVIET_HEADERS,
                timeout=10,
            )

            if response.status_code == 200:
                print("  ✓ API credentials valid")
                return True
            elif response.status_code == 401:
                print("  ❌ Invalid credentials (401 Unauthorized)")
                return False
            else:
                print(f"  ❌ API error: {response.status_code}")
                print(f"     {response.text}")
                return False

        except Exception as e:
            print(f"  ❌ Connection error: {e}")
            return False

    def create_product(self, product_data: Dict) -> Optional[str]:
        """Create a product in Kiotviet. Returns product ID if successful."""
        try:
            # Map CSV columns to Kiotviet API fields
            payload = {
                "name": product_data.get('ten_hang', 'Unnamed'),
                "code": product_data.get('ma_hang', ''),
                "barcode": product_data.get('ma_vach', ''),
                "unit": product_data.get('don_vi_tinh', 'Cái'),
                "categoryId": 0,  # Default category
                "price": int(product_data.get('gia_ban', 0)),
                "costPrice": int(product_data.get('gia_von', 0)),
                "quantity": int(product_data.get('ton_kho', 0)),
                "description": f"Demo product: {product_data.get('nhom_hang', '')}",
            }

            response = requests.post(
                f"{KIOTVIET_BASE_URL}/products",
                headers=KIOTVIET_HEADERS,
                json=payload,
                timeout=10,
            )

            time.sleep(REQUEST_DELAY)

            if response.status_code in [200, 201]:
                data = response.json()
                product_id = data.get('data', {}).get('id')
                return product_id
            else:
                error = f"Product {product_data.get('ma_hang')}: {response.status_code}"
                self.tracking['errors'].append(error)
                print(f"  ⚠️  {error}")
                return None

        except Exception as e:
            error = f"Product {product_data.get('ma_hang')}: {str(e)}"
            self.tracking['errors'].append(error)
            print(f"  ⚠️  {error}")
            return None

    def create_customer(self, customer_data: Dict) -> Optional[str]:
        """Create a customer in Kiotviet. Returns customer ID if successful."""
        try:
            payload = {
                "code": customer_data.get('ma_khach_hang', ''),
                "name": customer_data.get('ten_khach_hang', 'Unnamed'),
                "phone": customer_data.get('dien_thoai', ''),
                "email": customer_data.get('email', ''),
                "address": customer_data.get('dia_chi', ''),
                "type": 1,  # 1 = Customer
                "description": "Demo customer",
            }

            response = requests.post(
                f"{KIOTVIET_BASE_URL}/customers",
                headers=KIOTVIET_HEADERS,
                json=payload,
                timeout=10,
            )

            time.sleep(REQUEST_DELAY)

            if response.status_code in [200, 201]:
                data = response.json()
                customer_id = data.get('data', {}).get('id')
                return customer_id
            else:
                error = f"Customer {customer_data.get('ma_khach_hang')}: {response.status_code}"
                self.tracking['errors'].append(error)
                print(f"  ⚠️  {error}")
                return None

        except Exception as e:
            error = f"Customer {customer_data.get('ma_khach_hang')}: {str(e)}"
            self.tracking['errors'].append(error)
            print(f"  ⚠️  {error}")
            return None

    def create_invoice(self, invoice_data: Dict, items_data: List[Dict],
                      kiotviet_customer_map: Dict, kiotviet_product_map: Dict) -> Optional[str]:
        """Create an invoice in Kiotviet. Returns invoice ID if successful."""
        try:
            # Get customer ID from mapping
            customer_id = kiotviet_customer_map.get(invoice_data.get('ma_khach_hang'))
            if not customer_id:
                print(f"  ⚠️  Customer not found for invoice {invoice_data.get('ma_hoa_don')}")
                return None

            # Build invoice items
            invoice_items = []
            for item in items_data:
                product_id = kiotviet_product_map.get(item.get('ma_hang'))
                if not product_id:
                    continue

                invoice_items.append({
                    "productId": product_id,
                    "quantity": int(item.get('so_luong', 1)),
                    "price": int(item.get('don_gia', 0)),
                    "discount": int(item.get('giam_gia', 0)),
                })

            if not invoice_items:
                print(f"  ⚠️  No valid items for invoice {invoice_data.get('ma_hoa_don')}")
                return None

            payload = {
                "customerId": customer_id,
                "code": invoice_data.get('ma_hoa_don', ''),
                "invoiceDate": invoice_data.get('thoi_gian', ''),
                "description": "Demo invoice",
                "items": invoice_items,
                "totalAmount": int(invoice_data.get('khach_da_tra', 0)),
            }

            response = requests.post(
                f"{KIOTVIET_BASE_URL}/invoices",
                headers=KIOTVIET_HEADERS,
                json=payload,
                timeout=10,
            )

            time.sleep(REQUEST_DELAY)

            if response.status_code in [200, 201]:
                data = response.json()
                invoice_id = data.get('data', {}).get('id')
                return invoice_id
            else:
                error = f"Invoice {invoice_data.get('ma_hoa_don')}: {response.status_code}"
                self.tracking['errors'].append(error)
                print(f"  ⚠️  {error}")
                return None

        except Exception as e:
            error = f"Invoice {invoice_data.get('ma_hoa_don')}: {str(e)}"
            self.tracking['errors'].append(error)
            print(f"  ⚠️  {error}")
            return None

    def save_tracking(self):
        """Save tracking file for cleanup later"""
        with open(TRACKING_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.tracking, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Tracking file saved: {TRACKING_FILE}")
        print(f"   Use this to cleanup: python cleanup_kiotviet_demo.py")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution flow"""
    print("=" * 70)
    print("📊 PUSHING DEMO DATA TO KIOTVIET")
    print("=" * 70)

    uploader = KiotvietDemoUploader()

    # Validate credentials
    if not uploader.validate_credentials():
        print("\n❌ Cannot proceed without valid API credentials")
        return False

    # Check CSV files exist
    print("\n🔎 Checking CSV files...")
    for name, file in CSV_FILES.items():
        if Path(file).exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ❌ {file} not found")
            print("   Run: python generate_synthetic_data.py")
            return False

    # Load CSV files
    print("\n📖 Loading CSV files...")
    try:
        products_df = pd.read_csv(CSV_FILES['products'])
        customers_df = pd.read_csv(CSV_FILES['customers'])
        invoices_df = pd.read_csv(CSV_FILES['invoices'])
        items_df = pd.read_csv(CSV_FILES['invoice_items'])

        print(f"  ✓ {len(products_df)} products")
        print(f"  ✓ {len(customers_df)} customers")
        print(f"  ✓ {len(invoices_df)} invoices")
        print(f"  ✓ {len(items_df)} invoice items")
    except Exception as e:
        print(f"  ❌ Error reading CSV: {e}")
        return False

    # Create products
    print("\n📦 Creating products in Kiotviet...")
    kiotviet_product_map = {}  # CSV product ID → Kiotviet product ID
    success_count = 0

    for idx, product in products_df.iterrows():
        kiotviet_id = uploader.create_product(product)
        if kiotviet_id:
            kiotviet_product_map[product['ma_hang']] = kiotviet_id
            uploader.tracking['products'].append({
                'csv_id': product['ma_hang'],
                'kiotviet_id': kiotviet_id,
                'name': product['ten_hang'],
            })
            success_count += 1
            if (idx + 1) % 10 == 0:
                print(f"  ✓ Created {idx + 1}/{len(products_df)} products")

    print(f"  ✓ Successfully created {success_count}/{len(products_df)} products")

    # Create customers
    print("\n👥 Creating customers in Kiotviet...")
    kiotviet_customer_map = {}  # CSV customer ID → Kiotviet customer ID
    success_count = 0

    for idx, customer in customers_df.iterrows():
        kiotviet_id = uploader.create_customer(customer)
        if kiotviet_id:
            kiotviet_customer_map[customer['ma_khach_hang']] = kiotviet_id
            uploader.tracking['customers'].append({
                'csv_id': customer['ma_khach_hang'],
                'kiotviet_id': kiotviet_id,
                'name': customer['ten_khach_hang'],
            })
            success_count += 1
            if (idx + 1) % 10 == 0:
                print(f"  ✓ Created {idx + 1}/{len(customers_df)} customers")

    print(f"  ✓ Successfully created {success_count}/{len(customers_df)} customers")

    # Create invoices
    print("\n🧾 Creating invoices in Kiotviet...")
    success_count = 0

    for idx, invoice in invoices_df.iterrows():
        # Get items for this invoice
        invoice_items = items_df[items_df['ma_hoa_don'] == invoice['ma_hoa_don']]

        kiotviet_id = uploader.create_invoice(
            invoice,
            invoice_items.to_dict('records'),
            kiotviet_customer_map,
            kiotviet_product_map
        )

        if kiotviet_id:
            uploader.tracking['invoices'].append({
                'csv_id': invoice['ma_hoa_don'],
                'kiotviet_id': kiotviet_id,
            })
            success_count += 1
            if (idx + 1) % 10 == 0:
                print(f"  ✓ Created {idx + 1}/{len(invoices_df)} invoices")

    print(f"  ✓ Successfully created {success_count}/{len(invoices_df)} invoices")

    # Save tracking
    uploader.save_tracking()

    # Summary
    print("\n" + "=" * 70)
    print("✅ DEMO DATA PUSHED TO KIOTVIET!")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"  • Products: {len(uploader.tracking['products'])}")
    print(f"  • Customers: {len(uploader.tracking['customers'])}")
    print(f"  • Invoices: {len(uploader.tracking['invoices'])}")
    if uploader.tracking['errors']:
        print(f"  • Errors: {len(uploader.tracking['errors'])}")

    print(f"\n🎯 Your Kiotviet shop now displays demo data!")
    print(f"\n📌 Important:")
    print(f"   • Tracking file saved: {TRACKING_FILE}")
    print(f"   • To cleanup later: python cleanup_kiotviet_demo.py")
    print(f"   • Visit your shop: https://kiotviet.vn")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
