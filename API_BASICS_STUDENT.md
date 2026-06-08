# 📡 API Cơ Bản - Hiểu API Kiotviet & Zalo

**API là gì?** API = "Cách để máy tính nói chuyện với nhau"

---

## 🎯 Khái Niệm Cơ Bản

### Tưởng Tượng

```
Bạn muốn gọi pizza:
1. Bạn gọi điện (REQUEST)
2. Nhân viên nghe (API nhận)
3. Nhân viên ghi order (API xử lý)
4. Nhân viên trả lời "OK, 30 phút" (RESPONSE)
5. Pizza đến (kết quả)

API là nhân viên nhận điện thoại đó!
```

### Trong Code

```python
# Bạn yêu cầu (REQUEST)
response = get_customers_from_kiotviet()

# API xử lý và trả về (RESPONSE)
# {"status": "success", "data": [...]}
```

---

## 🏪 API Kiotviet

**Kiotviet là gì?**  
Phần mềm quản lý cửa hàng bán lẻ. Nó lưu:
- 👥 Khách hàng
- 🛍️ Sản phẩm
- 💳 Hoá đơn/Đơn hàng
- 📊 Doanh số

**Chúng ta nói chuyện với nó qua API để lấy dữ liệu.**

---

## 📚 Các Endpoint Chính

### 1️⃣ Lấy Khách Hàng

**Mục đích:** Biết ai là khách, họ mua gì, bao nhiêu lần

**Code:**
```python
from src.kiotviet_client import KiotvietClient

client = KiotvietClient()

# Lấy tất cả khách hàng
customers = client.get_customers()

# Kết quả:
[
    {
        "id": "cust_001",
        "name": "Nguyễn Văn A",
        "phone": "0912345678",
        "email": "a@gmail.com",
        "total_spent": 500000
    },
    ...
]
```

**Dùng để:** RFM Scoring, Marketing

---

### 2️⃣ Lấy Sản Phẩm

**Mục đích:** Biết cửa hàng bán cái gì

**Code:**
```python
# Lấy tất cả sản phẩm
products = client.get_products()

# Kết quả:
[
    {
        "id": "prod_001",
        "name": "Bánh mì",
        "price": 20000,
        "category": "Bánh",
        "stock": 50
    },
    ...
]
```

**Dùng để:** Apriori Recommendations, Dashboard

---

### 3️⃣ Lấy Hoá Đơn / Đơn Hàng

**Mục đích:** Biết ai mua cái gì, lúc nào, giá bao nhiêu

**Code:**
```python
# Lấy hoá đơn
invoices = client.get_invoices()

# Kết quả:
[
    {
        "id": "inv_001",
        "customer_id": "cust_001",
        "date": "2024-06-08",
        "total": 100000,
        "items": [
            {"product_id": "prod_001", "qty": 2, "price": 20000},
            {"product_id": "prod_002", "qty": 1, "price": 60000}
        ]
    },
    ...
]
```

**Dùng để:** RFM Analysis, Cross-Sell Recommendations

---

## 🔑 Xác Thực (Authentication)

**Tại Sao Cần?**  
Kiotviet cần biết bạn là ai (và bạn có quyền không).

**Cách Hoạt Động:**
```
Bạn: "Cho tôi dữ liệu khách hàng"
Kiotviet: "Bạn là ai?"
Bạn: "Tôi là A, đây là API Key của tôi: xyz123"
Kiotviet: "OK, đúng là bạn, đây là dữ liệu của cửa hàng A"
```

**Trong Code:**
```python
# .env file
KIOTVIET_RETAIL_ID=your_retail_id
KIOTVIET_API_KEY=your_api_key_here

# Code Python
import os
from dotenv import load_dotenv

load_dotenv()
retail_id = os.getenv('KIOTVIET_RETAIL_ID')
api_key = os.getenv('KIOTVIET_API_KEY')

# Kiotviet kiểm tra xem bạn có quyền không
```

---

