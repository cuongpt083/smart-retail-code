# 📊 Load Data to SQLite - Complete Guide

## Quy Trình Tổng Thể

```
Step 1: Generate CSV
python generate_synthetic_data.py
↓ (Tạo: products.csv, customers.csv, invoices.csv, invoice_items.csv)
↓
Step 2: Load to SQLite
python load_data_to_sqlite.py
↓ (Tạo: retail.db với 4 bảng + indices)
↓
Step 3: Run Dashboard
streamlit run app.py
↓ (Hiển thị: Dashboard với Apriori recommendations)
```

## 🚀 Cách Sử Dụng

### Bước 1: Tạo Dữ Liệu CSV (Nếu Chưa Có)

```bash
python generate_synthetic_data.py
```

**Output:**
```
✅ Data generation complete!
📊 Summary:
  • Products: 100
  • Customers: 100
  • Invoices: 300
  • Invoice items: 1250
💾 Files saved:
  • products.csv
  • customers.csv
  • invoices.csv
  • invoice_items.csv
```

### Bước 2: Nạp Dữ Liệu Vào SQLite

```bash
python load_data_to_sqlite.py
```

**Output:**
```
======================================================================
📊 LOADING SYNTHETIC DATA INTO SQLITE DATABASE
======================================================================

🔎 Checking for CSV files...
  ✓ products.csv (45.2 KB)
  ✓ customers.csv (38.5 KB)
  ✓ invoices.csv (52.1 KB)
  ✓ invoice_items.csv (85.3 KB)

🗄️  Connecting to database: retail.db...
  ✓ Connected to retail.db

📋 Creating database schema...
  ✓ products table created
  ✓ customers table created
  ✓ invoices table created
  ✓ invoice_items table created

📦 Loading products from products.csv...
  ✓ Loaded 100 products

👥 Loading customers from customers.csv...
  ✓ Loaded 100 customers

🧾 Loading invoices from invoices.csv...
  ✓ Loaded 300 invoices

📝 Loading invoice items from invoice_items.csv...
  ✓ Loaded 1250 invoice items

🔍 Verifying data integrity...
  ✓ Products: 100
  ✓ Customers: 100
  ✓ Invoices: 300
  ✓ Invoice items: 1250

✓ Checking foreign key references...
  ✓ All invoices reference valid customers
  ✓ All invoice items reference valid products and invoices

⚡ Creating indices for performance...
  ✓ Indices created

======================================================================
✅ DATA LOADING COMPLETE!
======================================================================

📊 Summary:
  • Database: retail.db
  • Products: 100
  • Customers: 100
  • Invoices: 300
  • Invoice items: 1250

🎯 Next steps:
  1. Start the Streamlit app: streamlit run app.py
  2. Dashboard should now display Apriori recommendations
  3. Check Admin dashboard to see RFM segments
```

### Bước 3: Chạy Dashboard

```bash
streamlit run app.py
```

Dashboard sẽ **tự động sử dụng retail.db** và hiển thị Apriori recommendations.

---

## 📋 Cấu Trúc Database

### Schema được tạo

```sql
-- 4 tables
products          -- 100 hàng (ma_hang, ten_hang, gia_ban, ...)
customers         -- 100 hàng (ma_khach_hang, ten_khach_hang, ...)
invoices          -- 300 hàng (ma_hoa_don, ma_khach_hang, tong_tien_hang, ...)
invoice_items     -- 1250 hàng (ma_hoa_don, ma_hang, so_luong, ...)

-- 8 indices (tối ưu hóa truy vấn)
idx_invoices_customer
idx_invoices_date
idx_items_invoice
idx_items_product
idx_customer_region
idx_product_category
```

### Foreign Key Constraints

```
invoices.ma_khach_hang → customers.ma_khach_hang
invoice_items.ma_hoa_don → invoices.ma_hoa_don
invoice_items.ma_hang → products.ma_hang
```

---

## 🔍 Kiểm Tra Dữ Liệu Được Nạp

### Cách 1: Dùng SQLite CLI

```bash
# Kết nối database
sqlite3 retail.db

# Kiểm tra số bảng
.tables

# Kiểm tra cấu trúc
.schema products

# Đếm dữ liệu
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM invoices;

# Xem sample
SELECT * FROM products LIMIT 5;
SELECT * FROM invoices LIMIT 5;

# Exit
.exit
```

### Cách 2: Dùng Python

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('retail.db')

# Đọc dữ liệu
products = pd.read_sql('SELECT * FROM products', conn)
print(f"Total products: {len(products)}")

invoices = pd.read_sql('SELECT * FROM invoices', conn)
print(f"Total invoices: {len(invoices)}")

# Xem sample
print(products.head())

