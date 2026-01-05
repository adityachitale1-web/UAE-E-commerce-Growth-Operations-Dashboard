import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Souq Leadership Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    h1 {
        color: #FF6B35;
        font-weight: 700;
    }
    h2 {
        color: #004E89;
        font-weight: 600;
    }
    h3 {
        color: #1A659E;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 5px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF6B35;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Load data with caching
@st.cache_data
def load_data():
    """Load all CSV files and return dataframes"""
    try:
        customers = pd.read_csv('data/customers.csv')
        orders = pd.read_csv('data/orders.csv')
        order_items = pd.read_csv('data/order_items.csv')
        fulfillment = pd.read_csv('data/fulfillment.csv')
        returns = pd.read_csv('data/returns.csv')
        
        # Convert date columns
        customers['signup_date'] = pd.to_datetime(customers['signup_date'])
        orders['order_date'] = pd.to_datetime(orders['order_date'])
        fulfillment['promised_date'] = pd.to_datetime(fulfillment['promised_date'])
        fulfillment['actual_delivery_date'] = pd.to_datetime(fulfillment['actual_delivery_date'])
        returns['return_date'] = pd.to_datetime(returns['return_date'])
        
        return customers, orders, order_items, fulfillment, returns
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Please ensure all CSV files are in the 'data' folder")
        return None, None, None, None, None

# Load data
customers_df, orders_df, order_items_df, fulfillment_df, returns_df = load_data()

# Check if data loaded successfully
if customers_df is None:
    st.stop()

# Merge dataframes for analysis
@st.cache_data
def prepare_data(customers, orders, order_items, fulfillment, returns):
    """Prepare merged dataframes for analysis"""
    # Merge orders with customers
    orders_full = orders.merge(customers[['customer_id', 'city', 'customer_segment']], on='customer_id', how='left')
    
    # Merge orders with fulfillment
    orders_full = orders_full.merge(fulfillment[['order_id', 'warehouse_hub', 'delivery_status', 'delay_reason', 'delivery_partner']], 
                                     on='order_id', how='left')
    
    # Add month and week columns
    orders_full['order_month'] = orders_full['order_date'].dt.to_period('M').astype(str)
    orders_full['order_week'] = orders_full['order_date'].dt.to_period('W').astype(str)
    orders_full['order_day'] = orders_full['order_date'].dt.date
    
    return orders_full

orders_full = prepare_data(customers_df, orders_df, order_items_df, fulfillment_df, returns_df)

# Sidebar filters
st.sidebar.image("https://via.placeholder.com/200x80/FF6B35/FFFFFF?text=SOUQ", use_container_width=True)
st.sidebar.title("🔍 Filters")

# Date range filter
min_date = orders_df['order_date'].min().date()
max_date = orders_df['order_date'].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# City filter
cities = ['All'] + sorted(customers_df['city'].unique().tolist())
selected_city = st.sidebar.selectbox("Select City", cities)

# Channel filter
channels = ['All'] + sorted(orders_df['order_channel'].unique().tolist())
selected_channel = st.sidebar.selectbox("Select Channel", channels)

# Customer segment filter
segments = ['All'] + sorted(customers_df['customer_segment'].unique().tolist())
selected_segment = st.sidebar.selectbox("Select Customer Segment", segments)

# Apply filters
filtered_orders = orders_full.copy()

if len(date_range) == 2:
    filtered_orders = filtered_orders[
        (filtered_orders['order_date'].dt.date >= date_range[0]) & 
        (filtered_orders['order_date'].dt.date <= date_range[1])
    ]

if selected_city != 'All':
    filtered_orders = filtered_orders[filtered_orders['city'] == selected_city]

if selected_channel != 'All':
    filtered_orders = filtered_orders[filtered_orders['order_channel'] == selected_channel]

if selected_segment != 'All':
    filtered_orders = filtered_orders[filtered_orders['customer_segment'] == selected_segment]

# Main dashboard
st.title("🛒 Souq Leadership Dashboard")
st.markdown("### Real-time Business Intelligence for E-commerce Excellence")

# Create tabs for different pages
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Executive Summary", 
    "💰 Sales Performance", 
    "🚚 Operations & Fulfillment", 
    "👥 Customer & Returns"
])

