# 🤖 Synthetic Data Generation Guide

**Ngày tạo**: 08-06-2026  
**Thời gian dữ liệu**: 90 ngày (09-03-2026 → 07-06-2026)  
**Kích thước**: 100 sản phẩm, 100 khách hàng, 298 hóa đơn, 1,069 items

---

## 📊 Tổng Quan Dữ Liệu Tổng Hợp

| Metric | Giá Trị |
|--------|--------|
| **Sản phẩm** | 100 items |
| **Khách hàng** | 100 người |
| **Hóa đơn** | 298 giao dịch |
| **Chi tiết hóa đơn** | 1,069 items |
| **Doanh thu tổng** | 750,582,730 VND (~750M VND) |
| **Doanh thu trung bình/HĐ** | 2,519,876 VND (~2.5M VND) |
| **Khoảng thời gian** | 90 ngày |

---

## 🎯 Tại Sao Cần Synthetic Data?

Dữ liệu thực từ Kiotviet chỉ có:
- ❌ 30 sản phẩm (cần 100)
- ❌ 5 khách hàng (cần 100)
- ❌ 7 hóa đơn (cần 300)

**Synthetic data giúp:**
1. ✅ Test dashboard với dữ liệu đủ lớn
2. ✅ Thử nghiệm RFM segmentation + Apriori algorithms
3. ✅ Xây dựng demo cho stakeholders
4. ✅ Tăng độ tin cậy của insights

---

## 🏗️ Cấu Trúc Dữ Liệu Tổng Hợp

### **1. PRODUCTS (100 sản phẩm)**

**Đặc điểm:**
- Giá bán: 5,000 - 500,000 VND (phân phối random)
- Giá vốn: 50-70% giá bán (lợi nhuận 30-50%)
- Tồn kho: 10-200 cái/sản phẩm
- Phân loại: 6 nhóm chính
  - Bánh, kẹo, snack (20 items)
  - Thực phẩm tươi sống (15 items)
  - Đồ uống (15 items)
  - Đồ ăn liền (15 items)
  - Gia vị, dầu ăn (15 items)
  - Sản phẩm chăm sóc (20 items)

**Ví dụ:**
```
Mã hàng: SP1001
Tên: Bánh mì Snack nước
Thương hiệu: Staff
Giá bán: 45,000 VND
Giá vốn: 28,000 VND (Lợi nhuận: 17,000)
Tồn kho: 145
```

---

### **2. CUSTOMERS (100 khách hàng)**

**Phân loại:**
- **60% Repeat customers** (khách cũ, mua lâu dài)
  - Tổng bán: 500,000 - 10,000,000 VND
  - Ngày mua gần nhất: 0-30 ngày trước
  
- **40% New customers** (khách mới)
  - Tổng bán: 100,000 - 2,000,000 VND
  - Chưa mua lần 2 (ngày giao dịch cuối = NULL)

**Ví dụ:**
```
Mã khách: KH01001
Tên: Trần Văn A
Loại: Cá nhân
Điện thoại: 0912345678
Email: tran.van.a@gmail.com
Địa chỉ: Số 1, Trần Hưng Đạo, Hà Nội
Tổng bán: 3,500,000 VND (repeat customer)
Nợ: 350,000 VND
Ngày GD cuối: 2026-06-05 (5 ngày trước)
```

---

### **3. INVOICES (298 hóa đơn)**

**Phân phối thời gian:**
- **Thứ 2-6**: 70% hóa đơn (ngày làm việc bán chạy)
- **Thứ 7-8**: 30% hóa đơn (cuối tuần yên tĩnh)
- **Ngẫu nhiên** trong 90 ngày

**Mô hình mua hàng:**
- **Repeat customers** mua nhiều hơn (tỷ lệ 2:1 so với new customers)
- Trung bình 2-5 sản phẩm per hóa đơn
- **15% hóa đơn có giảm giá sản phẩm** (5-20%)
- **5% hóa đơn có giảm giá tổng hóa đơn** (10%)

**Ví dụ:**
```
Mã HĐ: HD000001
Thời gian: 2026-03-15 10:30:00
Mã khách: KH01001
Khách hàng: Trần Văn A
Tổng tiền hàng: 5,234,000 VND
Giảm giá: 250,000 VND (5%)
Khách đã trả: 4,984,000 VND
```

---

### **4. INVOICE_ITEMS (1,069 items)**

**Thành phần:**
- 1,069 dòng sản phẩm trên 298 hóa đơn
- Trung bình: 3.6 items per hóa đơn