conn.close()
```

### Cách 3: Dùng Database Browser

Dùng **DB Browser for SQLite** (miễn phí):
1. Tải từ: https://sqlitebrowser.org/
2. Mở `retail.db`
3. Xem dữ liệu trực quan

---

## 📊 Kết Quả Kỳ Vọng

Khi mở dashboard sau khi nạp dữ liệu:

### Tab "Bán Hàng" (Apriori)

```
✅ Top Products Sold Together
┌───────────────────────────┬─────────┬────────────┐
│ Product Association        │ Support │ Confidence │
├───────────────────────────┼─────────┼────────────┤
│ SP1003 (Bánh mì) → SP1008 │ 20%     │ 75%        │
│ (Nước)                     │         │            │
├───────────────────────────┼─────────┼────────────┤
│ SP1004 (Gia vị) → SP1031  │ 15%     │ 68%        │
│ (Cơm hộp)                 │         │            │
└───────────────────────────┴─────────┴────────────┘

Recommendation: "Khách mua Bánh mì → Gợi ý Nước"
```

### Tab "Marketing" (RFM)

```
✅ Customer Segments
Champions:  25 khách (mua thường, mua lâu gần đây)
Potential:  30 khách (khách mới hoặc sắp quay lại)
Loyal:      20 khách (mua quen nhưng lâu không mua)
Lost:       25 khách (khách cũ không mua lâu)
```

---

## ⚙️ Tùy Chỉnh

### Thay Đổi Database Path

Sửa trong `load_data_to_sqlite.py`:
```python
DB_PATH = "path/to/your/database.db"
```

### Xóa Database Cũ

```bash
# Windows
del retail.db

# Mac/Linux
rm retail.db
```

Rồi chạy lại script sẽ tạo database mới.

### Append Dữ Liệu Mới (Không Xóa Cũ)

Script mặc định **append** dữ liệu:
```python
df.to_sql('products', conn, if_exists='append', index=False)
```

Nếu muốn **xóa cũ rồi load lại**:
```python
df.to_sql('products', conn, if_exists='replace', index=False)
```

---

## 🐛 Troubleshooting

### ❌ "products.csv not found"

**Nguyên nhân:** Chưa chạy `generate_synthetic_data.py`

**Sửa:**
```bash
python generate_synthetic_data.py
python load_data_to_sqlite.py
```

### ❌ "Database is locked"

**Nguyên nhân:** Dashboard đang sử dụng database

**Sửa:**
1. Đóng Streamlit app
2. Chạy lại script

### ❌ "Foreign key constraint failed"

**Nguyên nhân:** Dữ liệu không nhất quán

**Sửa:**
1. Xóa `retail.db`
2. Chạy lại từ đầu

### ❌ "ModuleNotFoundError: pandas"

**Sửa:**
```bash
pip install pandas sqlite3
```

---

## 📈 Performance Tips

Script đã tối ưu bằng:
- ✅ **Indices** trên foreign keys
- ✅ **Foreign key constraints** để đảm bảo data integrity
- ✅ **WAL mode** (nếu có)
- ✅ **Type conversion** khi load

Nếu vẫn chậm với dữ liệu lớn:
```python
# Thêm vào load_data_to_sqlite.py
conn.execute("PRAGMA synchronous = NORMAL")  # Tăng tốc
conn.execute("PRAGMA journal_mode = WAL")     # Write-ahead logging
```

---

## 🔄 Workflow Hoàn Chỉnh

```bash
# 1. Generate dữ liệu với combos
python generate_synthetic_data.py

# 2. Load vào SQLite
python load_data_to_sqlite.py

# 3. Kiểm tra (tùy chọn)
sqlite3 retail.db "SELECT COUNT(*) FROM products;"

# 4. Chạy dashboard
streamlit run app.py

# 5. Xem Apriori recommendations ✨
# Browser sẽ mở tự động
# Vào tab "Bán Hàng" để xem combos
```

---

## 💡 Lợi Ích Của SQLite

| Yếu Tố | Lợi Ích |
|--------|--------|
| **Setup** | Không cần máy chủ, chỉ 1 file |
| **CSV vs DB** | Query nhanh hơn (indices, where clauses) |
| **Data Integrity** | Foreign keys, constraints |
| **Portability** | Copy file `retail.db` là xong |
| **Performance** | 300+ invoices load nhanh |

---

## 🎯 Tiếp Theo

Sau khi nạp dữ liệu thành công:

1. ✅ Dashboard hiển thị Apriori combos
2. ✅ RFM segmentation hoạt động
3. ✅ Có thể export dữ liệu từ database
4. ✅ Có thể viết script phân tích thêm

---

**Sẵn sàng? Chạy ngay!** 🚀
```bash
python generate_synthetic_data.py
python load_data_to_sqlite.py
streamlit run app.py
```