## ⚡ Cơ Bản Về HTTP Requests

**4 Loại Yêu Cầu (HTTP Methods):**

| Loại | Mục Đích | Ví Dụ |
|------|---------|-------|
| **GET** | Lấy dữ liệu | Lấy danh sách khách hàng |
| **POST** | Tạo dữ liệu mới | Tạo khách hàng mới |
| **PUT** | Cập nhật dữ liệu | Cập nhật thông tin khách |
| **DELETE** | Xóa dữ liệu | Xóa sản phẩm |

**Chúng ta chủ yếu dùng GET và POST.**

---

### GET Request (Lấy Dữ Liệu)

```python
import requests

# Lấy khách hàng từ Kiotviet
response = requests.get(
    url="https://public.kiotviet.vn/customers",
    headers={
        "Retail-ID": "your_retail_id",
        "Authorization": "Bearer your_api_key"
    }
)

# Kiểm tra thành công
if response.status_code == 200:
    customers = response.json()
    print(f"Got {len(customers)} customers")
else:
    print(f"Error: {response.status_code}")
```

---

### POST Request (Tạo Dữ Liệu)

```python
# Tạo khách hàng mới
response = requests.post(
    url="https://public.kiotviet.vn/customers",
    headers={
        "Retail-ID": "your_retail_id",
        "Authorization": "Bearer your_api_key"
    },
    json={
        "name": "Nguyễn Văn B",
        "phone": "0987654321",
        "email": "b@gmail.com"
    }
)

if response.status_code == 201:  # Created
    new_customer = response.json()
    print(f"Created customer: {new_customer['id']}")
```

---

## 💬 API Zalo

**Zalo là gì?**  
App chat phổ biến ở Việt Nam. Chúng ta dùng nó để gửi tin nhắn cho khách.

---

### Kết Nối Zalo

**Bước 1: Tạo Zalo Official Account (OA)**
- Vào https://oa.zalo.me/
- Tạo account
- Phê duyệt (mất 1-2 ngày)

**Bước 2: Lấy Access Token**
- Vào Settings → API
- Copy Access Token
- Paste vào .env

**Bước 3: Kết Nối**
```python
from src.zalo_messenger import ZaloMessenger

# Kết nối
messenger = ZaloMessenger(
    access_token="your_zalo_token_here"
)

# Gửi tin
messenger.send_message(
    phone="0912345678",  # Số điện thoại khách
    message="Xin chào! Chúng tôi có khuyến mãi mới cho bạn 🎁"
)
```

---

### Gửi Tin Nhắn (Thực Tế)

**Loại Tin:**

1. **Text Message** (tin nhắn chữ)
```python
messenger.send_message(
    phone="0912345678",
    message="Hello từ Smart Retail!"
)
```

2. **Campaign Message** (tin marketing)
```python
messenger.send_campaign(
    segment="champions",  # Nhóm khách
    template="welcome",   # Mẫu tin
    personalization={
        "customer_name": "Nguyễn Văn A",
        "recommendations": ["Bánh mì", "Nước"]
    }
)
```

---

## 🔄 Quy Trình Đầu Cuối

**Cảm Biến Dữ Liệu:**
```
1. Khách mua hàng ở Kiotviet
   ↓
2. Chúng ta lấy dữ liệu qua API Kiotviet (GET request)
   ↓
3. Lưu vào database SQLite
   ↓
4. Tính RFM score, Apriori rules
   ↓
5. Dashboard hiển thị
   ↓
6. Nếu tìm thấy "khách cần chăm sóc" → gửi tin Zalo (POST request)
```

---

## 🛠️ Code Ví Dụ

### Lấy Dữ Liệu & Phân Tích

