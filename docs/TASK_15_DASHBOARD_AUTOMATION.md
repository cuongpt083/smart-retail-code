# 📱 Task #15: Add Zalo Campaign Automation to Dashboards

**Task ID**: #15  
**Status**: Pending  
**Effort**: 16 hours  
**Priority**: HIGH (User-facing feature)  
**Owner**: Development Team  
**Start Date**: June 10, 2026  
**Target Completion**: June 11, 2026

---

## 🎯 Objective

Enable Marketing Managers to **send Zalo campaigns to RFM customer segments** directly from Streamlit dashboard with:
- One-click campaign sending
- Message preview before sending
- Campaign history & tracking
- Success notifications
- Delivery status monitoring

---

## 📋 Requirements

### Functional Requirements
1. **Campaign Sending**
   - Send to Champions segment with 1 click
   - Send to Potential segment with 1 click
   - Send to Loyal segment with 1 click
   - Send to Lost segment with 1 click
   - Show loading state during send

2. **Message Preview**
   - Display formatted message before sending
   - Show with sample customer data
   - Allow message editing (optional)
   - Show delivery status per customer

3. **Campaign History**
   - Table showing past campaigns
   - Columns: Date, Segment, Count, Success Rate, Status
   - Filter by date range
   - Filter by segment
   - Click to view details

4. **Notifications**
   - Success: "✅ Sent to 50 customers"
   - Error: "❌ Failed to send: Invalid phone"
   - Info: "📊 Campaign history: 95% success"

### Non-Functional Requirements
- Performance: Campaign send < 30 seconds for 100 customers
- Reliability: Retry failed messages automatically
- Security: Don't log customer phone numbers
- UX: Clear, intuitive interface
- Accessibility: Works on mobile view

---

## 🏗️ Architecture & Design

### Current State
```
Marketing Dashboard (app.py)
├── RFM Segmentation Matrix
│   ├── Champions display
│   ├── Potential display
│   ├── Loyal display
│   └── Lost display
├── Top Customers by Segment
└── Segment Statistics
```

### New State
```
Marketing Dashboard (app.py)
├── RFM Segmentation Matrix
│   ├── Champions display
│   │   ├── [Send Zalo to Champions] ← NEW BUTTON
│   │   └── Campaign info
│   ├── Potential display
│   │   ├── [Send Zalo to Potential]
│   │   └── Campaign info
│   ├── Loyal display
│   │   ├── [Send Zalo to Loyal]
│   │   └── Campaign info
│   └── Lost display
│       ├── [Send Zalo to Lost]
│       └── Campaign info
├── Campaign Template Selector ← NEW SECTION
│   └── Radio buttons for templates
├── Message Preview ← NEW SECTION
│   └── Formatted message display
├── Top Customers by Segment
├── Segment Statistics
└── Campaign History ← NEW TAB
    └── Table of past campaigns
```

### Component Flow
```
User clicks "Send Zalo" button
    ↓
Template selector appears
    ↓
Message preview shows
    ↓
User clicks "Send Campaign"
    ↓
API call to zalo_messenger.send_segment_campaign()
    ↓
Progress bar shows (optional)
    ↓
Results displayed:
  - Success: "✅ Sent to X customers"
  - Errors: "❌ Failed: Y messages"
  - History updated
```

---

## 💻 Implementation Details

### Step 1: Campaign Template Selector (Hours 0-2)

**Location**: `app.py` - Marketing Manager Dashboard section

```python
elif role == "Marketing Manager":
    st.title("👥 Marketing Dashboard - Customer Segmentation")
    
    # ... existing RFM matrix code ...
    
    st.divider()
    st.subheader("📧 Campaign Settings")
    
    # Template selector
    campaign_template = st.radio(
        "Select message template:",
        options=[
            "Default VIP Rewards (Champions)",
            "New Product Announcement (Potential)",
            "Win-Back Campaign (Loyal)",
            "Reactivation Offer (Lost)",
            "Custom Message"
        ],
        help="Choose pre-built template or write custom message"
    )
    
    # If custom, show text editor
    if campaign_template == "Custom Message":
        custom_message = st.text_area(
            "Write your message:",
            height=150,
            placeholder="Your message here..."
        )
```

**Tests**:
- ✅ Radio button options displayed
- ✅ All 5 templates available
- ✅ Custom message editor works
- ✅ Template selection persists

---

### Step 2: Message Preview Component (Hours 2-5)

**Location**: `app.py` - After template selector

