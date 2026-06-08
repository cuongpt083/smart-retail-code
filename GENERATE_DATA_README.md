# 📊 Synthetic Data Generation Script (SDV)

## Tổng Quan

Script này tạo dữ liệu bán lẻ giả lập **với các combo sản phẩm**, đảm bảo thuật toán **Apriori** có thể phát hiện mối liên kết giữa các sản phẩm.

## 🎯 Vấn Đề Cũ

Dữ liệu cũ **quá random** → Apriori không tìm được combo:
```
Sản phẩm X + Y → Không đủ lần xuất hiện
→ Không vượt qua min_support
→ Dashboard không hiển thị gợi ý
```

## ✨ Giải Pháp Mới

Script này **đảm bảo**:
- ✅ **35% hoá đơn** chứa combo sản phẩm
- ✅ **Bánh mì + Nước** xuất hiện **25% hoá đơn**
- ✅ **Gia vị + Ready-to-eat** xuất hiện **18% hoá đơn**
- ✅ **Nước + Snack** xuất hiện **15% hoá đơn**
- ✅ Dữ liệu **đồng nhất** (seed cố định)

## 🚀 Cách Sử Dụng

### Cách 1: Chạy Script (Dễ nhất)

```bash
# Đi vào thư mục project
cd smart-retail-code

# Chạy script
python generate_synthetic_data.py

# Output:
# 🔄 Generating synthetic retail data with product combos...
#   ✓ Generating 100 products...
#   ✓ Generating 100 customers...
#   ✓ Generating 300 invoices with product combo rules...
# ✅ Data generation complete!
```

**Kết quả:** Tạo 4 file CSV mới:
- `products.csv`
- `customers.csv`
- `invoices.csv`
- `invoice_items.csv`

### Cách 2: Chạy Từ Python

```python
from generate_synthetic_data import main

# Generate dữ liệu
main()
```

## 📋 Cấu Trúc Dữ Liệu

### products.csv (100 sản phẩm)
```
ma_hang,ten_hang,thuong_hieu,loai_hang,nhom_hang,gia_ban,gia_von,ton_kho,...
SP1001,Bánh mì trong,Vissan,Hàng hóa,Bánh, kẹo, snack >> Bánh mì,51000,31000,16,...
SP1002,Nước ngọt và,Coca,Hàng hóa,Đồ uống >> Nước ngọt,366000,192000,106,...
```

### customers.csv (100 khách)
```
ma_khach_hang,ten_khach_hang,loai_khach,dien_thoai,email,...
KH01001,Nguyễn Văn A,Cá nhân,0912345678,customer1@example.com,...
```

### invoices.csv (300 hoá đơn)
```
ma_hoa_don,thoi_gian,ma_khach_hang,ten_khach_hang,tong_tien_hang,giam_gia,...
HD000001,2026-04-10T00:00:00,KH01001,Nguyễn Văn A,2000000,0,...
```

### invoice_items.csv (Chi tiết hoá đơn)
```
ma_hoa_don,ma_hang,so_luong,don_gia,giam_gia_phan_tram,giam_gia,...
HD000001,SP1003,2,51000,0,0,102000,2026-04-10T00:00:00
HD000001,SP1008,3,366000,10,109800,988200,2026-04-10T00:00:00
```

## 🎯 Product Combo Rules

### Đã Cấu Hình

| Combo | Sản phẩm | Tần suất | Mục đích |
|-------|---------|---------|---------|
| **bánh_mì_nước** | Bánh mì + Nước | **25%** | Người bán gạo cùng nước uống |
| **bánh_mì_sữa** | Bánh mì + Sữa | 20% | Ăn sáng combo |
| **gia_vị_ready_to_eat** | Gia vị + Thực phẩm liền | 18% | Nấu ăn cơ bản |
| **nước_snack** | Nước + Snack | 15% | Giải khát vặt |
| **chăm_sóc** | Sản phẩm chăm sóc | 12% | Combo cá nhân |

