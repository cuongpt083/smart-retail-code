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
import numpy as np
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
# HELPER: DATA VALIDATION & SANITIZATION
# ============================================================================

def safe_int(value, default=0):
    """Safely convert to int, handling NaN, None, inf values"""
    try:
        if value is None or pd.isna(value):
            return default
        # Check for infinity
        if isinstance(value, float):
            if np.isinf(value) or np.isnan(value):
                return default
        return int(float(value))
    except (ValueError, TypeError, OverflowError):
        return default

def safe_string(value, default=''):
    """Safely convert to string, handling None and special characters"""
    try:
        if value is None or pd.isna(value):
            return default
        s = str(value).strip()
        # Remove problematic characters
        s = s.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        return s if s else default
    except Exception:
        return default

def safe_email(value):
    """Validate and sanitize email"""
    try:
        if value is None or pd.isna(value):
            return ''
        email = safe_string(value).lower()
        # Basic email validation
        if '@' in email and '.' in email:
            return email
        return ''
    except Exception:
        return ''

def safe_phone(value):
    """Validate and sanitize phone number"""
    try:
        if value is None or pd.isna(value):
            return ''
        phone = safe_string(value)
        # Remove non-digit characters except + and spaces
        phone = ''.join(c for c in phone if c.isdigit() or c in ['+', ' ', '-'])
        return phone[:20] if phone else ''  # Limit to 20 chars
    except Exception:
        return ''

