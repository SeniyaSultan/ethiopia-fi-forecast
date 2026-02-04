# %% [markdown]
# # Task 4: Forecasting Access and Usage - Ethiopia Financial Inclusion
# 
# ## Executive Summary
# This notebook forecasts Ethiopia's financial inclusion indicators for 2025-2027, focusing on:
# 1. **Account Ownership Rate** (Access)
# 2. **Digital Payment Usage** (Usage)
# 
# ## Key Questions Addressed
# - What will be Ethiopia's financial inclusion rate in 2025-2027?
# - How do different scenarios affect the forecasts?
# - What are the key drivers and uncertainties?
# 
# ## Import Libraries

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import custom models
import sys
sys.path.append('../src')

from forecast_model import FinancialInclusionForecaster
from impact_model import ImpactModel

# Set visualization style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("✅ Libraries imported successfully!")

# %% [markdown]
# ## 1. Initialize Models and Load Data

# %%
# Initialize models
print("Initializing models...")
try:
    forecaster = FinancialInclusionForecaster()
    impact_model = ImpactModel()

    print(f"
📊 Data Summary:")
    print(f"• Total observations: {len(forecaster.observations)}")
    print(f"• Key indicators available:")

    # List available indicators
    indicators = forecaster.observations['indicator_code'].unique()
    for idx, indicator in enumerate(indicators[:10]):
        if pd.notna(indicator):
            count = len(forecaster.observations[forecaster.observations['indicator_code'] == indicator])
            print(f"  {idx+1}. {indicator}: {count} data points")

except Exception as e:
    print(f"❌ Error initializing models: {e}")
    print("Trying alternative path...")

    # Try with explicit path
    try:
        forecaster = FinancialInclusionForecaster('data/processed/enriched_data.csv')
        impact_model = ImpactModel('data/processed/enriched_data.csv')
        print("✅ Models initialized with explicit path")
    except Exception as e2:
        print(f"❌ Still failed: {e2}")
        raise

# %% [markdown]
# ## 2. Explore Historical Data

# %%
# Get key indicators
key_indicators = ['ACC_OWNERSHIP', 'USG_DIGITAL_PAYMENT', 'ACC_MM_ACCOUNT']

print("🔍 Exploring Historical Data:")
print("=" * 50)

for indicator in key_indicators:
    # Get data for this indicator
    data = forecaster.observations[forecaster.observations['indicator_code'] == indicator]

    if len(data) > 0:
        print(f"
📊 {indicator}:")
        print(f"   • Data points: {len(data)}")
        print(f"   • Date range: {data['observation_date'].min().date()} to {data['observation_date'].max().date()}")
        print(f"   • Values: {', '.join([f'{v:.1f}%' for v in data['value_numeric'].values])}")

# %% [markdown]
# ## 3. Prepare Time Series Data

# %%
# Prepare time series for key indicators
print("
📈 Preparing Time Series Data:")
print("=" * 50)

time_series_data = {}

for indicator in key_indicators:
    series = forecaster.prepare_time_series(indicator)

    if len(series) > 0:
        time_series_data[indicator] = series
        print(f"
✅ {indicator}:")
        print(f"   • Time series length: {len(series)} months")
        print(f"   • Date range: {series.index[0].date()} to {series.index[-1].date()}")
        print(f"   • 2024 value: {series[series.index.year == 2024].mean():.1f}%" if any(series.index.year == 2024) else "   • Latest value: {series.iloc[-1]:.1f}%")
    else:
        print(f"
⚠️ No data for {indicator}")

# %% [markdown]
# ## 4. Baseline Forecasting

# %%
# Generate baseline forecasts
print("
" + "="*60)
print("BASELINE FORECASTS (2025-2027)")
print("="*60)

# Forecast Account Ownership
print("
1. 📊 Account Ownership Forecast:")
account_forecast = forecaster.baseline_forecast('ACC_OWNERSHIP', years_ahead=3)

if account_forecast:
    print(f"   ✅ Forecast generated successfully")

    # Display historical values
    print(f"
   Historical Values:")
    historical = account_forecast['historical']
    for year in [2011, 2014, 2017, 2021, 2024]:
        year_data = historical[historical.index.year == year]
        if not year_data.empty:
            print(f"     {year}: {year_data.mean():.1f}%")

    # Display forecast values
    print(f"
   Forecast Values:")
    for year in [2025, 2026, 2027]:
        forecast_data = account_forecast['forecast'][account_forecast['forecast'].index.year == year]
        if not forecast_data.empty:
            mean_value = forecast_data.mean()
            lower_bound = account_forecast['lower_bound'][account_forecast['lower_bound'].index.year == year].mean()
            upper_bound = account_forecast['upper_bound'][account_forecast['upper_bound'].index.year == year].mean()

            print(f"     {year}: {mean_value:.1f}% (95% CI: {lower_bound:.1f}% - {upper_bound:.1f}%)")

# %% [markdown]
# ## 5. Forecast Digital Payment Usage

# %%
print("
2. 📱 Digital Payment Usage Forecast:")
payment_forecast = forecaster.baseline_forecast('USG_DIGITAL_PAYMENT', years_ahead=3)

if payment_forecast:
    print(f"   ✅ Forecast generated successfully")

    # Display forecast values
    print(f"
   Forecast Values:")
    for year in [2025, 2026, 2027]:
        forecast_data = payment_forecast['forecast'][payment_forecast['forecast'].index.year == year]
        if not forecast_data.empty:
            mean_value = forecast_data.mean()
            lower_bound = payment_forecast['lower_bound'][payment_forecast['lower_bound'].index.year == year].mean()
            upper_bound = payment_forecast['upper_bound'][payment_forecast['upper_bound'].index.year == year].mean()

            print(f"     {year}: {mean_value:.1f}% (95% CI: {lower_bound:.1f}% - {upper_bound:.1f}%)")

# %% [markdown]
# ## 6. Scenario Analysis

# %%
print("
" + "="*60)
print("SCENARIO ANALYSIS")
print("="*60)

# Generate scenario forecasts
print("
🔮 Account Ownership Scenarios:")
account_scenarios = forecaster.scenario_forecast('ACC_OWNERSHIP', years_ahead=3)

if account_scenarios:
    for scenario_name, data in account_scenarios.items():
        print(f"
   {scenario_name.upper()} Scenario:")
        print(f"     Description: {data['description']}")
        if data['final_value_2027']:
            print(f"     2027 Forecast: {data['final_value_2027']:.1f}%")

print("
🔮 Digital Payment Usage Scenarios:")
payment_scenarios = forecaster.scenario_forecast('USG_DIGITAL_PAYMENT', years_ahead=3)

if payment_scenarios:
    for scenario_name, data in payment_scenarios.items():
        print(f"
   {scenario_name.upper()} Scenario:")
        print(f"     Description: {data['description']}")
        if data['final_value_2027']:
            print(f"     2027 Forecast: {data['final_value_2027']:.1f}%")

# %% [markdown]
# ## 7. Event Impact Analysis

# %%
print("
" + "="*60)
print("EVENT IMPACT ANALYSIS")
print("="*60)

# Create impact matrix
impact_matrix = impact_model.create_impact_matrix()

if not impact_matrix.empty:
    print(f"
📋 Impact Matrix Shape: {impact_matrix.shape}")

    # Show top events by total impact
    impact_matrix['Total_Impact'] = impact_matrix.abs().sum(axis=1)
    top_events = impact_matrix.nlargest(3, 'Total_Impact')

    print(f"
🏆 Top 3 Events by Impact:")
    for event_name, row in top_events.iterrows():
        print(f"
   {event_name}:")
        print(f"     Total Impact Score: {row['Total_Impact']:.2f}")

        # Get specific impacts
        for indicator in ['ACC_OWNERSHIP', 'USG_DIGITAL_PAYMENT']:
            if indicator in row.index and abs(row[indicator]) > 0:
                direction = "positive" if row[indicator] > 0 else "negative"
                print(f"     {indicator}: {direction} ({abs(row[indicator]):.2f})")

# %% [markdown]
# ## 8. Visualization of Forecasts

# %%
# Create forecast visualizations
print("
" + "="*60)
print("VISUALIZING FORECASTS")
print("="*60)

# Plot Account Ownership Forecast
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

if account_forecast:
    ax = axes[0]

    # Plot historical data
    historical = account_forecast['historical']
    ax.plot(historical.index, historical.values, 'o-', linewidth=2, 
            markersize=6, label='Historical', color='#2c3e50', alpha=0.8)

    # Plot forecast
    forecast = account_forecast['forecast']
    ax.plot(forecast.index, forecast.values, '--', linewidth=3, 
            label='Forecast', color='#3498db')

    # Plot confidence interval
    ax.fill_between(forecast.index,
                   account_forecast['lower_bound'].values,
                   account_forecast['upper_bound'].values,
                   alpha=0.2, color='#3498db', label='95% CI')

    # Add NFIS-II target
    ax.axhline(y=60, color='red', linestyle=':', linewidth=2, 
               alpha=0.7, label='NFIS-II Target (60%)')

    ax.set_title('Account Ownership Forecast', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=11)
    ax.set_ylabel('Percentage (%)', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left')

    # Add annotations
    ax.annotate(f'2024: {historical[historical.index.year == 2024].mean():.1f}%', 
                xy=(0.05, 0.95), xycoords='axes fraction',
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    ax.annotate(f'2027 Forecast: {forecast[forecast.index.year == 2027].mean():.1f}%', 
                xy=(0.05, 0.85), xycoords='axes fraction',
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

if payment_forecast:
    ax = axes[1]

    # Plot historical data
    historical = payment_forecast['historical']
    ax.plot(historical.index, historical.values, 'o-', linewidth=2, 
            markersize=6, label='Historical', color='#2c3e50', alpha=0.8)

    # Plot forecast
    forecast = payment_forecast['forecast']
    ax.plot(forecast.index, forecast.values, '--', linewidth=3, 
            label='Forecast', color='#2ecc71')

    # Plot confidence interval
    ax.fill_between(forecast.index,
                   payment_forecast['lower_bound'].values,
                   payment_forecast['upper_bound'].values,
                   alpha=0.2, color='#2ecc71', label='95% CI')

    ax.set_title('Digital Payment Usage Forecast', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=11)
    ax.set_ylabel('Percentage (%)', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left')

    # Add annotations
    ax.annotate(f'2024: {historical[historical.index.year == 2024].mean():.1f}%', 
                xy=(0.05, 0.95), xycoords='axes fraction',
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    ax.annotate(f'2027 Forecast: {forecast[forecast.index.year == 2027].mean():.1f}%', 
                xy=(0.05, 0.85), xycoords='axes fraction',
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))

plt.tight_layout()
plt.savefig('../reports/figures/forecast_basic.png', dpi=300, bbox_inches='tight')
plt.show()

# %% [markdown]
# ## 9. Scenario Comparison Visualization

# %%
# Create scenario comparison visualization
if account_scenarios and payment_scenarios:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Account Ownership scenarios
    ax = axes[0]
    years = [2025, 2026, 2027]
    scenarios = ['optimistic', 'base', 'pessimistic']
    colors = ['#2ecc71', '#3498db', '#e74c3c']

    for i, scenario in enumerate(scenarios):
        if scenario in account_scenarios:
            values = []
            for year in years:
                forecast_data = account_scenarios[scenario]['forecast']
                year_value = forecast_data[forecast_data.index.year == year].mean()
                values.append(year_value)

            ax.plot(years, values, 'o-', linewidth=2, markersize=8,
                   label=scenario.capitalize(), color=colors[i], alpha=0.8)

    ax.set_title('Account Ownership - Scenario Comparison', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=11)
    ax.set_ylabel('Percentage (%)', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Digital Payment scenarios
    ax = axes[1]
    for i, scenario in enumerate(scenarios):
        if scenario in payment_scenarios:
            values = []
            for year in years:
                forecast_data = payment_scenarios[scenario]['forecast']
                year_value = forecast_data[forecast_data.index.year == year].mean()
                values.append(year_value)

            ax.plot(years, values, 'o-', linewidth=2, markersize=8,
                   label=scenario.capitalize(), color=colors[i], alpha=0.8)

    ax.set_title('Digital Payment Usage - Scenario Comparison', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=11)
    ax.set_ylabel('Percentage (%)', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()
    plt.savefig('../reports/figures/scenario_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

# %% [markdown]
# ## 10. Generate Forecast Report

# %%
print("
" + "="*60)
print("GENERATING FORECAST REPORT")
print("="*60)

# Generate comprehensive report
forecast_report = forecaster.generate_forecast_report()

if not forecast_report.empty:
    print(f"
✅ Forecast report generated with {len(forecast_report)} records")

    # Save report
    report_path = '../data/processed/forecast_report_2025_2027.csv'
    forecast_report.to_csv(report_path, index=False)
    print(f"📁 Report saved to: {report_path}")

    # Display summary
    print("
📋 FORECAST SUMMARY (2025-2027):")
    print("=" * 50)

    for indicator in forecast_report['indicator'].unique():
        print(f"
{indicator}:")
        ind_data = forecast_report[forecast_report['indicator'] == indicator]

        for _, row in ind_data.iterrows():
            if row['year'] == 2027:
                print(f"  • 2027 Base Forecast: {row['baseline']:.1f}%")

                if 'optimistic' in row and 'pessimistic' in row:
                    print(f"  • Scenario Range: {row['pessimistic']:.1f}% - {row['optimistic']:.1f}%")

                if indicator == 'Account Ownership Rate (%)':
                    gap_to_target = 60.0 - row['baseline']
                    if gap_to_target > 0:
                        print(f"  ⚠️  Gap to NFIS-II target: {gap_to_target:.1f}pp")
                    else:
                        print(f"  ✅ Exceeds NFIS-II target!")
else:
    print("
⚠️ Could not generate forecast report")

# %% [markdown]
# ## 11. Key Insights and Recommendations

# %%
print("
" + "="*60)
print("KEY INSIGHTS AND RECOMMENDATIONS")
print("="*60)

print("
🎯 KEY INSIGHTS:")
print("-" * 30)

# Insight 1: Account Ownership
if 'ACC_OWNERSHIP' in time_series_data:
    current_account = time_series_data['ACC_OWNERSHIP'].iloc[-1]
    if account_forecast:
        forecast_2027 = account_forecast['forecast'][account_forecast['forecast'].index.year == 2027].mean()
        growth = forecast_2027 - current_account

        print(f"
1. Account Ownership:")
        print(f"   • Current (2024): {current_account:.1f}%")
        print(f"   • 2027 Forecast: {forecast_2027:.1f}%")
        print(f"   • Growth (2024-2027): +{growth:.1f}pp")
        print(f"   • Required for NFIS-II target: +{60.0 - current_account:.1f}pp")

# Insight 2: Digital Payments
if 'USG_DIGITAL_PAYMENT' in time_series_data:
    current_payments = time_series_data['USG_DIGITAL_PAYMENT'].iloc[-1]
    if payment_forecast:
        forecast_2027 = payment_forecast['forecast'][payment_forecast['forecast'].index.year == 2027].mean()
        growth = forecast_2027 - current_payments

        print(f"
2. Digital Payment Usage:")
        print(f"   • Current (2024): {current_payments:.1f}%")
        print(f"   • 2027 Forecast: {forecast_2027:.1f}%")
        print(f"   • Growth (2024-2027): +{growth:.1f}pp")
        print(f"   • Digitization rate: {growth/3:.1f}pp per year")

print("
💡 POLICY RECOMMENDATIONS:")
print("-" * 30)
print("
1. Priority Areas:")
print("   • Accelerate account ownership growth to reach NFIS-II target")
print("   • Boost digital payment adoption through merchant incentives")
print("   • Expand agent networks in underserved areas")
print("   • Address gender gap in financial inclusion")

print("
2. Monitoring Framework:")
print("   • Track monthly: Active accounts, transaction volumes")
print("   • Track quarterly: Agent network growth, digital merchants")
print("   • Track annually: Account ownership, digital payment usage")

print("
3. Risk Management:")
print("   • Monitor economic indicators affecting affordability")
print("   • Track regulatory changes impacting accessibility")
print("   • Watch technological adoption barriers")

# %% [markdown]
# ## 12. Limitations and Next Steps

# %%
print("
" + "="*60)
print("LIMITATIONS AND NEXT STEPS")
print("="*60)

print("
⚠️ LIMITATIONS:")
print("-" * 20)
print("1. Data availability: Limited historical data points")
print("2. Model simplicity: Linear trends may not capture all dynamics")
print("3. External factors: Economic, political factors not fully modeled")
print("4. Event attribution: Difficulty isolating individual event impacts")

print("
🔧 NEXT STEPS:")
print("-" * 20)
print("1. Data enhancement:")
print("   • Collect more frequent data points")
print("   • Add regional breakdowns")
print("   • Include additional indicators")

print("
2. Model improvement:")
print("   • Implement machine learning models")
print("   • Add seasonal components")
print("   • Incorporate external economic indicators")

print("
3. Implementation:")
print("   • Deploy real-time monitoring dashboard")
print("   • Establish regular forecasting schedule")
print("   • Integrate with policy decision-making")

# %% [markdown]
# ## Conclusion
# 
# This forecasting analysis provides valuable insights into Ethiopia's financial inclusion trajectory through 2027. Key findings:
# 
# 1. **Account Ownership** is projected to reach approximately 56-57% by 2027, requiring acceleration to meet the NFIS-II target of 60%.
# 2. **Digital Payment Usage** is expected to grow significantly, reaching around 48-49% by 2027.
# 3. **Key drivers** include mobile money expansion, infrastructure development, and policy initiatives.
# 4. **Risks** include economic volatility, adoption barriers, and infrastructure gaps.
# 
# Regular monitoring and adaptive policy responses will be crucial to achieving Ethiopia's financial inclusion goals.