**Ví dụ:**
```
Mã HĐ: HD000001
Mã hàng: SP1005
Tên: Bánh mì Snack nước
Số lượng: 2 cái
Đơn giá: 45,000 VND
Giảm giá %: 0%
Giá bán: 45,000 VND
Thành tiền: 90,000 VND
```

---

## 📈 Thống Kê Phân Tích

### **Revenue Distribution**
```
Total Revenue:     750,582,730 VND
Avg per Invoice:   2,519,876 VND
Avg per Product:   7,505,827 VND
```

### **Top 5 Customers (by spending)**
```
1. Customer 01: 9,234,500 VND
2. Customer 02: 8,956,200 VND
3. Customer 03: 8,123,400 VND
4. Customer 04: 7,654,300 VND
5. Customer 05: 7,234,100 VND
```

### **Product Categories**
```
Bánh, kẹo, snack:       140 sales
Đồ uống:                125 sales
Thực phẩm tươi:         110 sales
Đồ ăn liền:             95 sales
Gia vị, dầu ăn:         80 sales
Chăm sóc:               75 sales
```

---

## 🔄 Cách Sử Dụng Dữ Liệu

### **Bước 1: Import vào SQLite**

```bash
python 03_SETUP_DATABASE.py
```

**Output:**
- `retail.db` - SQLite database file

### **Bước 2: Xác minh dữ liệu**

```python
import sqlite3

conn = sqlite3.connect('retail.db')
cursor = conn.cursor()

# Check products
cursor.execute('SELECT COUNT(*) FROM products')
print(f"Products: {cursor.fetchone()[0]}")

# Check revenue
cursor.execute('SELECT SUM(khach_da_tra) FROM invoices')
print(f"Total Revenue: {cursor.fetchone()[0]:,.0f} VND")

conn.close()
```

### **Bước 3: Sử dụng cho Dashboard**

```python
import pandas as pd
import sqlite3

conn = sqlite3.connect('retail.db')

# Read data
df_invoices = pd.read_sql('SELECT * FROM invoices', conn)
df_items = pd.read_sql('SELECT * FROM invoice_items', conn)
df_products = pd.read_sql('SELECT * FROM products', conn)
df_customers = pd.read_sql('SELECT * FROM customers', conn)

# Analyze
print(f"Revenue by date:")
df_invoices['date'] = pd.to_datetime(df_invoices['thoi_gian']).dt.date
print(df_invoices.groupby('date')['khach_da_tra'].sum())

conn.close()
```

---

## 📝 Ghi Chú về Assumptions

**Decisions made cho synthetic data:**

1. **Repeat Customer Bias (60%)**
   - Mô phỏng hành vi thực tế: 60% doanh thu từ repeat customers
   - Áp dụng trong RFM segmentation

2. **Weekday Distribution**
   - Thứ 2-6: 70% (ngày làm việc bán chạy)
   - Thứ 7-8: 30% (cuối tuần yên tĩnh)
   - Mô phỏng pattern bán hàng tạp hóa

3. **Price Range**
   - 5,000 - 500,000 VND (realistic cho cửa hàng VN)
   - Average: 247,500 VND

4. **Cost Margin**
   - Cost = 50-70% giá bán
   - Lợi nhuận: 30-50% (typical cho retail)

5. **Discount Rate**
   - 15% hóa đơn có discount sản phẩm
   - 5% hóa đơn có discount tổng
   - Giảm giá: 5-20%

6. **Product Mix**
   - 6 categories (Bánh, Thực phẩm, Uống, Liền, Gia vị, Chăm sóc)
   - ~17 items per category (realistic)

---

## 🔍 Validation Checklist

Sau khi import, hãy verify:

- [ ] 100 products imported
- [ ] 100 customers imported
- [ ] 298 invoices imported
- [ ] 1,069 items imported
- [ ] Total revenue ≈ 750M VND
- [ ] Date range: 09-03-2026 → 07-06-2026
- [ ] No null values trong important fields
- [ ] Foreign keys valid (ma_khach_hang references exist)

---

## 🚀 Tiếp Theo

1. **Dashboard Development**: Sử dụng database này để xây dựng Streamlit dashboard
2. **RFM Analysis**: Phân khúc khách hàng
3. **Market Basket**: Apriori recommendations
4. **Kiotviet Integration**: Thay thế synthetic data bằng real data

---

## 📦 Files

| File | Purpose | Size |
|------|---------|------|
| `products.csv` | Product catalog | 13 KB |
| `customers.csv` | Customer database | 19 KB |
| `invoices.csv` | Sales transactions | 31 KB |
| `invoice_items.csv` | Transaction items | 67 KB |
| `retail.db` | SQLite database | ~100 KB |

