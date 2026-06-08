# 📚 Hướng Dẫn Các Thư Viện Python (Libraries Guide)

**Dành cho học sinh lớp 11 muốn hiểu các thư viện dùng trong Smart Retail Analytics.**

---

## 🎯 Thư Viện Là Gì?

**Thư viện = Bộ công cụ sẵn có, bạn không cần phát minh lại**

```
Ví dụ:
❌ Bạn muốn vẽ biểu đồ → Phải viết 500 dòng code
✅ Dùng thư viện Matplotlib → Viết 5 dòng code

Thư viện giúp tiết kiệm thời gian + giảm lỗi
```

---

## 📦 Các Thư Viện Trong Dự Án

### 🔵 Tầng 1: Dashboard & Web

#### **Streamlit** (Tạo Dashboard)
**Làm Gì?** Biến Python code thành website interactif  
**Dùng Để?** Tạo dashboard mà không cần HTML/CSS  
**Ví Dụ:**
```python
import streamlit as st

st.title("Doanh Số Hôm Nay")
st.metric("Tổng Tiền", "1,500,000 VND")
st.line_chart(data)  # Vẽ biểu đồ
```

**Lợi Ích:**
- ✅ Dễ, không cần học web development
- ✅ Vẽ biểu đồ/bảng chỉ cần 1-2 dòng
- ✅ Tự động làm đẹp giao diện
- ❌ Hơi chậm so với website thực
- ❌ Không tùy chỉnh chi tiết được

**Cài Đặt:**
```bash
pip install streamlit==1.28.1
```

**Kiểm Tra:**
```bash
streamlit --version
```

---

### 🟣 Tầng 2: Xử Lý Dữ Liệu

#### **Pandas** (Làm Việc Với Dữ Liệu)
**Làm Gì?** Đọc, sửa, phân tích dữ liệu (từ CSV, database, etc)  
**Dùng Để?** Tính toán, lọc, nhóm dữ liệu  
**Ví Dụ:**
```python
import pandas as pd

# Đọc file CSV
df = pd.read_csv('invoices.csv')

# Lọc dữ liệu (chỉ lấy hoá đơn > 100k)
high_value = df[df['amount'] > 100000]

# Nhóm và tính tổng
by_customer = df.groupby('customer_id')['amount'].sum()
```

**Lợi Ích:**
- ✅ Dễ đọc/sửa dữ liệu
- ✅ Nhóm, lọc, sắp xếp nhanh
- ✅ Tính toán thống kê dễ dàng
- ❌ Tốn bộ nhớ với dữ liệu lớn

**Cài Đặt:**
```bash
pip install pandas==2.1.3
```

---

#### **NumPy** (Tính Toán Số Học)
**Làm Gì?** Tính toán ma trận, mảng (nhanh hơn Python thuần)  
**Dùng Để?** Tính RFM scores, chuẩn hóa dữ liệu  
**Ví Dụ:**
```python
import numpy as np

# Tạo mảng
scores = np.array([1, 2, 3, 4, 5])

# Chuẩn hóa (từ 0-5 thành 0-1)
normalized = (scores - scores.min()) / (scores.max() - scores.min())
```

**Lợi Ích:**
- ✅ Tính toán cực nhanh
- ✅ Xử lý ma trận dễ dàng
- ❌ Khó học hơn Pandas

**Cài Đặt:**
```bash
pip install numpy==1.26.2
```

---

### 🟢 Tầng 3: Machine Learning & Analytics

#### **Scikit-learn** (Machine Learning)
**Làm Gì?** Các thuật toán AI/ML (clustering, classification, etc)  
**Dùng Để?** Nhóm khách hàng (RFM), dự báo, phân loại  
**Ví Dụ:**
```python
from sklearn.preprocessing import StandardScaler

# Chuẩn hóa dữ liệu RFM (đưa về thang 0-1)
scaler = StandardScaler()
rfm_normalized = scaler.fit_transform(rfm_data)
```

