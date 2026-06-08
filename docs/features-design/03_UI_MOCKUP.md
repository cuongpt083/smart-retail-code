# 🎨 UI Mockup & Wireframes

**Giao diện dashboard thiết kế cho Smart Retail Analytics**

---

## 📐 Layout Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  🏠 SMART RETAIL ANALYTICS          [🔔] [⚙️] [👤] [🚪]            │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│ [Dashboard] [Analyze] [Reports]    Filter: 📅 Today  🏷️ All       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐        │
│  │ 💰 Revenue  │ 📦 Orders   │ 👥 Customers│ ⭐ Top Prod │        │
│  │ 890,000 VND │ 12          │ 8           │ Bánh mì    │        │
│  │ ⬆️ 12%     │ ⬆️ 8%       │ ⬇️ 3%       │ 45 sold    │        │
│  └─────────────┴─────────────┴─────────────┴─────────────┘        │
│                                                                     │
│  ┌──────────────────────────────────┐  ┌────────────────────┐   │
│  │                                  │  │ TOP PRODUCTS       │   │
│  │    REVENUE TREND (7 days)        │  │ (This week)        │   │
│  │                                  │  │                    │   │
│  │        📈                        │  │ 1. Bánh mì   2.0M  │   │
│  │                                  │  │ 2. Nước      1.7M  │   │
│  │      ┌─────────────────┐         │  │ 3. Mì ăn   900K    │   │
│  │      │ ▂▄▆█▄▂▅▃▆▂     │ VND     │  │ 4. Trứng   750K    │   │
│  │      │                 │ 2.5M    │  │ 5. Gia vị  650K    │   │
│  │      │                 │ 2.0M    │  │                    │   │
│  │      │                 │ 1.5M    │  │                    │   │
│  │      │                 │ 1.0M    │  │                    │   │
│  │      │                 │ 0       │  │                    │   │
│  │      └─────────────────┘         │  │                    │   │
│  │   Mon Tue Wed Thu Fri Sat Sun    │  └────────────────────┘   │
│  └──────────────────────────────────┘                             │
│                                                                     │
│  ┌──────────────────────────────────┐  ┌────────────────────┐   │
│  │ TOP CUSTOMERS (This week)        │  │ RFM SEGMENTATION   │   │
│  │                                  │  │                    │   │
│  │ 1. Trần Văn A - 5.5M - 🔴VIP    │  │ Champions:   12 👤 │   │
│  │ 2. Nguyễn Thị B - 4.2M - 🔴VIP  │  │ Potential:   28 👤 │   │
│  │ 3. Lê Văn C - 3.8M - 🟡Loyal    │  │ Loyal:       14 👤 │   │
│  │ 4. Phạm Thị D - 2.1M - 🟡Loyal  │  │ Lost:        46 👤 │   │
│  │ 5. Trần Văn E - 1.9M - 🟠AtRisk │  │                    │   │
│  │ ...                              │  │                    │   │
│  └──────────────────────────────────┘  └────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ ✅ Data updated 2 minutes ago | 🔄 Next refresh in 3 min   │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📱 Desktop Layout (Full View - 1920x1080)

### **Section 1: Header & Navigation**

```
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│ 🏢 SMART RETAIL ANALYTICS    v1.0        [🔔 3] [⚙️] [👤 Admin]  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

**Components**:
- **Logo**: Smart Retail logo (left)
- **Title**: "Smart Retail Analytics" (center-left)
- **Notifications**: Bell icon with badge (right)
- **Settings**: Gear icon (right)
- **User**: Profile icon + "Admin" text (right)

**Color scheme**:
- Background: #F5F7FA (light gray)
- Text: #2C3E50 (dark blue)
- Accent: #00BCD4 (cyan)

---

### **Section 2: Main Tabs & Filters**

```
┌────────────────────────────────────────────────────────────────────┐
│ [Dashboard] [Analyze] [Reports]  |  📅 Today ▼  🏷️ All Categories ▼ │
│                                                                    │
│ • Dashboard (active) | Analyze | Reports                         │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

**Tabs**:
1. **Dashboard** (default, shows KPIs + charts)
2. **Analyze** (RFM, Apriori details)
3. **Reports** (Export, Zalo send)

