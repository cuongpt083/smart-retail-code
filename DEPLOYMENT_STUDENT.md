# 🚀 Triển Khai (Deployment) - Đưa Lên Server Thực Tế

**Triển khai = Đưa ứng dụng từ máy tính cá nhân lên máy chủ để mọi người dùng được.**

---

## 🎯 Tổng Quan

### Hiện Tại (Local)
```
Máy tính cá nhân → Dashboard chỉ bạn thấy → Dữ liệu cá nhân
```

### Sau Triển Khai (Server)
```
Máy chủ trên Internet → Dashboard mọi người thấy → Dữ liệu dùng chung
```

---

## 📋 Yêu Cầu Triển Khai

### Option 1: Streamlit Cloud (Dễ, Miễn Phí)
- ✅ Miễn phí
- ✅ Dễ cài đặt (5 phút)
- ✅ Phù hợp cho học sinh
- ❌ Chậm hơn
- ❌ Giới hạn tài nguyên

### Option 2: Heroku (Dễ, Có Phí)
- ✅ Dễ cài đặt
- ✅ Mạnh hơn Streamlit Cloud
- ❌ Có phí ($5-50/tháng)
- ❌ Chậm hơn VPS

### Option 3: VPS (Khó, Rẻ)
- ✅ Rẻ nhất ($1-5/tháng)
- ✅ Mạnh nhất
- ❌ Khó cài đặt
- ❌ Cần hiểu Linux

**Khuyến Nghị:** Bắt đầu với **Streamlit Cloud** vì dễ nhất.

---

## 🔵 Cách 1: Streamlit Cloud (Dễ)

### Bước 1: Chuẩn Bị Mã

**Tệp cần có:**
```
smart-retail-code/
  ├── app.py
  ├── src/
  ├── requirements.txt
  ├── .streamlit/
  │   └── config.toml
  └── .env  (KHÔNG nên commit)
```

**Tạo `.streamlit/config.toml`:**
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[client]
showErrorDetails = false

[logger]
level = "info"
```

**Tạo `.gitignore`:**
```
.env
*.db
*.db-shm
*.db-wal
logs/
__pycache__/
*.pyc
.DS_Store
.venv/
venv/
```

---

### Bước 2: Push Lên GitHub

```bash
# 1. Tạo repo GitHub
# Vào github.com → New Repository
# Đặt tên: smart-retail-code
# Chọn: Public (để Streamlit Cloud thấy)

# 2. Kết nối local repository
cd smart-retail-code
git init
git add .
git commit -m "Initial commit - Smart Retail Analytics"
git branch -M main

# 3. Kết nối với GitHub
git remote add origin https://github.com/YOUR_USERNAME/smart-retail-code.git
git push -u origin main
```

---

### Bước 3: Kết Nối Streamlit Cloud

**Trên Streamlit Cloud:**
1. Vào https://streamlit.io/cloud
2. Đăng nhập (hoặc tạo tài khoản)
3. Bấm "New app"
4. Chọn GitHub repo: `smart-retail-code`
5. Chọn file: `app.py`
6. Bấm "Deploy"

**Đợi 2-3 phút, app sẽ sống!**

---

### Bước 4: Cấu Hình Secrets (Bảo Mật)

**Không để API Key ở GitHub!** Dùng Streamlit Secrets:

1. Vào app.streamlit.io → ⚙️ Settings
2. Chọn "Secrets"
3. Paste vào:
```toml
KIOTVIET_RETAIL_ID = "your_id"
KIOTVIET_API_KEY = "your_key"
ZALO_ACCESS_TOKEN = "your_token"
```

4. Cập nhật code để đọc từ secrets:
```python
import streamlit as st

retail_id = st.secrets["KIOTVIET_RETAIL_ID"]
api_key = st.secrets["KIOTVIET_API_KEY"]
```

---

### Bước 5: Test

Vào URL: `https://yourapp-username.streamlit.app`

Nếu dashboard hiển thị → ✅ Thành công!

---

## 🟠 Cách 2: Heroku (Trung Bình)

### Yêu Cầu
- GitHub account
- Heroku account (heroku.com)
- Heroku CLI

### Bước 1: Tạo File Heroku

**Tạo `Procfile`:**
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

**Tạo `runtime.txt`:**
```
python-3.11.0
```

### Bước 2: Deploy

```bash
# Login Heroku
heroku login

# Tạo app
heroku create smart-retail-app

# Set environment variables
heroku config:set KIOTVIET_RETAIL_ID=your_id
heroku config:set KIOTVIET_API_KEY=your_key
heroku config:set ZALO_ACCESS_TOKEN=your_token

# Deploy
git push heroku main

# Check logs
heroku logs --tail
```

**URL:** `https://smart-retail-app.herokuapp.com`

---

## 🔴 Cách 3: VPS (Khó, Mạnh)

### Provider Khuyến Nghị
- DigitalOcean ($5/tháng)
- Linode ($5/tháng)
- AWS EC2 (free tier)

### Bước 1: Tạo VPS

```bash
# 1. Tạo server Ubuntu 20.04
# 2. SSH vào server
ssh root@your_server_ip

# 3. Cập nhật package
apt update && apt upgrade -y

# 4. Cài Python
apt install -y python3.9 python3.9-venv python3-pip git
```

### Bước 2: Clone & Setup

```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/smart-retail-code.git
cd smart-retail-code

# Tạo venv
python3.9 -m venv venv
source venv/bin/activate

# Cài dependencies
pip install -r requirements.txt

# Tạo .env
cp .env.example .env
nano .env  # Điền API keys

# Test chạy
python -m src.data_loader
streamlit run app.py
```

