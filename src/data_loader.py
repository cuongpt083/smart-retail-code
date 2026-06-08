"""Data Loader - Read from SQLite database"""

import sqlite3
import pandas as pd
from typing import Optional


class DataLoader:
    """Load data from SQLite retail database"""

    def __init__(self, db_path: str = "retail.db"):
        """Initialize with database path"""
        self.db_path = db_path

    def load_products(self) -> pd.DataFrame:
        """Load products table"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql("SELECT * FROM products", conn)
        conn.close()
        return df

    def load_customers(self) -> pd.DataFrame:
        """Load customers table"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql("SELECT * FROM customers", conn)
        conn.close()
        return df

    def load_invoices(self) -> pd.DataFrame:
        """Load invoices table"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql("SELECT * FROM invoices", conn)
        conn.close()
        return df

    def load_invoice_items(self) -> pd.DataFrame:
        """Load invoice items table"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql("SELECT * FROM invoice_items", conn)
        conn.close()
        return df

    def load_vendors(self) -> pd.DataFrame:
        """Load vendors table"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql("SELECT * FROM vendors", conn)
        conn.close()
        return df
