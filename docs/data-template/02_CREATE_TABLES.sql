-- ========================================================================
-- Smart Retail Analytics - SQLite Database Schema
-- Dùng cho phân tích khách hàng, RFM segmentation, Market basket analysis
-- ========================================================================

-- Drop existing tables (nếu muốn reset database)
-- DROP TABLE IF EXISTS invoice_items;
-- DROP TABLE IF EXISTS po_items;
-- DROP TABLE IF EXISTS invoices;
-- DROP TABLE IF EXISTS purchase_orders;
-- DROP TABLE IF EXISTS products;
-- DROP TABLE IF EXISTS customers;
-- DROP TABLE IF EXISTS vendors;

-- ========================================================================
-- 1. PRODUCTS (Sản Phẩm)
-- ========================================================================
CREATE TABLE IF NOT EXISTS products (
    ma_hang TEXT PRIMARY KEY,
    ten_hang TEXT NOT NULL,
    thuong_hieu TEXT,
    loai_hang TEXT,
    nhom_hang TEXT,
    gia_ban REAL DEFAULT 0,
    gia_von REAL DEFAULT 0,
    ton_kho INTEGER DEFAULT 0,
    ma_vach TEXT UNIQUE,
    don_vi_tinh TEXT,
    quy_doi INTEGER DEFAULT 1,
    trang_thai INTEGER DEFAULT 1,  -- 1: Đang bán, 0: Ngừng
    thoi_gian_tao DATETIME DEFAULT CURRENT_TIMESTAMP,

    CHECK (gia_ban >= 0),
    CHECK (gia_von >= 0),
    CHECK (ton_kho >= 0)
);

-- Index để tìm kiếm sản phẩm nhanh
CREATE INDEX idx_products_ten_hang ON products(ten_hang);
CREATE INDEX idx_products_thuong_hieu ON products(thuong_hieu);
CREATE INDEX idx_products_nhom_hang ON products(nhom_hang);

-- ========================================================================
-- 2. CUSTOMERS (Khách Hàng)
-- ========================================================================
CREATE TABLE IF NOT EXISTS customers (
    ma_khach_hang TEXT PRIMARY KEY,
    ten_khach_hang TEXT NOT NULL,
    loai_khach TEXT DEFAULT 'Cá nhân',  -- 'Cá nhân' or 'Công ty'
    dien_thoai TEXT,
    email TEXT,
    dia_chi TEXT,
    khu_vuc_giao_hang TEXT,
    phuong_xa TEXT,
    ngay_sinh DATE,
    gioi_tinh TEXT,  -- 'M', 'F', NULL
    tong_ban REAL DEFAULT 0,
    no_can_thu REAL DEFAULT 0,
    ngay_giao_dich_cuoi DATE,
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,
    trang_thai INTEGER DEFAULT 1,  -- 1: Active, 0: Inactive

    CHECK (tong_ban >= 0),
    CHECK (no_can_thu >= 0)
);

-- Index cho nhanh lookup
CREATE INDEX idx_customers_ten ON customers(ten_khach_hang);
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_dien_thoai ON customers(dien_thoai);
CREATE INDEX idx_customers_ngay_giao_dich ON customers(ngay_giao_dich_cuoi);

-- ========================================================================
-- 3. INVOICES (Hóa Đơn Bán Hàng) - Transaction records
-- ========================================================================
CREATE TABLE IF NOT EXISTS invoices (
    ma_hoa_don TEXT PRIMARY KEY,
    thoi_gian DATETIME NOT NULL,
    ma_khach_hang TEXT NOT NULL,
    ten_khach_hang TEXT,  -- Denormalized for quick access
    tong_tien_hang REAL DEFAULT 0,
    giam_gia REAL DEFAULT 0,
    khach_da_tra REAL DEFAULT 0,  -- Amount customer paid
    con_can_thu REAL DEFAULT 0,  -- Remaining amount
    trang_thai TEXT DEFAULT 'Hoàn thành',
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (ma_khach_hang) REFERENCES customers(ma_khach_hang) ON DELETE CASCADE,
    CHECK (tong_tien_hang >= 0),
    CHECK (giam_gia >= 0),
    CHECK (khach_da_tra >= 0)
);

-- Index cho nhanh lookup theo khách hàng và thời gian
CREATE INDEX idx_invoices_ma_khach ON invoices(ma_khach_hang);
CREATE INDEX idx_invoices_thoi_gian ON invoices(thoi_gian);
CREATE INDEX idx_invoices_thoi_gian_desc ON invoices(thoi_gian DESC);

