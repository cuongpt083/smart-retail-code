# ⚡ Bắt Đầu Nhanh (Quick Start) - 10 Phút

## 🎯 Mục Tiêu
Sau 10 phút, bạn sẽ:
- ✅ Cài đặt chương trình
- ✅ Chạy dashboard
- ✅ Thấy dữ liệu bán hàng đầu tiên

---

## 📋 Yêu Cầu Trước

### Máy Tính Của Bạn
- Windows 10 trở lên HOẶC Mac HOẶC Linux
- Ít nhất 4GB RAM
- Ít nhất 500MB dung lượng trống
- Kết nối Internet

### Phần Mềm Cần Cài Đặt
- **Python 3.9+** (cần cài)
- **Git** (cần cài)
- **Kiotviet Account** (có rồi)
- **Zalo Official Account** (tùy chọn, nhưng nên có)

**Kiểm tra:**
```bash
python --version    # Phải là 3.9 hoặc cao hơn
git --version       # Phải có kết quả
```

---

## 🚀 Cài Đặt (5 Phút)

### Bước 1: Tải Mã Chương Trình
```bash
# Mở Command Prompt hoặc Terminal

# Đi đến nơi bạn muốn lưu project
cd C:\Users\YourName\Documents

# Tải mã chương trình
git clone https://github.com/shelterseed/smart-retail-code.git

# Vào thư mục project
cd smart-retail-code
```

### Bước 2: Cài Đặt Python Libraries
```bash
# Cải đặt pip (Python package manager)
python -m pip install --upgrade pip

# Cài các thư viện cần thiết
pip install -r requirements.txt
```

**Tại sao lâu?** Nó đang tải ~20 thư viện Python. Uống nước, đợi hoàn thành (3-5 phút).

### Bước 3: Cấu Hình (Nhất Thiết)
```bash
# Copy file cấu hình
cp .env.example .env

# Mở file .env bằng Notepad
# Tìm 2 dòng này và điền thông tin:
# KIOTVIET_RETAIL_ID=your_retail_id_here
# KIOTVIET_API_KEY=your_api_key_here
```

**Lấy từ đâu?**
1. Vào https://oauth.kiotviet.vn/
2. Đăng nhập với tài khoản Kiotviet của bạn
3. Copy `Retail ID` và `API Key`
4. Dán vào file `.env`

---

## 🎮 Chạy Chương Trình (2 Phút)

### Cách 1: Chạy Dashboard (Dễ)
```bash
# Chắc chắn bạn đang ở thư mục smart-retail-code

# Chạy dashboard
streamlit run app.py
```

**Kết quả:** Trình duyệt tự mở, hiển thị dashboard 🎉

### Cách 2: Chạy Backend Trước (Nâng Cao)
Nếu bạn muốn chạy lấy dữ liệu trước:
```bash
# Terminal 1: Chạy backend (lấy dữ liệu)
python -m src.data_loader

# Terminal 2: Chạy dashboard (mở cửa sổ)
streamlit run app.py
```

---

## 📊 Nhìn Thấy Gì?

### Dashboard Có 3 Tab:

#### 1️⃣ **Tab Bán Hàng** (Cross-sell)
```
Top products bought together:
┌─────────────────────┐
│ Sữa + Bánh mì      │ 
│ Nước + Bánh mì     │
│ Sữa + Nước         │
└─────────────────────┘
```
👉 Dùng để gợi ý khi khách mua hàng

#### 2️⃣ **Tab Marketing** (Customer Care)
```
Khách cần chăm sóc:
┌──────────────┐
│ Champions: 2 │
│ Potential: 3 │
│ Loyal: 1     │
│ Lost: 4      │
└──────────────┘
[Nút] Gửi tin Zalo
```
👉 Dùng để gửi tin nhắn cho khách

#### 3️⃣ **Tab Quản Lý** (Analytics)
```
Doanh thu hôm nay: 1.500.000 VND
Số khách: 10
Sản phẩm bán chạy: Bánh mì (8), Nước (6)
```
👉 Dùng để báo cáo cho chủ cửa hàng

---

## ⚠️ Thường Gặp Lỗi

### ❌ Lỗi: "Python not found"
```
'python' is not recognized
```
**Cách sửa:**
1. Cài lại Python
2. Chọn "Add Python to PATH"
3. Khởi động lại Command Prompt
4. Chạy lại

### ❌ Lỗi: "requirements.txt not found"
```
ERROR: Could not open requirements.txt
```
**Cách sửa:**
```bash
# Kiểm tra bạn đang ở đúng thư mục
ls         # hoặc "dir" nếu Windows

# Phải thấy: app.py, src/, requirements.txt
```

### ❌ Lỗi: "Kiotviet API Key không hợp lệ"
```
401 Unauthorized
```
**Cách sửa:**
1. Kiểm tra file `.env`
2. Paste đúng API Key (không có khoảng trắng)
3. Lưu file
4. Chạy lại

### ❌ Lỗi: "Port 8501 already in use"
```
Port 8501 is already in use
```
**Cách sửa:**
```bash
# Tìm chương trình dùng port này và đóng nó
# Hoặc chạy dashboard ở port khác:
streamlit run app.py --server.port=8502
```

---

## 🔄 Làm Gì Tiếp?

### Ngay Lập Tức (Hôm Nay)
- ✅ Chạy dashboard
- 📱 Kết nối Zalo (xem API_BASICS.md)
- 📊 Kiểm tra dữ liệu

### 1-2 Ngày
- 🔧 Tùy chỉnh tin nhắn (DEPLOYMENT.md)
- 📝 Lưu log (check logs/app.log)
- 🧪 Test gửi tin

### 1 Tuần
- 📈 Xem kết quả bán hàng
- 💬 Nhận phản hồi khách
- 🎯 Tối ưu tin nhắn

---

## 📞 Nếu Có Vấn Đề

### Kiểm Tra Trước
1. **Kết nối Internet?** ✅ Phải có
2. **Kiotviet API Key đúng?** ✅ Kiểm tra lại
3. **Python 3.9+?** ✅ Chạy `python --version`
4. **Tất cả libraries cài?** ✅ Chạy `pip install -r requirements.txt`

### Nếu Vẫn Lỗi
Xem file `TROUBLESHOOTING.md` để biết chi tiết hơn.

---

## 🎓 Bạn Sẽ Học

- 💻 Cài đặt Python packages
- 🚀 Chạy ứng dụng Streamlit
- 🔗 Kết nối API thực tế
- 📊 Xem dữ liệu trực tiếp
- 🔑 Sử dụng khóa API an toàn

---

## ✅ Hoàn Thành Nếu...

- ✅ Dashboard mở lên
- ✅ Thấy dữ liệu từ Kiotviet
- ✅ Tab Marketing hiển thị khách hàng
- ✅ Không có lỗi màu đỏ

**Nếu tất cả đều có, chúc mừng! 🎉**

---

## 📚 Tài Liệu Tiếp Theo

| Tài Liệu | Khi Nào Đọc |
|----------|-----------|
| **API_BASICS.md** | Muốn hiểu API Kiotviet và Zalo |
| **DEPLOYMENT.md** | Muốn đưa lên máy chủ thực tế |
| **TROUBLESHOOTING.md** | Khi gặp lỗi chi tiết |
| **README_STUDENT.md** | Muốn hiểu dự án từ đầu |

---

**Sẵn sàng? Gõ lệnh đầu tiên!** 💪

```bash
python --version
```

Nếu thấy `Python 3.9+`, bạn đã sẵn sàng! 🚀
