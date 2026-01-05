# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="SouqPlus Executive Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1f77b4;
        padding-bottom: 20px;
    }
    h2 {
        color: #2c3e50;
        padding-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Data Generation Functions
@st.cache_data
def generate_sample_data():
    """Generate comprehensive sample data for SouqPlus"""
    np.random.seed(42)
    
    # Date range
    dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
    
    # Cities and Channels
    cities = ['Riyadh', 'Jeddah', 'Dammam', 'Mecca', 'Medina']
    channels = ['Mobile App', 'Website', 'Social Media', 'Marketplace']
    categories = ['Electronics', 'Fashion', 'Home & Kitchen', 'Beauty', 'Sports', 'Books']
    fulfillment_centers = ['FC_Riyadh', 'FC_Jeddah', 'FC_Dammam']
    
    # Generate orders data
    orders_data = []
    for date in dates:
        for city in cities:
            for channel in channels:
                for category in categories:
                    # Base orders with trends
                    base_orders = np.random.poisson(50)
                    
                    # Add city weight
                    city_weight = {'Riyadh': 1.5, 'Jeddah': 1.3, 'Dammam': 1.0, 'Mecca': 0.8, 'Medina': 0.7}
                    orders = int(base_orders * city_weight[city])
                    
                    # Revenue calculation
                    avg_order_value = np.random.uniform(100, 500)
                    revenue = orders * avg_order_value
                    
                    # Delivery metrics
                    delivered = int(orders * np.random.uniform(0.85, 0.95))
                    cancelled = int(orders * np.random.uniform(0.02, 0.08))
                    returned = int(delivered * np.random.uniform(0.05, 0.15))
                    
                    # Delivery time
                    avg_delivery_time = np.random.uniform(24, 72)
                    
                    # Fulfillment center
                    fc = np.random.choice(fulfillment_centers)
                    
                    orders_data.append({
                        'date': date,
                        'city': city,
                        'channel': channel,
                        'category': category,
                        'fulfillment_center': fc,
                        'orders': orders,
                        'revenue': revenue,
                        'delivered': delivered,
                        'cancelled': cancelled,
                        'returned': returned,
                        'avg_delivery_time': avg_delivery_time,
                        'avg_order_value': avg_order_value
                    })
    
    df = pd.DataFrame(orders_data)
    
    # Calculate additional metrics
    df['delivery_rate'] = (df['delivered'] / df['orders'] * 100).round(2)
    df['cancellation_rate'] = (df['cancelled'] / df['orders'] * 100).round(2)
    df['return_rate'] = (df['returned'] / df['delivered'] * 100).round(2)
    
    return df

# Load data
df = generate_sample_data()

# Sidebar Filters
st.sidebar.title("🔍 Filters")
st.sidebar.markdown("---")

# Date range filter
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(df['date'].min(), df['date'].max()),
    min_value=df['date'].min(),
    max_value=df['date'].max()
)

# City filter
cities = st.sidebar.multiselect(
    "Select Cities",
    options=df['city'].unique(),
    default=df['city'].unique()
)

# Channel filter
channels = st.sidebar.multiselect(
    "Select Channels",
    options=df['channel'].unique(),
    default=df['channel'].unique()
)

# Category filter
categories = st.sidebar.multiselect(
    "Select Categories",
    options=df['category'].unique(),
    default=df['category'].unique()
)

# Apply filters
if len(date_range) == 2:
    mask = (
        (df['date'] >= pd.to_datetime(date_range[0])) &
        (df['date'] <= pd.to_datetime(date_range[1])) &
        (df['city'].isin(cities)) &
        (df['channel'].isin(channels)) &
        (df['category'].isin(categories))
    )
    filtered_df = df[mask]
else:
    filtered_df = df

# Main Dashboard
st.title("📊 SouqPlus Executive Dashboard")
st.markdown("### Unified Business Performance & Operational Health Monitor")
st.markdown("---")

# Key Metrics Row
col1, col2, col3, col4, col5 = st.columns(5)

