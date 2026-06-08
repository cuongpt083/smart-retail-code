# 📋 Smart Retail Analytics - Features List

**Phiên bản**: MVP 1.0  
**Ngày**: 08-06-2026  
**Audience**: Quản lý cửa hàng, Marketing team, Sales team

---

## 🎯 Product Vision

**Mục tiêu**: Giúp cửa hàng tạp hóa:
- 📊 Theo dõi doanh thu & bán hàng real-time
- 👥 Hiểu rõ hành vi khách hàng (RFM segmentation)
- 🎁 Gợi ý sản phẩm bán chéo/bán thêm (Apriori)
- 💬 Gửi tin nhắn Zalo tới khách (marketing automation)
- 🔄 Tự động pull dữ liệu từ Kiotviet (ETL)

---

## 📱 User Personas

### **Persona 1: Người Quản Lý Cửa Hàng (Store Manager)**
- **Tên**: Anh Hoàng (45 tuổi)
- **Mục tiêu**: Monitor doanh thu, nhận biết khách VIP
- **Thường dùng**: Dashboard overview, Top products, Customer list
- **Tần suất**: Hàng ngày (5 phút/lần)
- **Thiết bị**: Desktop (office) + Laptop (tại cửa hàng)

### **Persona 2: Người Quản Lý Marketing (Marketing Manager)**
- **Tên**: Chị Linh (32 tuổi)
- **Mục tiêu**: Phân khúc khách, gửi promotion, tăng repeat purchase
- **Thường dùng**: RFM segmentation, Apriori recommendations, Zalo integration
- **Tần suất**: 2-3 lần/tuần
- **Thiết bị**: Desktop, Mobile

### **Persona 3: Nhân Viên Bán Hàng (Sales Staff)**
- **Tên**: Em Lan (22 tuổi)
- **Mục tiêu**: Biết sản phẩm nào bán chạy, khách nào quay lại
- **Thường dùng**: Top products, Top customers, Quick insight
- **Tần suất**: Hàng ngày (1-2 phút)
- **Thiết bị**: Mobile (Tablet tại counter)

---

## 🎨 Core Features

### **Feature 1: Dashboard Overview** 🏠
**Mục đích**: Cung cấp snapshot doanh thu & KPIs chính

**Components**:
```
┌─────────────────────────────────────────┐
│ 📊 SMART RETAIL ANALYTICS - Dashboard   │
├─────────────────────────────────────────┤
│                                         │
│ 💰 Total Revenue (Today)   💵 890,000   │ ← Key Metric #1
│ 📦 Orders (Today)          📈 12        │ ← Key Metric #2
│ 👥 Unique Customers (Today) 👤 8        │ ← Key Metric #3
│ ⭐ Top Product (Today)     🏆 Bánh mì   │ ← Key Metric #4
│                                         │
└─────────────────────────────────────────┘
```

**Specifications**:
- Display 4 KPI cards (metric + number + trending arrow)
- Auto-refresh every 5 minutes
- Time period: Today / This week / This month (dropdown)
- Color coding: Green (good), Red (needs attention)

**User Actions**:
- Select time period
- Click metric to drill down