**Lợi Ích:**
- ✅ ML algorithms sẵn có
- ✅ Không cần viết từ đầu
- ❌ Khó hiểu cách hoạt động

**Cài Đặt:**
```bash
pip install scikit-learn==1.3.2
```

---

#### **MLxtend** (Apriori Algorithm)
**Làm Gì?** Thuật toán tìm quy luật mua hàng (Ai mua X thì mua Y)  
**Dùng Để?** Gợi ý sản phẩm kèm theo  
**Ví Dụ:**
```python
from mlxtend.frequent_patterns import apriori

# Tìm các cặp sản phẩm bán cùng nhau
frequent_items = apriori(transactions, min_support=0.1)
```

**Lợi Ích:**
- ✅ Tìm mối liên kết sản phẩm tự động
- ✅ Dễ sử dụng
- ❌ Chỉ dùng cho market basket analysis

**Cài Đặt:**
```bash
pip install mlxtend==0.23.0
```

---

### 🟡 Tầng 4: Database & Storage

#### **SQLAlchemy** (Kết Nối Database)
**Làm Gì?** Kết nối, đọc, viết database (SQLite, MySQL, PostgreSQL)  
**Dùng Để?** Lưu/lấy dữ liệu từ database  
**Ví Dụ:**
```python
from sqlalchemy import create_engine, text

# Kết nối database
engine = create_engine('sqlite:///retail.db')

# Đọc dữ liệu
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM customers"))
    data = result.fetchall()
```

**Lợi Ích:**
- ✅ Dễ kết nối database
- ✅ Không cần viết SQL thuần
- ❌ Hơi phức tạp với database lớn

**Cài Đặt:**
```bash
pip install sqlalchemy==2.0.23
```

---

### 🔴 Tầng 5: API & Communication

#### **Requests** (Gọi API)
**Làm Gì?** Gửi HTTP request đến API (lấy/gửi dữ liệu)  
**Dùng Để?** Kết nối Kiotviet API, Zalo API  
**Ví Dụ:**
```python
import requests

# Gọi Kiotviet API lấy khách hàng
response = requests.get(
    'https://public.kiotviet.vn/customers',
    headers={'Authorization': 'Bearer token_here'}
)
customers = response.json()
```

**Lợi Ích:**
- ✅ Dễ gọi API
- ✅ Xử lý JSON tự động
- ❌ Cần hiểu HTTP basics

**Cài Đặt:**
```bash
pip install requests==2.31.0
```

---

#### **python-dotenv** (Lưu API Keys An Toàn)
**Làm Gì?** Đọc biến môi trường từ file `.env`  
**Dùng Để?** Lưu API key mà không lộ code  
**Ví Dụ:**
```python
from dotenv import load_dotenv
import os

load_dotenv()  # Đọc file .env
api_key = os.getenv('KIOTVIET_API_KEY')
```

**Lợi Ích:**
- ✅ An toàn (không lộ API key)
- ✅ Dễ quản lý config
- ❌ Cần file `.env` riêng

**Cài Đặt:**
```bash
pip install python-dotenv==1.0.0
```

---

### ⏰ Tầng 6: Scheduling (Tự Động Làm Việc)

#### **APScheduler** (Lập Lịch Tự Động)
**Làm Gì?** Chạy code vào thời gian cụ thể (hàng ngày, mỗi 5 phút, etc)  
**Dùng Để?** Tự động lấy dữ liệu Kiotviet mỗi 5 phút  
**Ví Dụ:**
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

# Chạy hàm fetch_data mỗi 5 phút
scheduler.add_job(fetch_data, 'interval', minutes=5)
scheduler.start()
```

**Lợi Ích:**
- ✅ Tự động chạy code
- ✅ Không cần người can thiệp
- ❌ Máy phải bật 24/7

**Cài Đặt:**
```bash
pip install APScheduler==3.10.4
```

---

#### **pytz** (Múi Giờ)
**Làm Gì?** Xử lý múi giờ (GMT+7, UTC, etc)  
**Dùng Để?** Đặt lịch chính xác theo giờ Việt Nam  
**Ví Dụ:**
```python
import pytz