## 📊 Dữ Liệu Kỳ Vọng

### Khi Chạy Dashboard

**Dashboard Bán Hàng (Apriori):**
```
Top Product Associations:
┌────────────────────────────┬──────────┬────────────┐
│ Sản phẩm A + B              │ Support  │ Confidence │
├────────────────────────────┼──────────┼────────────┤
│ Bánh mì + Nước              │ 20%      │ 75%        │
│ Gia vị + Ready-to-eat       │ 15%      │ 68%        │
│ Nước + Snack                │ 12%      │ 60%        │
└────────────────────────────┴──────────┴────────────┘
```

**Recommendation:** "Khách mua Bánh mì → Gợi ý Nước"

## ⚙️ Tùy Chỉnh

Muốn thay đổi tần suất? Sửa `PRODUCT_COMBOS`:

```python
PRODUCT_COMBOS = {
    "bánh_mì_nước": ([...product_ids...], 0.35),  # Tăng từ 0.25 → 0.35 (35%)
    "bánh_mì_sữa": ([...product_ids...], 0.25),   # Tăng từ 0.20 → 0.25
}
```

## 🧪 Kiểm Tra Kết Quả

Sau khi chạy script, kiểm tra Apriori:

```python
# test_apriori.py
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

# Load dữ liệu
items = pd.read_csv('invoice_items.csv')
invoices = pd.read_csv('invoices.csv')

# Tạo transaction matrix
transactions = items.groupby('ma_hoa_don')['ma_hang'].apply(list)

# Chạy Apriori
frequent_itemsets = apriori(transactions, min_support=0.05, use_colnames=True)
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.3)

print(f"✅ Found {len(rules)} rules!")
print(rules[['antecedants', 'consequents', 'support', 'confidence']].head(10))
```

## 📋 Lợi Ích

| Trước | Sau |
|-------|-----|
| ❌ Dữ liệu random | ✅ Dữ liệu có ý nghĩa |
| ❌ Không có combo | ✅ 300 hoá đơn với combo |
| ❌ Dashboard trống | ✅ Dashboard hiển thị gợi ý |
| ❌ Học sinh không hiểu | ✅ Kết quả có logic |

## 🔄 Tái Tạo Dữ Liệu

Nếu muốn dữ liệu khác:

```python
# Bước 1: Thay đổi RANDOM_SEED
RANDOM_SEED = 123  # Từ 42 thành 123

# Bước 2: Chạy lại
python generate_synthetic_data.py
```

## 📞 Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'pandas'"

```bash
pip install pandas numpy
```

### ❌ "Apriori vẫn không tìm combo"

Kiểm tra:
1. **Tần suất combo**: Có ≥ 5% hoá đơn không?
2. **Min support**: Có > 5% không?
3. **Min confidence**: Có > 30% không?

Sửa:
```python
frequent_itemsets = apriori(transactions, min_support=0.03)  # Giảm từ 0.05 → 0.03
```

## 📊 Ví Dụ Output

```
✅ Data generation complete!

📊 Summary:
  • Products: 100
  • Customers: 100
  • Invoices: 300
  • Invoice items: 1250

🎯 Product Combos (for Apriori):
  • bánh_mì_nước: 25% frequency
  • bánh_mì_sữa: 20% frequency
  • gia_vị_ready_to_eat: 18% frequency
  • nước_snack: 15% frequency
  • chăm_sóc: 12% frequency

💾 Files saved:
  • products.csv
  • customers.csv
  • invoices.csv
  • invoice_items.csv
```

## 🎓 Học Từ Đây

Từ script này, bạn học được:
- 📊 Cách tạo dữ liệu giả lập (synthetic data)
- 🔗 Cách thiết kế business rules vào dữ liệu
- 💡 Cách đảm bảo thuật toán hoạt động đúng
- 🎯 Tư duy "dữ liệu → Thuật toán → Kết quả"

---

**Sẵn sàng? Chạy ngay!** 🚀
```bash
python generate_synthetic_data.py
```