```python
st.divider()
st.subheader("👁️ Message Preview")

# Load template or custom message
if campaign_template == "Custom Message":
    preview_message = custom_message
else:
    # Get template from zalo_messenger
    template_key = {
        "Default VIP Rewards (Champions)": "CHAMPIONS",
        "New Product Announcement (Potential)": "POTENTIAL",
        "Win-Back Campaign (Loyal)": "LOYAL",
        "Reactivation Offer (Lost)": "LOST"
    }[campaign_template]
    
    # Format with sample customer
    preview_message = format_template(
        template_key,
        customer_name="Nguyễn Văn A",
        recommendations=["Bánh mì", "Nước", "Gia vị"]
    )

# Show preview in box
st.info(f"""
📱 **Message Preview**

{preview_message}

---
*This preview shows how message appears to customer*
""")

# Show segment selector
segment_col, count_col = st.columns(2)
with segment_col:
    target_segment = st.selectbox(
        "Send to segment:",
        ["Champions", "Potential", "Loyal", "Lost"]
    )

with count_col:
    segment_data = rfm_data[rfm_data['rfm_segment'] == target_segment]
    count = len(segment_data)
    st.metric("Customers in segment", count)
```

**Tests**:
- ✅ Preview shows correct message
- ✅ Customer name replaced
- ✅ Recommendations formatted
- ✅ Segment count accurate
- ✅ Custom message preview works

---

### Step 3: Campaign Send Button & Logic (Hours 5-8)

**Location**: `app.py` - After preview

```python
st.divider()
st.subheader("🚀 Send Campaign")

send_col1, send_col2, send_col3 = st.columns(3)

with send_col1:
    if st.button("📤 Send Campaign", use_container_width=True, key="send_campaign"):
        # Validation
        if not target_segment:
            st.error("❌ Please select a segment")
        elif not preview_message:
            st.error("❌ Message is empty")
        else:
            # Show progress
            with st.spinner("Sending campaign..."):
                # Get customers in segment
                segment_customers = rfm_data[
                    rfm_data['rfm_segment'] == target_segment
                ][['ma_khach_hang', 'ten_khach_hang', 'dien_thoai']].to_dict('records')
                
                # Initialize Zalo messenger
                access_token = os.getenv("ZALO_ACCESS_TOKEN")
                messenger = ZaloMessenger(access_token)
                
                # Send campaign
                try:
                    result = messenger.send_segment_campaign(
                        segment=SegmentType[target_segment.upper()],
                        customers=segment_customers,
                        recommendations=extract_products(target_segment)
                    )
                    
                    # Track in database
                    campaign_id = f"camp_{datetime.now().isoformat()}"
                    messenger.track_campaign(
                        campaign_id=campaign_id,
                        segment=target_segment,
                        sent_count=result['sent'],
                        success_count=result['sent'] - result['failed']
                    )
                    
                    # Show results
                    st.success(f"""
✅ **Campaign Sent Successfully!**

📊 Results:
- Sent to: **{result['sent']} customers**
- Failed: **{result['failed']} messages**
- Success rate: **{100 * result['sent'] / (result['sent'] + result['failed']) if (result['sent'] + result['failed']) > 0 else 0:.0f}%**

Campaign ID: `{campaign_id}`
                    """)
                    
                    # Refresh campaign history
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error sending campaign: {e}")
                    logger.error(f"Campaign send failed: {e}")

with send_col2:
    if st.button("👁️ Preview Only", use_container_width=True):
        st.info("✅ Message preview displayed above")

with send_col3:
    if st.button("📊 Campaign History", use_container_width=True):
        st.session_state.show_history = True
```

**Error Handling**:
```python
try:
    result = messenger.send_segment_campaign(...)
except ConnectionError:
    st.error("❌ Connection failed - check internet & API credentials")
except ValueError:
    st.error("❌ Invalid message format")
except Exception as e:
    st.error(f"❌ Unexpected error: {str(e)[:100]}")
    logger.exception("Campaign send error", exc_info=True)
```

**Tests**:
- ✅ Button triggers send
- ✅ Validation works (no empty segment/message)
- ✅ Progress spinner shows
- ✅ Success message displayed
- ✅ Campaign tracked in database
- ✅ Error handling works
- ✅ Failed sends show errors

---

### Step 4: Campaign History View (Hours 8-11)

**Location**: `app.py` - New tab or section