# Lấy giờ Việt Nam
tz = pytz.timezone('Asia/Ho_Chi_Minh')
now = datetime.now(tz)
```

**Cài Đặt:**
```bash
pip install pytz==2023.3
```

---

### 🧪 Tầng 7: Testing (Kiểm Thử)

#### **Pytest** (Framework Kiểm Thử)
**Làm Gì?** Viết test để kiểm tra code có chạy đúng không  
**Dùng Để?** Viết unit test, integration test  
**Ví Dụ:**
```python
# test_rfm.py
def test_rfm_calculation():
    result = calculate_rfm(sample_data)
    assert 'R' in result.columns
    assert len(result) > 0

# Chạy test
# $ pytest test_rfm.py
```

**Lợi Ích:**
- ✅ Tự động kiểm tra code
- ✅ Phát hiện lỗi sớm
- ❌ Cần thời gian viết test

**Cài Đặt:**
```bash
pip install pytest==7.4.3
```

---

#### **pytest-cov** (Kiểm Tra Độ Bao Phủ)
**Làm Gì?** Kiểm tra % code được test  
**Dùng Để?** Biết cần viết test thêm cái nào  
**Ví Dụ:**
```bash
pytest --cov=src test_*.py
# Kết quả: 94% code được test
```

**Cài Đặt:**
```bash
pip install pytest-cov==4.1.0
```

---

### 🔨 Tầng 8: Code Quality (Chất Lượng Code)

#### **Black** (Định Dạng Code)
**Làm Gì?** Tự động format code đẹp đẽ  
**Dùng Để?** Code đảm bảo có style thống nhất  
**Ví Dụ:**
```bash
# Trước (xấu)
def calc_rfm(data,r,f,m):
  return (r+f+m)/3

# Sau (đẹp)
def calc_rfm(data, r, f, m):
    return (r + f + m) / 3

# Chạy
$ black src/
```

**Cài Đặt:**
```bash
pip install black==23.12.0
```

---

#### **Flake8** (Kiểm Tra Lỗi Code)
**Làm Gì?** Tìm lỗi code (unused variable, style issue, etc)  
**Dùng Để?** Phát hiện code xấu  
**Ví Dụ:**
```bash
$ flake8 src/
# E501 line too long
# F841 local variable assigned but never used
```

**Cài Đặt:**
```bash
pip install flake8==6.1.0
```

---

#### **mypy** (Type Checking)
**Làm Gì?** Kiểm tra kiểu dữ liệu (string, int, list, etc)  
**Dùng Để?** Phát hiện lỗi type sớm  
**Ví Dụ:**
```python
def add(a: int, b: int) -> int:
    return a + b

add("5", 3)  # mypy báo lỗi: expected int, got str

# Chạy
$ mypy src/
```

**Cài Đặt:**
```bash
pip install mypy==1.7.1
```

---

## 🚀 Cách Cài Đặt Tất Cả

### Cách 1: Cài Tất Cả Một Lần (Dễ)
```bash
# Đi vào thư mục project
cd smart-retail-code

# Cài tất cả từ requirements.txt
pip install -r requirements.txt
```

**Mất thời gian:** 5-10 phút (lần đầu)

---

### Cách 2: Cài Riêng Lẻ (Nếu Có Vấn Đề)
```bash
# Cài Streamlit
pip install streamlit==1.28.1

# Cài Pandas
pip install pandas==2.1.3

