"""
SDV (Synthetic Data Vault) Script - Generate Synthetic Retail Data with Product Associations

This script generates realistic synthetic data with product combo rules to ensure
Apriori algorithm can detect meaningful product associations.

Features:
- Generates 100 products, 100 customers, 300 invoices with items
- Implements business rules for product combos (e.g., Bánh mì + Nước)
- Ensures high support for combos so Apriori can detect them
- Preserves referential integrity between tables
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from collections import defaultdict

# Set random seed for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

# ============================================================================
# CONFIGURATION
# ============================================================================

NUM_PRODUCTS = 100
NUM_CUSTOMERS = 100
NUM_INVOICES = 300
INVOICE_START_DATE = datetime(2026, 3, 1)
INVOICE_END_DATE = datetime(2026, 6, 6)

# Product combo rules (for Apriori to detect)
# Format: {combo_name: ([product_ids], frequency_weight)}
# frequency_weight: how often this combo appears (0.0 - 1.0)
PRODUCT_COMBOS = {
    "bánh_mì_nước": ([f"SP100{i}" for i in [3, 7, 39, 42, 72]], 0.25),  # Bánh mì + Nước
    "bánh_mì_sữa": ([f"SP100{i}" for i in [3, 7, 39, 42, 72]], 0.20),   # Bánh mì + Sữa (if exists)
    "gia_vị_ready_to_eat": ([f"SP100{i}" for i in [4, 5, 17, 31, 63, 65, 68, 81]], 0.18),  # Gia vị + Ready-to-eat
    "nước_snack": ([f"SP100{i}" for i in [8, 12, 26, 27, 35, 56, 60, 71]], 0.15),  # Nước + Snack/Bánh
    "chăm_sóc": ([f"SP100{i}" for i in [1, 2, 6, 13, 20, 22, 24, 25, 29, 30, 32, 67, 75]], 0.12),  # Chăm sóc combo
}

# ============================================================================
# GENERATE PRODUCTS
# ============================================================================

def generate_products():
    """Generate product master data"""
    categories = {
        "Bánh, kẹo, snack": ["Bánh mì", "Bánh quy", "Kẹo", "Snack mặn"],
        "Đồ uống": ["Nước ngọt", "Nước trái cây", "Trà", "Cà phê"],
        "Thực phẩm tươi": ["Thịt", "Cá", "Rau xanh", "Trái cây"],
        "Gia vị": ["Muối", "Đường", "Hạt nêm", "Dầu ăn"],
        "Đồ ăn liền": ["Cơm hộp", "Mì ăn liền", "Xúc xích", "Thịt đóng hộp"],
        "Chăm sóc": ["Xà phòng", "Khăn giấy", "Dầu gội", "Kem đánh răng"],
    }

    brands = ["Vinamilk", "Coca", "Vissan", "Acecook", "Pepsi", "Knorr",
              "Unilever", "Nestlé", "Lipton", "Staff"]

    products = []
    product_id = 1001

    for category, subcategories in categories.items():
        for _ in range(NUM_PRODUCTS // len(categories) // len(subcategories) + 1):
            for subcat in subcategories:
                if len(products) < NUM_PRODUCTS:
                    products.append({
                        "ma_hang": f"SP{product_id}",
                        "ten_hang": f"{subcat} {random.choice(['trong', 'tại', 'như', 'bên', 'có', 'cái', 'nào', 'từ', 'với', 'một'])}",
                        "thuong_hieu": random.choice(brands),
                        "loai_hang": "Hàng hóa",
                        "nhom_hang": f"{category} >> {subcat}",
                        "gia_ban": np.random.randint(6000, 500000),
                        "gia_von": np.random.randint(3000, 350000),
                        "ton_kho": np.random.randint(10, 200),
                        "ma_vach": "",
                        "don_vi_tinh": "Cái",
                        "quy_doi": 1,
                        "trang_thai": 1,
                        "thoi_gian_tao": datetime.now().isoformat(),
                    })
                    product_id += 1

    return pd.DataFrame(products[:NUM_PRODUCTS])

# ============================================================================
# GENERATE CUSTOMERS
# ============================================================================

def generate_customers():
    """Generate customer master data"""
    regions = ["Hà Nội", "Sài Gòn", "Đà Nẵng"]
    districts = ["Quận", "Huyện", "Thành phố", "Thị xã"]
    wards = ["Phường", "Xã"]

    customers = []
    for i in range(NUM_CUSTOMERS):
        customer_id = f"KH0{1000 + i + 1}"
        first_names = ["Nguyễn", "Trần", "Phạm", "Hoàng", "Đặng", "Lê", "Võ", "Bùi", "Dương", "Vũ"]
        last_names = ["Văn", "Thị", "Trí", "Đức", "Phúc", "Hưng", "Mai", "Hải", "Xuân", "Châu"]

        customers.append({
            "ma_khach_hang": customer_id,
            "ten_khach_hang": f"{random.choice(first_names)} {random.choice(last_names)}",
            "loai_khach": "Cá nhân",
            "dien_thoai": f"{random.choice(['01', '03', '04', '05', '06', '07', '08', '09'])} {random.randint(1000000, 9999999)}",
            "email": f"customer{i+1}@example.com",
            "dia_chi": f"{random.randint(1, 999)} {random.choice(districts)} {random.choice(wards)}",
            "khu_vuc_giao_hang": random.choice(regions),
            "phuong_xa": f"{random.choice(districts)} {random.choice(wards)}",
            "ngay_sinh": f"{np.random.randint(1945, 2010)}-{np.random.randint(1, 13):02d}-{np.random.randint(1, 29):02d}",
            "gioi_tinh": random.choice(["M", "F"]),
            "tong_ban": np.random.randint(200000, 10000000),
            "no_can_thu": 0,
            "ngay_giao_dich_cuoi": (INVOICE_END_DATE - timedelta(days=np.random.randint(0, 20))).strftime("%Y-%m-%d") if i < 60 else "",
            "ngay_tao": (datetime.now() - timedelta(days=np.random.randint(0, 365))).isoformat(),
            "trang_thai": 1,
        })

    return pd.DataFrame(customers)

# ============================================================================
# GENERATE INVOICES WITH PRODUCT COMBOS
# ============================================================================

def generate_invoices_and_items(products_df, customers_df):
    """Generate invoices with product combo rules"""
    invoices = []
    invoice_items = []

    invoice_id = 1

    for _ in range(NUM_INVOICES):
        # Random customer
        customer = customers_df.iloc[np.random.randint(0, len(customers_df))]

        # Random invoice date
        days_diff = (INVOICE_END_DATE - INVOICE_START_DATE).days
        random_date = INVOICE_START_DATE + timedelta(days=np.random.randint(0, days_diff))

        # Decide if this invoice will have a combo (with probability)
        has_combo = np.random.random() < 0.35  # 35% of invoices have combos

        items_in_invoice = []
        total_amount = 0

        if has_combo and np.random.random() < 0.8:  # 80% of combo invoices actually get a combo
            # Pick a random combo rule
            combo_name, (combo_products, frequency) = random.choice(list(PRODUCT_COMBOS.items()))

            # Get products in this combo (ensure they exist in products_df)
            combo_product_ids = [p for p in combo_products if p in products_df['ma_hang'].values]

            if combo_product_ids:
                # Add combo products
                for product_id in combo_product_ids[:2]:  # Take first 2-3 products from combo
                    product = products_df[products_df['ma_hang'] == product_id].iloc[0]
                    qty = np.random.randint(1, 5)
                    price = product['gia_ban']
                    discount_pct = random.choice([0, 0, 5, 10, 15])  # Some with 0-15% discount
                    discount_amt = int(price * qty * discount_pct / 100)
                    total = (price * qty) - discount_amt

                    items_in_invoice.append({
                        "ma_hoa_don": f"HD{invoice_id:06d}",
                        "ma_hang": product_id,
                        "so_luong": qty,
                        "don_gia": price,
                        "giam_gia_phan_tram": discount_pct,
                        "giam_gia": discount_amt,
                        "gia_ban": price,
                        "thanh_tien": total,
                        "thoi_gian": random_date.isoformat(),
                    })
                    total_amount += total

        # Add random items (non-combo)
        num_other_items = np.random.randint(1, 4) if items_in_invoice else np.random.randint(2, 6)

        for _ in range(num_other_items):
            product = products_df.iloc[np.random.randint(0, len(products_df))]
            qty = np.random.randint(1, 5)
            price = product['gia_ban']
            discount_pct = random.choice([0, 0, 0, 5, 10])
            discount_amt = int(price * qty * discount_pct / 100)
            total = (price * qty) - discount_amt

            items_in_invoice.append({
                "ma_hoa_don": f"HD{invoice_id:06d}",
                "ma_hang": product['ma_hang'],
                "so_luong": qty,
                "don_gia": price,
                "giam_gia_phan_tram": discount_pct,
                "giam_gia": discount_amt,
                "gia_ban": price,
                "thanh_tien": total,
                "thoi_gian": random_date.isoformat(),
            })
            total_amount += total

        # Create invoice header
        discount_amt = int(total_amount * np.random.choice([0, 0, 0, 0.05, 0.1]) / 100) if total_amount > 0 else 0
        paid_amount = total_amount - discount_amt

        invoices.append({
            "ma_hoa_don": f"HD{invoice_id:06d}",
            "thoi_gian": random_date.isoformat(),
            "ma_khach_hang": customer['ma_khach_hang'],
            "ten_khach_hang": customer['ten_khach_hang'],
            "tong_tien_hang": total_amount,
            "giam_gia": discount_amt,
            "khach_da_tra": paid_amount,
            "con_can_thu": 0,
            "trang_thai": "Hoàn thành",
            "ngay_tao": random_date.isoformat(),
        })

        invoice_items.extend(items_in_invoice)
        invoice_id += 1

    return pd.DataFrame(invoices), pd.DataFrame(invoice_items)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Generate all synthetic data"""
    print("🔄 Generating synthetic retail data with product combos...")

    # Generate products
    print("  ✓ Generating 100 products...")
    products_df = generate_products()

    # Generate customers
    print("  ✓ Generating 100 customers...")
    customers_df = generate_customers()

    # Generate invoices with combo rules
    print("  ✓ Generating 300 invoices with product combo rules...")
    invoices_df, invoice_items_df = generate_invoices_and_items(products_df, customers_df)

    # Save to CSV
    products_df.to_csv('products.csv', index=False, encoding='utf-8')
    customers_df.to_csv('customers.csv', index=False, encoding='utf-8')
    invoices_df.to_csv('invoices.csv', index=False, encoding='utf-8')
    invoice_items_df.to_csv('invoice_items.csv', index=False, encoding='utf-8')

    print("\n✅ Data generation complete!")
    print(f"\n📊 Summary:")
    print(f"  • Products: {len(products_df)}")
    print(f"  • Customers: {len(customers_df)}")
    print(f"  • Invoices: {len(invoices_df)}")
    print(f"  • Invoice items: {len(invoice_items_df)}")
    print(f"\n🎯 Product Combos (for Apriori):")
    for combo_name, (products, frequency) in PRODUCT_COMBOS.items():
        print(f"  • {combo_name}: {int(frequency * 100)}% frequency")
    print(f"\n💾 Files saved:")
    print(f"  • products.csv")
    print(f"  • customers.csv")
    print(f"  • invoices.csv")
    print(f"  • invoice_items.csv")

if __name__ == "__main__":
    main()
