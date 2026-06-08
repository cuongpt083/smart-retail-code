# 🔄 User Flows & Interactions

**Tài liệu này mô tả cách người dùng tương tác với hệ thống**

---

## 🎭 User Flows by Persona

### **FLOW 1: Store Manager - Morning Briefing** ⏰

**Scenario**: Anh Hoàng (Quản lý cửa hàng) vào sáng 8h để check doanh thu hôm qua

```
┌─────────────────────────────────────────────────────────────────┐
│ FLOW: Morning Revenue Check                                    │
└─────────────────────────────────────────────────────────────────┘

START
  ↓
[1] Open Dashboard
  ↓
[2] System loads KPIs (auto-refresh 5 min)
  ├─ 💰 Revenue: 890,000 VND ⬆️ 12% vs yesterday
  ├─ 📦 Orders: 12
  ├─ 👥 Unique customers: 8
  └─ ⭐ Top product: Bánh mì (45 sold)
  ↓
[3] Anh Hoàng thinks: "Good day! But which products made the money?"
  ↓
[4] Click on "Top Products" chart
  ↓
[5] System shows Top 10 products:
    ┌──────────────────────────────────┐
    │ 1. Bánh mì      | 45 | 2M VND    │
    │ 2. Nước ngọt    | 38 | 1.7M VND  │
    │ 3. Mì ăn liền  | 32 | 900K VND  │
    │ ...                              │
    └──────────────────────────────────┘
  ↓
[6] Anh Hoàng decides: "Bánh mì is bestseller, let's promote it"
  ↓
[7] Click "Create Bundle" next to "Bánh mì + Nước ngọt"
  ↓
[8] System opens bundle creation dialog
  ↓
[9] Anh Hoàng sets discount (10% off when buy both)
  ↓
[10] System saves bundle & displays confirmation ✅
  ↓
END
```

**User Actions Needed**:
- ✅ Open dashboard (initial load)
- ✅ Click "Top Products" (navigate)
- ✅ Click "Create Bundle" (action)
- ✅ Fill discount % (input)
- ✅ Click "Save" (confirm)

**System Responses**:
- ✅ Load dashboard in <2 sec
- ✅ Refresh KPIs every 5 min
- ✅ Show Top Products table instantly
- ✅ Save bundle in <1 sec

**Success Outcome**: Bundle created, ready to promote 🎉

---

### **FLOW 2: Marketing Manager - RFM Segmentation** 👥

**Scenario**: Chị Linh (Marketing) wants to send special offer to VIP customers

```
┌─────────────────────────────────────────────────────────────────┐
│ FLOW: Send VIP Campaign via Zalo                               │
└─────────────────────────────────────────────────────────────────┘

START
  ↓
[1] Click "Analyze" tab → See RFM Matrix
  ↓
[2] System shows:
    ┌─────────────────────────────────┐
    │ Champions: 12 customers         │  ← VIP
    │ Potential: 28 customers         │
    │ Loyal: 14 customers             │
    │ Lost: 46 customers              │
    └─────────────────────────────────┘
  ↓
[3] Chị Linh clicks on "Champions" segment
  ↓
[4] System highlights Champions, shows customer list:
    ┌─────────────────────────────────┐
    │ 1. Trần Văn A (9.5M spent)      │ ← Click to message
    │ 2. Nguyễn Thị B (8.9M spent)    │
    │ 3. Lê Văn C (7.2M spent)        │
    │ ... (12 total)                  │
    └─────────────────────────────────┘
  ↓
[5] Chị Linh clicks "Send Zalo to Segment"
  ↓
[6] System opens message composer:
    ┌───────────────────────────────────────┐
    │ Send to: Champions (12 customers)     │
    │                                       │
    │ Template: ▼ [Select message]         │
    │ - "VIP Special Offer"                 │
    │ - "New arrivals just in!"            │
    │ - "Loyalty reward"                    │
    │                                       │
    │ Selected: "VIP Special Offer"         │
    │                                       │
    │ Message preview:                      │
    │ "Dear VIP customer, we have a        │
    │  special 20% off offer just for you" │
    │                                       │
    │ [Preview] [Send]                     │
    └───────────────────────────────────────┘
  ↓
[7] Chị Linh clicks "Send"
  ↓
[8] System shows progress:
    🔄 Sending to 12 customers...
    ✅ Sent to Trần Văn A
    ✅ Sent to Nguyễn Thị B
    ✅ Sent to Lê Văn C
    ...
    ✅ All 12 messages sent!
  ↓
[9] System shows confirmation:
    "Campaign sent successfully! 
     12 messages delivered in 2 seconds"
  ↓
END
```

