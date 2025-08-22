import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration - Professional investor dashboard
st.set_page_config(
    page_title="Vahan Vehicle Analytics Dashboard", 
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #1f77b4; margin-bottom: 0;}
    .sub-header {color: #2ca02c; font-weight: 600; margin-top: 1rem;}
    .metric-card {background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid #1f77b4;}
    .insight-box {background-color: #e8f4f8; padding: 15px; border-radius: 10px; margin: 10px 0; color: #333;}
    .success-box {background-color: #d4edda; padding: 15px; border-radius: 10px; margin: 10px 0; color: #155724; border: 1px solid #c3e6cb;}
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<h1 class="main-header">🚗 Vahan Vehicle Registration Analytics</h1>', unsafe_allow_html=True)
st.markdown("**Investor Dashboard | Year-over-Year Growth Analysis | Market Intelligence**")

# Function to load cleaned data
@st.cache_data
def load_clean_data():
    all_data = []
    years = [2021, 2022, 2023, 2024]  # Removed 2025 as requested
    
    for year in years:
        filename = f"vahan_data_{year}.csv"
        if os.path.exists(filename):
            try:
                # Simple read - no skiprows needed now
                df = pd.read_csv(filename, encoding='latin1')
                
                # Name the columns properly - ADAPTIVE VERSION
                expected_columns = ['SNo', 'Manufacturer', 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
                                  'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC', 'TOTAL']

                # Use only the columns that actually exist
                actual_columns = []
                for i, col_name in enumerate(expected_columns):
                    if i < len(df.columns):
                        actual_columns.append(col_name)
                    else:
                        break

                # Keep any extra columns as they are
                df.columns = actual_columns + list(df.columns[len(actual_columns):])
                
                # Melt to long format
                months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
                available_months = [col for col in months if col in df.columns]
                
                df_long = df.melt(
                    id_vars=['SNo', 'Manufacturer'],
                    value_vars=available_months,
                    var_name='Month',
                    value_name='Registrations'
                )
                
                # Clean data
                df_long['Registrations'] = pd.to_numeric(df_long['Registrations'], errors='coerce')
                df_long = df_long.dropna(subset=['Registrations'])
                
                # Add year and clean names
                df_long['Year'] = year
                df_long['Manufacturer'] = df_long['Manufacturer'].astype(str).str.strip()
                
                # Map months to numbers
                month_map = {'JAN':1, 'FEB':2, 'MAR':3, 'APR':4, 'MAY':5, 'JUN':6,
                           'JUL':7, 'AUG':8, 'SEP':9, 'OCT':10, 'NOV':11, 'DEC':12}
                df_long['Month_Num'] = df_long['Month'].map(month_map)
                df_long['Date'] = pd.to_datetime(df_long['Year'].astype(str) + '-' + df_long['Month_Num'].astype(str) + '-01')
                
                all_data.append(df_long)
                st.sidebar.success(f"✅ {year}: {len(df_long):,} records")
                
            except Exception as e:
                st.sidebar.error(f"❌ {year}: {str(e)}")
        else:
            st.sidebar.warning(f"⚠️ {year}: File not found")
    
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

# Load data
with st.spinner("🔄 Loading and processing data..."):
    df = load_clean_data()

if df.empty:
    st.error("No data loaded. Please check your files.")
    st.stop()

# Display success
st.markdown(f'<div class="success-box">✅ Successfully loaded {len(df):,} records from {df["Year"].min()}-{df["Year"].max()}</div>', unsafe_allow_html=True)

# Calculate key metrics
total_registrations = df['Registrations'].sum()
unique_manufacturers = df['Manufacturer'].nunique()
years_covered = f"{df['Year'].min()}-{df['Year'].max()}"

# Create quarterly data
df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)

# Display key metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Total Registrations", f"{total_registrations:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)
    
with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Manufacturers", f"{unique_manufacturers:,}")
    st.markdown('</div>', unsafe_allow_html=True)
    
with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Time Period", years_covered)
    st.markdown('</div>', unsafe_allow_html=True)
    
with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    avg_monthly = total_registrations / len(df['Date'].unique())
    st.metric("Avg Monthly", f"{avg_monthly:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)

# Main analysis tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Growth Trends", "🏭 Market Analysis", "📊 Quarterly View", "💡 Investment Insights"])

with tab1:
    st.markdown('<h3 class="sub-header">Year-over-Year Growth Analysis</h3>', unsafe_allow_html=True)
    
    # YoY growth
    yearly_data = df.groupby('Year')['Registrations'].sum().reset_index()
    yearly_data['YoY_Growth'] = yearly_data['Registrations'].pct_change() * 100
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(yearly_data, x='Year', y='Registrations', 
                    title="Total Yearly Registrations", color='Year')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.line(yearly_data, x='Year', y='YoY_Growth', markers=True,
                     title="Year-over-Year Growth %", labels={'YoY_Growth': 'Growth %'})
        fig.add_hline(y=0, line_dash="dash", line_color="red")
        st.plotly_chart(fig, use_container_width=True)
        
    # Show growth metrics
    growth_col1, growth_col2, growth_col3 = st.columns(3)
    with growth_col1:
        avg_growth = yearly_data['YoY_Growth'].mean()
        st.metric("Average YoY Growth", f"{avg_growth:.1f}%")
    
    with growth_col2:
        latest_growth = yearly_data['YoY_Growth'].iloc[-1]
        st.metric("Latest YoY Growth", f"{latest_growth:.1f}%")
    
    with growth_col3:
        total_growth = ((yearly_data['Registrations'].iloc[-1] - yearly_data['Registrations'].iloc[0]) / 
                       yearly_data['Registrations'].iloc[0]) * 100
        st.metric("Total 4-Year Growth", f"{total_growth:.1f}%")

with tab2:
    st.markdown('<h3 class="sub-header">Market Share Analysis</h3>', unsafe_allow_html=True)
    
    # Top manufacturers
    top_manufacturers = df.groupby('Manufacturer')['Registrations'].sum().nlargest(10).reset_index()
    top_manufacturers['Market_Share'] = (top_manufacturers['Registrations'] / total_registrations) * 100
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(top_manufacturers, x='Registrations', y='Manufacturer', orientation='h',
                    title="Top 10 Manufacturers by Volume", color='Registrations')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(top_manufacturers, values='Market_Share', names='Manufacturer',
                    title="Market Share Distribution", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    # Manufacturer growth analysis
    st.markdown('<h4 class="sub-header">Manufacturer Growth Rates</h4>', unsafe_allow_html=True)
    manufacturer_growth = df.groupby(['Year', 'Manufacturer'])['Registrations'].sum().reset_index()
    manufacturer_growth['YoY_Growth'] = manufacturer_growth.groupby('Manufacturer')['Registrations'].pct_change() * 100
    
    top_growth = manufacturer_growth.groupby('Manufacturer')['YoY_Growth'].mean().nlargest(5).reset_index()
    fig = px.bar(top_growth, x='YoY_Growth', y='Manufacturer', orientation='h',
                title="Top 5 Manufacturers by Average YoY Growth", color='YoY_Growth')
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown('<h3 class="sub-header">Quarterly Analysis (QoQ)</h3>', unsafe_allow_html=True)
    
    # Quarterly analysis
    quarterly_data = df.groupby(['Year', 'Quarter'])['Registrations'].sum().reset_index()
    quarterly_data['QoQ_Growth'] = quarterly_data['Registrations'].pct_change() * 100
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(quarterly_data, x='Quarter', y='Registrations', color='Year',
                    title="Quarterly Registration Volumes", barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.line(quarterly_data, x='Quarter', y='QoQ_Growth', markers=True,
                     title="Quarter-over-Quarter Growth %", color='Year')
        fig.add_hline(y=0, line_dash="dash", line_color="red")
        st.plotly_chart(fig, use_container_width=True)
    
    # Seasonal analysis
    st.markdown('<h4 class="sub-header">Seasonal Patterns</h4>', unsafe_allow_html=True)
    monthly_avg = df.groupby('Month_Num')['Registrations'].mean().reset_index()
    fig = px.line(monthly_avg, x='Month_Num', y='Registrations', markers=True,
                 title="Average Monthly Registration Pattern", labels={'Month_Num': 'Month'})
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown('<h3 class="sub-header">Investment Insights & Recommendations</h3>', unsafe_allow_html=True)
    
    # Calculate insights
    yearly_data = df.groupby('Year')['Registrations'].sum().reset_index()
    avg_yoy_growth = yearly_data['Registrations'].pct_change().mean() * 100
    latest_growth = yearly_data['Registrations'].pct_change().iloc[-1] * 100
    
    top_5_share = df.groupby('Manufacturer')['Registrations'].sum().nlargest(5).sum() / total_registrations * 100
    
    insights = [
        f"🚀 **Strong Market Growth**: Average YoY growth of {avg_yoy_growth:.1f}% indicates healthy market expansion",
        f"🏭 **Market Concentration**: Top 5 manufacturers control {top_5_share:.1f}% of total market share",
        f"📈 **Consistent Performance**: {latest_growth:.1f}% growth in latest year shows sustained demand",
        "💰 **Stable Investment**: Consistent quarterly patterns suggest market maturity and reduced volatility",
        "🔋 **Growth Opportunities**: Emerging manufacturers showing above-average growth rates present acquisition targets",
        "📊 **Data-Driven Decisions**: Use quarterly trends for optimal investment timing and portfolio balancing"
    ]
    
    for insight in insights:
        st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)
    
    # Investment recommendations
    st.markdown('<h4 class="sub-header">🎯 Investment Recommendations</h4>', unsafe_allow_html=True)
    
    rec_col1, rec_col2 = st.columns(2)
    
    with rec_col1:
        st.info("""
        **Short-Term Strategy (1-2 years):**
        - Focus on top 3 market leaders for stability
        - Monitor high-growth emerging manufacturers
        - Consider Q1-Q2 for entry points (seasonal lows)
        """)
    
    with rec_col2:
        st.info("""
        **Long-Term Strategy (3-5 years):**
        - Diversify across multiple manufacturers
        - Watch electric vehicle segment growth
        - Consider geographic expansion patterns
        """)

# Data download section
st.markdown("---")
st.markdown('<h3 class="sub-header">📊 Data Export</h3>', unsafe_allow_html=True)

csv = df.to_csv(index=False)
st.download_button(
    label="📥 Download Processed Data (CSV)",
    data=csv,
    file_name="vahan_vehicle_analysis_2021_2024.csv",
    mime="text/csv",
    help="Download the complete analyzed dataset for further analysis"
)

# Raw data preview
with st.expander("📋 View Raw Data Preview"):
    st.dataframe(df.head(10))
    st.write(f"**Total records:** {len(df):,}")
    st.write(f"**Columns:** {list(df.columns)}")

# Footer
st.markdown("---")
st.markdown("**Data Source**: Vahan Dashboard (vahan.parivahan.gov.in) | **Analysis Period**: 2021-2024")
st.markdown("*This dashboard provides investor analytics based on public vehicle registration data*")

# Refresh button
if st.button("🔄 Refresh Analysis"):
    st.cache_data.clear()
    st.experimental_rerun()