**Data Source**: `invoices` table (today's khach_da_tra sum)

**Success Criteria**:
- ✅ Load in <2 seconds
- ✅ Updates within 5 minutes
- ✅ Mobile responsive

---

### **Feature 2: Revenue Chart** 📈
**Mục đích**: Visualize doanh thu theo thời gian (xu hướng)

**Chart Type**: Line chart (time series)

**Specifications**:
- **X-axis**: Dates (09-03-2026 → 07-06-2026)
- **Y-axis**: Revenue (VND)
- **Granularity**: Daily / Weekly / Monthly (selector)
- **Color**: Blue line with light blue area fill
- **Hover**: Show date + revenue in tooltip

**User Actions**:
- Toggle granularity (Daily / Weekly / Monthly)
- Hover over points to see details
- Click to export as image

**Data Source**: `invoices.thoi_gian`, `invoices.khach_da_tra`

**Example Data**:
```
Date         Revenue
2026-03-09   2,450,000 VND
2026-03-10   3,120,000 VND
2026-03-11   2,890,000 VND
...
```

**Success Criteria**:
- ✅ Smooth rendering with 300+ data points
- ✅ Responsive to window resize
- ✅ Clear tooltip on hover

---

### **Feature 3: Top Products** 🏆
**Mục đích**: Hiển thị sản phẩm bán chạy nhất

**Display**: Table + Bar chart (dual view)

**Specifications**:
- **Metrics**: Product name, Quantity sold, Total revenue, Profit
- **Sorting**: Revenue descending (default)
- **Rows**: Top 10 products
- **Time period**: Today / This week / This month (selector)

**Table Columns**:
| # | Sản phẩm | Số lượng | Doanh thu | Lợi nhuận | % Tổng |
|---|----------|---------|-----------|-----------|--------|
| 1 | Bánh mì Snack | 45 | 2,025,000 | 677,500 | 8.2% |
| 2 | Nước ngọt 1.5L | 38 | 1,710,000 | 513,000 | 7.1% |
| 3 | Mì ăn liền | 32 | 896,000 | 268,800 | 5.9% |

**Bar Chart**: Horizontal bars showing revenue

**User Actions**:
- Switch between Table / Chart view
- Sort by: Revenue / Quantity / Profit
- Filter by category
- Click product → See customer details who bought it

**Data Source**: 
```sql
SELECT p.ten_hang, COUNT(*) as qty, SUM(ii.thanh_tien) as revenue
FROM invoice_items ii
JOIN products p ON ii.ma_hang = p.ma_hang
GROUP BY ii.ma_hang
ORDER BY revenue DESC LIMIT 10
```

**Success Criteria**:
- ✅ Load in <1 second
- ✅ Sortable columns
- ✅ Drill-down capability

---

### **Feature 4: Top Customers** 👥
**Mục đích**: Xác định khách hàng giá trị cao

**Display**: Table + Ranking

**Specifications**:
- **Metrics**: Customer name, Spending, Purchase count, Last purchase date, Status
- **Rows**: Top 15 customers
- **Status**: VIP / Loyal / At-risk / Inactive (based on RFM)

**Table Columns**:
| # | Tên KH | Tổng chi | Lần mua | Lần cuối mua | Trạng thái |
|---|--------|----------|---------|--------------|-----------|
| 1 | Trần Văn A | 9,500,000 | 28 | 2 ngày trước | 🔴 VIP |
| 2 | Nguyễn Thị B | 8,900,000 | 25 | 5 ngày trước | 🔴 VIP |
| 3 | Lê Văn C | 7,200,000 | 19 | 15 ngày trước | 🟡 Loyal |

**Status Colors**:
- 🔴 **VIP** (High value, frequent, recent)
- 🟡 **Loyal** (Regular buyer, not recent)
- 🟠 **At-risk** (Used to buy, but not recent)
- ⚪ **Inactive** (Haven't bought in 30+ days)

**User Actions**:
- Click customer → View purchase history
- Filter by status
- Send Zalo message (icon next to name)
- Export list

**Data Source**: RFM analysis view + calculation

**Success Criteria**:
- ✅ RFM segmentation accurate
- ✅ Status colors intuitive
- ✅ Click-to-message working

---

### **Feature 5: RFM Segmentation Chart** 📊
**Mục đích**: Visual segmentation of customers (Recency, Frequency, Monetary)

**Display**: 2x2 Matrix + Segment details

**RFM Scores**:
- **R (Recency)**: Days since last purchase (0-90)
- **F (Frequency)**: Number of purchases (0-30)
- **M (Monetary)**: Total spending (0-10M VND)

**Segmentation Matrix**:
```
                 High Frequency    Low Frequency
High Recency     Champions         Potential      ← Recent buyers
                 (Good!)           (Need nurture)

Low Recency      Loyal Customers   Lost Causes    ← Old buyers
                 (At risk!)        (Churn?)
```

**Segments Explained**:
1. **Champions** (Recency: recent, Frequency: high, Monetary: high)
   - Best customers, buy often & recently
   - Action: VIP program, loyalty rewards
   - Count: Usually 10-15% of customers

2. **Potential** (Recency: recent, Frequency: low, Monetary: low/high)
   - New or occasional buyers
   - Action: Nurture with product recommendations
   - Count: Usually 20-30%

3. **Loyal Customers** (Recency: old, Frequency: high, Monetary: high)
   - Used to be champions, but haven't bought recently
   - Action: Win-back campaigns, re-engagement
   - Count: Usually 10-15%

4. **Lost Causes** (Recency: old, Frequency: low, Monetary: low)
   - Inactive customers
   - Action: Might not be worth targeting
   - Count: Usually 30-40%

**Visualization**:
```
┌────────────────────────────────────────┐
│     RFM Segmentation Matrix            │
├────────────────────────────────────────┤
│                                        │
│  Champions (12)    | Potential (28)    │  <- Recent
│  ━━━━━━━━━━━━━━   | ━━━━━━━━━━━━━━   |
│  ████████████████  | ████████████████  │
│                    |                    │
│  Loyal (14)        | Lost (46)         │  <- Old
│  ━━━━━━━━━━━━━━   | ━━━━━━━━━━━━━━   |
│  ████████████████  | ████████████████  │
│                                        │
└────────────────────────────────────────┘
```

**Each Segment Shows**:
- Segment name
- Customer count
- Avg spending
- Avg frequency
- Actions (buttons to send message, view customers)

**User Actions**:
- Click segment → Filter main customer list
- View segment details
- Send Zalo message to segment
- Export segment

**Data Source**: Custom RFM calculation

**Success Criteria**:
- ✅ RFM logic correct
- ✅ Segments balanced
- ✅ Visual intuitive

---

### **Feature 6: Apriori Recommendations** 🎁
**Mục đích**: Market basket analysis - hiện sản phẩm thường mua cùng nhau

**Algorithm**: Apriori (Association Rules Mining)

**Concepts**:
- **Support**: % khách hàng mua cả 2 sản phẩm
- **Confidence**: Nếu mua A, bao nhiêu % mua B?
- **Lift**: A và B mua cùng gấp mấy lần so với độc lập?

**Example Output**:
```
Nếu khách mua [Bánh mì], khả năng mua [Nước ngọt] = 65% ✅
   - Support: 12% khách mua cả 2
   - Confidence: 65% (65% người mua Bánh cũng mua Nước)
   - Lift: 2.3 (gấp 2.3 lần lợi suất)

Nếu khách mua [Thịt tươi], khả năng mua [Gia vị] = 48%
   - Support: 8% khách mua cả 2
   - Confidence: 48%
   - Lift: 1.8
```

**Display**: Table of product pairs

**Table Columns**:
| Product A | Product B | Confidence | Support | Lift | Action |
|-----------|-----------|-----------|---------|------|--------|
| Bánh mì | Nước ngọt | 65% | 12% | 2.3 | 📌 Bundle |
| Thịt tươi | Gia vị | 48% | 8% | 1.8 | 📌 Bundle |
| Mì ăn liền | Đồ uống | 55% | 10% | 1.9 | 📌 Bundle |

**User Actions**:
- Sort by Confidence / Lift
- Click → Create bundle promotion
- Send recommendation to customers
- Filter min/max confidence

**Data Source**: Apriori algorithm on invoice_items

**Success Criteria**:
- ✅ Algorithm efficient (<5 sec computation)
- ✅ Insights actionable
- ✅ Bundle creation easy

---

### **Feature 7: Data Refresh & Status** 🔄
**Mục đích**: Show data freshness + integration status

**Display**: Status bar (bottom of page)

**Shows**:
- Last updated: "Updated 2 minutes ago"
- Kiotviet sync status: "✅ Connected" or "❌ Offline"
- Next refresh: "Next refresh in 3 min"
- Zalo connection: "✅ Active" or "⚠️ Error"

**Refresh Mechanism**:
- Auto-refresh every 5 minutes
- Button to "Refresh now" manually
- Spinner animation while loading

**Success Criteria**:
- ✅ Accurate timestamps
- ✅ Non-blocking refresh
- ✅ Error notifications clear

---

### **Feature 8: Filters & Navigation** 🎚️
**Mục đích**: Quick filtering & navigation

**Global Filters** (top of page):
- **Date range**: Date picker (Today / This week / This month / Custom)
- **Category**: Multi-select (Bánh, Thực phẩm, Uống, Liền, Gia vị, Chăm sóc)
- **View**: Dashboard / Analysis / Reports (tabs)

**Per-Feature Filters**:
- Revenue chart: Granularity (Daily/Weekly/Monthly)
- Top products: Sorting (Revenue/Quantity/Profit), Category
- Top customers: Status (VIP/Loyal/At-risk/Inactive), Sorting
- RFM: Segment selector
- Apriori: Min confidence slider

**Success Criteria**:
- ✅ All filters in one place
- ✅ No page reload needed
- ✅ Filters persist during session

---

### **Feature 9: Export & Reporting** 📥
**Mục đích**: Allow users to export data

**Export Options**:
- **CSV**: For Excel analysis
- **PDF**: For sharing reports
- **Zalo**: Direct send to customer group

**What's Exportable**:
- Top products table
- Top customers list
- RFM segments
- Full customer database

**Success Criteria**:
- ✅ CSV format correct
- ✅ PDF layout professional
- ✅ File naming clear

---

### **Feature 10: Zalo Integration** 💬
**Mục đích**: Send marketing messages to customers

**Workflows**:

**Workflow A: Bulk message to segment**
```
1. Select RFM segment (e.g., Loyal customers)
2. Choose template:
   - "We miss you! Buy now and get 10% off"
   - "Best sellers this week: Bánh mì, Nước"
   - "Your favorites are back in stock"
3. Preview message
4. Send → API call to Zalo → Message delivered ✅
```

**Workflow B: Personalized recommendation**
```
1. Click customer → View purchase history
2. System suggests: "This customer bought [Bánh]. 
   Recommend [Nước ngọt] (65% of people who bought Bánh also buy this)"
3. Generate message: "Hi Anh Hoàng, we think you'll love [Nước ngọt]!"
4. Send via Zalo ✅
```

**Message Templates**:
- Segment-based: "Hi, we have a special offer for you!"
- Product recommendation: "Based on your favorites..."
- Reactivation: "We miss you! Come back and get..."
- Birthday: "Happy birthday! Here's 20% off..."

**Success Criteria**:
- ✅ Message delivered in <10 seconds
- ✅ Delivery confirmation received
- ✅ Template library extensible

---

## 📊 Feature Priority & Timeline

| Priority | Feature | Effort | Phase |
|----------|---------|--------|-------|
| 🔴 P1 | Dashboard Overview | 2 days | MVP |
| 🔴 P1 | Revenue Chart | 2 days | MVP |
| 🔴 P1 | Top Products | 2 days | MVP |
| 🔴 P1 | Top Customers | 2 days | MVP |
| 🔴 P1 | RFM Segmentation | 3 days | MVP |
| 🟡 P2 | Apriori Recommendations | 3 days | MVP |
| 🟡 P2 | Filters & Navigation | 1 day | MVP |
| 🟡 P2 | Data Refresh | 1 day | MVP |
| 🟢 P3 | Export & Reporting | 1 day | Phase 2 |
| 🟢 P3 | Zalo Integration | 2 days | Phase 2 |

**MVP Timeline**: ~16 days (P1 + P2 features)

---

## 🎯 Success Metrics

| Metric | Target | How to Measure |
|--------|--------|---|
| **Load time** | <2 sec | Chrome DevTools |
| **Dashboard refresh** | <5 sec | Manual test |
| **RFM accuracy** | 100% | Validate against manual calc |
| **Apriori insights** | Actionable | Ask manager: "Useful?" |
| **User satisfaction** | >4/5 | Survey |
| **Data freshness** | 5 min max | Check timestamps |

---

## 📝 Notes

- All percentages in VND
- Time zones: Vietnam (UTC+7)
- Mobile responsive required
- Accessibility: Basic (good contrast, readable fonts)
- Browser support: Chrome, Firefox, Safari (latest versions)

