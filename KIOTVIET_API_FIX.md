# 🔧 Fix Lỗi 503 - Kiotviet API

## 🔴 Vấn Đề Gốc

Script `push_data_to_kiotviet.py` gặp lỗi **503 Service Unavailable** vì:

```
✗ Validating Kiotviet API credentials...
  ❌ API error: 503
```

---

## 🎯 Nguyên Nhân

### **Lỗi 1: Endpoint URL Sai ❌**

```python
# ❌ SAI (script cũ)
KIOTVIET_BASE_URL = "https://public.kiotviet.vn"

# ✅ ĐÚNG (theo tài liệu Kiotviet)
KIOTVIET_BASE_URL = "https://public.kiotapi.com"
```

**Lý do**: Kiotviet Public API dùng domain `kiotapi.com`, không phải `kiotviet.vn`

### **Lỗi 2: Header Sai ❌**

```python
# ❌ SAI (script cũ)
KIOTVIET_HEADERS = {
    "Retail-ID": KIOTVIET_RETAIL_ID,  # ← Header name sai
    "Authorization": f"Bearer {KIOTVIET_API_KEY}",
    "Content-Type": "application/json",
}

# ✅ ĐÚNG (theo tài liệu Kiotviet)
KIOTVIET_HEADERS = {
    "Retailer": tên_gian_hang,  # ← Tên header đúng
    "Authorization": f"Bearer {access_token}",  # ← Phải là access token
    "Content-Type": "application/json",
}
```

**Lý do**: Kiotviet API yêu cầu:
- Header `"Retailer"` (tên gian hàng) thay vì `"Retail-ID"`
- Authorization dùng **access token**, không phải API key

### **Lỗi 3: .env Credentials Sai ❌**

```bash
# ❌ SAI (script cũ)
KIOTVIET_RETAIL_ID=...
KIOTVIET_API_KEY=...

# ✅ ĐÚNG (Cách 1: Access Token)
KIOTVIET_ACCESS_TOKEN=...
KIOTVIET_RETAILER_NAME=...

# ✅ ĐÚNG (Cách 2: OAuth)
KIOTVIET_CLIENT_ID=...
KIOTVIET_CLIENT_SECRET=...
KIOTVIET_RETAILER_NAME=...
```

---

## ✅ Cách Fix

### **Bước 1: Update Script**

Scripts đã được fix:
- ✅ `push_data_to_kiotviet.py` (v2)
- ✅ `cleanup_kiotviet_demo.py` (v2)
- ✅ `PUSH_DATA_README.md` (updated)

**Điều thay đổi:**
1. Endpoint: `kiotapi.com` (sửa)
2. Header name: `Retailer` (sửa)
3. Thêm hàm `get_access_token()` để lấy token tự động
4. Support 2 cách xác thực: direct token + OAuth

### **Bước 2: Update .env**

**Cách 1: Dùng Access Token Trực Tiếp (Dễ)**

```bash
# .env file
KIOTVIET_ACCESS_TOKEN=<copy từ Kiotviet dashboard>
KIOTVIET_RETAILER_NAME=<tên gian hàng của bạn>
```

**Lấy từ đâu:**
1. https://kiotviet.vn → Đăng nhập Admin
2. Thiết lập → Kết nối API → Public API
3. Copy **Access Token**
4. Copy **Tên gian hàng**
5. Paste vào `.env`

**Cách 2: Dùng OAuth (Nâng Cao)**

```bash
# .env file
KIOTVIET_CLIENT_ID=<lấy từ Kiotviet dashboard>
KIOTVIET_CLIENT_SECRET=<lấy từ Kiotviet dashboard>
KIOTVIET_RETAILER_NAME=<tên gian hàng>
```

Script sẽ tự động lấy access token.

### **Bước 3: Chạy Script**

```bash
# Push data to Kiotviet
python push_data_to_kiotviet.py

# Kết quả kỳ vọng:
# ✓ API credentials valid (endpoint: https://public.kiotapi.com)
# ✓ Created 100/100 products
# ✓ Created 100/100 customers
# ✓ Created 300/300 invoices
```

---

## 📋 So Sánh: Cũ vs Mới

| Aspect | Cũ (SAI) | Mới (ĐÚNG) |
|--------|----------|-----------|
| **Endpoint** | `public.kiotviet.vn` ❌ | `public.kiotapi.com` ✅ |
| **Header 1** | `Retail-ID` ❌ | `Retailer` ✅ |
| **Header 2** | API Key ❌ | Access Token ✅ |
| **.env Var 1** | `KIOTVIET_RETAIL_ID` ❌ | `KIOTVIET_RETAILER_NAME` ✅ |
| **.env Var 2** | `KIOTVIET_API_KEY` ❌ | `KIOTVIET_ACCESS_TOKEN` ✅ |
| **OAuth** | Không support ❌ | Hỗ trợ ✅ |
| **Lỗi** | 503 Service Unavailable ❌ | Hoạt động ✅ |

---

## 🧪 Kiểm Tra Fix

### Test 1: Validate Credentials

```bash
python push_data_to_kiotviet.py
```

**Output thành công:**
```
🔐 Validating Kiotviet API credentials...
  ✓ API credentials valid (endpoint: https://public.kiotapi.com)

🔎 Checking CSV files...
  ✓ products.csv
  ✓ customers.csv
  ✓ invoices.csv
  ✓ invoice_items.csv
```

### Test 2: Check .env

```bash
# Verify variables
echo $KIOTVIET_ACCESS_TOKEN  # Phải có giá trị
echo $KIOTVIET_RETAILER_NAME  # Phải có giá trị
```

### Test 3: Check Endpoint

```bash
# Verify endpoint URL in script
grep "KIOTVIET_BASE_URL" push_data_to_kiotviet.py
# Kết quả phải là: https://public.kiotapi.com
```

---

## 📚 Tài Liệu Tham Khảo

**Kiotviet Official API Docs:**
- https://www.kiotviet.vn/huong-dan-su-dung-kiotviet/retail-ket-noi-api/public-api/

**Key Sections:**
- Section 2.2: Lấy thông tin Access Token
- Section 2.4: Hàng hóa (Products API)
- Section 2.5: Đặt hàng (Orders API)
- Section 2.6: Khách hàng (Customers API)

---

## 🆘 Still Having Issues?

### Lỗi: "401 Unauthorized"
- Check .env credentials
- Verify access token không hết hạn
- Try lấy token mới từ dashboard

### Lỗi: "Cannot get access token from .env"
- Set `KIOTVIET_ACCESS_TOKEN` + `KIOTVIET_RETAILER_NAME`
- HOẶC set `KIOTVIET_CLIENT_ID` + `KIOTVIET_CLIENT_SECRET`

### Lỗi: "Connection error"
- Check internet connection
- Verify firewall không block `public.kiotapi.com`

---

## ✨ Summary

**Các lỗi đã fix:**
1. ✅ Endpoint URL: `kiotviet.vn` → `kiotapi.com`
2. ✅ Header name: `Retail-ID` → `Retailer`
3. ✅ Authentication: API Key → Access Token
4. ✅ OAuth support: Thêm hỗ trợ lấy token tự động

**File đã update:**
- ✅ `push_data_to_kiotviet.py` (v2 - fix)
- ✅ `cleanup_kiotviet_demo.py` (v2 - fix)
- ✅ `PUSH_DATA_README.md` (updated)

**Ready to push?** 🚀

```bash
# 1. Update .env with correct credentials
# 2. python push_data_to_kiotviet.py
# 3. Check shop at https://kiotviet.vn
```
