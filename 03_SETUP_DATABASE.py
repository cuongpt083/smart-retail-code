#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 Setup SQLite Database from Synthetic CSV Data

Tệp này import dữ liệu CSV vào SQLite database để chuẩn bị cho dashboard analytics.

Cách sử dụng:
  python 03_SETUP_DATABASE.py

Yêu cầu:
  pip install pandas sqlite3
"""

import sqlite3
import pandas as pd
from pathlib import Path
import sys

def setup_database():
    """Tạo SQLite database từ CSV files"""

    print("="*70)
    print("🚀 Smart Retail Analytics - Database Setup")
    print("="*70)

    # Paths
    script_dir = Path(__file__).parent
    csv_dir = script_dir
    db_path = script_dir / 'retail.db'

    # Check if CSV files exist
    csv_files = {
        'products': csv_dir / 'products.csv',
        'customers': csv_dir / 'customers.csv',
        'invoices': csv_dir / 'invoices.csv',
        'invoice_items': csv_dir / 'invoice_items.csv',
    }

    print("\n📋 Checking CSV files...")
    for name, path in csv_files.items():
        if path.exists():
            print(f"  ✅ {name}: {path}")
        else:
            print(f"  ❌ {name}: NOT FOUND - {path}")
            print("\n⚠️  Make sure all CSV files are in the same directory as this script:")
            print(f"   - {csv_dir}")
            return False

    # Read CSV files
    print("\n📖 Reading CSV files...")
    try:
        df_products = pd.read_csv(csv_files['products'])
        print(f"  ✅ products.csv: {len(df_products)} rows")

        df_customers = pd.read_csv(csv_files['customers'])
        print(f"  ✅ customers.csv: {len(df_customers)} rows")

        df_invoices = pd.read_csv(csv_files['invoices'])
        print(f"  ✅ invoices.csv: {len(df_invoices)} rows")

        df_items = pd.read_csv(csv_files['invoice_items'])
        print(f"  ✅ invoice_items.csv: {len(df_items)} rows")
    except Exception as e:
        print(f"\n❌ Error reading CSV: {e}")
        return False

    # Remove existing database if exists
    if db_path.exists():
        print(f"\n🗑️  Removing existing database: {db_path}")
        db_path.unlink()

    # Create database
    print(f"\n💾 Creating SQLite database: {db_path}")
    try:
        conn = sqlite3.connect(str(db_path))

        # Insert data
        print("\n📥 Inserting data into database...")

        print("   • Inserting products...")
        df_products.to_sql('products', conn, if_exists='replace', index=False)

        print("   • Inserting customers...")
        df_customers.to_sql('customers', conn, if_exists='replace', index=False)

        print("   • Inserting invoices...")
        df_invoices.to_sql('invoices', conn, if_exists='replace', index=False)

        print("   • Inserting invoice_items...")
        df_items.to_sql('invoice_items', conn, if_exists='replace', index=False)

        conn.commit()

        # Verify data
        print("\n✅ Database created successfully!")

        cursor = conn.cursor()
        print("\n📊 Data Summary:")

        # Product stats
        n_products = cursor.execute('SELECT COUNT(*) FROM products').fetchone()[0]
        avg_price = cursor.execute('SELECT AVG(gia_ban) FROM products').fetchone()[0]
        print(f"   Products: {n_products} items (avg price: {avg_price:,.0f} VND)")

        # Customer stats
        n_customers = cursor.execute('SELECT COUNT(*) FROM customers').fetchone()[0]
        avg_spend = cursor.execute('SELECT AVG(tong_ban) FROM customers').fetchone()[0]
        print(f"   Customers: {n_customers} (avg spend: {avg_spend:,.0f} VND)")

        # Invoice stats
        n_invoices = cursor.execute('SELECT COUNT(*) FROM invoices').fetchone()[0]
        total_revenue = cursor.execute('SELECT SUM(khach_da_tra) FROM invoices').fetchone()[0]
        avg_revenue = cursor.execute('SELECT AVG(khach_da_tra) FROM invoices').fetchone()[0]
        print(f"   Invoices: {n_invoices} (total: {total_revenue:,.0f} VND, avg: {avg_revenue:,.0f} VND)")

        # Items stats
        n_items = cursor.execute('SELECT COUNT(*) FROM invoice_items').fetchone()[0]
        print(f"   Items: {n_items} line items")

        # Time range
        date_range = cursor.execute('SELECT MIN(thoi_gian), MAX(thoi_gian) FROM invoices').fetchone()
        print(f"   Time range: {date_range[0]} to {date_range[1]}")

        conn.close()

        print(f"\n🎉 Database ready at: {db_path}")
        print("\nNext steps:")
        print("   1. Use this database for Streamlit dashboard")
        print("   2. Run RFM analysis and market basket analysis")
        print("   3. Build visualizations from the data")

        return True

    except Exception as e:
        print(f"\n❌ Error creating database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = setup_database()
    sys.exit(0 if success else 1)
