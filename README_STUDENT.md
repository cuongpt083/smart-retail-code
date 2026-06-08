# 🎓 Smart Retail Analytics - Hướng Dẫn Cho Học Sinh

## 📚 Dự Án Này Là Gì?

Tưởng tượng bạn có một cửa hàng bán hàng. Mỗi ngày có rất nhiều khách hàng mua hàng. Bạn cần biết:
- 💰 Hôm nay bán được bao nhiêu tiền?
- 👥 Ai là khách hàng thân thiết nhất?
- 🎁 Nên bán cái gì kèm theo sản phẩm khác?
- 📱 Gửi tin nhắn gì cho khách để họ quay lại?

**Smart Retail Analytics** là một chương trình giúp bạn trả lời những câu hỏi này!

---

## 🎯 Chương Trình Làm Gì?

### 1️⃣ **Nhận Dữ Liệu** (Lấy thông tin bán hàng)
- Kết nối với hệ thống Kiotviet (phần mềm quán đó là)
- Mỗi 5 phút, lấy thông tin: ai mua, mua cái gì, giá bao nhiêu

### 2️⃣ **Phân Tích Khách Hàng** (Hiểu khách hàng)
- Chia khách thành 4 nhóm:
  - 🔴 **Champions**: Khách mua nhiều, mua thường xuyên, mua gần đây
  - 🟡 **Potential**: Khách mới hoặc chưa quen, nhưng sắp sửa quay lại
  - 🟠 **Loyal**: Khách quen, nhưng lâu rồi không mua
  - ⚪ **Lost**: Khách cũ, không mua lâu rồi

### 3️⃣ **Gợi Ý Sản Phẩm** (Biết nên bán cái gì)
- Tìm quy luật: "Ai mua Bánh mì thì thường mua Nước"
- Giúp bán thêm khi khách qua cửa hàng

### 4️⃣ **Gửi Tin Nhắn** (Kết nối với khách)
- Dùng Zalo gửi tin nhắn cho khách:
  - Khách Champions: "Cảm ơn bạn, đây là quà đặc biệt cho bạn"
  - Khách Lost: "Bạn ơi, chúng tôi nhớ bạn lắm, quay lại được không?"

---

## 🔧 Cách Hoạt Động

```
Hôm nay:
↓
Mỗi 5 phút, máy tính tự lấy dữ liệu từ Kiotviet
↓
Xử lý dữ liệu: tính toán khách hàng, tìm quy luật
↓
Hiển thị lên dashboard (bảng thông tin)
↓
Tự động gửi tin nhắn Zalo cho khách
↓
Lưu lại kết quả để lần tới phân tích
```

---

## 📱 Ba Cái "Bảng Điều Khiển" (Dashboards)

### 🎁 **Bảng Bán Hàng** (Dành cho nhân viên)
- Hiển thị: Nên bán cái gì kèm theo
- Ví dụ: Khách mua Bánh mì → Gợi ý bán Nước

### 👥 **Bảng Marketing** (Dành cho người quản lý bán hàng)
- Hiển thị: Khách nào cần chăm sóc
- Có nút bấm: Gửi tin Zalo ngay

### 📊 **Bảng Quản Lý** (Dành cho chủ cửa hàng)
- Hiển thị: Tất cả thông tin
- Kiếm được: Doanh thu, khách, sản phẩm hot

---

## 💡 Ví Dụ Thực Tế

**Tình huống 1: Khách Champions**
```
Khách: Nguyễn Văn A
→ Mua 10 lần, tổng 500.000 VND, mua 5 ngày trước
→ Phân loại: Champions (khách thân thiết)
→ Gửi tin: "Cảm ơn bạn là khách VIP, dành tặng bạn 10% discount"
→ Kết quả: Khách quay lại, mua thêm
```

**Tình huống 2: Khách Lost**
```
Khách: Trần Thị B
→ Mua 3 lần, tổng 150.000 VND, mua 3 tháng trước
→ Phân loại: Lost (khách cũ, không mua lâu)
→ Gửi tin: "Bạn ơi, chúng tôi có hàng mới, quay lại xem nhé"
→ Kết quả: Khách nhớ lại, quay lại mua
```

---

## 🚀 Để Bắt Đầu

1. **Cài đặt** (xem QUICK_START.md)
2. **Chạy chương trình** (mở dashboard)
3. **Xem dữ liệu** (đợi 5 phút để dữ liệu cập nhật)
4. **Dùng chức năng** (bấm nút gửi tin)

---

## 📚 Tài Liệu Khác

| Tài Liệu | Nội Dung |
|----------|---------|
| **QUICK_START.md** | Cài đặt và chạy nhanh trong 10 phút |
| **DEPLOYMENT.md** | Đưa lên máy chủ thực tế |
| **TROUBLESHOOTING.md** | Khi có lỗi, xem đây |
| **API_BASICS.md** | Hiểu API Kiotviet và Zalo |

---

## ❓ Câu Hỏi Thường Gặp

**Q: Tôi cần biết lập trình không?**
A: Không! Nó đã lập trình sẵn rồi. Bạn chỉ cần chạy và dùng thôi.

**Q: Dữ liệu an toàn không?**
A: Có, toàn bộ dữ liệu chỉ ở máy của bạn. Không gửi cho ai.

**Q: Nếu máy tính tắt thì sao?**
A: Dữ liệu vẫn lưu ở cơ sở dữ liệu. Bật lại máy thì vẫn có.

**Q: Gửi tin Zalo có phí không?**
A: Không, dùng Zalo Official Account của bạn (phí do ZaloApp tính).

**Q: Mất bao lâu để thấy kết quả?**
A: 
- Ngay lập tức: Xem dashboard
- 1-2 tuần: Thấy hiệu quả thực tế (khách quay lại)

---

## 🎓 Bạn Sẽ Học Được Gì?

Từ dự án này, bạn hiểu được:
- 📊 Cách phân tích dữ liệu
- 🔗 Cách các API kết nối với nhau
- 💾 Cách lưu dữ liệu
- 📱 Cách tạo giao diện (dashboard)
- 🚀 Cách triển khai ứng dụng

---

## 👨‍💻 Ai Làm Cái Này?

Dự án này được tạo bởi một nhóm học sinh (lớp 11) tại Shelter & Seed Initiative.
Nó dùng các công nghệ mới nhất: Python, Streamlit, SQLite, Zalo API, Kiotviet API.

---

## 🎯 Mục Tiêu Tiếp Theo

- ✅ Hiểu cơ bản (bạn đang đây)
- 📖 Cài đặt và chạy (QUICK_START.md)
- 🚀 Triển khai thực tế (DEPLOYMENT.md)
- 🔧 Tùy chỉnh cho cửa hàng của bạn
- 📈 Theo dõi kết quả bán hàng

---

**Sẵn sàng bắt đầu? → Đọc QUICK_START.md!** 🚀