**Filters**:
- Date range dropdown (Today / Week / Month / Custom)
- Category multi-select

---

### **Section 3: KPI Cards (4 columns)**

```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ 💰 REVENUE      │ 📦 ORDERS       │ 👥 CUSTOMERS    │ ⭐ TOP PRODUCT  │
│                 │                 │                 │                 │
│ 890,000 VND     │ 12              │ 8               │ Bánh mì         │
│ ⬆️ 12%         │ ⬆️ 8%           │ ⬇️ 3%           │ 45 sold         │
│ vs yesterday    │ vs yesterday    │ vs yesterday    │ this period     │
│                 │                 │                 │                 │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

**Each card contains**:
- Icon (emoji or SVG)
- Metric name
- Current value
- Trend (↑/↓ + percentage)
- Comparison text
- Background color: White
- Border: Light gray
- Icon color: Blue (#00BCD4)

**Responsive**: On tablet (4 → 2 columns), on mobile (4 → 1 column)

---

### **Section 4: Revenue Trend Chart**

```
┌──────────────────────────────────────────────────────────────────┐
│ 📈 REVENUE TREND                        [Daily ▼] [📊] [💾]      │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│     VND                                                          │
│  3.0M  ┌────┐                                                   │
│  2.5M  │    └────┬────┐                                         │
│  2.0M  │         │    └────┬──┐                                 │
│  1.5M  │    ▁▂▃▄▅▆▅▄▃▂▁▂▃▄▅▆▇█▅▄▃▂   ← Smooth curve            │
│  1.0M  │                                                        │
│  0.5M  │                                                        │
│  0     └──────────────────────────────────────────────────────  │
│        Mar 9   Mar 16  Mar 23  Mar 30  Apr 6   Apr 13  ... Jun 7│
│                                                                  │
│   Legend: ─ Revenue (fill area below = light blue)             │
│                                                                  │
│   Tooltip on hover: "Mar 15: 2,450,000 VND"                    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Chart specifications**:
- Type: Area chart (line + filled area)
- X-axis: Dates (09-03 to 07-06, 90 days)
- Y-axis: Revenue (VND, auto-scale)
- Grid: Horizontal lines for readability
- Colors:
  - Line: #00BCD4 (cyan)
  - Area fill: #00BCD4 20% (light cyan)
- Interactive:
  - Hover: Tooltip shows date + revenue
  - Click: Drill down to daily view
  - Zoom: Drag to zoom into date range

**Tools** (top-right):
- Granularity selector: Daily / Weekly / Monthly
- Fullscreen icon
- Export icon (PNG)

---

### **Section 5: Top Products Table**