total_orders = filtered_df['orders'].sum()
total_revenue = filtered_df['revenue'].sum()
avg_order_value = filtered_df['revenue'].sum() / filtered_df['orders'].sum() if filtered_df['orders'].sum() > 0 else 0
overall_delivery_rate = (filtered_df['delivered'].sum() / filtered_df['orders'].sum() * 100) if filtered_df['orders'].sum() > 0 else 0
overall_cancellation_rate = (filtered_df['cancelled'].sum() / filtered_df['orders'].sum() * 100) if filtered_df['orders'].sum() > 0 else 0

with col1:
    st.metric(
        label="Total Orders",
        value=f"{total_orders:,.0f}",
        delta=f"{(total_orders / len(filtered_df['date'].unique())):.0f} per day"
    )

with col2:
    st.metric(
        label="Total Revenue",
        value=f"${total_revenue:,.0f}",
        delta=f"${(total_revenue / len(filtered_df['date'].unique())):.0f} per day"
    )

with col3:
    st.metric(
        label="Avg Order Value",
        value=f"${avg_order_value:.2f}",
        delta="2.3%" if avg_order_value > 250 else "-1.2%"
    )

with col4:
    st.metric(
        label="Delivery Rate",
        value=f"{overall_delivery_rate:.1f}%",
        delta=f"{overall_delivery_rate - 90:.1f}%"
    )

with col5:
    st.metric(
        label="Cancellation Rate",
        value=f"{overall_cancellation_rate:.1f}%",
        delta=f"{overall_cancellation_rate - 5:.1f}%",
        delta_color="inverse"
    )

st.markdown("---")

# Row 1: Revenue Trends and City Performance
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Revenue Trend Over Time")
    daily_revenue = filtered_df.groupby('date').agg({
        'revenue': 'sum',
        'orders': 'sum'
    }).reset_index()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=daily_revenue['date'], y=daily_revenue['revenue'], 
                   name="Revenue", line=dict(color='#1f77b4', width=3),
                   fill='tozeroy'),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(x=daily_revenue['date'], y=daily_revenue['orders'], 
                   name="Orders", line=dict(color='#ff7f0e', width=2)),
        secondary_y=True
    )
    
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Revenue ($)", secondary_y=False)
    fig.update_yaxes(title_text="Orders", secondary_y=True)
    fig.update_layout(height=400, hovermode='x unified')
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🏙️ Top Cities by Revenue")
    city_performance = filtered_df.groupby('city').agg({
        'revenue': 'sum',
        'orders': 'sum'
    }).reset_index().sort_values('revenue', ascending=False)
    
    fig = px.bar(city_performance, x='revenue', y='city', 
                 orientation='h',
                 color='revenue',
                 color_continuous_scale='Blues',
                 text='revenue')
    fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig.update_layout(height=400, showlegend=False, xaxis_title="Revenue ($)", yaxis_title="")
    
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Row 2: Channel Performance and Category Analysis
col1, col2 = st.columns(2)

