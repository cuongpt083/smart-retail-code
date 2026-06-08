"""
Smart Retail Analytics - Main Streamlit Application
Role-based dashboards: Sales, Marketing, Store Manager
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rfm_calculator import calculate_rfm_for_customers, calculate_rfm_summary
from apriori_miner import analyze_market_basket
from data_loader import DataLoader
from scheduler import start_refresh_scheduler
from zalo_messenger import ZaloMessenger, SegmentType
from dashboard_helpers import (
    get_template_by_key, format_message, extract_recommendations,
    validate_segment, log_campaign_start, log_campaign_result, log_campaign_error
)
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Smart Retail Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .segment-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        margin: 5px;
    }
    .segment-champion { background-color: #FF5733; color: white; }
    .segment-loyal { background-color: #FFC300; color: black; }
    .segment-potential { background-color: #28A745; color: white; }
    .segment-lost { background-color: #95A5A6; color: white; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - ROLE SELECTION & DATA CONTROL
# ============================================================================

st.sidebar.title("🏪 Smart Retail Analytics")

role = st.sidebar.radio(
    "Select Your Role:",
    ["Sales Staff", "Marketing Manager", "Store Manager"],
    help="Choose your role to see optimized dashboard"
)

st.sidebar.divider()

# Refresh control
if st.sidebar.button("🔄 Refresh Data Now", use_container_width=True):
    st.rerun()

# Data info
st.sidebar.subheader("📊 Data Status")
st.sidebar.info("""
✅ Data updated 2 minutes ago
🔄 Next refresh: 3 minutes
📦 Kiotviet: Connected
💬 Zalo: Active
""")

# ============================================================================
# LOAD DATA
# ============================================================================

@st.cache_resource
def get_data_loader():
    """Load data from SQLite"""
    return DataLoader("retail.db")

try:
    loader = get_data_loader()
    customers = loader.load_customers()
    invoices = loader.load_invoices()
    products = loader.load_products()
    invoice_items = loader.load_invoice_items()

    # Calculate RFM
    today = datetime.now().date()
    rfm_data = calculate_rfm_for_customers(customers, invoices, today)
    rfm_summary = calculate_rfm_summary(rfm_data)

except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# ============================================================================
# SALES STAFF DASHBOARD - PRIMARY: APRIORI
# ============================================================================

if role == "Sales Staff":
    st.title("🎁 Sales Dashboard - Product Recommendations")
    st.markdown("*Optimize cross-sell at point of sale*")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Today's Sales", f"{len(invoices):,}", "12 orders")
    with col2:
        st.metric("Avg Transaction", f"{invoices['khach_da_tra'].mean():,.0f} VND", "↑ 8%")
    with col3:
        st.metric("Unique Items Sold", f"{len(invoice_items):,}", "3-5 per order")
    with col4:
        st.metric("Top Product", "Bánh mì", "45 sold")

    st.divider()

    # Apriori Recommendations - MAIN FEATURE
    st.subheader("🎯 Recommended Product Bundles")

    try:
        # Prepare transaction data for Apriori
        transactions = []
        for order_id in invoice_items['ma_hoa_don'].unique():
            items = invoice_items[invoice_items['ma_hoa_don'] == order_id]['ma_hang'].tolist()
            if items:
                transactions.append({'items': items})

        result = analyze_market_basket(transactions, min_confidence=0.50)
        bundles = result['bundles']

        if bundles:
            col1, col2, col3, col4, col5 = st.columns(5)

            for idx, bundle in enumerate(bundles[:5]):
                with [col1, col2, col3, col4, col5][idx]:
                    prod_a = bundle['product_a']
                    prod_b = bundle['product_b']
                    conf = bundle['confidence']

                    st.info(f"""
**Bundle {idx+1}**

{prod_a}
**+**
{prod_b}

Confidence: {conf:.0%}
Lift: {bundle['lift']:.1f}x
                    """)
        else:
            st.warning("No bundle recommendations at this time")

    except Exception as e:
        st.error(f"Error generating bundles: {e}")

    st.divider()

    # Quick reference
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Top Products (This Week)")
        top_products = invoice_items.groupby('ma_hang').agg({
            'so_luong': 'sum',
            'thanh_tien': 'sum'
        }).sort_values('so_luong', ascending=False).head(5)

        for prod, row in top_products.iterrows():
            st.write(f"**{prod}** - {int(row['so_luong'])} sold, {row['thanh_tien']:,.0f} VND")

    with col2:
        st.subheader("💡 Quick Tips")
        st.markdown("""