```
┌──────────────────────────────────────────────────────────────────┐
│ 🏆 TOP PRODUCTS (This week)             [Profit ▼] [📊] [💾]     │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ # │ Sản phẩm              │ Qty │ Doanh thu │ Lợi nhuận │ % |  │
│───┼───────────────────────┼─────┼───────────┼───────────┼──── │
│ 1 │ Bánh mì Snack         │ 45  │ 2,025,000 │ 677,500   │ 8.2%│
│ 2 │ Nước ngọt 1.5L        │ 38  │ 1,710,000 │ 513,000   │ 7.1%│
│ 3 │ Mì ăn liền Acecook   │ 32  │   896,000 │ 268,800   │ 5.9%│
│ 4 │ Trứng gà tươi (30)   │ 28  │ 1,400,000 │ 280,000   │ 5.8%│
│ 5 │ Gia vị Knorr         │ 24  │   720,000 │ 216,000   │ 4.7%│
│ 6 │ Dầu ăn 1L            │ 19  │   570,000 │ 114,000   │ 3.7%│
│ 7 │ Xà phòng Lifebuoy     │ 18  │   540,000 │ 162,000   │ 3.5%│
│ 8 │ Cơm hộp Vissan        │ 16  │   432,000 │ 129,600   │ 2.8%│
│ 9 │ Bánh quy Oreo         │ 14  │   560,000 │ 168,000   │ 2.9%│
│10 │ Kẹo Daimin           │ 12  │   480,000 │ 144,000   │ 2.5%│
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Table features**:
- **Sorting**: Click column header to sort (up/down arrows)
- **Filtering**: Filter by category dropdown
- **Colors**: Alternating row colors (white / light gray)
- **Highlighting**: Top row has slightly darker background
- **Percentage bars**: Visual indicator (small bar next to %)
- **Hover**: Row highlights on hover
- **Mobile**: Horizontal scroll on mobile view

**Column specs**:
- #: Index (1-10)
- Sản phẩm: Product name (clickable → details)
- Qty: Quantity sold (integer)
- Doanh thu: Revenue (formatted with commas)
- Lợi nhuận: Profit (formatted with commas)
- %: Percentage of total revenue (with small bar)

---

### **Section 6: Top Customers List**

```
┌──────────────────────────────────────────────────────────────────┐
│ 👥 TOP CUSTOMERS (This week)           [Spending ▼] [📊] [💾]    │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ # │ Khách hàng        │ Tổng chi  │ Lần mua │ Lần cuối│ Status │
│───┼──────────────────┼───────────┼────────┼────────┼──────── │
│ 1 │ Trần Văn A       │ 5,500,000 │ 28     │ 2 ngày │ 🔴VIP  │
│ 2 │ Nguyễn Thị B     │ 4,200,000 │ 22     │ 7 ngày │ 🔴VIP  │
│ 3 │ Lê Văn C         │ 3,800,000 │ 19     │ 12ngày │ 🟡Loyal│
│ 4 │ Phạm Thị D       │ 2,100,000 │ 14     │ 21ngày │ 🟡Loyal│
│ 5 │ Vũ Minh E        │ 1,900,000 │  8     │ 30ngày │🟠AtRisk│
│ ... (more rows)                                                │
│15 │ Trần Thị O       │   950,000 │  5     │ 45ngày │🟠AtRisk│
│                                                                  │
│                       [Send Zalo] [View Details] [Export]      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Status colors**:
- 🔴 **VIP** (Red): High value + frequent + recent
- 🟡 **Loyal** (Yellow): Regular but not recent
- 🟠 **At-risk** (Orange): Used to be regular, now distant
- ⚪ **Inactive** (Gray): Haven't bought in 30+ days

**Actions**:
- Click row → View customer purchase history
- Click 💬 icon → Send Zalo message
- Select multiple rows → Bulk action (send campaign)

---

### **Section 7: RFM Segmentation Matrix**

```
┌──────────────────────────────────────────────────────────────────┐
│ 📊 RFM SEGMENTATION                    [Details ▼] [🎯] [💾]     │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │               HIGH RECENCY (Recent buyers)              │   │
│  │                                                         │   │
│  │  Champions          │          Potential              │   │
│  │  (12 customers)     │        (28 customers)           │   │
│  │  Avg: 7.5M/person  │        Avg: 1.2M/person         │   │
│  │  [View] [Message]  │        [View] [Message]          │   │
│  │  ─────────────────────────────────────────────────────│   │
│  │                                                         │   │
│  │  Loyal Customers    │          Lost Causes            │   │
│  │  (14 customers)     │        (46 customers)           │   │
│  │  Avg: 5.8M/person  │        Avg: 0.8M/person         │   │
│  │  [View] [Message]  │        [View] [Message]          │   │
│  │                                                         │   │
│  │               LOW RECENCY (Old buyers)                │   │
│  └─────────────────────────────────────────────────────────┘   │
│        ← LOW FREQUENCY          HIGH FREQUENCY →               │
│                                                                  │
│  Segment Metrics:                                              │
│  • Champions: R=5d avg, F=16 purchases, M=7.5M avg           │
│  • Potential: R=2d avg, F=2 purchases, M=1.2M avg            │
│  • Loyal: R=25d avg, F=15 purchases, M=5.8M avg              │
│  • Lost: R=45d avg, F=2 purchases, M=0.8M avg                │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Interactive**:
- Click segment box → Filter customer list to show that segment
- View button → See detailed list
- Message button → Open Zalo composer for that segment
- Hover → Show tooltip with segment description

---

### **Section 8: Apriori Recommendations**

```
┌──────────────────────────────────────────────────────────────────┐
│ 🎁 APRIORI RECOMMENDATIONS (Product pairs)    [Min Conf: 40% ▼]  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Product A         + Product B         │ Conf │ Support│ Lift   │
│───────────────────────────────────────┼──────┼────────┼────── │
│ Bánh mì           + Nước ngọt        │ 65%  │ 12%    │ 2.3   │
│ [Bundle]          [Message]                                    │
│                                                                  │
│ Thịt tươi         + Gia vị Knorr     │ 48%  │  8%    │ 1.8   │
│ [Bundle]          [Message]                                    │
│                                                                  │
│ Mì ăn liền        + Nước ngọt        │ 55%  │ 10%    │ 1.9   │
│ [Bundle]          [Message]                                    │
│                                                                  │
│ Rau xanh          + Dầu ăn           │ 42%  │  7%    │ 1.6   │
│ [Bundle]          [Message]                                    │
│                                                                  │
│ Trứng tươi        + Bánh mì          │ 38%  │  6%    │ 1.4   │
│ [Bundle]          [Message]                                    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Meanings**:
- **Confidence (Conf)**: If customer buys A, % chance they also buy B
- **Support**: % of all customers who buy both A and B
- **Lift**: How much more likely A and B are bought together vs separately