# Cài tất cả
pip install streamlit pandas numpy sqlalchemy scikit-learn mlxtend requests python-dotenv APScheduler pytest black flake8
```

---

## 🔍 Kiểm Tra Cài Đặt

### Cách 1: Kiểm Tra Từng Thư Viện
```bash
# Kiểm tra Streamlit
python -c "import streamlit; print(streamlit.__version__)"

# Kiểm tra Pandas
python -c "import pandas; print(pandas.__version__)"

# Kiểm tra tất cả
pip list
```

### Cách 2: Chạy Code Test
```python
# test_imports.py
try:
    import streamlit
    print("✅ Streamlit OK")
except:
    print("❌ Streamlit lỗi")

try:
    import pandas
    print("✅ Pandas OK")
except:
    print("❌ Pandas lỗi")

try:
    import sqlalchemy
    print("✅ SQLAlchemy OK")
except:
    print("❌ SQLAlchemy lỗi")

# Chạy
python test_imports.py
```

---

## 📊 Bảng Tóm Tắt Thư Viện

| Thư Viện | Dùng Để | Khó | Cần Biết Gì |
|---------|---------|-----|-----------|
| **Streamlit** | Dashboard | 1/10 | HTML/CSS |
| **Pandas** | Xử lý dữ liệu | 3/10 | Cấu trúc dữ liệu |
| **NumPy** | Tính toán | 4/10 | Ma trận, mảng |
| **Scikit-learn** | Machine Learning | 6/10 | Algorithm cơ bản |
| **MLxtend** | Apriori | 3/10 | Market basket |
| **SQLAlchemy** | Database | 5/10 | SQL cơ bản |
| **Requests** | API | 2/10 | HTTP, JSON |
| **APScheduler** | Scheduling | 3/10 | Cron expressions |
| **Pytest** | Testing | 4/10 | Testing concepts |
| **Black** | Formatting | 1/10 | Python style |
| **Flake8** | Linting | 2/10 | Code issues |
| **mypy** | Type checking | 5/10 | Type hints |

---

## 🎓 Lộ Trình Học

### Tuần 1: Cơ Bản
```
Cài đặt:
1. Streamlit (tạo dashboard)
2. Pandas (xử lý dữ liệu)
3. Requests (gọi API)

Làm:
- Đọc CSV
- In ra Streamlit
- Gọi Kiotviet API
```

### Tuần 2: Phân Tích
```
Cài đặt:
1. NumPy (tính toán)
2. Scikit-learn (ML)
3. MLxtend (Apriori)

Làm:
- Tính RFM
- Nhóm khách
- Gợi ý sản phẩm
```

### Tuần 3: Tối Ưu
```
Cài đặt:
1. APScheduler (auto)
2. SQLAlchemy (database)
3. python-dotenv (config)

Làm:
- Tự động lấy dữ liệu
- Lưu vào database
- Config API key an toàn
```

### Tuần 4: Chất Lượng
```
Cài đặt:
1. Pytest (test)
2. Black (format)
3. Flake8 (lint)

Làm:
- Viết test
- Format code
- Kiểm tra chất lượng
```

---

## ❓ Câu Hỏi Thường Gặp

**Q: Tôi chỉ cần cài một số thư viện, không cần cả cai được không?**  
A: Được, nhưng một số phụ thuộc lẫn nhau. Tốt nhất cài hết.

**Q: Sao pip install lâu quá?**  
A: Lần đầu lâu vì cài 15+ thư viện. Lần 2 sẽ nhanh.

**Q: Làm sao biết thư viện nào cũ?**  
A: Chạy `pip install --upgrade -r requirements.txt`

**Q: Có thể xóa thư viện không cần thiết?**  
A: Có thể, nhưng không khuyến khích vì có thể quên dùng sau.

**Q: Windows vs Mac/Linux có khác không?**  
A: Không, tất cả thư viện chạy được cả ba.

---

**Chúc bạn cài đặt thành công!** 🚀

Nếu lỗi, xem `TROUBLESHOOTING_STUDENT.md`