```python
st.divider()
st.subheader("📜 Campaign History")

# Get campaign stats
messenger = ZaloMessenger(os.getenv("ZALO_ACCESS_TOKEN"))
campaign_stats = messenger.get_campaign_stats()

if campaign_stats:
    # Convert to DataFrame for nice display
    df = pd.DataFrame([
        {
            "Date": stat['sent_at'][:10],  # YYYY-MM-DD
            "Segment": stat['segment'],
            "Sent": stat['sent_count'],
            "Success": stat['success_count'],
            "Failed": stat['sent_count'] - stat['success_count'],
            "Success Rate": f"{stat['success_rate']:.0%}"
        }
        for stat in campaign_stats
    ])
    
    # Display with formatting
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "Success Rate": st.column_config.ProgressColumn(
                min_value=0,
                max_value=1
            )
        }
    )
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        date_range = st.date_input("Date range:", value=[df['Date'].min(), df['Date'].max()])
    with col2:
        segment_filter = st.multiselect("Segment:", df['Segment'].unique(), default=df['Segment'].unique())
    with col3:
        min_success = st.slider("Min success rate:", 0, 100, 0)
    
    # Apply filters
    df_filtered = df[
        (df['Date'] >= date_range[0].isoformat()) &
        (df['Date'] <= date_range[1].isoformat()) &
        (df['Segment'].isin(segment_filter)) &
        (df['Success Rate'].str.rstrip('%').astype(float) >= min_success)
    ]
    
    st.dataframe(df_filtered, use_container_width=True)
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Campaigns", len(df_filtered))
    with col2:
        st.metric("Total Sent", df_filtered['Sent'].sum())
    with col3:
        st.metric("Total Success", df_filtered['Success'].sum())
    with col4:
        avg_success = (df_filtered['Success'].sum() / df_filtered['Sent'].sum() * 100) if df_filtered['Sent'].sum() > 0 else 0
        st.metric("Avg Success Rate", f"{avg_success:.0f}%")
        
else:
    st.info("📭 No campaigns sent yet. Send your first campaign above!")
```

**Tests**:
- ✅ Campaign history table displays
- ✅ Date filtering works
- ✅ Segment filtering works
- ✅ Success rate filtering works
- ✅ Statistics calculated correctly
- ✅ Empty state message shows
- ✅ Sorts by date (most recent first)

---

### Step 5: Delivery Tracking & Status (Hours 11-13)

**Location**: In campaign history or new "Campaign Details" modal

```python
# Expandable campaign details
with st.expander(f"📊 Campaign Details - {campaign['Date']} ({campaign['Segment']})"):
    # Get detailed delivery status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Messages Sent", campaign['Sent'])
    with col2:
        st.metric("Delivered", campaign['Success'])
    with col3:
        st.metric("Failed", campaign['Failed'])
    
    # Delivery status breakdown
    status_data = {
        "Delivered": campaign['Success'],
        "Failed": campaign['Failed'],
        "Pending": 0  # Could add if tracking ongoing sends
    }
    
    st.bar_chart(status_data)
    
    # Option to retry failed messages
    if campaign['Failed'] > 0:
        if st.button("🔄 Retry Failed Messages", key=f"retry_{campaign['campaign_id']}"):
            st.info("⏳ Retrying failed messages...")
            # Logic to retry
            st.success("✅ Retried 5 failed messages")
```

**Tests**:
- ✅ Campaign details expandable
- ✅ Delivery breakdown shows
- ✅ Retry button works
- ✅ Failed messages retried

---

### Step 6: Integration with Existing Code (Hours 13-15)

**Changes to existing code**:

1. **Import statements** (top of app.py):
```python
from zalo_messenger import ZaloMessenger, SegmentType
from datetime import datetime
import os
```

2. **Helper function** (add to app.py):
```python
def extract_products(segment: str) -> List[str]:
    """Get product recommendations for segment"""
    if segment == "Champions":
        return ["Premium Product A", "Exclusive Service B"]
    elif segment == "Potential":
        return ["Popular Product X", "Trending Product Y"]
    elif segment == "Loyal":
        return ["Your Favorites", "New Arrivals"]
    else:  # Lost
        return ["Best Sellers", "Limited Time Offer"]
```

3. **Environment setup** (in app.py or .env):
```python
access_token = os.getenv("ZALO_ACCESS_TOKEN")
if not access_token:
    st.warning("⚠️ Zalo access token not configured")
```

**Tests**:
- ✅ Imports work
- ✅ Helper functions work
- ✅ Environment variables loaded
- ✅ Error handling for missing config

---

### Step 7: Testing & QA (Hours 15-16)

#### Unit Tests
```python
# tests/test_dashboard_zalo.py

def test_template_selector_displayed():
    """Test template selector radio button"""
    # Verify all 5 options available
    templates = [
        "Default VIP Rewards (Champions)",
        "New Product Announcement (Potential)",
        "Win-Back Campaign (Loyal)",
        "Reactivation Offer (Lost)",
        "Custom Message"
    ]
    # Assert in rendered dashboard

def test_message_preview_formatting():
    """Test message preview with variables"""
    message = "Hello {customer_name}!"
    formatted = message.format(customer_name="Nguyễn Văn A")
    assert formatted == "Hello Nguyễn Văn A!"

def test_segment_customer_count_accurate():
    """Test segment count matches data"""
    champions = rfm_data[rfm_data['rfm_segment'] == 'Champions']
    assert len(champions) > 0
```