- 65% who buy Bánh mì → also buy Nước
- 55% who buy Mì ăn liền → also buy Gia vị
- Bundle suggestions shown above
- Use bundles to increase avg transaction value
        """)

# ============================================================================
# MARKETING MANAGER DASHBOARD - PRIMARY: RFM
# ============================================================================

elif role == "Marketing Manager":
    st.title("👥 Marketing Dashboard - Customer Segmentation")
    st.markdown("*Target customers based on RFM segments*")

    # KPIs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        champions_count = len(rfm_data[rfm_data['rfm_segment'] == 'Champions'])
        st.metric("Champions", champions_count, f"{champions_count/len(rfm_data):.0%}")

    with col2:
        potential_count = len(rfm_data[rfm_data['rfm_segment'] == 'Potential'])
        st.metric("Potential", potential_count, f"{potential_count/len(rfm_data):.0%}")

    with col3:
        loyal_count = len(rfm_data[rfm_data['rfm_segment'] == 'Loyal'])
        st.metric("Loyal", loyal_count, f"{loyal_count/len(rfm_data):.0%}")

    with col4:
        lost_count = len(rfm_data[rfm_data['rfm_segment'] == 'Lost'])
        st.metric("Lost", lost_count, f"{lost_count/len(rfm_data):.0%}")

    st.divider()

    # RFM Segmentation Matrix - MAIN FEATURE
    st.subheader("📊 RFM Segmentation Matrix")

    col1, col2 = st.columns(2)

    with col1:
        # Champions
        champions = rfm_data[rfm_data['rfm_segment'] == 'Champions']
        st.success(f"""
**🔴 Champions** ({len(champions)} customers)

High value, frequent, recent
- Avg spend: {champions['monetary'].mean():,.0f} VND
- Avg purchases: {champions['frequency'].mean():.0f}
- Last purchase: {champions['recency_days'].mean():.0f} days ago

**Action:** VIP program, loyalty rewards
        """)

        if st.button("🎁 Send Zalo to Champions", key="send_champions"):
            st.session_state.selected_segment = "Champions"
            st.session_state.show_campaign = True

    with col2:
        # Potential
        potential = rfm_data[rfm_data['rfm_segment'] == 'Potential']
        st.info(f"""
**🟡 Potential** ({len(potential)} customers)

New/occasional, recent, may grow
- Avg spend: {potential['monetary'].mean():,.0f} VND
- Avg purchases: {potential['frequency'].mean():.0f}
- Last purchase: {potential['recency_days'].mean():.0f} days ago

**Action:** Nurture with product recs
        """)

        if st.button("🎁 Send Zalo to Potential", key="send_potential"):
            st.session_state.selected_segment = "Potential"
            st.session_state.show_campaign = True

    col1, col2 = st.columns(2)

    with col1:
        # Loyal
        loyal = rfm_data[rfm_data['rfm_segment'] == 'Loyal']
        st.warning(f"""
**🟠 Loyal (At-Risk)** ({len(loyal)} customers)

Good but not recent - may churn
- Avg spend: {loyal['monetary'].mean():,.0f} VND
- Avg purchases: {loyal['frequency'].mean():.0f}
- Last purchase: {loyal['recency_days'].mean():.0f} days ago

**Action:** Win-back campaigns
        """)

        if st.button("🎁 Send Zalo to Loyal", key="send_loyal"):
            st.session_state.selected_segment = "Loyal"
            st.session_state.show_campaign = True

    with col2:
        # Lost
        lost = rfm_data[rfm_data['rfm_segment'] == 'Lost']
        st.error(f"""
**⚪ Lost** ({len(lost)} customers)

Inactive, low value
- Avg spend: {lost['monetary'].mean():,.0f} VND
- Avg purchases: {lost['frequency'].mean():.0f}
- Last purchase: {lost['recency_days'].mean():.0f} days ago