# ============================================================================
# TAB 1: EXECUTIVE SUMMARY
# ============================================================================
with tab1:
    st.header("Executive Summary")
    
    # Calculate KPIs
    total_revenue = filtered_orders['net_amount'].sum()
    total_orders = len(filtered_orders)
    avg_order_value = filtered_orders['net_amount'].mean()
    
    # Calculate previous period for comparison
    if len(date_range) == 2:
        period_days = (date_range[1] - date_range[0]).days
        prev_start = date_range[0] - timedelta(days=period_days)
        prev_end = date_range[0] - timedelta(days=1)
        
        prev_orders = orders_full[
            (orders_full['order_date'].dt.date >= prev_start) & 
            (orders_full['order_date'].dt.date <= prev_end)
        ]
        
        prev_revenue = prev_orders['net_amount'].sum()
        prev_order_count = len(prev_orders)
        prev_aov = prev_orders['net_amount'].mean()
        
        revenue_growth = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        order_growth = ((total_orders - prev_order_count) / prev_order_count * 100) if prev_order_count > 0 else 0
        aov_growth = ((avg_order_value - prev_aov) / prev_aov * 100) if prev_aov > 0 else 0
    else:
        revenue_growth = 0
        order_growth = 0
        aov_growth = 0
    
    # Customer metrics
    unique_customers = filtered_orders['customer_id'].nunique()
    
    # Display KPIs in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total Revenue",
            value=f"AED {total_revenue:,.0f}",
            delta=f"{revenue_growth:+.1f}% vs prev period"
        )
    
    with col2:
        st.metric(
            label="📦 Total Orders",
            value=f"{total_orders:,}",
            delta=f"{order_growth:+.1f}% vs prev period"
        )
    
    with col3:
        st.metric(
            label="🛍️ Average Order Value",
            value=f"AED {avg_order_value:,.0f}",
            delta=f"{aov_growth:+.1f}% vs prev period"
        )
    
    with col4:
        st.metric(
            label="👥 Active Customers",
            value=f"{unique_customers:,}",
            delta=None
        )
    
    st.markdown("---")
    
    # Revenue trend chart
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Revenue Trend")
        
        # Daily revenue trend
        daily_revenue = filtered_orders.groupby('order_day')['net_amount'].sum().reset_index()
        daily_revenue.columns = ['Date', 'Revenue']
        
        fig_revenue_trend = px.line(
            daily_revenue,
            x='Date',
            y='Revenue',
            title='Daily Revenue Trend',
            labels={'Revenue': 'Revenue (AED)'},
            template='plotly_white'
        )
        fig_revenue_trend.update_traces(line_color='#FF6B35', line_width=3)
        fig_revenue_trend.update_layout(height=400)
        st.plotly_chart(fig_revenue_trend, use_container_width=True)
    
    with col2:
        st.subheader("🏙️ Revenue by City")
        
        city_revenue = filtered_orders.groupby('city')['net_amount'].sum().reset_index()
        city_revenue = city_revenue.sort_values('net_amount', ascending=False)
        
        fig_city = px.bar(
            city_revenue,
            x='net_amount',
            y='city',
            orientation='h',
            title='Revenue Distribution',
            labels={'net_amount': 'Revenue (AED)', 'city': 'City'},
            color='net_amount',
            color_continuous_scale='Oranges',
            template='plotly_white'
        )
        fig_city.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_city, use_container_width=True)
    
    # Top products
    st.subheader("🏆 Top 5 Products by Revenue")
    
    # Merge order items with orders to get revenue
    items_with_orders = order_items_df.merge(
        filtered_orders[['order_id', 'order_date']], 
        on='order_id', 
        how='inner'
    )
    
    top_products = items_with_orders.groupby('product_name')['item_total'].sum().reset_index()
    top_products = top_products.sort_values('item_total', ascending=False).head(5)
    top_products.columns = ['Product', 'Revenue']
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        fig_top_products = px.bar(
            top_products,
            x='Revenue',
            y='Product',
            orientation='h',
            title='Top 5 Products',
            labels={'Revenue': 'Revenue (AED)'},
            color='Revenue',
            color_continuous_scale='Blues',
            template='plotly_white'
        )
        fig_top_products.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_top_products, use_container_width=True)
    
    with col2:
        # Order status distribution
        st.subheader("📊 Order Status Distribution")
        status_dist = filtered_orders['order_status'].value_counts().reset_index()
        status_dist.columns = ['Status', 'Count']
        
        fig_status = px.pie(
            status_dist,
            values='Count',
            names='Status',
            title='Order Status Breakdown',
            color_discrete_sequence=px.colors.sequential.RdBu,
            template='plotly_white'
        )
        fig_status.update_layout(height=350)
        st.plotly_chart(fig_status, use_container_width=True)

