# 🔧 Troubleshooting - Khi Có Lỗi

**Phần này giúp bạn sửa những vấn đề thường gặp.**

---

## 🚨 Lỗi Cài Đặt

### ❌ Python: "command not found"

**Triệu chứng:**
```
python: command not found
```

**Nguyên nhân:**
- Python chưa cài
- Hoặc cài nhưng chưa thêm vào PATH

**Cách sửa:**
```bash
# Kiểm tra
python --version

# Nếu không hoạt động:
# 1. Cài lại Python từ python.org
# 2. Chọn "Add Python to PATH" 
# 3. Khởi động lại Command Prompt
# 4. Thử lại
```

---

### ❌ Git: "command not found"

**Triệu chứng:**
```
git: command not found
```

**Nguyên nhân:**
- Git chưa cài

**Cách sửa:**
```bash
# Cài Git từ git-scm.com
# Sau khi cài, kiểm tra:
git --version
```

---

### ❌ Pip: "No module named pip"

**Triệu chứng:**
```
No module named pip
```

**Cách sửa:**
```bash
# Cách 1: Cập nhật pip
python -m pip install --upgrade pip

# Cách 2: Nếu cách 1 không hoạt động, cài lại Python
# Xem hướng dẫn: python.org/downloads
```

---

### ❌ Requirements: "ERROR: Could not find a version"

**Triệu chứng:**
```
ERROR: Could not find a version that satisfies the requirement streamlit==1.xx.x
```

**Nguyên nhân:**
- Thư viện cũ, không còn trên PyPI
- Hoặc lỗi phiên bản Python

**Cách sửa:**
```bash
# Cách 1: Cập nhật pip trước
python -m pip install --upgrade pip

# Cách 2: Cài lại requirements
pip install --upgrade -r requirements.txt

# Cách 3: Nếu vẫn không hoạt động, kiểm tra Python version
python --version  # Phải là 3.9 hoặc cao hơn
```

---

## 🌐 Lỗi Kiotviet API

### ❌ 401 Unauthorized

**Triệu chứng:**
```
Error: 401 Unauthorized
Kiotviet API rejected request
```

**Nguyên nhân:**
- API Key sai hoặc hết hạn
- Retail ID sai

**Cách sửa:**
```bash
# 1. Kiểm tra file .env
nano .env  # hoặc mở bằng Notepad

# Tìm những dòng này:
KIOTVIET_RETAIL_ID=your_retail_id_here
KIOTVIET_API_KEY=your_api_key_here

# 2. Lấy API Key mới:
# - Vào https://oauth.kiotviet.vn/
# - Đăng nhập
# - Copy Retail ID và API Key
# - Paste vào .env (không có khoảng trắng)

# 3. Lưu file .env

# 4. Khởi động lại chương trình
```

**Kiểm tra:**
```bash
# Mở Python console
python

# Gõ:
import os
from dotenv import load_dotenv
load_dotenv()
print(os.getenv('KIOTVIET_API_KEY'))  # Phải hiển thị key của bạn
```

---

### ❌ 404 Not Found

**Triệu chứng:**
```
Error: 404 Not Found
Endpoint not found
```

**Nguyên nhân:**
- API Kiotviet thay đổi
- Hoặc sử dụng phiên bản API cũ

**Cách sửa:**
```bash
# Kiểm tra phiên bản API
# Xem file: src/kiotviet_client.py
# Tìm dòng: BASE_URL = "https://public.kiotviet.vn/..."

# Nếu 404, có thể API đã update
# Xem tài liệu mới: https://oauth.kiotviet.vn/api-reference
```

---

### ❌ Connection Timeout

**Triệu chứng:**
```
requests.exceptions.ConnectTimeout
Connection to Kiotviet failed after 5 seconds
```

**Nguyên nhân:**
- Kết nối Internet kém
- Máy chủ Kiotviet quá tải

**Cách sửa:**
```bash
# 1. Kiểm tra Internet
ping google.com  # Phải có phản hồi

# 2. Đợi một chút, rồi chạy lại

# 3. Nếu vẫn lỗi, tăng thời gian timeout
# Mở: src/kiotviet_client.py
# Tìm: timeout=5
# Đổi thành: timeout=10

# 4. Kiểm tra Kiotviet có bảo trì không
# Xem: https://kiotviet.vn/
```

---

## 📊 Lỗi Streamlit Dashboard

### ❌ Port 8501 Already in Use

**Triệu chứng:**
```
Port 8501 is already in use
Use a different port with --server.port
```

**Nguyên nhân:**
- Dashboard đã chạy ở cửa sổ khác
- Hoặc chương trình khác dùng port 8501