-- ========================================================================
-- 4. INVOICE_ITEMS (Chi Tiết Hóa Đơn) - Product items per invoice
-- ========================================================================
CREATE TABLE IF NOT EXISTS invoice_items (
    ma_hoa_don TEXT NOT NULL,
    ma_hang TEXT NOT NULL,
    so_luong INTEGER NOT NULL,
    don_gia REAL NOT NULL,
    giam_gia_phan_tram INTEGER DEFAULT 0,
    giam_gia REAL DEFAULT 0,
    gia_ban REAL NOT NULL,  -- Don gia sau giam gia
    thanh_tien REAL NOT NULL,  -- so_luong * gia_ban
    thoi_gian DATETIME NOT NULL,

    PRIMARY KEY (ma_hoa_don, ma_hang),
    FOREIGN KEY (ma_hoa_don) REFERENCES invoices(ma_hoa_don) ON DELETE CASCADE,
    FOREIGN KEY (ma_hang) REFERENCES products(ma_hang) ON DELETE RESTRICT,

    CHECK (so_luong > 0),
    CHECK (don_gia > 0),
    CHECK (gia_ban > 0),
    CHECK (thanh_tien > 0)
);

-- Index cho market basket analysis
CREATE INDEX idx_invoice_items_ma_hang ON invoice_items(ma_hang);
CREATE INDEX idx_invoice_items_ma_hoa_don ON invoice_items(ma_hoa_don);

-- ========================================================================
-- 5. VENDORS (Nhà Cung Cấp) - Suppliers
-- ========================================================================
CREATE TABLE IF NOT EXISTS vendors (
    ma_nha_cung_cap TEXT PRIMARY KEY,
    ten_nha_cung_cap TEXT NOT NULL,
    dien_thoai TEXT,
    email TEXT,
    dia_chi TEXT,
    khu_vuc TEXT,
    phuong_xa TEXT,
    tong_mua REAL DEFAULT 0,
    no_can_tra REAL DEFAULT 0,
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,
    trang_thai INTEGER DEFAULT 1,

    CHECK (tong_mua >= 0),
    CHECK (no_can_tra >= 0)
);

CREATE INDEX idx_vendors_ten ON vendors(ten_nha_cung_cap);

-- ========================================================================
-- 6. PURCHASE_ORDERS (Đơn Nhập Hàng) - Inbound orders
-- ========================================================================
CREATE TABLE IF NOT EXISTS purchase_orders (
    ma_nhap_hang TEXT PRIMARY KEY,
    thoi_gian DATETIME NOT NULL,
    ma_nha_cung_cap TEXT NOT NULL,
    ten_nha_cung_cap TEXT,
    can_tra_ncc REAL DEFAULT 0,
    da_tra_ncc REAL DEFAULT 0,
    trang_thai TEXT DEFAULT 'Đã nhập hàng',
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (ma_nha_cung_cap) REFERENCES vendors(ma_nha_cung_cap) ON DELETE RESTRICT,
    CHECK (can_tra_ncc >= 0),
    CHECK (da_tra_ncc >= 0)
);

CREATE INDEX idx_po_ma_ncc ON purchase_orders(ma_nha_cung_cap);
CREATE INDEX idx_po_thoi_gian ON purchase_orders(thoi_gian);

-- ========================================================================
-- 7. PO_ITEMS (Chi Tiết Nhập Hàng) - Products per PO
-- ========================================================================
CREATE TABLE IF NOT EXISTS po_items (
    ma_nhap_hang TEXT NOT NULL,
    ma_hang TEXT NOT NULL,
    so_luong INTEGER NOT NULL,
    don_gia REAL NOT NULL,
    giam_gia REAL DEFAULT 0,
    gia_nhap REAL NOT NULL,
    thanh_tien REAL NOT NULL,
    thoi_gian DATETIME NOT NULL,

    PRIMARY KEY (ma_nhap_hang, ma_hang),
    FOREIGN KEY (ma_nhap_hang) REFERENCES purchase_orders(ma_nhap_hang) ON DELETE CASCADE,
    FOREIGN KEY (ma_hang) REFERENCES products(ma_hang) ON DELETE RESTRICT,

    CHECK (so_luong > 0),
    CHECK (don_gia > 0)
);

CREATE INDEX idx_po_items_ma_hang ON po_items(ma_hang);

-- ========================================================================
-- VIEWS FOR ANALYTICS (Tạo views để dễ query)
-- ========================================================================