# ============================================================================
# TAB 2: SALES PERFORMANCE
# ============================================================================
with tab2:
    st.header("💰 Sales Performance Analysis")
    
    # Sales metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_gross = filtered_orders['gross_amount'].sum()
        st.metric("Gross Revenue", f"AED {total_gross:,.0f}")
    
    with col2:
        total_discount = filtered_orders['discount_amount'].sum()
        discount_rate = (total_discount / total_gross * 100) if total_gross > 0 else 0
        st.metric("Total Discounts", f"AED {total_discount:,.0f}", f"{discount_rate:.1f}%")
    
    with col3:
        orders_with_discount = filtered_orders[filtered_orders['discount_amount'] > 0]
        discount_penetration = (len(orders_with_discount) / len(filtered_orders) * 100) if len(filtered_orders) > 0 else 0
        st.metric("Discount Penetration", f"{discount_penetration:.1f}%")
    
    with col4:
        avg_discount = orders_with_discount['discount_amount'].mean() if len(orders_with_discount) > 0 else 0
        st.metric("Avg Discount", f"AED {avg_discount:.0f}")
    
    st.markdown("---")
    
    # Revenue breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📱 Revenue by Channel")
        channel_revenue = filtered_orders.groupby('order_channel')['net_amount'].sum().reset_index()
        channel_revenue = channel_revenue.sort_values('net_amount', ascending=False)
        
        fig_channel = px.bar(
            channel_revenue,
            x='order_channel',
            y='net_amount',
            title='Channel Performance',
            labels={'net_amount': 'Revenue (AED)', 'order_channel': 'Channel'},
            color='net_amount',
            color_continuous_scale='Viridis',
            template='plotly_white'
        )
        fig_channel.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_channel, use_container_width=True)
    
    with col2:
        st.subheader("💳 Revenue by Payment Method")
        payment_revenue = filtered_orders.groupby('payment_method')['net_amount'].sum().reset_index()
        
        fig_payment = px.pie(
            payment_revenue,
            values='net_amount',
            names='payment_method',
            title='Payment Method Distribution',
            color_discrete_sequence=px.colors.sequential.Sunset,
            template='plotly_white'
        )
        fig_payment.update_layout(height=400)
        st.plotly_chart(fig_payment, use_container_width=True)
    
    # Customer segment analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Revenue by Customer Segment")
        segment_revenue = filtered_orders.groupby('customer_segment').agg({
            'net_amount': 'sum',
            'order_id': 'count'
        }).reset_index()
        segment_revenue.columns = ['Segment', 'Revenue', 'Orders']
        segment_revenue['AOV'] = segment_revenue['Revenue'] / segment_revenue['Orders']
        
        fig_segment = px.bar(
            segment_revenue,
            x='Segment',
            y='Revenue',
            title='Segment Revenue Contribution',
            labels={'Revenue': 'Revenue (AED)'},
            color='Revenue',
            color_continuous_scale='Teal',
            template='plotly_white',
            text='Revenue'
        )
        fig_segment.update_traces(texttemplate='AED %{text:,.0f}', textposition='outside')
        fig_segment.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_segment, use_container_width=True)
    
    with col2:
        st.subheader("🛍️ Category Performance")
        
        # Get category revenue
        items_filtered = order_items_df.merge(
            filtered_orders[['order_id']], 
            on='order_id', 
            how='inner'
        )
        
        category_revenue = items_filtered.groupby('product_category')['item_total'].sum().reset_index()
        category_revenue = category_revenue.sort_values('item_total', ascending=False)
        
        fig_category = px.bar(
            category_revenue,
            x='product_category',
            y='item_total',
            title='Revenue by Product Category',
            labels={'item_total': 'Revenue (AED)', 'product_category': 'Category'},
            color='item_total',
            color_continuous_scale='Purples',
            template='plotly_white'
        )
        fig_category.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_category, use_container_width=True)
    
    # Discount impact analysis
    st.subheader("🎯 Discount Impact Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Orders with vs without discount
        discount_comparison = filtered_orders.groupby(
            filtered_orders['discount_amount'] > 0
        ).agg({
            'net_amount': 'mean',
            'order_id': 'count'
        }).reset_index()
        discount_comparison['discount_amount'] = discount_comparison['discount_amount'].map({True: 'With Discount', False: 'No Discount'})
        discount_comparison.columns = ['Type', 'Avg Order Value', 'Order Count']
        
        fig_discount_impact = px.bar(
            discount_comparison,
            x='Type',
            y='Avg Order Value',
            title='Average Order Value: Discount vs No Discount',
            labels={'Avg Order Value': 'AOV (AED)'},
            color='Type',
            color_discrete_map={'With Discount': '#FF6B35', 'No Discount': '#004E89'},
            template='plotly_white',
            text='Avg Order Value'
        )
        fig_discount_impact.update_traces(texttemplate='AED %{text:,.0f}', textposition='outside')
        fig_discount_impact.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_discount_impact, use_container_width=True)
    
    with col2:
        # Coupon usage
        coupon_usage = filtered_orders[filtered_orders['coupon_code'].notna()]['coupon_code'].value_counts().reset_index()
        coupon_usage.columns = ['Coupon', 'Usage Count']
        
        fig_coupon = px.bar(
            coupon_usage,
            x='Coupon',
            y='Usage Count',
            title='Coupon Code Usage',
            labels={'Usage Count': 'Number of Uses'},
            color='Usage Count',
            color_continuous_scale='Reds',
            template='plotly_white'
        )
        fig_coupon.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_coupon, use_container_width=True)