### Bước 3: Chạy Dưới Dạng Service

**Tạo `/etc/systemd/system/retail-app.service`:**
```ini
[Unit]
Description=Smart Retail Analytics
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/smart-retail-code
Environment="PATH=/root/smart-retail-code/venv/bin"
ExecStart=/root/smart-retail-code/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Chạy:**
```bash
# Reload systemd
systemctl daemon-reload

# Start service
systemctl start retail-app
systemctl enable retail-app  # Tự chạy khi reboot

# Check status
systemctl status retail-app
```

### Bước 4: Setup Nginx (Reverse Proxy)

```bash
# Cài Nginx
apt install -y nginx

# Tạo config
nano /etc/nginx/sites-available/retail
```

**Nội dung:**
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
    }
}
```

**Enable:**
```bash
ln -s /etc/nginx/sites-available/retail /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Bước 5: SSL Certificate (HTTPS)

```bash
# Cài Certbot
apt install -y certbot python3-certbot-nginx

# Tạo certificate
certbot --nginx -d your_domain.com
```

---

## 📱 Cấu Hình Cho Mobile

Thêm vào `app.py`:
```python
import streamlit as st

st.set_page_config(
    page_title="Smart Retail",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Mobile-friendly CSS
st.markdown("""
    <style>
    @media (max-width: 600px) {
        .block-container {
            padding: 0.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)
```

---

## 🔒 Bảo Mật Khi Deploy

### 1. Không Expose API Keys
```python
# ❌ SAI
API_KEY = "abc123def456"

# ✅ ĐÚNG
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv('API_KEY')
```

### 2. Dùng HTTPS
- Luôn dùng HTTPS (không HTTP)
- Lấy SSL cert từ Let's Encrypt

### 3. Giới Hạn Truy Cập
```python
import streamlit as st

# Yêu cầu password (tùy chọn)
if 'authenticated' not in st.session_state:
    password = st.text_input("Nhập mật khẩu:", type="password")
    if password == "your_password":
        st.session_state.authenticated = True
    else:
        st.stop()
```

### 4. Logging & Monitoring
```python
import logging
logging.basicConfig(filename='logs/access.log', level=logging.INFO)
logging.info(f"User accessed dashboard from {request.remote_addr}")
```

---

## 📊 Giám Sát Sau Deploy

### Streamlit Cloud
- Analytics: Dashboard → Manage app → Analytics
- Logs: Look at browser console (F12)

### Heroku
```bash
# Xem logs
heroku logs --tail

# Kiểm tra dyno
heroku ps
```

### VPS
```bash
# Xem service status
systemctl status retail-app

# Xem logs
journalctl -u retail-app -f

# Kiểm tra CPU/Memory
htop
```

---

## 🔄 Cập Nhật Sau Deploy

### Streamlit Cloud
```bash
# Commit & push lên GitHub
git add .
git commit -m "Update dashboard"
git push origin main

# Streamlit Cloud tự cập nhật! (1-2 phút)
```

### Heroku
```bash
git add .
git commit -m "Update"
git push heroku main
```

### VPS
```bash
# Vào server
ssh root@your_ip

# Pull code mới
cd smart-retail-code
git pull origin main

# Cài dependencies mới
pip install -r requirements.txt

# Restart service
systemctl restart retail-app
```

---

## ✅ Checklist Triển Khai

Trước khi deploy, kiểm tra:

- [ ] Code chạy tốt trên máy local
- [ ] Không có lỗi Python (thử `python app.py`)
- [ ] requirements.txt đầy đủ (tất cả libraries)
- [ ] .env không committed lên GitHub
- [ ] API keys hoạt động
- [ ] Database có dữ liệu
- [ ] Dashboard hiển thị đúng
- [ ] Mobile-friendly (test trên phone)
- [ ] HTTPS bật (nếu VPS)
- [ ] Logs đang ghi (check logs/)

---

## 🐛 Lỗi Deploy Thường Gặp

### ❌ "ModuleNotFoundError"
**Sửa:** Thêm module vào requirements.txt

### ❌ "Connection Timeout"
**Sửa:** Kiotviet/Zalo API có thể down, chờ một chút

### ❌ "Out of Memory"
**Sửa:** Cử nằm trong 512MB (Heroku free tier)
- Xóa logs cũ
- Tối ưu database

### ❌ "Port Already in Use"
**Sửa:** Dùng port khác
```bash
streamlit run app.py --server.port 8502
```

---

## 📈 Sau Triển Khai

### 1. Monitor
- Kiểm tra logs mỗi ngày
- Kiểm tra doanh số

### 2. Optimize
- Tăng cache TTL nếu chậm
- Xóa logs cũ (lưu disk)
- Tối ưu SQL queries

### 3. Scale
- Nếu slow, nâng cấp server
- Thêm Redis cache
- Load balancing

---

## 🎓 Bạn Sẽ Học

- 🚀 Deploying web apps
- 🔒 API key management
- 📊 Monitoring & logging
- 🔧 Server maintenance
- 🌍 Internet & domains

---

## 🆘 Nếu Không Biết

| Vấn Đề | Hỏi |
|--------|-----|
| Streamlit Cloud không deploy | Streamlit docs |
| VPS SSH không hoạt động | Linux tutorials |
| Domain không resolve | DNS provider |
| Heroku credits hết | Upgrade plan |

---

**Chúc mừng! Bạn sắp ra mắt sản phẩm! 🎉**

**Bước tiếp theo:**
1. Chọn platform (Streamlit Cloud)
2. Follow hướng dẫn
3. Deploy! 🚀
4. Chia sẻ link với bạn bè

---

**URL Chia Sẻ:** `https://yourapp.streamlit.app` 🌍