**Cách sửa:**
```bash
# Cách 1: Đóng cửa sổ dashboard đang chạy
# (Nhấn Ctrl+C ở cửa sổ Command Prompt)

# Cách 2: Dùng port khác
streamlit run app.py --server.port=8502

# Cách 3: Tìm PID và kill (nâng cao)
# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Mac/Linux:
lsof -i :8501
kill -9 <PID>
```

---

### ❌ Module Not Found Error

**Triệu chứng:**
```
ModuleNotFoundError: No module named 'streamlit'
```

**Nguyên nhân:**
- Thư viện chưa cài

**Cách sửa:**
```bash
# Cài lại requirements
pip install -r requirements.txt

# Hoặc cài từng thư viện
pip install streamlit pandas sqlalchemy requests
```

---

### ❌ DataFrame is Empty

**Triệu chứng:**
```
Dashboard hiển thị, nhưng dữ liệu trống
Bảng hiển thị: 0 rows
```

**Nguyên nhân:**
- Kiotviet API chưa lấy dữ liệu
- Hoặc chưa có hoá đơn nào

**Cách sửa:**
```bash
# 1. Kiểm tra Kiotviet có dữ liệu không
# - Vào Kiotviet app
# - Xem có hoá đơn không

# 2. Chạy data loader trước
python -m src.data_loader

# 3. Đợi 5-10 phút cho dữ liệu cập nhật

# 4. Refresh dashboard (F5)

# 5. Kiểm tra database tồn tại
ls retail.db  # hoặc "dir retail.db"
```

---

## 💬 Lỗi Zalo Messaging

### ❌ Zalo Token Invalid

**Triệu chứng:**
```
Error: Invalid Zalo access token
401 Unauthorized
```

**Nguyên nhân:**
- Token hết hạn
- Token sai
- Account Zalo chưa được phê duyệt

**Cách sửa:**
```bash
# 1. Kiểm tra .env file
grep ZALO_ACCESS_TOKEN .env

# 2. Lấy token mới:
# - Vào https://oa.zalo.me/
# - Vào "Settings" → "API"
# - Copy "Access Token"
# - Paste vào .env

# 3. Kiểm tra account được phê duyệt
# - Trên Zalo OA page
# - Phải có badge "Official"

# 4. Lưu .env và khởi động lại
```

---

### ❌ No Recipients to Send

**Triệu chứng:**
```
Error: No valid recipients found
Message not sent
```

**Nguyên nhân:**
- Chưa có khách hàng nào trong database
- Hoặc số điện thoại khách không hợp lệ

**Cách sửa:**
```bash
# 1. Kiểm tra database có khách không
python -c "
import sqlite3
conn = sqlite3.connect('retail.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM customers')
print(f'Total customers: {cursor.fetchone()[0]}')
"

# 2. Nếu 0 khách, hãy:
# - Tạo hoá đơn ở Kiotviet
# - Chạy data loader
python -m src.data_loader

# - Đợi 5 phút
# - Kiểm tra lại
```

---

## 💾 Lỗi Database

### ❌ Database is Locked

**Triệu chứng:**
```
sqlite3.OperationalError: database is locked
```

**Nguyên nhân:**
- Nhiều chương trình dùng database cùng lúc
- Hoặc file database bị khóa

**Cách sửa:**
```bash
# 1. Đóng tất cả cửa sổ chương trình
# (Nhấn Ctrl+C ở tất cả terminal)

# 2. Đợi 5 phút

# 3. Khởi động lại chương trình

# 4. Nếu vẫn lỗi, xóa file lock
rm retail.db-shm retail.db-wal  # Mac/Linux
del retail.db-shm retail.db-wal  # Windows
```

---

### ❌ Disk Full / No Space Left

**Triệu chứng:**
```
IOError: [Errno 28] No space left on device
```

**Nguyên nhân:**
- Ổ cứng gần đầy
- Database quá lớn

**Cách sửa:**
```bash
# 1. Kiểm tra dung lượng
# Windows: Mở "File Explorer" → "This PC" → xem dung lượng trống
# Mac/Linux:
df -h

# 2. Giải phóng không gian
# - Xóa file không cần
# - Xóa cache

# 3. Nếu vẫn không đủ, nâng cấp ổ cứng

# 4. Tạm thời, xóa log cũ
rm logs/*.log  # Xóa file log cũ
```

---

## 🐛 Lỗi Logic / Tính Toán

### ❌ RFM Scores Không Cập Nhật

**Triệu chứng:**
```
Dashboard hiển thị RFM score, nhưng không thay đổi
```

