"""
Load Synthetic Data into SQLite Database

This script reads the generated CSV files and loads them into SQLite database
with proper schema creation and data integrity.

Flow:
1. CSV files (products.csv, customers.csv, invoices.csv, invoice_items.csv)
   ↓
2. This script creates SQLite tables
   ↓
3. Load data with type conversion and validation
   ↓
4. SQLite database (retail.db) ready to use
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# ============================================================================
# CONFIGURATION
# ============================================================================

DB_PATH = "retail.db"
CSV_FILES = {
    "products": "products.csv",
    "customers": "customers.csv",
    "invoices": "invoices.csv",
    "invoice_items": "invoice_items.csv",
}

# ============================================================================
# CREATE TABLES
# ============================================================================

def create_tables(conn):
    """Create SQLite tables with proper schema"""
    cursor = conn.cursor()

    print("📋 Creating database schema...")

    # Products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            ma_hang TEXT PRIMARY KEY,
            ten_hang TEXT NOT NULL,
            thuong_hieu TEXT,
            loai_hang TEXT,
            nhom_hang TEXT,
            gia_ban REAL,
            gia_von REAL,
            ton_kho INTEGER,
            ma_vach TEXT,
            don_vi_tinh TEXT,
            quy_doi INTEGER,
            trang_thai INTEGER,
            thoi_gian_tao TEXT
        )
    """)
    print("  ✓ products table created")

    # Customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            ma_khach_hang TEXT PRIMARY KEY,
            ten_khach_hang TEXT NOT NULL,
            loai_khach TEXT,
            dien_thoai TEXT,
            email TEXT,
            dia_chi TEXT,
            khu_vuc_giao_hang TEXT,
            phuong_xa TEXT,
            ngay_sinh TEXT,
            gioi_tinh TEXT,
            tong_ban REAL,
            no_can_thu REAL,
            ngay_giao_dich_cuoi TEXT,
            ngay_tao TEXT,
            trang_thai INTEGER
        )
    """)
    print("  ✓ customers table created")

    # Invoices table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            ma_hoa_don TEXT PRIMARY KEY,
            thoi_gian TEXT,
            ma_khach_hang TEXT NOT NULL,
            ten_khach_hang TEXT,
            tong_tien_hang REAL,
            giam_gia REAL,
            khach_da_tra REAL,
            con_can_thu REAL,
            trang_thai TEXT,
            ngay_tao TEXT,
            FOREIGN KEY (ma_khach_hang) REFERENCES customers(ma_khach_hang)
        )
    """)
    print("  ✓ invoices table created")

    # Invoice items table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_hoa_don TEXT NOT NULL,
            ma_hang TEXT NOT NULL,
            so_luong INTEGER,
            don_gia REAL,
            giam_gia_phan_tram REAL,
            giam_gia REAL,
            gia_ban REAL,
            thanh_tien REAL,
            thoi_gian TEXT,
            FOREIGN KEY (ma_hoa_don) REFERENCES invoices(ma_hoa_don),
            FOREIGN KEY (ma_hang) REFERENCES products(ma_hang)
        )
    """)
    print("  ✓ invoice_items table created")

    conn.commit()

# ============================================================================
# LOAD DATA FROM CSV
# ============================================================================

def load_products(conn, csv_file):
    """Load products from CSV"""
    print(f"\n📦 Loading products from {csv_file}...")

    # Check if file exists
    if not Path(csv_file).exists():
        print(f"  ❌ File not found: {csv_file}")
        return False

    try:
        df = pd.read_csv(csv_file, dtype={
            'ma_hang': str,
            'ten_hang': str,
            'thuong_hieu': str,
            'loai_hang': str,
            'nhom_hang': str,
            'gia_ban': float,
            'gia_von': float,
            'ton_kho': int,
        })

        # Insert data
        df.to_sql('products', conn, if_exists='append', index=False)
        print(f"  ✓ Loaded {len(df)} products")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def load_customers(conn, csv_file):
    """Load customers from CSV"""
    print(f"\n👥 Loading customers from {csv_file}...")

    if not Path(csv_file).exists():
        print(f"  ❌ File not found: {csv_file}")
        return False

    try:
        df = pd.read_csv(csv_file, dtype={
            'ma_khach_hang': str,
            'ten_khach_hang': str,
            'loai_khach': str,
            'dien_thoai': str,
            'email': str,
            'tong_ban': float,
        })

        df.to_sql('customers', conn, if_exists='append', index=False)
        print(f"  ✓ Loaded {len(df)} customers")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def load_invoices(conn, csv_file):
    """Load invoices from CSV"""
    print(f"\n🧾 Loading invoices from {csv_file}...")

    if not Path(csv_file).exists():
        print(f"  ❌ File not found: {csv_file}")
        return False

    try:
        df = pd.read_csv(csv_file, dtype={
            'ma_hoa_don': str,
            'thoi_gian': str,
            'ma_khach_hang': str,
            'ten_khach_hang': str,
            'tong_tien_hang': float,
            'giam_gia': float,
            'khach_da_tra': float,
            'con_can_thu': float,
        })

        df.to_sql('invoices', conn, if_exists='append', index=False)
        print(f"  ✓ Loaded {len(df)} invoices")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def load_invoice_items(conn, csv_file):
    """Load invoice items from CSV"""
    print(f"\n📝 Loading invoice items from {csv_file}...")

    if not Path(csv_file).exists():
        print(f"  ❌ File not found: {csv_file}")
        return False

    try:
        df = pd.read_csv(csv_file, dtype={
            'ma_hoa_don': str,
            'ma_hang': str,
            'so_luong': int,
            'don_gia': float,
            'giam_gia_phan_tram': float,
            'giam_gia': float,
            'gia_ban': float,
            'thanh_tien': float,
        })

        # Remove id column if it exists (SQLite will auto-generate)
        if 'id' in df.columns:
            df = df.drop('id', axis=1)

        df.to_sql('invoice_items', conn, if_exists='append', index=False)
        print(f"  ✓ Loaded {len(df)} invoice items")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

# ============================================================================
# VERIFY DATA
# ============================================================================

def verify_data(conn):
    """Verify loaded data integrity"""
    print("\n🔍 Verifying data integrity...")

    cursor = conn.cursor()

    # Check products
    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0]
    print(f"  ✓ Products: {product_count}")

    # Check customers
    cursor.execute("SELECT COUNT(*) FROM customers")
    customer_count = cursor.fetchone()[0]
    print(f"  ✓ Customers: {customer_count}")

    # Check invoices
    cursor.execute("SELECT COUNT(*) FROM invoices")
    invoice_count = cursor.fetchone()[0]
    print(f"  ✓ Invoices: {invoice_count}")

    # Check invoice items
    cursor.execute("SELECT COUNT(*) FROM invoice_items")
    item_count = cursor.fetchone()[0]
    print(f"  ✓ Invoice items: {item_count}")

    # Check foreign key constraints
    print("\n✓ Checking foreign key references...")

    # Invoices referencing non-existent customers
    cursor.execute("""
        SELECT COUNT(*) FROM invoices i
        WHERE NOT EXISTS (SELECT 1 FROM customers c WHERE c.ma_khach_hang = i.ma_khach_hang)
    """)
    orphan_invoices = cursor.fetchone()[0]
    if orphan_invoices == 0:
        print("  ✓ All invoices reference valid customers")
    else:
        print(f"  ⚠️  {orphan_invoices} invoices reference non-existent customers")

    # Invoice items referencing non-existent products/invoices
    cursor.execute("""
        SELECT COUNT(*) FROM invoice_items ii
        WHERE NOT EXISTS (SELECT 1 FROM products p WHERE p.ma_hang = ii.ma_hang)
        OR NOT EXISTS (SELECT 1 FROM invoices i WHERE i.ma_hoa_don = ii.ma_hoa_don)
    """)
    orphan_items = cursor.fetchone()[0]
    if orphan_items == 0:
        print("  ✓ All invoice items reference valid products and invoices")
    else:
        print(f"  ⚠️  {orphan_items} invoice items have invalid references")

    return {
        'products': product_count,
        'customers': customer_count,
        'invoices': invoice_count,
        'items': item_count,
    }

# ============================================================================
# CREATE INDICES
# ============================================================================

def create_indices(conn):
    """Create indices for better query performance"""
    print("\n⚡ Creating indices for performance...")

    cursor = conn.cursor()

    # Invoice indices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_customer ON invoices(ma_khach_hang)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(thoi_gian)")

    # Invoice items indices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_invoice ON invoice_items(ma_hoa_don)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_product ON invoice_items(ma_hang)")

    # Customer indices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_customer_region ON customers(khu_vuc_giao_hang)")

    # Product indices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_product_category ON products(nhom_hang)")

    conn.commit()
    print("  ✓ Indices created")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution flow"""
    print("=" * 70)
    print("📊 LOADING SYNTHETIC DATA INTO SQLITE DATABASE")
    print("=" * 70)

    # Check if CSV files exist
    print("\n🔎 Checking for CSV files...")
    missing_files = []
    for name, file in CSV_FILES.items():
        if Path(file).exists():
            size = Path(file).stat().st_size / 1024  # Size in KB
            print(f"  ✓ {file} ({size:.1f} KB)")
        else:
            print(f"  ❌ {file} NOT FOUND")
            missing_files.append(file)

    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        print("   Run: python generate_synthetic_data.py")
        return False

    # Connect to database
    print(f"\n🗄️  Connecting to database: {DB_PATH}...")
    try:
        # Enable foreign key constraints
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        print(f"  ✓ Connected to {DB_PATH}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

    # Create tables
    try:
        create_tables(conn)
    except Exception as e:
        print(f"  ❌ Error creating tables: {e}")
        conn.close()
        return False

    # Load data
    try:
        results = []
        results.append(load_products(conn, CSV_FILES['products']))
        results.append(load_customers(conn, CSV_FILES['customers']))
        results.append(load_invoices(conn, CSV_FILES['invoices']))
        results.append(load_invoice_items(conn, CSV_FILES['invoice_items']))

        if not all(results):
            print("\n⚠️  Some files failed to load")
            conn.close()
            return False

    except Exception as e:
        print(f"  ❌ Error loading data: {e}")
        conn.close()
        return False

    # Create indices
    try:
        create_indices(conn)
    except Exception as e:
        print(f"  ⚠️  Error creating indices: {e}")

    # Verify data
    try:
        stats = verify_data(conn)
    except Exception as e:
        print(f"  ❌ Error verifying data: {e}")
        conn.close()
        return False

    # Close connection
    conn.close()

    # Summary
    print("\n" + "=" * 70)
    print("✅ DATA LOADING COMPLETE!")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"  • Database: {DB_PATH}")
    print(f"  • Products: {stats['products']}")
    print(f"  • Customers: {stats['customers']}")
    print(f"  • Invoices: {stats['invoices']}")
    print(f"  • Invoice items: {stats['items']}")
    print(f"\n🎯 Next steps:")
    print(f"  1. Start the Streamlit app: streamlit run app.py")
    print(f"  2. Dashboard should now display Apriori recommendations")
    print(f"  3. Check Admin dashboard to see RFM segments")
    print(f"\n💡 Useful queries:")
    print(f"  • SELECT COUNT(*) FROM products;")
    print(f"  • SELECT COUNT(*) FROM invoices;")
    print(f"  • SELECT * FROM invoice_items LIMIT 10;")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
