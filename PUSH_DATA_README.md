# 📊 Push Demo Data to Kiotviet - Complete Guide

## Quy Trình Tổng Thể

```
Step 1: Generate CSV data
python generate_synthetic_data.py
↓
Step 2: Load to SQLite (optional, for local testing)
python load_data_to_sqlite.py
↓
Step 3: Setup .env with Kiotviet API credentials
Edit .env file
↓
Step 4: Push to live Kiotviet shop
python push_data_to_kiotviet.py
↓ (Tạo: demo_data_ids.json for cleanup)
↓
Step 5: Demo shop now displays data
Visit: https://kiotviet.vn/your-shop
↓
Step 6: (When done) Clean up all demo data
python cleanup_kiotviet_demo.py
```

---

## 🚀 Cách Sử Dụng

### Bước 1: Chuẩn Bị Dữ Liệu CSV

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

### Bước 2: Setup Kiotviet API Credentials

Tạo hoặc edit `.env` file:

```bash
# .env file
KIOTVIET_RETAIL_ID=your_retail_id
KIOTVIET_API_KEY=your_api_key
```

**Cách lấy credentials:**
1. Đi đến: https://kiotviet.vn
2. Vào: **Settings → Developers/API**
3. Tạo API Key hoặc lấy existing key
4. Copy vào `.env`

**Kiểm tra credentials:**
```bash
# Linux/Mac
cat .env

# Windows
type .env
```

### Bước 3: Push Dữ Liệu Lên Kiotviet

```bash
python push_data_to_kiotviet.py
```

**Output:**
```
======================================================================
📊 PUSHING DEMO DATA TO KIOTVIET
======================================================================

🔐 Validating Kiotviet API credentials...
  ✓ API credentials valid

🔎 Checking CSV files...
  ✓ products.csv
  ✓ customers.csv
  ✓ invoices.csv
  ✓ invoice_items.csv

📖 Loading CSV files...
  ✓ 100 products
  ✓ 100 customers
  ✓ 300 invoices
  ✓ 1250 invoice items

📦 Creating products in Kiotviet...
  ✓ Created 10/100 products
  ✓ Created 20/100 products
  ...
  ✓ Successfully created 100/100 products

👥 Creating customers in Kiotviet...
  ✓ Created 10/100 customers
  ✓ Created 20/100 customers
  ...
  ✓ Successfully created 100/100 customers

🧾 Creating invoices in Kiotviet...
  ✓ Created 10/300 invoices
  ✓ Created 20/300 invoices
  ...
  ✓ Successfully created 300/300 invoices

💾 Tracking file saved: demo_data_ids.json
   Use this to cleanup: python cleanup_kiotviet_demo.py

======================================================================
✅ DEMO DATA PUSHED TO KIOTVIET!
======================================================================

📊 Summary:
  • Products: 100
  • Customers: 100
  • Invoices: 300

🎯 Your Kiotviet shop now displays demo data!

📌 Important:
   • Tracking file saved: demo_data_ids.json
   • To cleanup later: python cleanup_kiotviet_demo.py
   • Visit your shop: https://kiotviet.vn
```

### Bước 4: Kiểm Tra Dữ Liệu Trên Shop

1. Đi đến: https://kiotviet.vn
2. Đăng nhập vào shop
3. Xem:
   - **📊 Danh sách sản phẩm** (100 sản phẩm mới)
   - **👥 Danh sách khách** (100 khách mới)
   - **🧾 Danh sách hoá đơn** (300 hoá đơn mới)

### Bước 5: Chạy Dashboard Với Kiotviet Data

Nếu muốn tích hợp dashboard với Kiotviet API:

```bash
streamlit run app.py
```

Dashboard sẽ đọc từ `retail.db` (nếu có) hoặc có thể sửa để đọc từ Kiotviet API.

### Bước 6: Cleanup Khi Kết Thúc Demo

```bash
python cleanup_kiotviet_demo.py
```

**Output:**
```
======================================================================
🧹 CLEANING UP KIOTVIET DEMO DATA
======================================================================

📖 Loading tracking file...
  ✓ Loaded tracking file
    - Products: 100
    - Customers: 100
    - Invoices: 300

⚠️  WARNING: This will DELETE all demo data from your Kiotviet shop!
   Press Ctrl+C to cancel, or wait 3 seconds...

🧾 Deleting invoices...
  ✓ Deleted 10/300 invoices
  ✓ Deleted 20/300 invoices
  ...
  ✓ Deleted 300/300 invoices

👥 Deleting customers...
  ✓ Deleted 10/100 customers
  ✓ Deleted 20/100 customers
  ...
  ✓ Deleted 100/100 customers

📦 Deleting products...
  ✓ Deleted 10/100 products
  ✓ Deleted 20/100 products
  ...
  ✓ Deleted 100/100 products

🗑️  Removed demo_data_ids.json

======================================================================
✅ DEMO DATA CLEANUP COMPLETE!
======================================================================

📊 Summary:
  • Invoices deleted: 300
  • Customers deleted: 100
  • Products deleted: 100

🎯 Total deleted: 500 items

✓ Your Kiotviet shop is back to clean state!
```

---

## 📋 Điểm Quan Trọng

### ⚠️ Cảnh Báo

1. **API Limits**: Kiotviet có giới hạn ~100 requests/min
   - Script tự động delay 700ms giữa các requests
   - Nếu lỗi, đợi 5 phút rồi thử lại

2. **Tracking File**: `demo_data_ids.json` là **rất quan trọng**
   - Lưu ID của tất cả data được push
   - Cần file này để cleanup
   - **Không xóa file này trước khi cleanup!**

