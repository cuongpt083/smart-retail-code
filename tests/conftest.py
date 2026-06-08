"""
pytest configuration and shared fixtures
Sample data for testing RFM, Apriori, and Dashboard components
"""

import pytest
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory):
    """Create temporary test database"""
    db_path = tmp_path_factory.mktemp("data") / "test_retail.db"
    return str(db_path)


@pytest.fixture(scope="session")
def test_db(test_db_path):
    """Create test database with sample data"""
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE products (
            ma_hang TEXT PRIMARY KEY,
            ten_hang TEXT NOT NULL,
            gia_ban REAL,
            gia_von REAL,
            ton_kho INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE customers (
            ma_khach_hang TEXT PRIMARY KEY,
            ten_khach_hang TEXT,
            tong_ban REAL,
            ngay_giao_dich_cuoi DATE,
            trang_thai INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE invoices (
            ma_hoa_don TEXT PRIMARY KEY,
            thoi_gian DATETIME,
            ma_khach_hang TEXT,
            khach_da_tra REAL,
            FOREIGN KEY (ma_khach_hang) REFERENCES customers(ma_khach_hang)
        )
    """)

    cursor.execute("""
        CREATE TABLE invoice_items (
            ma_hoa_don TEXT,
            ma_hang TEXT,
            so_luong INTEGER,
            don_gia REAL,
            thanh_tien REAL,
            PRIMARY KEY (ma_hoa_don, ma_hang),
            FOREIGN KEY (ma_hoa_don) REFERENCES invoices(ma_hoa_don),
            FOREIGN KEY (ma_hang) REFERENCES products(ma_hang)
        )
    """)

    conn.commit()
    conn.close()

    return test_db_path


# ============================================================================
# SAMPLE DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_products():
    """Sample 10 products for testing"""
    return pd.DataFrame({
        'ma_hang': [f'SP{1001+i}' for i in range(10)],
        'ten_hang': [
            'Bánh mì', 'Nước ngọt', 'Mì ăn liền', 'Trứng tươi', 'Gia vị',
            'Dầu ăn', 'Xà phòng', 'Cơm hộp', 'Bánh quy', 'Kẹo'
        ],
        'gia_ban': [45000, 45000, 25000, 50000, 20000, 60000, 25000, 30000, 40000, 15000],
        'gia_von': [28000, 25000, 12000, 30000, 10000, 35000, 10000, 18000, 20000, 8000],
        'ton_kho': [100, 150, 120, 80, 200, 60, 180, 90, 110, 250]
    })


@pytest.fixture
def sample_customers():
    """Sample 10 customers for testing"""
    today = datetime.now().date()

    return pd.DataFrame({
        'ma_khach_hang': [f'KH{1001+i}' for i in range(10)],
        'ten_khach_hang': [
            'Trần Văn A', 'Nguyễn Thị B', 'Lê Văn C', 'Phạm Thị D', 'Vũ Minh E',
            'Hoàng Văn F', 'Đỗ Thị G', 'Bùi Văn H', 'Trần Thị I', 'Ngô Văn J'
        ],
        'tong_ban': [5500000, 4200000, 3800000, 2100000, 1900000, 1200000, 950000, 750000, 600000, 400000],
        'ngay_giao_dich_cuoi': [
            today - timedelta(days=2),   # KH01: 2 days ago
            today - timedelta(days=7),   # KH02: 7 days ago
            today - timedelta(days=12),  # KH03: 12 days ago
            today - timedelta(days=21),  # KH04: 21 days ago
            today - timedelta(days=30),  # KH05: 30 days ago
            today - timedelta(days=45),  # KH06: 45 days ago
            today - timedelta(days=60),  # KH07: 60 days ago
            None,                         # KH08: Never purchased
            today - timedelta(days=15),  # KH09: 15 days ago
            today - timedelta(days=3),   # KH10: 3 days ago
        ],
        'trang_thai': [1] * 10
    })


@pytest.fixture
def sample_invoices():
    """Sample 30 invoices for testing RFM"""
    today = datetime.now().date()

    invoices = []
    for i in range(30):
        ma_hoa_don = f'HD{1001+i}'
        # Distribute purchases over 90 days
        days_ago = (i % 20) * 5  # Spread across 90 days
        thoi_gian = today - timedelta(days=days_ago)

        # Mix of customer IDs (some repeat, some once)
        ma_khach = f'KH{1001 + (i % 8)}'  # Customers 01-08
        khach_da_tra = 1000000 + (i * 100000)

        invoices.append({
            'ma_hoa_don': ma_hoa_dan,
            'thoi_gian': thoi_gian.isoformat(),
            'ma_khach_hang': ma_khach,
            'khach_da_tra': khach_da_tra
        })

    return pd.DataFrame(invoices)


@pytest.fixture
def sample_invoice_items():
    """Sample 100 invoice items for testing Apriori"""
    items = []

    # Define product pairs that are frequently bought together
    product_pairs = [
        ('SP1001', 'SP1002', 15),  # Bánh mì + Nước (15 times)
        ('SP1001', 'SP1006', 8),   # Bánh mì + Dầu ăn (8 times)
        ('SP1003', 'SP1005', 12),  # Mì ăn liền + Gia vị (12 times)
        ('SP1004', 'SP1005', 6),   # Trứng + Gia vị (6 times)
        ('SP1002', 'SP1007', 10),  # Nước + Xà phòng (10 times)
    ]

    item_id = 1
    for ma_hang_a, ma_hang_b, times in product_pairs:
        for t in range(times):
            ma_hoa_don = f'HD{1001 + (item_id % 30)}'

            items.append({
                'ma_hoa_don': ma_hoa_don,
                'ma_hang': ma_hang_a,
                'so_luong': 1,
                'don_gia': 45000,
                'thanh_tien': 45000
            })

            items.append({
                'ma_hoa_don': ma_hoa_don,
                'ma_hang': ma_hang_b,
                'so_luong': 1,
                'don_gia': 45000,
                'thanh_tien': 45000
            })

            item_id += 1

    return pd.DataFrame(items)


# ============================================================================
# RFM TEST DATA
# ============================================================================

@pytest.fixture
def rfm_test_customers():
    """Customers with known RFM scores for validation"""
    today = datetime.now().date()

    return pd.DataFrame({
        'ma_khach_hang': ['KH_CHAMPION', 'KH_POTENTIAL', 'KH_LOYAL', 'KH_LOST'],
        'ten_khach_hang': ['Champion', 'Potential', 'Loyal', 'Lost'],
        'tong_ban': [8000000, 1500000, 6000000, 500000],
        'ngay_giao_dich_cuoi': [
            today - timedelta(days=2),    # Champion: recent
            today - timedelta(days=1),    # Potential: very recent
            today - timedelta(days=25),   # Loyal: not recent
            today - timedelta(days=60),   # Lost: very old
        ],
        'trang_thai': [1, 1, 1, 1]
    })


@pytest.fixture
def rfm_test_invoices():
    """Invoices data for RFM calculation test"""
    today = datetime.now().date()

    return pd.DataFrame({
        'ma_hoa_don': [f'HD{i}' for i in range(50)],
        'thoi_gian': [today - timedelta(days=i % 30) for i in range(50)],
        'ma_khach_hang': [
            'KH_CHAMPION', 'KH_CHAMPION', 'KH_CHAMPION',
            'KH_POTENTIAL',
            'KH_LOYAL', 'KH_LOYAL',
            'KH_LOST',
        ] + ['KH_CHAMPION'] * (50-7),  # Fill rest with champion
        'khach_da_tra': [2000000 + (i * 10000) for i in range(50)]
    })


# ============================================================================
# APRIORI TEST DATA
# ============================================================================

@pytest.fixture
def apriori_test_data():
    """Transaction data for Apriori testing"""

    # 100 transactions with known patterns
    transactions = [
        # Bánh mì + Nước (65% confidence)
        {'transaction_id': i, 'products': ['SP1001', 'SP1002']} for i in range(65)
    ] + [
        # Bánh mì alone
        {'transaction_id': i+65, 'products': ['SP1001']} for i in range(35)
    ] + [
        # Mì ăn liền + Gia vị (55% confidence)
        {'transaction_id': i+100, 'products': ['SP1003', 'SP1005']} for i in range(55)
    ] + [
        # Mì ăn liền alone
        {'transaction_id': i+155, 'products': ['SP1003']} for i in range(45)
    ]

    return pd.DataFrame(transactions)


# ============================================================================
# DASHBOARD TEST DATA
# ============================================================================

@pytest.fixture
def dashboard_sample_data(sample_products, sample_customers, sample_invoices, sample_invoice_items):
    """Complete sample data for dashboard testing"""
    return {
        'products': sample_products,
        'customers': sample_customers,
        'invoices': sample_invoices,
        'invoice_items': sample_invoice_items
    }


# ============================================================================
# MOCK DATA LOADERS
# ============================================================================

@pytest.fixture
def mock_data_loader(sample_products, sample_customers, sample_invoices, sample_invoice_items):
    """Mock data loader that returns test data"""
    class MockDataLoader:
        def load_products(self):
            return sample_products

        def load_customers(self):
            return sample_customers

        def load_invoices(self):
            return sample_invoices

        def load_invoice_items(self):
            return sample_invoice_items

    return MockDataLoader()


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "rfm: mark test as RFM-related"
    )
    config.addinivalue_line(
        "markers", "apriori: mark test as Apriori-related"
    )
    config.addinivalue_line(
        "markers", "dashboard: mark test as dashboard-related"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