**User Actions**:
- ✅ Click "Analyze" tab
- ✅ Click "Champions" segment
- ✅ Click "Send Zalo to Segment"
- ✅ Select template
- ✅ Click "Send"

**System Responses**:
- ✅ Show RFM matrix in <1 sec
- ✅ Filter customers by segment instantly
- ✅ Send 12 Zalo messages in <10 sec
- ✅ Show confirmation ✅

**Success Outcome**: 12 VIP customers notified about offer 🎉

---

### **FLOW 3: Sales Staff - Quick Insight (Mobile)** 📱

**Scenario**: Em Lan (Sales staff) checks top products on tablet at counter

```
┌─────────────────────────────────────────────────────────────────┐
│ FLOW: Mobile Quick Check (30 seconds)                           │
└─────────────────────────────────────────────────────────────────┘

START
  ↓
[1] Em Lan opens dashboard on tablet
  ↓
[2] System loads (mobile-optimized, <2 sec)
  ↓
[3] She sees dashboard with big metrics:
    ┌──────────────────┐
    │ 💰 890,000 VND  │  ← Today's revenue
    │ 📦 12 Orders    │  ← Today's orders
    │ ⭐ Bánh mì      │  ← Top product
    └──────────────────┘
  ↓
[4] She scrolls down → Sees Top Products
    ┌──────────────────────────┐
    │ 1. Bánh mì      45 sold  │
    │ 2. Nước ngọt    38 sold  │
    │ 3. Mì ăn liền   32 sold  │
    └──────────────────────────┘
  ↓
[5] Customer asks: "What's the best seller today?"
  ↓
[6] Em Lan points to screen: "Bánh mì! 45 sold"
  ↓
[7] Customer decides to buy Bánh mì
  ↓
END ✅
```

**User Actions**:
- ✅ Open app (initial)
- ✅ Scroll to see products

**System Responses**:
- ✅ Mobile-responsive layout
- ✅ Load in <2 sec
- ✅ Big, readable fonts
- ✅ Minimal data usage

**Success Outcome**: Staff has quick answer for customer 🎉

---

### **FLOW 4: Apriori Recommendation - Create Cross-sell** 🎁

**Scenario**: System discovers that people who buy Bánh mì often buy Nước, suggest bundle

```
┌─────────────────────────────────────────────────────────────────┐
│ FLOW: Create Cross-sell Bundle from Apriori                    │
└─────────────────────────────────────────────────────────────────┘

START
  ↓
[1] Chị Linh clicks "Apriori Recommendations"
  ↓
[2] System shows product pairs:
    ┌────────────────────────────────┐
    │ Bánh mì + Nước ngọt  │ 65%     │ ← If buy A, likely buy B
    │ Thịt tươi + Gia vị   │ 48%     │
    │ Mì ăn liền + Uống    │ 55%     │
    │ ...                             │
    └────────────────────────────────┘
  ↓
[3] Chị Linh sees: "65% who buy Bánh mì also buy Nước"
    She thinks: "Perfect for bundle!"
  ↓
[4] Clicks "📌 Create Bundle" on Bánh mì + Nước
  ↓
[5] System opens bundle editor:
    ┌──────────────────────────────────┐
    │ Bundle Name: Bánh & Drink        │
    │ Product 1: Bánh mì (45K)         │
    │ Product 2: Nước ngọt (45K)       │
    │ Bundle price: 85K (save 5K!)     │
    │ Discount: 5.5%                   │
    │                                  │
    │ [Create] [Cancel]                │
    └──────────────────────────────────┘
  ↓
[6] System creates bundle & shows:
    "Bundle created! 
     When customer buys Bánh, 
     system recommends Nước for bundle"
  ↓
END ✅
```

**User Actions**:
- ✅ Click "Apriori Recommendations"
- ✅ Click "📌 Create Bundle"
- ✅ Confirm settings
- ✅ Click "Create"

**System Responses**:
- ✅ Show recommendations in <2 sec
- ✅ Open bundle editor instantly
- ✅ Save bundle in <1 sec

**Success Outcome**: New bundle ready to promote 🎉

---

## 🔀 Error Handling Flows

### **FLOW 5: Data Not Fresh** ⚠️

**Scenario**: Kiotviet API offline, data not updated

```
┌─────────────────────────────────────────────────────────────────┐
│ FLOW: Handle API Error                                         │
└─────────────────────────────────────────────────────────────────┘

User opens dashboard
  ↓
[Error] System tries to refresh from Kiotviet → Timeout (5 sec)
  ↓
System shows:
┌───────────────────────────────────────────┐
│ ⚠️ Data might be outdated                 │
│ Last sync: 25 minutes ago                  │
│ Kiotviet connection: ❌ Offline            │
│                                           │
│ [Retry] [Use cached data]                 │
└───────────────────────────────────────────┘
  ↓
User clicks [Use cached data]
  ↓
System shows dashboard with cached data
+ Warning badge: "Data from 25 min ago"
  ↓
User can still see insights
  ↓
END (Graceful degradation) ✅
```