# ============================================================================
# TAB 3: OPERATIONS & FULFILLMENT
# ============================================================================
with tab3:
    st.header("🚚 Operations & Fulfillment Performance")
    
    # Merge fulfillment data
    fulfillment_analysis = filtered_orders.merge(
        fulfillment_df[['order_id', 'warehouse_hub', 'delivery_zone', 'delivery_status', 
                        'delay_reason', 'delivery_partner', 'promised_date', 'actual_delivery_date']], 
        on='order_id', 
        how='left'
    )
    
    # Calculate delivery metrics
    delivered_orders = fulfillment_analysis[fulfillment_analysis['delivery_status'] == 'On Time']
    on_time_rate = (len(delivered_orders) / len(fulfillment_analysis) * 100) if len(fulfillment_analysis) > 0 else 0
    
    delayed_orders = fulfillment_analysis[fulfillment_analysis['delivery_status'] == 'Delayed']
    delay_rate = (len(delayed_orders) / len(fulfillment_analysis) * 100) if len(fulfillment_analysis) > 0 else 0
    
    # Calculate average delay
    fulfillment_analysis['promised_date'] = pd.to_datetime(fulfillment_analysis['promised_date'])
    fulfillment_analysis['actual_delivery_date'] = pd.to_datetime(fulfillment_analysis['actual_delivery_date'])
    
    delayed_with_dates = fulfillment_analysis[
        (fulfillment_analysis['delivery_status'] == 'Delayed') & 
        (fulfillment_analysis['actual_delivery_date'].notna())
    ].copy()
    
    if len(delayed_with_dates) > 0:
        delayed_with_dates['delay_days'] = (
            delayed_with_dates['actual_delivery_date'] - delayed_with_dates['promised_date']
        ).dt.days
        avg_delay = delayed_with_dates['delay_days'].mean()
    else:
        avg_delay = 0
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("✅ On-Time Delivery Rate", f"{on_time_rate:.1f}%")
    
    with col2:
        st.metric("⏰ Delayed Orders", f"{delay_rate:.1f}%")
    
    with col3:
        st.metric("📅 Avg Delay", f"{avg_delay:.1f} days")
    
    with col4:
        failed_rate = (len(fulfillment_analysis[fulfillment_analysis['delivery_status'] == 'Failed']) / 
                      len(fulfillment_analysis) * 100) if len(fulfillment_analysis) > 0 else 0
        st.metric("❌ Failed Deliveries", f"{failed_rate:.1f}%")
    
    st.markdown("---")
    
    # Delivery status distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Delivery Status Distribution")
        status_dist = fulfillment_analysis['delivery_status'].value_counts().reset_index()
        status_dist.columns = ['Status', 'Count']
        
        fig_delivery_status = px.pie(
            status_dist,
            values='Count',
            names='Status',
            title='Delivery Performance Overview',
            color='Status',
            color_discrete_map={
                'On Time': '#28a745',
                'Delayed': '#ffc107',
                'Failed': '#dc3545',
                'Pending': '#6c757d'
            },
            template='plotly_white'
        )
        fig_delivery_status.update_layout(height=400)
        st.plotly_chart(fig_delivery_status, use_container_width=True)
    
    with col2:
        st.subheader("🏭 Fulfillment by Warehouse")
        warehouse_perf = fulfillment_analysis.groupby('warehouse_hub').agg({
            'order_id': 'count',
            'delivery_status': lambda x: (x == 'On Time').sum()
        }).reset_index()
        warehouse_perf.columns = ['Warehouse', 'Total Orders', 'On Time Orders']
        warehouse_perf['On Time Rate'] = (warehouse_perf['On Time Orders'] / warehouse_perf['Total Orders'] * 100)
        
        fig_warehouse = px.bar(
            warehouse_perf,
            x='Warehouse',
            y='On Time Rate',
            title='On-Time Delivery Rate by Warehouse',
            labels={'On Time Rate': 'On-Time Rate (%)'},
            color='On Time Rate',
            color_continuous_scale='Greens',
            template='plotly_white',
            text='On Time Rate'
        )
        fig_warehouse.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_warehouse.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_warehouse, use_container_width=True)
    
    # Delivery partner comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚛 Delivery Partner Performance")
        partner_perf = fulfillment_analysis.groupby('delivery_partner').agg({
            'order_id': 'count',
            'delivery_status': lambda x: (x == 'On Time').sum()
        }).reset_index()
        partner_perf.columns = ['Partner', 'Total Deliveries', 'On Time Deliveries']
        partner_perf['On Time Rate'] = (partner_perf['On Time Deliveries'] / partner_perf['Total Deliveries'] * 100)
        
        fig_partner = px.bar(
            partner_perf,
            x='Partner',
            y='On Time Rate',
            title='Partner On-Time Performance',
            labels={'On Time Rate': 'On-Time Rate (%)'},
            color='On Time Rate',
            color_continuous_scale='Blues',
            template='plotly_white',
            text='On Time Rate'
        )
        fig_partner.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_partner.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_partner, use_container_width=True)
    
    with col2:
        st.subheader("⚠️ Delay Reasons Analysis")
        delay_reasons = fulfillment_analysis[fulfillment_analysis['delay_reason'].notna()]['delay_reason'].value_counts().reset_index()
        delay_reasons.columns = ['Reason', 'Count']
        
        fig_delay_reasons = px.bar(
            delay_reasons,
            x='Count',
            y='Reason',
            orientation='h',
            title='Top Delay Reasons',
            labels={'Count': 'Number of Delays'},
            color='Count',
            color_continuous_scale='Reds',
            template='plotly_white'
        )
        fig_delay_reasons.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_delay_reasons, use_container_width=True)
    
    # Delivery zone performance
    st.subheader("📍 Delivery Zone Performance")
    zone_perf = fulfillment_analysis.groupby('delivery_zone').agg({
        'order_id': 'count',
        'delivery_status': lambda x: (x == 'On Time').sum()
    }).reset_index()
    zone_perf.columns = ['Zone', 'Total Orders', 'On Time Orders']
    zone_perf['On Time Rate'] = (zone_perf['On Time Orders'] / zone_perf['Total Orders'] * 100)
    zone_perf = zone_perf.sort_values('On Time Rate', ascending=False)
    
    fig_zone = px.bar(
        zone_perf,
        x='Zone',
        y='On Time Rate',
        title='On-Time Delivery Rate by Zone',
        labels={'On Time Rate': 'On-Time Rate (%)'},
        color='On Time Rate',
        color_continuous_scale='Teal',
        template='plotly_white',
        text='On Time Rate'
    )
    fig_zone.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_zone.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_zone, use_container_width=True)