**Nguyên nhân:**
- Cache chưa hết hạn
- Hoặc công thức tính sai

**Cách sửa:**
```bash
# 1. Xóa cache
python -c "
from src.cache_manager import CacheManager
cache = CacheManager()
cache.invalidate_all()
print('Cache cleared!')
"

# 2. Refresh dashboard (F5)

# 3. Kiểm tra công thức (file: src/rfm_calculator.py)
# Công thức phải là:
# R = days since last purchase (nhỏ = tốt)
# F = number of purchases (lớn = tốt)
# M = total spent (lớn = tốt)
```

---

### ❌ Apriori Recommendations Sai

**Triệu chứng:**
```
Gợi ý sản phẩm không có sense
Ví dụ: Bánh mì + Nước (không liên quan)
```

**Nguyên nhân:**
- Dữ liệu chưa đủ
- Hoặc support threshold quá thấp

**Cách sửa:**
```bash
# 1. Kiểm tra dữ liệu
# Cần ít nhất 50+ hoá đơn để có kết quả tốt

# 2. Nếu không đủ, tạo thêm hoá đơn
# - Ở Kiotviet
# - Hoặc dùng sample data

# 3. Tăng min_support
# Mở: src/apriori_miner.py
# Tìm: min_support = 0.01
# Đổi thành: min_support = 0.05  # Strict hơn

# 4. Chạy lại
python -m src.data_loader
```

---

## 📋 Chuyên Sâu (Dành Cho Lập Trình Viên)

### ❌ KeyError trong DataFrame

**Triệu chứng:**
```
KeyError: 'customer_id'
```

**Cách sửa:**
```bash
# Kiểm tra cột trong CSV
python -c "
import pandas as pd
df = pd.read_csv('invoices.csv')
print(df.columns)
"

# Phải có cột: customer_id, product_id, price, date, ...
```

---

### ❌ Type Error trong Calculation

**Triệu chứng:**
```
TypeError: unsupported operand type(s)
```

**Cách sửa:**
```bash
# Kiểm tra kiểu dữ liệu
python -c "
import sqlite3
conn = sqlite3.connect('retail.db')
cursor = conn.cursor()
cursor.execute('SELECT typeof(price) FROM items LIMIT 1')
print(cursor.fetchone())
"

# Phải là INTEGER hoặc REAL, không phải TEXT
```

---

## 📞 Nếu Không Tìm Thấy Giải Pháp

### Bước 1: Xem Log
```bash
# Xem file log gần đây nhất
tail -f logs/app.log

# Tìm lỗi gần nhất (dòng cuối cùng)
```

### Bước 2: Tìm Tin Nhắn Lỗi
```bash
# Lấy toàn bộ error message
grep -i error logs/app.log | tail -20
```

### Bước 3: Cộng Đồng
- Hỏi bạn cùng lớp
- Hoặc hỏi Slack team

### Bước 4: Khởi Động Lại
```bash
# Đối với 90% lỗi, khởi động lại có thể sửa:
# 1. Đóng tất cả cửa sổ (Ctrl+C)
# 2. Đợi 30 giây
# 3. Chạy lại chương trình
```

---

## 🎯 Cách Tìm Giúp Đỡ

| Vấn Đề | Xem Tài Liệu |
|--------|-----------|
| Không chạy được | QUICK_START.md |
| Lỗi API | API_BASICS.md |
| Lỗi Zalo | DEPLOYMENT.md |
| Muốn hiểu code | README_STUDENT.md |
| Deploy lên server | DEPLOYMENT.md |

---

## ✅ Kiểm Tra Hệ Thống

Chạy cái này để kiểm tra tất cả:

```bash
python -c "
import sys
print(f'✅ Python: {sys.version}')

try:
    import streamlit
    print('✅ Streamlit cài đặt')
except:
    print('❌ Streamlit chưa cài')

try:
    import sqlite3
    print('✅ SQLite cài đặt')
except:
    print('❌ SQLite lỗi')

try:
    import pandas
    print('✅ Pandas cài đặt')
except:
    print('❌ Pandas chưa cài')

try:
    from dotenv import load_dotenv
    load_dotenv()
    import os
    key = os.getenv('KIOTVIET_API_KEY')
    if key and key != 'your_api_key_here':
        print('✅ .env file đúng')
    else:
        print('❌ .env file chưa điền hoặc sai')
except:
    print('❌ .env file không tìm thấy')

print('\\n✅ Nếu tất cả là ✅, bạn sẵn sàng!')
"
```

---

**Có vấn đề? Kiên nhẫn và cố gắng, bạn sẽ giải quyết được!** 💪