**Actions**:
- [Bundle]: Create promotional bundle from pair
- [Message]: Send recommendation message to customers who bought A

---

### **Section 9: Footer - Data Refresh Status**

```
┌──────────────────────────────────────────────────────────────────┐
│ ✅ Data updated 2 minutes ago           🔄 Next refresh: 3 min   │
│                                                                  │
│ Kiotviet: ✅ Connected  |  Zalo: ✅ Active  |  Database: ✅ OK   │
└──────────────────────────────────────────────────────────────────┘
```

**Status indicators**:
- ✅ Green: Connected/Active
- ⚠️ Yellow: Degraded/Slow
- ❌ Red: Error/Offline
- 🔄 Spinner: Loading/Syncing

---

## 📱 Mobile Layout (375px width)

### **Mobile Dashboard** (stacked vertical)

```
┌─────────────────────────────────────┐
│ 🏠 Smart Retail (Mobile)   [☰]     │
├─────────────────────────────────────┤
│                                     │
│ [Dashboard][Analyze][Reports]      │
│                                     │
│ 💰 Revenue: 890K VND ⬆️ 12%        │
│                                     │
│ 📦 Orders: 12 ⬆️ 8%                 │
│                                     │
│ 👥 Customers: 8 ⬇️ 3%               │
│                                     │
│ ⭐ Top: Bánh mì (45)               │
│                                     │
├─────────────────────────────────────┤
│ 📈 REVENUE TREND                    │
│                                     │
│   ▁▂▃▄▅▆▇█▅▄▃▂▁▂▃                  │
│                                     │
│   [Swipe left for older days]      │
│                                     │
├─────────────────────────────────────┤
│ 🏆 TOP PRODUCTS (5 shown)           │
│                                     │
│ 1. Bánh mì ......... 2,025,000 VND  │
│ 2. Nước ............ 1,710,000 VND  │
│ 3. Mì ăn liền ..... 896,000 VND     │
│ 4. Trứng ........... 1,400,000 VND  │
│ 5. Gia vị .......... 720,000 VND    │
│                                     │
│ [More products →]                  │
│                                     │
├─────────────────────────────────────┤
│ 👥 TOP CUSTOMERS (5 shown)          │
│                                     │
│ 1. Trần Văn A 🔴VIP ... 5.5M       │
│ 2. Nguyễn B 🔴VIP .... 4.2M        │
│ 3. Lê Văn C 🟡Loyal ... 3.8M       │
│ 4. Phạm Thị D 🟡Loyal  2.1M        │
│ 5. Vũ Minh E 🟠AtRisk  1.9M        │
│                                     │
│ [💬 View all →]                    │
│                                     │
├─────────────────────────────────────┤
│ ✅ Updated 2 min ago | 🔄 3 min    │
│                                     │
└─────────────────────────────────────┘
```