def safe_float(value, default=0.0):
    """Safely convert to float, handling NaN, inf values"""
    try:
        if value is None or pd.isna(value):
            return default
        f = float(value)
        if np.isinf(f) or np.isnan(f):
            return default
        return f
    except (ValueError, TypeError, OverflowError):
        return default

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
        self.categories_cache = {}  # Cache for categories: name → id
        self.default_category_id = None  # Will be set during initialization
        self.branch_id = None  # Will be set during initialization

    def validate_credentials(self) -> bool:
        """Validate API credentials and get access token"""
        print("🔐 Validating Kiotviet API credentials...")

        # Step 1: Get access token
        if not get_access_token():
            print("  ❌ Cannot get access token from .env")
            print("   Please set one of:")
            print("     - KIOTVIET_ACCESS_TOKEN + KIOTVIET_RETAILER_NAME")
            print("     - KIOTVIET_CLIENT_ID + KIOTVIET_CLIENT_SECRET")
            return False

        # Step 2: Test API connectivity
        try:
            response = requests.get(
                f"{KIOTVIET_BASE_URL}/categories",
                headers=KIOTVIET_HEADERS,
                timeout=10,
            )

            if response.status_code == 200:
                print("  ✓ API credentials valid (endpoint: " + KIOTVIET_BASE_URL + ")")
                return True
            elif response.status_code == 401:
                print("  ❌ Invalid credentials (401 Unauthorized)")
                print("   Headers: ", KIOTVIET_HEADERS)
                return False
            elif response.status_code == 503:
                print("  ❌ Kiotviet service unavailable (503)")
                print("   Kiểm tra endpoint URL:")
                print(f"     - BASE_URL: {KIOTVIET_BASE_URL}")
                print(f"     - Phải dùng kiotapi.com, không phải kiotviet.vn")
                return False
            else:
                print(f"  ❌ API error: {response.status_code}")
                print(f"     {response.text}")
                return False

        except Exception as e:
            print(f"  ❌ Connection error: {e}")
            return False

    def fetch_categories(self) -> bool:
        """Fetch product categories from Kiotviet. Caches them for later use."""
        print("\n📂 Fetching product categories from Kiotviet...")
        try:
            response = requests.get(
                f"{KIOTVIET_BASE_URL}/categories",
                headers=KIOTVIET_HEADERS,
                timeout=10,
            )

            if response.status_code != 200:
                print(f"  ❌ Error fetching categories: {response.status_code}")
                print(f"     {response.text[:200]}")
                return False

            data = response.json()
            categories = data.get('data', [])

            if not categories:
                print("  ❌ No categories found in Kiotviet")
                return False

            # Build category cache: name → id
            for cat in categories:
                cat_id = cat.get('categoryId')
                cat_name = cat.get('categoryName', '')
                if cat_id:
                    self.categories_cache[cat_name] = cat_id
                    # Use first category as default
                    if self.default_category_id is None:
                        self.default_category_id = cat_id

            print(f"  ✓ Found {len(categories)} categories")
            print(f"  ✓ Default category: {self.default_category_id}")

            # Print first 5 for debugging
            for i, cat_name in enumerate(list(self.categories_cache.keys())[:5]):
                cat_id = self.categories_cache[cat_name]
                print(f"     - {cat_name}: {cat_id}")

            return True

        except Exception as e:
            print(f"  ❌ Error fetching categories: {e}")
            return False

    def get_category_id(self, nhom_hang: str) -> int:
        """Get category ID from cache, or use default if not found."""
        # Try exact match
        if nhom_hang in self.categories_cache:
            return self.categories_cache[nhom_hang]

        # Try substring match (e.g., "Bánh, kẹo, snack >> Bánh mì" → "Bánh, kẹo, snack")
        for cat_name, cat_id in self.categories_cache.items():
            if cat_name in nhom_hang or nhom_hang in cat_name:
                return cat_id

        # Use default
        if self.default_category_id:
            return self.default_category_id

        # Fallback: return first category ID
        if self.categories_cache:
            return list(self.categories_cache.values())[0]

        # Last resort
        print(f"  ⚠️  No categories available, using ID 1 (may fail)")
        return 1

    def fetch_branches(self) -> bool:
        """Fetch branches (chi nhánh) from Kiotviet"""
        print("\n🏢 Fetching branches from Kiotviet...")
        try:
            response = requests.get(
                f"{KIOTVIET_BASE_URL}/branches",
                headers=KIOTVIET_HEADERS,
                timeout=10,
            )

            if response.status_code != 200:
                print(f"  ❌ Error fetching branches: {response.status_code}")
                return False

            data = response.json()
            branches = data.get('data', [])

            if not branches:
                print("  ❌ No branches found")
                return False

            # Use first branch as default
            self.branch_id = branches[0].get('branchId')
            branch_name = branches[0].get('branchName', 'Unknown')

            print(f"  ✓ Found {len(branches)} branches")
            print(f"  ✓ Using branch: {branch_name} (ID: {self.branch_id})")

            return True

        except Exception as e:
            print(f"  ❌ Error fetching branches: {e}")
            return False

    def create_product(self, product_data: Dict) -> Optional[str]:
        """Create a product in Kiotviet. Returns product ID if successful."""
        try:
            # Sanitize and validate data
            ma_hang = safe_string(product_data.get('ma_hang', 'UNKNOWN'))
            ten_hang = safe_string(product_data.get('ten_hang', 'Unnamed'))
            nhom_hang = safe_string(product_data.get('nhom_hang', ''))
            gia_ban = safe_int(product_data.get('gia_ban', 0))
            gia_von = safe_int(product_data.get('gia_von', 0))
            ton_kho = safe_int(product_data.get('ton_kho', 0))

            # Validate prices are positive
            if gia_ban < 0:
                gia_ban = 0
            if gia_von < 0:
                gia_von = 0
            if ton_kho < 0:
                ton_kho = 0

            # Get valid category ID from Kiotviet
            category_id = self.get_category_id(nhom_hang)

            # Map CSV columns to Kiotviet API fields
            payload = {
                "name": ten_hang,
                "code": ma_hang,
                "barcode": safe_string(product_data.get('ma_vach', '')),
                "unit": safe_string(product_data.get('don_vi_tinh', 'Cái')),
                "categoryId": category_id,  # Use fetched category ID
                "price": gia_ban,
                "costPrice": gia_von,
                "quantity": ton_kho,
                "description": f"Demo product: {nhom_hang}",
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
                error = f"Product {ma_hang}: {response.status_code}"
                try:
                    error_detail = response.json().get('message', response.text)
                    error += f" - {error_detail}"
                except:
                    error += f" - {response.text[:100]}"
                self.tracking['errors'].append(error)
                print(f"  ⚠️  {error}")
                return None

        except Exception as e:
            error = f"Product {product_data.get('ma_hang', 'UNKNOWN')}: {str(e)}"
            self.tracking['errors'].append(error)
            print(f"  ⚠️  {error}")
            return None

    def create_customer(self, customer_data: Dict) -> Optional[str]:
        """Create a customer in Kiotviet. Returns customer ID if successful."""
        try:
            # Sanitize and validate data
            ma_khach = safe_string(customer_data.get('ma_khach_hang', 'UNKNOWN'))
            ten_khach = safe_string(customer_data.get('ten_khach_hang', 'Unnamed'))
            dien_thoai = safe_phone(customer_data.get('dien_thoai', ''))
            email = safe_email(customer_data.get('email', ''))
            dia_chi = safe_string(customer_data.get('dia_chi', ''))

            payload = {
                "code": ma_khach,
                "name": ten_khach,
                "phone": dien_thoai,
                "email": email,
                "address": dia_chi,
                "type": 1,  # 1 = Customer
                "description": "Demo customer",
                "branchId": self.branch_id,  # Required: chi nhánh
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
                error = f"Customer {ma_khach}: {response.status_code}"
                try:
                    error_detail = response.json().get('message', response.text)
                    error += f" - {error_detail}"
                except:
                    error += f" - {response.text[:100]}"
                self.tracking['errors'].append(error)
                print(f"  ⚠️  {error}")
                return None

        except Exception as e:
            error = f"Customer {customer_data.get('ma_khach_hang', 'UNKNOWN')}: {str(e)}"
            self.tracking['errors'].append(error)
            print(f"  ⚠️  {error}")
            return None

    def create_invoice(self, invoice_data: Dict, items_data: List[Dict],
                      kiotviet_customer_map: Dict, kiotviet_product_map: Dict) -> Optional[str]:
        """Create an invoice in Kiotviet. Returns invoice ID if successful."""
        try:
            # Sanitize invoice data
            ma_hoa_don = safe_string(invoice_data.get('ma_hoa_don', 'UNKNOWN'))

            # Get customer ID from mapping
            ma_khach = invoice_data.get('ma_khach_hang')
            customer_id = kiotviet_customer_map.get(ma_khach)
            if not customer_id:
                print(f"  ⚠️  Customer not found for invoice {ma_hoa_don}")
                return None

            # Build invoice items with sanitized data
            invoice_items = []
            for item in items_data:
                ma_hang = item.get('ma_hang')
                product_id = kiotviet_product_map.get(ma_hang)
                if not product_id:
                    continue

                # Sanitize item data
                so_luong = safe_int(item.get('so_luong', 1), 1)
                don_gia = safe_int(item.get('don_gia', 0))
                giam_gia = safe_int(item.get('giam_gia', 0))

                if so_luong > 0 and don_gia >= 0:
                    invoice_items.append({
                        "productId": product_id,
                        "quantity": so_luong,
                        "price": don_gia,
                        "discount": max(0, giam_gia),  # Discount cannot be negative
                    })

            if not invoice_items:
                print(f"  ⚠️  No valid items for invoice {ma_hoa_don}")
                return None

            # Sanitize invoice totals
            khach_da_tra = safe_int(invoice_data.get('khach_da_tra', 0))
            thoi_gian = safe_string(invoice_data.get('thoi_gian', ''))

            payload = {
                "customerId": customer_id,
                "code": ma_hoa_don,
                "invoiceDate": thoi_gian,
                "description": "Demo invoice",
                "items": invoice_items,
                "totalAmount": max(0, khach_da_tra),  # Total cannot be negative
                "branchId": self.branch_id,  # Required: chi nhánh
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
                error = f"Invoice {ma_hoa_don}: {response.status_code}"
                try:
                    error_detail = response.json().get('message', response.text)
                    error += f" - {error_detail}"
                except:
                    error += f" - {response.text[:100]}"
                self.tracking['errors'].append(error)
                print(f"  ⚠️  {error}")
                return None

        except Exception as e:
            ma_hoa_don = invoice_data.get('ma_hoa_don', 'UNKNOWN')
            error = f"Invoice {ma_hoa_don}: {str(e)}"
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

    # Fetch product categories from Kiotviet
    if not uploader.fetch_categories():
        print("\n❌ Cannot proceed without fetching categories from Kiotviet")
        return False

    # Fetch branches from Kiotviet
    if not uploader.fetch_branches():
        print("\n❌ Cannot proceed without fetching branches from Kiotviet")
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