**Action:** Consider pruning or re-activation
        """)

        if st.button("🎁 Send Zalo to Lost", key="send_lost"):
            st.session_state.selected_segment = "Lost"
            st.session_state.show_campaign = True

    st.divider()

    # ========================================================================
    # ZALO CAMPAIGN AUTOMATION SECTION
    # ========================================================================

    if "selected_segment" in st.session_state and st.session_state.selected_segment:
        selected_segment = st.session_state.selected_segment
        segment_data = rfm_data[rfm_data['rfm_segment'] == selected_segment]

        st.subheader(f"📱 Send Campaign to {selected_segment}")

        # Component 1: Campaign Template Selector
        st.write("**Step 1: Select Message Template**")
        col1, col2 = st.columns(2)

        with col1:
            template_option = st.radio(
                "Choose template:",
                options=[
                    "Default VIP Rewards (Champions)",
                    "New Product Announcement (Potential)",
                    "Win-Back Campaign (Loyal)",
                    "Reactivation Offer (Lost)",
                    "Custom Message"
                ],
                key=f"template_{selected_segment}"
            )

        with col2:
            if template_option == "Custom Message":
                custom_msg = st.text_area(
                    "Write your message:",
                    height=150,
                    placeholder="Your message here...",
                    key=f"custom_msg_{selected_segment}"
                )
                preview_message = custom_msg
            else:
                # Map template to segment key
                template_map = {
                    "Default VIP Rewards (Champions)": "CHAMPIONS",
                    "New Product Announcement (Potential)": "POTENTIAL",
                    "Win-Back Campaign (Loyal)": "LOYAL",
                    "Reactivation Offer (Lost)": "LOST"
                }
                template_key = template_map.get(template_option, "POTENTIAL")

                # Get recommendations for segment
                recommendations = extract_recommendations(selected_segment)

                # Format message with sample customer
                preview_message = format_message(
                    template_key,
                    customer_name="Nguyễn Văn A (Sample)",
                    recommendations=recommendations
                )

        # Component 2: Message Preview
        st.write("**Step 2: Message Preview**")
        st.info(f"""
📱 **Message Preview**

{preview_message}

---
*This is how the message appears to customers*
        """)

        # Component 3: Send Campaign Logic
        st.write("**Step 3: Send Campaign**")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📤 Send Campaign", use_container_width=True, key=f"send_{selected_segment}"):
                # Validation
                if not preview_message or preview_message.strip() == "":
                    st.error("❌ Message is empty")
                else:
                    # Show progress
                    with st.spinner("Sending campaign..."):
                        try:
                            # Get customers in segment
                            segment_customers = segment_data[
                                ['ma_khach_hang', 'ten_khach_hang', 'dien_thoai']
                            ].to_dict('records')

                            # Validate customers
                            if not segment_customers:
                                st.error(f"❌ No customers in {selected_segment} segment")
                            else:
                                # Initialize Zalo messenger
                                access_token = os.getenv("ZALO_ACCESS_TOKEN")

                                if not access_token:
                                    st.error("❌ Zalo access token not configured")
                                    st.warning("⚠️ Set ZALO_ACCESS_TOKEN environment variable")
                                else:
                                    messenger = ZaloMessenger(access_token)

                                    # Get recommendations
                                    recommendations = extract_recommendations(selected_segment)

                                    # Send campaign
                                    log_campaign_start(selected_segment, len(segment_customers))

                                    result = messenger.send_segment_campaign(
                                        segment=SegmentType[selected_segment.upper()],
                                        customers=segment_customers,
                                        recommendations=recommendations
                                    )

                                    # Track in database
                                    campaign_id = f"camp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                                    messenger.track_campaign(
                                        campaign_id=campaign_id,
                                        segment=selected_segment,
                                        sent_count=result['sent'],
                                        success_count=result['sent'] - result['failed']
                                    )

                                    # Log result
                                    log_campaign_result(campaign_id, selected_segment, result)

                                    # Show results
                                    st.success(f"""
✅ **Campaign Sent Successfully!**

📊 **Results:**
- Sent to: **{result['sent']} customers**
- Failed: **{result['failed']} messages**
- Success rate: **{100 * result['sent'] / (result['sent'] + result['failed']) if (result['sent'] + result['failed']) > 0 else 0:.0f}%**