with col1:
    st.subheader("📱 Channel Performance")
    channel_performance = filtered_df.groupby('channel').agg({
        'revenue': 'sum',
        'orders': 'sum',
        'delivered': 'sum',
        'cancelled': 'sum'
    }).reset_index()
    
    channel_performance['delivery_rate'] = (channel_performance['delivered'] / channel_performance['orders'] * 100).round(2)
    channel_performance['cancellation_rate'] = (channel_performance['cancelled'] / channel_performance['orders'] * 100).round(2)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Revenue',
        x=channel_performance['channel'],
        y=channel_performance['revenue'],
        marker_color='lightblue',
        yaxis='y',
        offsetgroup=1
    ))
    
    fig.add_trace(go.Scatter(
        name='Delivery Rate',
        x=channel_performance['channel'],
        y=channel_performance['delivery_rate'],
        marker_color='green',
        yaxis='y2',
        mode='lines+markers',
        line=dict(width=3)
    ))
    
    fig.update_layout(
        yaxis=dict(title='Revenue ($)'),
        yaxis2=dict(title='Delivery Rate (%)', overlaying='y', side='right'),
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🛍️ Category Performance")
    category_performance = filtered_df.groupby('category').agg({
        'revenue': 'sum',
        'orders': 'sum'
    }).reset_index().sort_values('revenue', ascending=False)
    
    fig = px.pie(category_performance, values='revenue', names='category',
                 hole=0.4,
                 color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Row 3: Operational Health Metrics
st.subheader("🚚 Operational Health Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### Delivery Performance by City")
    city_ops = filtered_df.groupby('city').agg({
        'orders': 'sum',
        'delivered': 'sum',
        'cancelled': 'sum',
        'avg_delivery_time': 'mean'
    }).reset_index()
    
    city_ops['delivery_rate'] = (city_ops['delivered'] / city_ops['orders'] * 100).round(2)
    city_ops = city_ops.sort_values('delivery_rate', ascending=True)
    
    fig = px.bar(city_ops, y='city', x='delivery_rate',
                 orientation='h',
                 color='delivery_rate',
                 color_continuous_scale=['red', 'yellow', 'green'],
                 text='delivery_rate')
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(height=350, showlegend=False, xaxis_title="Delivery Rate (%)")
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Average Delivery Time by FC")
    fc_performance = filtered_df.groupby('fulfillment_center').agg({
        'avg_delivery_time': 'mean',
        'orders': 'sum'
    }).reset_index()
    
    fig = px.bar(fc_performance, x='fulfillment_center', y='avg_delivery_time',
                 color='avg_delivery_time',
                 color_continuous_scale=['green', 'yellow', 'red'],
                 text='avg_delivery_time')
    fig.update_traces(texttemplate='%{text:.1f}h', textposition='outside')
    fig.update_layout(height=350, showlegend=False, 
                     xaxis_title="Fulfillment Center", 
                     yaxis_title="Avg Delivery Time (hours)")
    
    st.plotly_chart(fig, use_container_width=True)

with col3:
    st.markdown("#### Return Rate by Category")
    category_returns = filtered_df.groupby('category').agg({
        'delivered': 'sum',
        'returned': 'sum'
    }).reset_index()
    
    category_returns['return_rate'] = (category_returns['returned'] / category_returns['delivered'] * 100).round(2)
    category_returns = category_returns.sort_values('return_rate', ascending=False)
    
    fig = px.bar(category_returns, x='category', y='return_rate',
                 color='return_rate',
                 color_continuous_scale=['green', 'yellow', 'red'],
                 text='return_rate')
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(height=350, showlegend=False, 
                     xaxis_title="Category", 
                     yaxis_title="Return Rate (%)")
    
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Row 4: Detailed Performance Tables
st.subheader("📋 Detailed Performance Analysis")

tab1, tab2, tab3, tab4 = st.tabs(["City Analysis", "Channel Analysis", "Category Analysis", "Fulfillment Centers"])

with tab1:
    city_detail = filtered_df.groupby('city').agg({
        'orders': 'sum',
        'revenue': 'sum',
        'delivered': 'sum',
        'cancelled': 'sum',
        'returned': 'sum',
        'avg_delivery_time': 'mean',
        'avg_order_value': 'mean'
    }).reset_index()
    
    city_detail['delivery_rate'] = (city_detail['delivered'] / city_detail['orders'] * 100).round(2)
    city_detail['cancellation_rate'] = (city_detail['cancelled'] / city_detail['orders'] * 100).round(2)
    city_detail['return_rate'] = (city_detail['returned'] / city_detail['delivered'] * 100).round(2)
    
    city_detail = city_detail.sort_values('revenue', ascending=False)
    
    # Format columns
    city_detail['revenue'] = city_detail['revenue'].apply(lambda x: f"${x:,.0f}")
    city_detail['avg_order_value'] = city_detail['avg_order_value'].apply(lambda x: f"${x:.2f}")
    city_detail['avg_delivery_time'] = city_detail['avg_delivery_time'].apply(lambda x: f"{x:.1f}h")
    
    st.dataframe(city_detail, use_container_width=True, height=300)

with tab2:
    channel_detail = filtered_df.groupby('channel').agg({
        'orders': 'sum',
        'revenue': 'sum',
        'delivered': 'sum',
        'cancelled': 'sum',
        'returned': 'sum',
        'avg_order_value': 'mean'
    }).reset_index()
    
    channel_detail['delivery_rate'] = (channel_detail['delivered'] / channel_detail['orders'] * 100).round(2)
    channel_detail['cancellation_rate'] = (channel_detail['cancelled'] / channel_detail['orders'] * 100).round(2)
    channel_detail['return_rate'] = (channel_detail['returned'] / channel_detail['delivered'] * 100).round(2)
    
    channel_detail = channel_detail.sort_values('revenue', ascending=False)
    
    channel_detail['revenue'] = channel_detail['revenue'].apply(lambda x: f"${x:,.0f}")
    channel_detail['avg_order_value'] = channel_detail['avg_order_value'].apply(lambda x: f"${x:.2f}")
    
    st.dataframe(channel_detail, use_container_width=True, height=300)

with tab3:
    category_detail = filtered_df.groupby('category').agg({
        'orders': 'sum',
        'revenue': 'sum',
        'delivered': 'sum',
        'cancelled': 'sum',
        'returned': 'sum',
        'avg_order_value': 'mean'
    }).reset_index()
    
    category_detail['delivery_rate'] = (category_detail['delivered'] / category_detail['orders'] * 100).round(2)
    category_detail['cancellation_rate'] = (category_detail['cancelled'] / category_detail['orders'] * 100).round(2)
    category_detail['return_rate'] = (category_detail['returned'] / category_detail['delivered'] * 100).round(2)
    
    category_detail = category_detail.sort_values('revenue', ascending=False)
    
    category_detail['revenue'] = category_detail['revenue'].apply(lambda x: f"${x:,.0f}")
    category_detail['avg_order_value'] = category_detail['avg_order_value'].apply(lambda x: f"${x:.2f}")
    
    st.dataframe(category_detail, use_container_width=True, height=300)

with tab4:
    fc_detail = filtered_df.groupby('fulfillment_center').agg({
        'orders': 'sum',
        'delivered': 'sum',
        'cancelled': 'sum',
        'avg_delivery_time': 'mean'
    }).reset_index()
    
    fc_detail['delivery_rate'] = (fc_detail['delivered'] / fc_detail['orders'] * 100).round(2)
    fc_detail['cancellation_rate'] = (fc_detail['cancelled'] / fc_detail['orders'] * 100).round(2)
    fc_detail['avg_delivery_time'] = fc_detail['avg_delivery_time'].apply(lambda x: f"{x:.1f}h")
    
    fc_detail = fc_detail.sort_values('orders', ascending=False)
    
    st.dataframe(fc_detail, use_container_width=True, height=300)

st.markdown("---")

# Footer with insights
st.subheader("💡 Key Insights & Recommendations")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **Growth Drivers:**
    - Top performing city: Riyadh
    - Best channel: Mobile App
    - Highest revenue category: Electronics
    """)

with col2:
    st.warning("""
    **Areas of Concern:**
    - High return rates in Fashion category
    - Delivery delays in certain FCs
    - Cancellation rates above target in some cities
    """)

with col3:
    st.success("""
    **Recommendations:**
    - Optimize FC operations in underperforming centers
    - Investigate root causes of returns
    - Expand successful channel strategies
    """)

# Sidebar info
st.sidebar.markdown("---")
st.sidebar.info("""
**Dashboard Features:**
- Real-time performance metrics
- Multi-dimensional filtering
- Operational health monitoring
- Detailed drill-down analysis
""")

st.sidebar.markdown("---")
st.sidebar.markdown("**Last Updated:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