3. **Cleanup là Bắt Buộc**
   - Demo data không tự xóa
   - Phải chạy `cleanup_kiotviet_demo.py` để xóa sạch
   - Nếu mất `demo_data_ids.json`, phải xóa manual từ Kiotviet UI

### ✅ Best Practices

1. **Backup trước**: Nếu shop đã có data, backup trước
   ```bash
   # Hoặc export từ Kiotviet UI
   ```

2. **Test trước**: Chạy một lần với dữ liệu nhỏ trước
   ```bash
   # Sửa NUM_PRODUCTS, NUM_CUSTOMERS, NUM_INVOICES trong generate_synthetic_data.py
   NUM_PRODUCTS = 10
   NUM_CUSTOMERS = 10
   NUM_INVOICES = 30
   ```

3. **Monitor demo**: Theo dõi API responses
   - Nếu có lỗi, script sẽ ghi vào `demo_data_ids.json`
   - Check phần `"errors"` để debug

---

## 🔍 Troubleshooting

### ❌ "Missing KIOTVIET_RETAIL_ID or KIOTVIET_API_KEY"

**Nguyên nhân**: `.env` file không có credentials

**Sửa**:
```bash
# Tạo .env file
echo "KIOTVIET_RETAIL_ID=your_id" > .env
echo "KIOTVIET_API_KEY=your_key" >> .env

# Hoặc edit .env bằng text editor
```

### ❌ "Invalid credentials (401 Unauthorized)"

**Nguyên nhân**: API key sai hoặc hết hạn

**Sửa**:
1. Kiểm tra API key từ Kiotviet console
2. Kiểm tra Retail ID đúng không
3. Tạo API key mới

### ❌ "products.csv not found"

**Nguyên nhân**: Chưa generate dữ liệu

**Sửa**:
```bash
python generate_synthetic_data.py
python push_data_to_kiotviet.py
```

### ❌ "Connection timeout"

**Nguyên nhân**: Mạng bị gián đoạn hoặc Kiotviet API chậm

**Sửa**:
```bash
# Đợi vài phút, rồi thử lại
python push_data_to_kiotviet.py
```

### ❌ "demo_data_ids.json not found" (khi cleanup)

**Nguyên nhân**: Mất file tracking hoặc di chuyển thư mục

**Sửa**:
1. Kiểm tra file có trong thư mục không
2. Nếu mất, phải xóa manual:
   - Vào Kiotviet UI
   - Xóa products, customers, invoices tay

### ❌ Script quá chậm

**Nguyên nhân**: API requests chậm

**Tối ưu**:
```python
# Sửa REQUEST_DELAY trong script
REQUEST_DELAY = 0.5  # Giảm từ 0.7 → 0.5
```

**⚠️ Cảnh báo**: Không giảm dưới 0.3s (sẽ hit rate limit)

---

## 📊 Ví Dụ Workflow Hoàn Chỉnh

```bash
# 1. Generate dữ liệu (1-2 phút)
python generate_synthetic_data.py

# 2. (Optional) Load vào SQLite để test
python load_data_to_sqlite.py
streamlit run app.py  # Xem dashboard locally

# 3. Setup .env (copy API key)
nano .env  # hoặc vi .env

# 4. Push lên Kiotviet shop (5-10 phút, tùy API response)
python push_data_to_kiotviet.py

# 5. Kiểm tra shop
# Mở browser → https://kiotviet.vn
# Xem Products, Customers, Invoices

# 6. Demo xong? Cleanup
python cleanup_kiotviet_demo.py

# 7. Xác nhận shop sạch
# Mở browser → https://kiotviet.vn
# Kiểm tra danh sách không có data demo
```

---

## 💡 File Tracking (demo_data_ids.json)

Sau khi push, file sẽ như này:

```json
{
  "created_at": "2026-06-08T10:30:45.123456",
  "products": [
    {
      "csv_id": "SP1001",
      "kiotviet_id": "prod_abc123",
      "name": "Bánh mì trong"
    },
    {
      "csv_id": "SP1002",
      "kiotviet_id": "prod_def456",
      "name": "Nước ngọt và"
    }
  ],
  "customers": [
    {
      "csv_id": "KH01001",
      "kiotviet_id": "cust_xyz789",
      "name": "Nguyễn Văn A"
    }
  ],
  "invoices": [
    {
      "csv_id": "HD000001",
      "kiotviet_id": "inv_123abc"
    }
  ],
  "errors": []
}
```

**Sử dụng**:
- Cleanup script sẽ đọc file này
- Nếu có lỗi, sẽ hiển thị trong `"errors"`

---

## 🎯 Tiếp Theo

### Sau khi cleanup:

1. ✅ Demo shop sạch
2. ✅ Có thể push dữ liệu khác
3. ✅ Có thể integrate dashboard với Kiotviet API

### Sửa Dashboard Để Đọc Từ Kiotviet API:

```python
# app.py
# Thay vì:
import sqlite3
conn = sqlite3.connect('retail.db')

# Thành:
import requests
KIOTVIET_API_KEY = os.getenv('KIOTVIET_API_KEY')
# ...fetch data từ Kiotviet API
```

---

## 📞 Support

| Vấn Đề | Giải Pháp |
|--------|----------|
| API error 401 | Kiểm tra .env credentials |
| API error 429 (rate limit) | Đợi 5 phút, tăng REQUEST_DELAY |
| Connection timeout | Kiểm tra internet |
| Cleanup không xóa hết | Kiểm tra demo_data_ids.json |
| Script crash | Kiểm tra Python version (3.8+) |

---

**Sẵn sàng? Chạy ngay!** 🚀

```bash
python generate_synthetic_data.py
python push_data_to_kiotviet.py
```

Xem shop của bạn trên Kiotviet! 🎉
