# dashboard/app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from forecast_model import FinancialInclusionForecaster
from impact_model import ImpactModel

# Page configuration
st.set_page_config(
    page_title="Ethiopia Financial Inclusion Forecast",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 1.5rem;
        border-left: 5px solid #3B82F6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .forecast-highlight {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'enriched_data.csv')
    return pd.read_csv(data_path)

@st.cache_data
def load_forecasts():
    forecaster = FinancialInclusionForecaster()
    return forecaster.generate_forecast_report()

@st.cache_data
def load_impact_matrix():
    impact_model = ImpactModel()
    return impact_model.create_impact_matrix()

# Sidebar
st.sidebar.title("📊 Dashboard Controls")
st.sidebar.markdown("---")

# Date range selector
st.sidebar.subheader("Date Range")
start_year = st.sidebar.slider(
    "Start Year",
    min_value=2011,
    max_value=2027,
    value=2011,
    step=1
)

end_year = st.sidebar.slider(
    "End Year",
    min_value=2011,
    max_value=2027,
    value=2027,
    step=1
)

# Scenario selector
st.sidebar.subheader("Scenario")
scenario = st.sidebar.radio(
    "Select Forecast Scenario",
    ["Base", "Optimistic", "Pessimistic"],
    index=1
)

# Main content
st.markdown('<h1 class="main-header">📈 Ethiopia Financial Inclusion Forecasting System</h1>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Trends", "🔮 Forecasts", "🎯 Insights"])

with tab1:
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Current Account Ownership (2024)",
            value="49%",
            delta="+3pp from 2021"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Digital Payment Usage (2024)",
            value="35%",
            delta="+12pp from 2021"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Mobile Money Users (2024)",
            value="65M+",
            delta="Telebirr: 54M, M-Pesa: 10M"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="P2P/ATM Ratio (2024)",
            value="1.3x",
            delta="Digital transfers surpassed cash"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Key insights
    st.markdown("### 🎯 Key Insights")
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        st.info("""
        **Access Growth Slowdown**
        - Account ownership grew only +3pp (2021-2024) despite 65M+ mobile money accounts
        - Suggests many accounts are inactive or duplicate
        - Need to focus on usage, not just registration
        """)
        
        st.success("""
        **Digital Payments Accelerating**
        - P2P transfers now exceed ATM withdrawals
        - Mobile money driving payment digitization
        - Infrastructure improving rapidly
        """)
    
    with insights_col2:
        st.warning("""
        **Gender Gap Persists**
        - Women's account ownership lags men by ~10pp
        - Digital divide affects rural women most
        - Targeted interventions needed
        """)
        
        st.error("""
        **Infrastructure Challenges**
        - Rural agent networks still sparse
        - Internet connectivity gaps
        - Power reliability issues
        """)
    
    # Event timeline
    st.markdown("### 📅 Key Events Timeline")
    events = load_data()
    events = events[events['record_type'] == 'event']
    events['date'] = pd.to_datetime(events['observation_date'])
    
    fig = go.Figure()
    
    # Add events as vertical lines
    for _, event in events.iterrows():
        fig.add_vline(
            x=event['date'],
            line_width=2,
            line_dash="dash",
            line_color="orange",
            annotation_text=event['indicator'],
            annotation_position="top right"
        )
    
    fig.update_layout(
        title="Financial Inclusion Events Timeline",
        xaxis_title="Date",
        yaxis_title="",
        height=300,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("### 📈 Trend Analysis")
    
    # Indicator selector
    indicator_options = {
        "ACC_OWNERSHIP": "Account Ownership",
        "USG_DIGITAL_PAYMENT": "Digital Payment Usage",
        "ACC_MM_ACCOUNT": "Mobile Money Accounts",
        "INF_ATM_PER_100K": "ATM Density",
        "INF_AGENT_PER_100K": "Agent Density"
    }
    
    selected_indicators = st.multiselect(
        "Select Indicators to Compare",
        list(indicator_options.keys()),
        default=["ACC_OWNERSHIP", "USG_DIGITAL_PAYMENT"],
        format_func=lambda x: indicator_options[x]
    )
    
    if selected_indicators:
        forecaster = FinancialInclusionForecaster()
        
        fig = go.Figure()
        
        for indicator in selected_indicators:
            historical = forecaster.prepare_time_series(indicator)
            historical = historical[(historical.index.year >= start_year) & (historical.index.year <= end_year)]
            
            fig.add_trace(go.Scatter(
                x=historical.index,
                y=historical.values,
                mode='lines+markers',
                name=indicator_options.get(indicator, indicator),
                line=dict(width=3)
            ))
        
        fig.update_layout(
            title=f"Indicator Trends ({start_year}-{end_year})",
            xaxis_title="Date",
            yaxis_title="Percentage (%) / Per 100k adults",
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Correlation matrix
    st.markdown("### 🔗 Indicator Correlations")
    
    corr_data = load_data()
    numeric_data = corr_data[corr_data['record_type'] == 'observation']
    
    # Pivot to wide format
    pivot_data = numeric_data.pivot_table(
        index='observation_date',
        columns='indicator_code',
        values='value_numeric'
    ).corr()
    
    fig = px.imshow(
        pivot_data,
        text_auto='.2f',
        color_continuous_scale='RdBu',
        title="Correlation Matrix of Financial Inclusion Indicators"
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### 🔮 Financial Inclusion Forecasts")
    
    # Load forecasts
    forecast_report = load_forecasts()
    
    # Scenario description
    scenario_descriptions = {
        "Base": "Current trends continue with expected policy implementation",
        "Optimistic": "Rapid adoption, favorable policies, strong economic growth",
        "Pessimistic": "Slow adoption, regulatory challenges, economic headwinds"
    }
    
    st.markdown(f'<div class="forecast-highlight">', unsafe_allow_html=True)
    st.markdown(f"**Selected Scenario: {scenario}**")
    st.markdown(f"*{scenario_descriptions[scenario]}*")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Forecast visualization
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Account Ownership Forecast")
        
        access_data = forecast_report[forecast_report['indicator_code'] == 'ACC_OWNERSHIP']
        
        fig = go.Figure()
        
        # Historical data
        historical = [49]  # 2024 actual
        
        # Forecast data based on scenario
        if scenario == "Base":
            forecast_values = access_data['augmented'].tolist()
        elif scenario == "Optimistic":
            forecast_values = access_data['optimistic'].tolist()
        else:
            forecast_values = access_data['pessimistic'].tolist()
        
        years = access_data['year'].tolist()
        all_values = historical + forecast_values[1:]  # Skip 2024 from forecast
        
        fig.add_trace(go.Scatter(
            x=years,
            y=all_values,
            mode='lines+markers+text',
            name='Account Ownership',
            line=dict(color='blue', width=3),
            text=[f"{v:.1f}%" for v in all_values],
            textposition="top center"
        ))
        
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Percentage (%)",
            yaxis_range=[40, 70],
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Key milestone
        target_2027 = all_values[-1]
        target_gap = 60 - target_2027  # NFIS-II target is 60%
        
        if target_gap <= 0:
            st.success(f"🎯 **Target Achieved:** Account ownership projected to reach {target_2027:.1f}% by 2027, exceeding NFIS-II target of 60%")
        else:
            st.warning(f"⚠️ **Target Gap:** Account ownership projected at {target_2027:.1f}% by 2027, {target_gap:.1f}pp short of NFIS-II 60% target")
    
    with col2:
        st.markdown("##### Digital Payment Usage Forecast")
        
        usage_data = forecast_report[forecast_report['indicator_code'] == 'USG_DIGITAL_PAYMENT']
        
        fig = go.Figure()
        
        # Historical data
        historical = [35]  # 2024 actual
        
        # Forecast data based on scenario
        if scenario == "Base":
            forecast_values = usage_data['augmented'].tolist()
        elif scenario == "Optimistic":
            forecast_values = usage_data['optimistic'].tolist()
        else:
            forecast_values = usage_data['pessimistic'].tolist()
        
        years = usage_data['year'].tolist()
        all_values = historical + forecast_values[1:]  # Skip 2024 from forecast
        
        fig.add_trace(go.Scatter(
            x=years,
            y=all_values,
            mode='lines+markers+text',
            name='Digital Payment Usage',
            line=dict(color='green', width=3),
            text=[f"{v:.1f}%" for v in all_values],
            textposition="top center"
        ))
        
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Percentage (%)",
            yaxis_range=[30, 65],
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Growth metrics
        growth_2024_2027 = all_values[-1] - all_values[0]
        st.info(f"📈 **Projected Growth (2024-2027):** +{growth_2024_2027:.1f} percentage points")
    
    # Event impact table
    st.markdown("### ⚡ Event Impact Analysis")
    
    impact_matrix = load_impact_matrix()
    
    # Display top impacts
    impact_summary = impact_matrix.abs().sum(axis=1).nlargest(10)
    
    fig = go.Figure(data=[
        go.Bar(
            x=impact_summary.values,
            y=impact_summary.index,
            orientation='h',
            marker_color='indianred'
        )
    ])
    
    fig.update_layout(
        title="Top 10 Events by Total Impact Score",
        xaxis_title="Total Impact Score",
        yaxis_title="Event",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown("### 🎯 Consortium Questions Answered")
    
    # Q1: What drives financial inclusion in Ethiopia?
    st.markdown("#### 1. What drives financial inclusion in Ethiopia?")
    
    drivers_col1, drivers_col2 = st.columns(2)
    
    with drivers_col1:
        st.markdown("""
        **Primary Drivers:**
        
        ✅ **Mobile Money Expansion**
        - Telebirr's rapid growth to 54M users
        - M-Pesa's entry creating competition
        - Interoperability enabling network effects
        
        ✅ **Infrastructure Development**
        - Agent network expansion (40k+ agents)
        - 4G coverage reaching 60%+ population
        - Smartphone penetration increasing
        
        ✅ **Policy Initiatives**
        - NFIS-II implementation
        - Regulatory sandbox for innovation
        - Digital ID (Fayda) rollout
        """)
    
    with drivers_col2:
        st.markdown("""
        **Secondary Enablers:**
        
        🔄 **Payment Use Cases**
        - P2P transfers dominating
        - Merchant payments growing
        - Bill payments digitizing
        
        📱 **Technology Adoption**
        - USSD access for feature phones
        - App-based services for smartphones
        - QR code payments expanding
        
        🤝 **Partnerships**
        - Bank-mobile money interoperability
        - Government payment digitization
        - International remittance channels
        """)
    
    # Q2: How do events affect inclusion outcomes?
    st.markdown("#### 2. How do events affect inclusion outcomes?")
    
    event_analysis = """
    Based on our impact modeling:
    
    **Major Positive Impacts:**
    • **Telebirr Launch (May 2021):** +6pp on mobile money accounts
    • **M-Pesa Entry (Aug 2023):** +2pp on digital payments in first year
    • **Interoperability Launch (2022):** +1.5pp on payment usage
    
    **Policy Impacts:**
    • **NFIS-II Announcement:** Sets framework for +10pp growth target
    • **CBDC Exploration:** Potential +3-5pp if implemented effectively
    • **Digital ID Rollout:** Expected +4pp by simplifying KYC
    
    **Infrastructure Impacts:**
    • **4G Expansion:** Each 10pp increase correlates with +1.5pp digital payments
    • **Agent Network Growth:** 10k new agents = +0.8pp account ownership
    
    **Time Lag Patterns:**
    • Product launches: Immediate registration surge, usage grows over 18 months
    • Policy changes: 6-12 month implementation lag before effects
    • Infrastructure: Gradual effects as coverage expands
    """
    
    st.info(event_analysis)
    
    # Q3: 2025-2027 Outlook
    st.markdown("#### 3. 2025-2027 Financial Inclusion Outlook")
    
    outlook_col1, outlook_col2, outlook_col3 = st.columns(3)
    
    with outlook_col1:
        st.metric(
            label="Account Ownership (2027)",
            value="56.3%",
            delta="+7.3pp from 2024"
        )
        st.caption("Base Scenario Forecast")
    
    with outlook_col2:
        st.metric(
            label="Digital Payments (2027)",
            value="48.7%",
            delta="+13.7pp from 2024"
        )
        st.caption("Base Scenario Forecast")
    
    with outlook_col3:
        st.metric(
            label="Mobile Money Users (2027)",
            value="75M+",
            delta="+10M from 2024"
        )
        st.caption("Estimated")
    
    # Key milestones timeline
    st.markdown("##### Key Projected Milestones")
    
    milestones = pd.DataFrame({
        'Year': [2025, 2026, 2027],
        'Milestone': [
            "Fayda ID reaches 30M registrations",
            "Digital payments surpass 50% adoption",
            "Account ownership approaches 60% target"
        ],
        'Impact': ["High", "Very High", "Critical"]
    })
    
    st.dataframe(milestones, use_container_width=True)
    
    # Risk factors
    st.markdown("##### Key Risks and Uncertainties")
    
    risk_col1, risk_col2 = st.columns(2)
    
    with risk_col1:
        st.error("""
        **Downside Risks:**
        
        🔻 **Economic Factors**
        - Inflation affecting disposable income
        - Currency volatility
        - GDP growth slowdown
        
        🔻 **Regulatory Challenges**
        - KYC requirements too stringent
        - Interoperability delays
        - Tax policies on digital transactions
        """)
    
    with risk_col2:
        st.success("""
        **Upside Opportunities:**
        
        🔺 **Technology Adoption**
        - Smartphone penetration acceleration
        - AI-powered financial services
        - Blockchain applications
        
        🔺 **Policy Initiatives**
        - Government payment digitization
        - Social protection digitization
        - Cross-border payment integration
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>Developed by Selam Analytics | Data Source: World Bank Global Findex, NBE, GSMA, EthSwitch</p>
    <p>Forecast Period: 2025-2027 | Last Updated: February 2026</p>
</div>
""", unsafe_allow_html=True)

# Download functionality
st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 Data Export")

if st.sidebar.button("Download Forecast Data"):
    forecast_report = load_forecasts()
    csv = forecast_report.to_csv(index=False)
    st.sidebar.download_button(
        label="Download CSV",
        data=csv,
        file_name="ethiopia_fi_forecasts_2025_2027.csv",
        mime="text/csv"
    )