```python
from src.kiotviet_client import KiotvietClient
from src.zalo_messenger import ZaloMessenger
from src.rfm_calculator import RFMCalculator

# 1. Lấy dữ liệu từ Kiotviet
kiotviet = KiotvietClient()
customers = kiotviet.get_customers()
invoices = kiotviet.get_invoices()

# 2. Tính RFM
rfm = RFMCalculator()
rfm_scores = rfm.calculate(customers, invoices)

# 3. Tìm khách "Lost" (cần marketing)
lost_customers = [
    c for c in rfm_scores 
    if rfm_scores[c]['segment'] == 'lost'
]

# 4. Gửi tin Zalo
messenger = ZaloMessenger()
for customer_id in lost_customers:
    customer = customers[customer_id]
    messenger.send_message(
        phone=customer['phone'],
        message="Chúng tôi nhớ bạn, quay lại nhé! 🎁"
    )
```

---

## 📊 Kiểu Dữ Liệu Chính

### Customer Object
```python
{
    "id": "cust_001",           # ID khách
    "name": "Nguyễn Văn A",     # Tên
    "phone": "0912345678",      # SĐT
    "email": "a@gmail.com",     # Email
    "created_date": "2024-01-01", # Ngày tạo
    "total_spent": 500000       # Tổng chi tiêu
}
```

### Invoice Object
```python
{
    "id": "inv_001",                    # ID hoá đơn
    "customer_id": "cust_001",          # ID khách
    "date": "2024-06-08",               # Ngày
    "total": 100000,                    # Tổng tiền
    "items": [                          # Danh sách sản phẩm
        {
            "product_id": "prod_001",
            "product_name": "Bánh mì",
            "quantity": 2,
            "price": 20000,
            "total": 40000
        }
    ]
}
```

### Campaign Object
```python
{
    "id": "camp_001",                   # ID campaign
    "segment": "champions",             # Nhóm khách
    "template": "welcome",              # Mẫu tin
    "created_date": "2024-06-08",
    "sent_count": 10,                   # Số tin đã gửi
    "success_count": 9,                 # Số tin thành công
    "failed_count": 1                   # Số tin thất bại
}
```

---

## ⚠️ Lỗi Thường Gặp

### ❌ 401 Unauthorized
**Nguyên nhân:** API Key sai  
**Sửa:** Kiểm tra .env file

### ❌ 429 Too Many Requests
**Nguyên nhân:** Gửi quá nhiều request  
**Sửa:** Thêm delay `time.sleep(1)` giữa các request

### ❌ 500 Server Error
**Nguyên nhân:** Lỗi server Kiotviet/Zalo  
**Sửa:** Đợi một chút rồi thử lại

### ❌ {"status": "fail", "message": "..."}
**Nguyên nhân:** Dữ liệu không hợp lệ  
**Sửa:** Kiểm tra data format

---

## 📖 Tài Liệu Chính Thức

| API | Tài Liệu | Link |
|-----|----------|------|
| Kiotviet | API Reference | https://oauth.kiotviet.vn/api-reference |
| Zalo | Zalo API Docs | https://developers.zalo.me/ |
| HTTP Status | Status Codes | https://httpwg.org/specs/rfc7231.html |

---

## 🎓 Bạn Sẽ Học

- 🔗 Cách API hoạt động
- 🔐 Xác thực và bảo mật
- 📡 HTTP requests (GET/POST)
- 💾 Xử lý JSON data
- 🚀 Tích hợp 3rd-party APIs

---

## 🔄 Tiếp Theo

1. **Chạy code ví dụ** trên
2. **Thử Kiotviet API** ở https://oauth.kiotviet.vn/
3. **Tạo Zalo OA** ở https://oa.zalo.me/
4. **Kết nối cả hai** vào chương trình

---

**Sẵn sàng? Hãy thử gọi API đầu tiên của bạn!** 🚀

```python
# Kiểm tra kết nối Kiotviet
from src.kiotviet_client import KiotvietClient

client = KiotvietClient()
try:
    customers = client.get_customers()
    print(f"✅ Kết nối thành công! Có {len(customers)} khách hàng")
except Exception as e:
    print(f"❌ Lỗi: {e}")
```