#### Integration Tests
```python
def test_send_campaign_success():
    """Test full campaign send flow"""
    # Mock Zalo API
    # Call send_segment_campaign()
    # Verify result
    # Check campaign tracked

def test_send_campaign_with_errors():
    """Test error handling during send"""
    # Mock API to return some failures
    # Verify error message shown
    # Verify history includes failures

def test_campaign_history_display():
    """Test history loads and filters"""
    # Get campaign stats
    # Display in table
    # Apply date filter
    # Apply segment filter
    # Verify correct rows shown
```

#### E2E Tests
```
Scenario: Send campaign to Champions
1. Login as Marketing Manager
2. Navigate to Marketing Dashboard
3. Select "Champions" segment
4. Choose "Default VIP Rewards" template
5. Click "Send Campaign"
6. Verify success message
7. Check campaign history updated

Scenario: Filter campaign history
1. Send campaign to Champions
2. Send campaign to Potential
3. Open Campaign History
4. Filter by "Potential"
5. Verify only Potential campaign shows
6. Filter by date range
7. Verify date filtering works
```

---

## 📊 Test Coverage Target

| Component | Unit Tests | Integration Tests | E2E Tests | Coverage |
|-----------|-----------|------------------|-----------|----------|
| Template Selector | 3 | 2 | 1 | 100% |
| Message Preview | 4 | 2 | 1 | 95% |
| Campaign Send | 5 | 3 | 2 | 100% |
| Campaign History | 3 | 2 | 1 | 90% |
| Delivery Tracking | 2 | 1 | 1 | 80% |
| Error Handling | 4 | 2 | 1 | 100% |
| **TOTAL** | **21** | **12** | **7** | **93%** |

---

## ✅ Acceptance Criteria Checklist

- [ ] Campaign template selector displays with all 5 options
- [ ] Message preview shows formatted message with customer name
- [ ] User can select target segment (Champions/Potential/Loyal/Lost)
- [ ] Send button sends campaign to all customers in segment
- [ ] Success message shows: "✅ Sent to X customers"
- [ ] Campaign tracked in history with date, segment, count, success rate
- [ ] Campaign history table displays past campaigns (most recent first)
- [ ] History filters by date range work
- [ ] History filters by segment work
- [ ] Delivery status shows (Sent/Success/Failed count)
- [ ] Retry button allows resending failed messages
- [ ] Error handling works for invalid segments/messages
- [ ] Error handling works for API failures
- [ ] No customer data logged (only IDs)
- [ ] Works on mobile view
- [ ] All 21 unit tests passing
- [ ] All 12 integration tests passing
- [ ] All 7 E2E tests passing
- [ ] Code reviewed & merged
- [ ] Documentation updated

---

## 🚀 Deployment Checklist

Before deployment to production:
- [ ] Code review approved
- [ ] All tests passing
- [ ] Test with real Zalo test OA account
- [ ] Test with all 4 RFM segments
- [ ] Performance test: send to 1000 customers < 2 min
- [ ] Error scenario testing
- [ ] Staging environment verified
- [ ] Database backup taken
- [ ] Rollback plan documented
- [ ] Monitoring/alerts configured
- [ ] Documentation updated
- [ ] Team trained on feature
- [ ] User acceptance testing passed

---

## 📝 Documentation

**User Documentation**:
- How to send Zalo campaigns
- How to select templates
- How to review campaign history
- How to retry failed messages
- Troubleshooting common issues

**Developer Documentation**:
- Code architecture
- How Zalo integration works
- How to modify templates
- How to add custom templates
- Testing strategy

---

## 🔄 Rollback Plan

**If dashboard automation fails**:
1. Revert app.py to previous version
2. Dashboard reverts to without Zalo buttons
3. Campaigns can still be sent via code
4. Restart Streamlit app
5. Manual campaigns sent via script while fixing

---

## 📞 Questions & Answers

**Q: What if Zalo API is down?**
A: Show error message, allow retry, graceful degradation. No crashes.

**Q: Can users customize messages?**
A: Yes, "Custom Message" template option available.

**Q: How many campaigns can we send per day?**
A: Depends on Zalo OA plan - typically 50-1000/day. Show in dashboard.

**Q: Do we track individual message delivery?**
A: Yes, message IDs tracked, but aggregated in UI.

**Q: Can users schedule campaigns?**
A: Not in Task #15, but can add in Phase 5.

---

**Task Owner**: Development Team  
**Last Updated**: June 8, 2026  
**Version**: 1.0
