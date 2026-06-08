"""
Kiotviet API Client - Integration with Kiotviet retail platform

Handles:
- Authentication & token management
- Fetching orders, invoices, products
- Data mapping to SQLite schema
- Error recovery & retry logic
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sqlite3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KiotvietClient:
    """Client for Kiotviet API integration"""

    # API Configuration
    BASE_URL = "https://api.kiotviet.vn"
    VERSION = "1.0"

    def __init__(
        self,
        retail_id: str,
        api_key: str,
        db_path: str = "retail.db"
    ):
        """
        Initialize Kiotviet client

        Args:
            retail_id: Your Kiotviet retail ID (from Kiotviet account)
            api_key: Your Kiotviet API key (from Kiotviet developer portal)
            db_path: SQLite database path
        """
        self.retail_id = retail_id
        self.api_key = api_key
        self.db_path = db_path
        self.session = self._create_session()
        self.headers = {
            "Retailer": retail_id,
            "Authorization": api_key,
            "Content-Type": "application/json",
        }
        self.last_sync = None

    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic"""
        session = requests.Session()

        # Retry strategy: 3 retries with exponential backoff
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict:
        """
        Make API request with error handling

        Args:
            method: HTTP method (GET, POST, etc)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            data: Request body

        Returns:
            Response JSON
        """
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            if method == "GET":
                response = self.session.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=10
                )
            elif method == "POST":
                response = self.session.post(
                    url,
                    headers=self.headers,
                    json=data,
                    timeout=10
                )
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            logger.error(f"Timeout calling {endpoint}")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code} calling {endpoint}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error calling {endpoint}: {e}")
            raise

    # ========================================================================
    # CUSTOMER OPERATIONS
    # ========================================================================

    def get_customers(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Fetch customers from Kiotviet

        Returns list of customer dicts with:
        - ma_khach_hang (customer ID)
        - ten_khach_hang (customer name)
        - dien_thoai (phone)
        - dia_chi (address)
        """
        try:
            response = self._make_request(
                "GET",
                "customers",
                params={"limit": limit, "offset": offset}
            )

            customers = response.get("data", [])
            logger.info(f"Fetched {len(customers)} customers from Kiotviet")

            return [
                {
                    "ma_khach_hang": c.get("id"),
                    "ten_khach_hang": c.get("name"),
                    "dien_thoai": c.get("phone", ""),
                    "dia_chi": c.get("address", ""),
                    "email": c.get("email", ""),
                }
                for c in customers
            ]

        except Exception as e:
            logger.error(f"Error fetching customers: {e}")
            return []

    # ========================================================================
    # PRODUCT OPERATIONS
    # ========================================================================

    def get_products(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Fetch products from Kiotviet

        Returns list of product dicts with:
        - ma_hang (product ID)
        - ten_hang (product name)
        - gia_ban (selling price)
        - so_luong_ton (stock quantity)
        """
        try:
            response = self._make_request(
                "GET",
                "products",
                params={"limit": limit, "offset": offset}
            )

            products = response.get("data", [])
            logger.info(f"Fetched {len(products)} products from Kiotviet")

            return [
                {
                    "ma_hang": p.get("id"),
                    "ten_hang": p.get("name"),
                    "gia_ban": p.get("price", 0),
                    "so_luong_ton": p.get("stock", 0),
                    "mo_ta": p.get("description", ""),
                }
                for p in products
            ]

        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            return []

    # ========================================================================
    # INVOICE OPERATIONS (Main Data Source)
    # ========================================================================

    def get_orders(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Fetch invoices/orders from Kiotviet since last sync

        Args:
            from_date: Start date for fetching
            to_date: End date for fetching
            limit: Max orders to fetch
            offset: Pagination offset

        Returns:
            Tuple of (invoices, invoice_items)
        """
        try:
            # Default: fetch from last sync or last 24 hours
            if from_date is None:
                if self.last_sync:
                    from_date = self.last_sync
                else:
                    from_date = datetime.now() - timedelta(hours=24)

            if to_date is None:
                to_date = datetime.now()

            params = {
                "fromDate": from_date.isoformat(),
                "toDate": to_date.isoformat(),
                "limit": limit,
                "offset": offset,
            }

            response = self._make_request("GET", "invoices", params=params)

            invoices_data = response.get("data", [])
            logger.info(f"Fetched {len(invoices_data)} invoices from Kiotviet")

            # Process invoices and items
            invoices = []
            items = []

            for inv in invoices_data:
                invoice_dict = {
                    "ma_hoa_don": inv.get("id"),
                    "ma_khach_hang": inv.get("customer_id"),
                    "thoi_gian": inv.get("created_at", datetime.now().isoformat()),
                    "khach_da_tra": inv.get("total_amount", 0),
                    "thanh_tien": inv.get("total_amount", 0),
                    "ghi_chu": inv.get("note", ""),
                }
                invoices.append(invoice_dict)

                # Process items in invoice
                for item in inv.get("items", []):
                    item_dict = {
                        "ma_hoa_don": inv.get("id"),
                        "ma_hang": item.get("product_id"),
                        "so_luong": item.get("quantity", 0),
                        "gia_ban": item.get("price", 0),
                        "thanh_tien": item.get("amount", 0),
                    }
                    items.append(item_dict)

            # Update last sync time
            self.last_sync = to_date

            return invoices, items

        except Exception as e:
            logger.error(f"Error fetching invoices: {e}")
            return [], []

    # ========================================================================
    # DATABASE SYNC
    # ========================================================================

    def sync_to_sqlite(
        self,
        full_sync: bool = False
    ) -> Dict:
        """
        Sync Kiotviet data to SQLite database

        Args:
            full_sync: If True, fetch all data. If False, only new since last sync.

        Returns:
            Dict with sync results
        """
        results = {
            "customers_added": 0,
            "products_added": 0,
            "invoices_added": 0,
            "items_added": 0,
            "errors": [],
        }

        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Fetch customers
            logger.info("Syncing customers...")
            customers = self.get_customers()
            for cust in customers:
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO customers
                        (ma_khach_hang, ten_khach_hang, dien_thoai, dia_chi, email)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        cust["ma_khach_hang"],
                        cust["ten_khach_hang"],
                        cust["dien_thoai"],
                        cust["dia_chi"],
                        cust.get("email", "")
                    ))
                    results["customers_added"] += 1
                except Exception as e:
                    results["errors"].append(f"Customer sync error: {e}")

            # Fetch products
            logger.info("Syncing products...")
            products = self.get_products()
            for prod in products:
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO products
                        (ma_hang, ten_hang, gia_ban, so_luong_ton, mo_ta)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        prod["ma_hang"],
                        prod["ten_hang"],
                        prod["gia_ban"],
                        prod["so_luong_ton"],
                        prod.get("mo_ta", "")
                    ))
                    results["products_added"] += 1
                except Exception as e:
                    results["errors"].append(f"Product sync error: {e}")

            # Fetch invoices
            logger.info("Syncing invoices...")
            invoices, items = self.get_orders()

            for inv in invoices:
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO invoices
                        (ma_hoa_don, ma_khach_hang, thoi_gian, khach_da_tra, thanh_tien, ghi_chu)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        inv["ma_hoa_don"],
                        inv["ma_khach_hang"],
                        inv["thoi_gian"],
                        inv["khach_da_tra"],
                        inv["thanh_tien"],
                        inv.get("ghi_chu", "")
                    ))
                    results["invoices_added"] += 1
                except Exception as e:
                    results["errors"].append(f"Invoice sync error: {e}")

            # Sync items
            for item in items:
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO invoice_items
                        (ma_hoa_don, ma_hang, so_luong, gia_ban, thanh_tien)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        item["ma_hoa_don"],
                        item["ma_hang"],
                        item["so_luong"],
                        item["gia_ban"],
                        item["thanh_tien"]
                    ))
                    results["items_added"] += 1
                except Exception as e:
                    results["errors"].append(f"Item sync error: {e}")

            # Commit changes
            conn.commit()
            logger.info(f"Sync complete: {results}")

        except Exception as e:
            logger.error(f"Database sync error: {e}")
            results["errors"].append(f"Database error: {e}")
            if conn:
                conn.rollback()

        finally:
            if conn:
                conn.close()

        return results

    def close(self):
        """Close session"""
        self.session.close()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_kiotviet_client(
    retail_id: str,
    api_key: str,
    db_path: str = "retail.db"
) -> KiotvietClient:
    """Factory function to create Kiotviet client"""
    return KiotvietClient(retail_id, api_key, db_path)


def sync_kiotviet_to_sqlite(
    retail_id: str,
    api_key: str,
    db_path: str = "retail.db",
    full_sync: bool = False
) -> Dict:
    """
    One-shot sync function for convenience

    Usage:
        result = sync_kiotviet_to_sqlite("your_retail_id", "your_api_key")
    """
    client = KiotvietClient(retail_id, api_key, db_path)
    try:
        result = client.sync_to_sqlite(full_sync=full_sync)
        return result
    finally:
        client.close()