**Best Practice**: Never break functionality; use cached data + warning

---

### **FLOW 6: RFM Calculation Failed** 🔴

**Scenario**: RFM calculation has error, can't compute segments

```
┌─────────────────────────────────────────────────────────────────┐
│ FLOW: RFM Calculation Error                                    │
└─────────────────────────────────────────────────────────────────┘

User clicks "RFM Segmentation"
  ↓
[Error] System tries to calculate RFM → SQL error
  ↓
System shows:
┌───────────────────────────────────────────┐
│ ❌ Unable to load RFM data                │
│ Error: Missing customer data              │
│                                           │
│ [Try again] [Contact support]             │
└───────────────────────────────────────────┘
  ↓
User clicks [Try again]
  ↓
System retries calculation
  ↓
If success → Show RFM matrix
If fail → Show contact support info
  ↓
END (Informative error message) ✅
```

**Best Practice**: 
- Clear error message (what went wrong?)
- Action button (Try again)
- Fallback option (Contact support)

---

## 🔁 Data Refresh Flow

**Automatic refresh every 5 minutes**:

```
┌──────────────────────────────────────────┐
│ Data Refresh Cycle (5 minutes)           │
└──────────────────────────────────────────┘

[00:00] Refresh starts
  ├─ Pull from Kiotviet API
  ├─ Update SQLite database
  ├─ Recalculate RFM scores
  └─ Recalculate Apriori rules

[00:02] All data fresh ✅

[00:05] User sees updated dashboard
  └─ "Updated 5 seconds ago"

[05:00] Next refresh cycle starts

...repeat every 5 minutes
```

**Non-blocking**: Users can still interact while refresh happens in background

---

## 📊 Navigation Structure

**Overall app navigation**:

```
┌─────────────────────────────────────────┐
│ 🏠 SMART RETAIL ANALYTICS               │
├─────────────────────────────────────────┤
│                                         │
│ [Dashboard] [Analyze] [Reports]         │  ← Main tabs
│                                         │
├─ Dashboard (default view)               │
│  ├─ 4 KPI cards                         │
│  ├─ Revenue chart                       │
│  ├─ Top products                        │
│  ├─ Top customers                       │
│  └─ Quick stats                         │
│                                         │
├─ Analyze (detailed analysis)            │
│  ├─ RFM Segmentation                    │
│  ├─ Apriori Recommendations             │
│  ├─ Product analysis                    │
│  └─ Customer deep-dive                  │
│                                         │
├─ Reports (export & download)            │
│  ├─ Export to CSV                       │
│  ├─ Export to PDF                       │
│  └─ Send via Zalo                       │
│                                         │
└─ [Settings] [Help] [Logout] (top-right)│
```

---

## 🎨 Interaction Patterns

### **Pattern 1: Chart Exploration**
- Hover over chart → Show tooltip
- Click data point → Drill down to details
- Click legend → Toggle series on/off

### **Pattern 2: Table Operations**
- Click column header → Sort by that column
- Click row → Show details
- Multi-select → Bulk action

### **Pattern 3: Segmentation**
- Click segment → Filter related data
- Click action button → Perform action (send message)
- Preview before action

### **Pattern 4: Messaging**
- Select template → Preview → Send
- Show progress → Show confirmation
- Allow retry on failure

---

## ⌨️ Keyboard Shortcuts (Optional)

For power users, consider:

| Key | Action |
|-----|--------|
| `R` | Refresh data |
| `D` | Go to Dashboard |
| `A` | Go to Analyze |
| `S` | Open Segment menu |
| `Z` | Send Zalo |
| `?` | Show help |

---

## 📱 Mobile Considerations

**Mobile-specific flows**:

1. **Swipe between tabs** (instead of click)
2. **Larger touch targets** (buttons 48x48px minimum)
3. **Simplified menus** (dropdown → hamburger menu)
4. **Vertical layout** (charts stack vertically)
5. **Mobile keyboard** (number input uses numeric keyboard)

**Mobile viewport**: 320px - 480px width

---

## 🎯 Success Criteria for User Flows

- ✅ Each flow completes in <5 minutes (or faster)
- ✅ Minimum clicks to accomplish goal
- ✅ Clear feedback at each step
- ✅ Error handling graceful
- ✅ Mobile responsive
- ✅ Accessible (keyboard navigation, screen readers)