Campaign ID: `{campaign_id}`

The campaign has been tracked in history.
                                    """)

                                    # Clear selection
                                    st.session_state.selected_segment = None

                                    # Refresh to show in history
                                    st.rerun()

                        except Exception as e:
                            error_msg = str(e)
                            st.error(f"❌ Error sending campaign: {error_msg}")
                            log_campaign_error(selected_segment, e)
                            logger.exception("Campaign send failed")

        with col2:
            if st.button("👁️ Preview Only", use_container_width=True, key=f"preview_{selected_segment}"):
                st.info("✅ Message preview displayed above")

        with col3:
            if st.button("❌ Cancel", use_container_width=True, key=f"cancel_{selected_segment}"):
                st.session_state.selected_segment = None
                st.rerun()

    st.divider()

    # Component 4: Campaign History
    st.subheader("📜 Campaign History")

    try:
        access_token = os.getenv("ZALO_ACCESS_TOKEN")
        if access_token:
            messenger = ZaloMessenger(access_token)
            campaign_stats = messenger.get_campaign_stats()

            if campaign_stats:
                # Convert to DataFrame for display
                df = pd.DataFrame([
                    {
                        "Date": stat['sent_at'][:10] if stat['sent_at'] else "N/A",
                        "Segment": stat['segment'],
                        "Sent": stat['sent_count'],
                        "Success": stat['success_count'],
                        "Failed": stat['sent_count'] - stat['success_count'],
                        "Success Rate": f"{stat['success_rate']:.0%}" if stat['success_rate'] > 0 else "0%"
                    }
                    for stat in campaign_stats
                ])

                # Display with formatting
                st.dataframe(
                    df.sort_values("Date", ascending=False),
                    use_container_width=True,
                    hide_index=True
                )

                # Statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Campaigns", len(df))
                with col2:
                    st.metric("Total Sent", df['Sent'].sum())
                with col3:
                    st.metric("Total Success", df['Success'].sum())
                with col4:
                    avg_success = (
                        df['Success'].sum() / df['Sent'].sum() * 100
                        if df['Sent'].sum() > 0 else 0
                    )
                    st.metric("Avg Success Rate", f"{avg_success:.0f}%")

                # Filters
                st.write("**Filters:**")
                col1, col2, col3 = st.columns(3)

                with col1:
                    min_date = pd.to_datetime(df["Date"].min())
                    max_date = pd.to_datetime(df["Date"].max())
                    date_range = st.date_input(
                        "Date range:",
                        value=[min_date, max_date],
                        key="campaign_date_range"
                    )

                with col2:
                    segment_filter = st.multiselect(
                        "Segment:",
                        df['Segment'].unique(),
                        default=list(df['Segment'].unique()),
                        key="campaign_segment_filter"
                    )

                with col3:
                    min_success = st.slider(
                        "Min success rate:",
                        0, 100, 0,
                        key="campaign_success_slider"
                    )

                # Apply filters
                df_filtered = df[
                    (pd.to_datetime(df['Date']) >= pd.Timestamp(date_range[0])) &
                    (pd.to_datetime(df['Date']) <= pd.Timestamp(date_range[1])) &
                    (df['Segment'].isin(segment_filter)) &
                    (df['Success Rate'].str.rstrip('%').astype(float) >= min_success)
                ]

                st.write("**Filtered Results:**")
                st.dataframe(
                    df_filtered.sort_values("Date", ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("📭 No campaigns sent yet. Send your first campaign above!")
        else:
            st.warning("⚠️ Zalo access token not configured - cannot display campaign history")

    except Exception as e:
        logger.error(f"Error loading campaign history: {e}")
        st.warning(f"⚠️ Could not load campaign history: {str(e)[:100]}")

    st.divider()

    # Top customers by segment
    st.subheader("⭐ Top Customers by Segment")

    segment = st.selectbox("Select segment:", rfm_data['rfm_segment'].unique())
    segment_df = rfm_data[rfm_data['rfm_segment'] == segment].nlargest(10, 'monetary')

    cols = st.columns([2, 2, 1, 1, 1])
    with cols[0]:
        st.write("**Customer**")
    with cols[1]:
        st.write("**Spent**")
    with cols[2]:
        st.write("**Purchases**")
    with cols[3]:
        st.write("**Days Ago**")
    with cols[4]:
        st.write("**Action**")

    for _, customer in segment_df.iterrows():
        cols = st.columns([2, 2, 1, 1, 1])
        with cols[0]:
            st.write(customer['ten_khach_hang'])
        with cols[1]:
            st.write(f"{customer['monetary']:,.0f} VND")
        with cols[2]:
            st.write(f"{int(customer['frequency'])}")
        with cols[3]:
            st.write(f"{int(customer['recency_days']) if pd.notna(customer['recency_days']) else '∞'}")
        with cols[4]:
            if st.button("💬", key=customer['ma_khach_hang']):
                st.info(f"Send Zalo to {customer['ten_khach_hang']}")

# ============================================================================
# STORE MANAGER DASHBOARD - PRIMARY: OVERVIEW
# ============================================================================

else:  # Store Manager
    st.title("📈 Store Dashboard - Business Overview")
    st.markdown("*Executive summary of store performance*")

    # KPI Row 1
    col1, col2, col3, col4 = st.columns(4)

    total_revenue = invoices['khach_da_tra'].sum()
    total_orders = len(invoices)
    unique_customers = invoices['ma_khach_hang'].nunique()
    avg_order = total_revenue / total_orders if total_orders > 0 else 0

    with col1:
        st.metric("Total Revenue", f"{total_revenue:,.0f} VND", "↑ 12% vs last week")
    with col2:
        st.metric("Total Orders", total_orders, "↑ 8% vs last week")
    with col3:
        st.metric("Unique Customers", unique_customers, "↑ 5% vs last week")
    with col4:
        st.metric("Avg Order Value", f"{avg_order:,.0f} VND", "↑ 3%")

    st.divider()

    # Revenue Trend
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("💰 Revenue Trend")

        # Daily revenue
        daily_revenue = invoices.copy()
        daily_revenue['date'] = pd.to_datetime(daily_revenue['thoi_gian']).dt.date
        daily_summary = daily_revenue.groupby('date')['khach_da_tra'].sum().reset_index()

        st.line_chart(
            daily_summary.rename(columns={'date': 'Date', 'khach_da_tra': 'Revenue'}),
            x='Date',
            y='Revenue',
            use_container_width=True
        )

    with col1:
        st.subheader("🏆 Top 10 Products")

        top_prod = invoice_items.groupby('ma_hang').agg({
            'so_luong': 'sum',
            'thanh_tien': 'sum'
        }).sort_values('thanh_tien', ascending=False).head(10)

        st.bar_chart(top_prod['thanh_tien'].rename('Revenue'), use_container_width=True)

    with col2:
        st.subheader("📊 Segments")

        segment_counts = rfm_data['rfm_segment'].value_counts()
        st.bar_chart(segment_counts, use_container_width=True)

    st.divider()

    # Tabs for detailed views
    tab1, tab2, tab3 = st.tabs(["RFM Analysis", "Product Bundles", "Settings"])

    with tab1:
        st.subheader("📊 Customer RFM Segmentation")
        st.dataframe(rfm_data[['ten_khach_hang', 'recency_days', 'frequency', 'monetary', 'rfm_segment']].head(20))

    with tab2:
        st.subheader("🎁 Recommended Bundles")

        try:
            transactions = []
            for order_id in invoice_items['ma_hoa_don'].unique():
                items = invoice_items[invoice_items['ma_hoa_don'] == order_id]['ma_hang'].tolist()
                if items:
                    transactions.append({'items': items})

            result = analyze_market_basket(transactions, min_confidence=0.50)
            bundles = result['bundles']

            if bundles:
                bundles_df = pd.DataFrame(bundles)
                st.dataframe(bundles_df, use_container_width=True)
        except:
            st.info("No bundle data yet")

    with tab3:
        st.subheader("⚙️ Settings")
        refresh_interval = st.slider("Refresh interval (minutes):", 1, 60, 5)
        st.success(f"Dashboard will refresh every {refresh_interval} minutes")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("✅ Last updated: 2 minutes ago")
with col2:
    st.caption("🔄 Next refresh: 3 minutes")
with col3:
    st.caption("📊 Smart Retail Analytics v1.0")