# ============================================================================
# TAB 4: CUSTOMER & RETURNS
# ============================================================================
with tab4:
    st.header("👥 Customer Analytics & Returns Management")
    
    # Customer metrics
    total_customers = customers_df['customer_id'].nunique()
    
    # New customers in selected period
    if len(date_range) == 2:
        new_customers = customers_df[
            (customers_df['signup_date'].dt.date >= date_range[0]) & 
            (customers_df['signup_date'].dt.date <= date_range[1])
        ]
        new_customer_count = len(new_customers)
    else:
        new_customer_count = 0
    
    # Return metrics
    returns_in_period = returns_df.merge(
        filtered_orders[['order_id']], 
        on='order_id', 
        how='inner'
    )
    
    return_rate = (len(returns_in_period) / len(filtered_orders) * 100) if len(filtered_orders) > 0 else 0
    total_refunds = returns_in_period['refund_amount'].sum()
    avg_refund = returns_in_period['refund_amount'].mean() if len(returns_in_period) > 0 else 0
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Customers", f"{total_customers:,}")
    
    with col2:
        st.metric("🆕 New Customers", f"{new_customer_count:,}")
    
    with col3:
        st.metric("↩️ Return Rate", f"{return_rate:.1f}%")
    
    with col4:
        st.metric("💸 Total Refunds", f"AED {total_refunds:,.0f}")
    
    st.markdown("---")
    
    # Customer acquisition trends
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Customer Acquisition Trend")
        
        # Monthly signups
        customers_df['signup_month'] = customers_df['signup_date'].dt.to_period('M').astype(str)
        monthly_signups = customers_df.groupby('signup_month').size().reset_index()
        monthly_signups.columns = ['Month', 'New Customers']
        
        fig_signups = px.line(
            monthly_signups,
            x='Month',
            y='New Customers',
            title='Monthly Customer Signups',
            labels={'New Customers': 'Number of Signups'},
            template='plotly_white'
        )
        fig_signups.update_traces(line_color='#FF6B35', line_width=3)
        fig_signups.update_layout(height=400)
        st.plotly_chart(fig_signups, use_container_width=True)
    
    with col2:
        st.subheader("📱 Signup Channel Effectiveness")
        channel_signups = customers_df['signup_channel'].value_counts().reset_index()
        channel_signups.columns = ['Channel', 'Signups']
        
        fig_signup_channel = px.pie(
            channel_signups,
            values='Signups',
            names='Channel',
            title='Customer Acquisition by Channel',
            color_discrete_sequence=px.colors.sequential.Sunset,
            template='plotly_white'
        )
        fig_signup_channel.update_layout(height=400)
        st.plotly_chart(fig_signup_channel, use_container_width=True)
    
    # Customer segment analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Customer Segment Distribution")
        segment_dist = customers_df['customer_segment'].value_counts().reset_index()
        segment_dist.columns = ['Segment', 'Count']
        
        fig_segment_dist = px.bar(
            segment_dist,
            x='Segment',
            y='Count',
            title='Customers by Segment',
            labels={'Count': 'Number of Customers'},
            color='Count',
            color_continuous_scale='Viridis',
            template='plotly_white',
            text='Count'
        )
        fig_segment_dist.update_traces(textposition='outside')
        fig_segment_dist.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_segment_dist, use_container_width=True)
    
    with col2:
        st.subheader("💰 Revenue per Customer Segment")
        segment_revenue = filtered_orders.groupby('customer_segment').agg({
            'net_amount': 'sum',
            'customer_id': 'nunique'
        }).reset_index()
        segment_revenue.columns = ['Segment', 'Total Revenue', 'Customers']
        segment_revenue['Revenue per Customer'] = segment_revenue['Total Revenue'] / segment_revenue['Customers']
        
        fig_segment_revenue = px.bar(
            segment_revenue,
            x='Segment',
            y='Revenue per Customer',
            title='Average Revenue per Customer',
            labels={'Revenue per Customer': 'Avg Revenue (AED)'},
            color='Revenue per Customer',
            color_continuous_scale='Teal',
            template='plotly_white',
            text='Revenue per Customer'
        )
        fig_segment_revenue.update_traces(texttemplate='AED %{text:,.0f}', textposition='outside')
        fig_segment_revenue.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_segment_revenue, use_container_width=True)
    
    # Returns analysis
    st.markdown("---")
    st.subheader("↩️ Returns Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Return Reasons")
        return_reasons = returns_in_period['return_reason'].value_counts().reset_index()
        return_reasons.columns = ['Reason', 'Count']
        
        fig_return_reasons = px.bar(
            return_reasons,
            x='Count',
            y='Reason',
            orientation='h',
            title='Top Return Reasons',
            labels={'Count': 'Number of Returns'},
            color='Count',
            color_continuous_scale='Reds',
            template='plotly_white'
        )
        fig_return_reasons.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_return_reasons, use_container_width=True)
    
    with col2:
        st.subheader("💳 Refund Status")
        refund_status = returns_in_period['refund_status'].value_counts().reset_index()
        refund_status.columns = ['Status', 'Count']
        
        fig_refund_status = px.pie(
            refund_status,
            values='Count',
            names='Status',
            title='Refund Processing Status',
            color='Status',
            color_discrete_map={
                'Processed': '#28a745',
                'Pending': '#ffc107',
                'Rejected': '#dc3545'
            },
            template='plotly_white'
        )
        fig_refund_status.update_layout(height=400)
        st.plotly_chart(fig_refund_status, use_container_width=True)
    
    # Return rate by category
    st.subheader("📦 Return Rate by Product Category")
    
    # Get returns with product info
    returns_with_items = returns_in_period.merge(
        order_items_df[['order_id', 'product_category']], 
        on='order_id', 
        how='left'
    )
    
    category_returns = returns_with_items.groupby('product_category').size().reset_index()
    category_returns.columns = ['Category', 'Returns']
    
    # Get total orders by category
    items_filtered = order_items_df.merge(
        filtered_orders[['order_id']], 
        on='order_id', 
        how='inner'
    )
    category_orders = items_filtered.groupby('product_category')['order_id'].nunique().reset_index()
    category_orders.columns = ['Category', 'Orders']
    
    # Calculate return rate
    category_return_rate = category_returns.merge(category_orders, on='Category', how='left')
    category_return_rate['Return Rate'] = (category_return_rate['Returns'] / category_return_rate['Orders'] * 100)
    category_return_rate = category_return_rate.sort_values('Return Rate', ascending=False)
    
    fig_category_returns = px.bar(
        category_return_rate,
        x='Category',
        y='Return Rate',
        title='Return Rate by Product Category',
        labels={'Return Rate': 'Return Rate (%)'},
        color='Return Rate',
        color_continuous_scale='Oranges',
        template='plotly_white',
        text='Return Rate'
    )
    fig_category_returns.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_category_returns.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_category_returns, use_container_width=True)
    
    # Customer lifetime value indicators
    st.markdown("---")
    st.subheader("💎 Customer Lifetime Value Indicators")
    
    col1, col2, col3 = st.columns(3)
    
    # Calculate repeat customer rate
    customer_order_counts = filtered_orders.groupby('customer_id').size()
    repeat_customers = (customer_order_counts > 1).sum()
    repeat_rate = (repeat_customers / len(customer_order_counts) * 100) if len(customer_order_counts) > 0 else 0
    
    with col1:
        st.metric("🔄 Repeat Customer Rate", f"{repeat_rate:.1f}%")
    
    with col2:
        avg_orders_per_customer = customer_order_counts.mean()
        st.metric("📊 Avg Orders per Customer", f"{avg_orders_per_customer:.1f}")
    
    with col3:
        avg_customer_value = filtered_orders.groupby('customer_id')['net_amount'].sum().mean()
        st.metric("💰 Avg Customer Value", f"AED {avg_customer_value:,.0f}")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>Souq Leadership Dashboard</strong> | Built with Streamlit | Data updated in real-time</p>
        <p>📧 For questions or support, contact: analytics@souq.com</p>
    </div>
    """, unsafe_allow_html=True)