-- View: RFM scores cho từng khách hàng
-- R: Recency (ngày từ lần mua cuối)
-- F: Frequency (số lần mua)
-- M: Monetary (tổng tiền mua)
CREATE VIEW IF NOT EXISTS rfm_analysis AS
SELECT
    c.ma_khach_hang,
    c.ten_khach_hang,
    c.email,
    c.dien_thoai,
    JULIANDAY('now') - JULIANDAY(MAX(i.thoi_gian)) AS days_since_purchase,
    COUNT(DISTINCT i.ma_hoa_don) AS purchase_frequency,
    SUM(i.khach_da_tra) AS total_monetary,
    MAX(i.thoi_gian) AS last_purchase_date
FROM customers c
LEFT JOIN invoices i ON c.ma_khach_hang = i.ma_khach_hang
GROUP BY c.ma_khach_hang;

-- View: Top selling products
CREATE VIEW IF NOT EXISTS top_products AS
SELECT
    p.ma_hang,
    p.ten_hang,
    p.thuong_hieu,
    COUNT(DISTINCT ii.ma_hoa_don) AS num_sold,
    SUM(ii.so_luong) AS total_quantity,
    SUM(ii.thanh_tien) AS total_revenue,
    AVG(ii.don_gia) AS avg_price
FROM products p
LEFT JOIN invoice_items ii ON p.ma_hang = ii.ma_hang
GROUP BY p.ma_hang
ORDER BY total_revenue DESC;

-- View: Customer spending by month
CREATE VIEW IF NOT EXISTS customer_monthly_spending AS
SELECT
    c.ma_khach_hang,
    c.ten_khach_hang,
    strftime('%Y-%m', i.thoi_gian) AS month,
    COUNT(DISTINCT i.ma_hoa_don) AS num_invoices,
    SUM(i.khach_da_tra) AS monthly_total
FROM customers c
LEFT JOIN invoices i ON c.ma_khach_hang = i.ma_khach_hang
WHERE i.thoi_gian IS NOT NULL
GROUP BY c.ma_khach_hang, month;

-- View: Product pairs (cho Apriori - Market basket)
CREATE VIEW IF NOT EXISTS product_pairs AS
SELECT
    ii1.ma_hang AS product1,
    p1.ten_hang AS name1,
    ii2.ma_hang AS product2,
    p2.ten_hang AS name2,
    COUNT(DISTINCT ii1.ma_hoa_don) AS times_bought_together
FROM invoice_items ii1
JOIN invoice_items ii2
    ON ii1.ma_hoa_don = ii2.ma_hoa_don
    AND ii1.ma_hang < ii2.ma_hang
JOIN products p1 ON ii1.ma_hang = p1.ma_hang
JOIN products p2 ON ii2.ma_hang = p2.ma_hang
GROUP BY ii1.ma_hang, ii2.ma_hang
ORDER BY times_bought_together DESC;

-- ========================================================================
-- STORED PROCEDURES / TRIGGERS (SQLite không hỗ trợ stored procedures)
-- Nhưng có thể dùng TRIGGERS để auto-update
-- ========================================================================

-- Trigger: Update tong_ban & ngay_giao_dich_cuoi when new invoice added
CREATE TRIGGER IF NOT EXISTS update_customer_stats_after_invoice
AFTER INSERT ON invoices
BEGIN
    UPDATE customers
    SET
        tong_ban = (
            SELECT COALESCE(SUM(khach_da_tra), 0)
            FROM invoices
            WHERE ma_khach_hang = NEW.ma_khach_hang
        ),
        ngay_giao_dich_cuoi = (
            SELECT MAX(thoi_gian)
            FROM invoices
            WHERE ma_khach_hang = NEW.ma_khach_hang
        )
    WHERE ma_khach_hang = NEW.ma_khach_hang;
END;

-- Trigger: Update ton_kho when invoice item added
CREATE TRIGGER IF NOT EXISTS update_inventory_after_sale
AFTER INSERT ON invoice_items
BEGIN
    UPDATE products
    SET ton_kho = ton_kho - NEW.so_luong
    WHERE ma_hang = NEW.ma_hang;
END;

-- Trigger: Update ton_kho when PO item added
CREATE TRIGGER IF NOT EXISTS update_inventory_after_purchase
AFTER INSERT ON po_items
BEGIN
    UPDATE products
    SET ton_kho = ton_kho + NEW.so_luong
    WHERE ma_hang = NEW.ma_hang;
END;

-- ========================================================================
-- SAMPLE DATA (tùy chọn - để test)
-- ========================================================================

-- INSERT INTO products VALUES
-- ('1001', 'Bánh mì', 'Staff', 'Hàng hóa', 'Bánh', 25000, 15000, 100, NULL, 'Cái', 1, 1, CURRENT_TIMESTAMP);

-- ========================================================================
-- END OF SCHEMA
-- ========================================================================