**Mobile features**:
- Hamburger menu (☰) for navigation
- Single column layout
- Larger touch targets (44x44px)
- Swipe gestures for chart navigation
- Simplified tables (show top 5, link to view all)
- Scroll down for more content

---

## 🎨 Design System

### **Colors**

```
Primary:      #00BCD4 (Cyan)
Secondary:    #2C3E50 (Dark Blue)
Success:      #4CAF50 (Green)
Warning:      #FFC107 (Amber)
Error:        #F44336 (Red)
Background:   #F5F7FA (Light Gray)
Border:       #BDBDBD (Gray)
Text Primary: #2C3E50 (Dark Blue)
Text Secondary: #757575 (Medium Gray)
```

### **Typography**

```
Heading 1 (H1):   28px, Bold, #2C3E50
Heading 2 (H2):   22px, Bold, #2C3E50
Heading 3 (H3):   18px, Bold, #2C3E50
Body:             14px, Regular, #2C3E50
Small:            12px, Regular, #757575
Label:            12px, Medium, #2C3E50
```

### **Components**

```
Buttons:
  Primary: Blue (#00BCD4), 12px padding, 4px radius
  Secondary: Gray (#BDBDBD), 12px padding, 4px radius
  
Cards:
  Background: White (#FFFFFF)
  Border: 1px solid #BDBDBD
  Shadow: 0 2px 4px rgba(0,0,0,0.1)
  Padding: 16px
  
Inputs:
  Border: 1px solid #BDBDBD
  Focus: 2px solid #00BCD4
  Padding: 8px 12px
  
```

### **Spacing**

```
XS: 4px
S:  8px
M:  16px
L:  24px
XL: 32px
```

---

## 🔄 Component Interactions

### **Dropdown/Select**

```
Closed:  [Today ▼]
Open:    ╔═══════════════╗
         ║ Today         ║  ← Selected
         ║ This week     ║
         ║ This month    ║
         ║ Custom range  ║
         ╚═══════════════╝
```

### **Modal Dialog (Zalo Send)**

```
┌──────────────────────────────────────────┐
│ 📤 Send Message via Zalo         [✕]    │
├──────────────────────────────────────────┤
│                                          │
│ Send to: Champions (12 customers)        │
│                                          │
│ Template: [Select template ▼]            │
│  • VIP Special Offer                     │
│  • New arrivals                          │
│  • Loyalty reward                        │
│  • Custom message                        │
│                                          │
│ Message preview:                         │
│ ┌──────────────────────────────────────┐ │
│ │ Dear VIP customer, we have a         │ │
│ │ special 20% off offer just for you!  │ │
│ │ Don't miss out! 🎁                   │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ [Preview] [Send] [Cancel]                │
│                                          │
└──────────────────────────────────────────┘
```

---

## ✨ Visual Hierarchy

1. **Most Important**: KPI cards (largest, brightest colors)
2. **Important**: Charts (revenue, top products)
3. **Reference**: Tables (detailed data)
4. **Secondary**: Filters, buttons
5. **Least Important**: Timestamps, metadata

---

## 📐 Responsive Breakpoints

```
Desktop:  1920px+ (all features)
Tablet:   768px - 1024px (2-column layout)
Mobile:   320px - 767px (1-column, optimized)
```

---

## ⌨️ Accessibility

- ✅ Color contrast ratio ≥ 4.5:1 (WCAG AA)
- ✅ Font size ≥ 14px (readable)
- ✅ Touch targets ≥ 44x44px (mobile)
- ✅ Alt text for images/icons
- ✅ Keyboard navigation (Tab, Enter, Arrow keys)
- ✅ Screen reader support (ARIA labels)

---

## 🎬 Animation & Transitions

**Smooth animations** (avoid flashing):
- Chart updates: 500ms fade-in
- Modal open: 300ms slide-in from top
- Button hover: 200ms color change
- Data refresh: Pulse effect on updated values

---

## 📸 Mockup Tools Recommendation

To create actual mockups:
- **Figma** (free, collaborative)
- **Draw.io** (free, simple)
- **Balsamiq** (paid, wireframe-focused)
- **Adobe XD** (paid, professional)

---

**Next step**: Developers use these wireframes to build Streamlit components! 🚀

