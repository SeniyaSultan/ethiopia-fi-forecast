
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

class FinancialInclusionForecaster:
    def __init__(self, data_path='data/processed/enriched_data.csv'):
        """
        Initialize the Financial Inclusion Forecaster

        Args:
            data_path: Path to the enriched data CSV file
        """
        try:
            # Load data
            self.data = pd.read_csv(data_path)
            print(f"✅ Data loaded successfully: {len(self.data)} records")

            # Extract observations
            self.observations = self.data[self.data['record_type'] == 'observation'].copy()
            self.events = self.data[self.data['record_type'] == 'event'].copy()
            self.impacts = self.data[self.data['record_type'] == 'impact_link'].copy()

            # Convert dates
            self.observations['observation_date'] = pd.to_datetime(self.observations['observation_date'])
            self.events['observation_date'] = pd.to_datetime(self.events['observation_date'])
            self.impacts['observation_date'] = pd.to_datetime(self.impacts['observation_date'])

            print(f"   • Observations: {len(self.observations)}")
            print(f"   • Events: {len(self.events)}")
            print(f"   • Impact links: {len(self.impacts)}")

        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            print("   Creating sample data...")
            self._create_sample_data()
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            self._create_sample_data()

    def _create_sample_data(self):
        """Create sample data for demonstration"""
        sample_data = {
            'record_type': ['observation'] * 5,
            'indicator': ['Account Ownership'] * 5,
            'indicator_code': ['ACC_OWNERSHIP'] * 5,
            'value_numeric': [14.0, 22.0, 35.0, 46.0, 49.0],
            'observation_date': ['2011-12-31', '2014-12-31', '2017-12-31', '2021-12-31', '2024-12-31']
        }

        self.data = pd.DataFrame(sample_data)
        self.observations = self.data[self.data['record_type'] == 'observation'].copy()
        self.observations['observation_date'] = pd.to_datetime(self.observations['observation_date'])
        self.events = pd.DataFrame()
        self.impacts = pd.DataFrame()
        print("   ✅ Sample data created")

    def prepare_time_series(self, indicator_code):
        """
        Prepare time series data for forecasting

        Args:
            indicator_code: The indicator code to prepare

        Returns:
            Series: Monthly time series
        """
        # Filter data for the indicator
        indicator_data = self.observations[
            self.observations['indicator_code'] == indicator_code
        ].copy()

        if len(indicator_data) == 0:
            print(f"⚠️ No data found for indicator: {indicator_code}")
            return pd.Series()

        # Sort by date
        indicator_data = indicator_data.sort_values('observation_date')

        # Create annual series
        annual_series = {}
        for _, row in indicator_data.iterrows():
            year = row['observation_date'].year
            value = row['value_numeric']
            annual_series[year] = value

        # Create complete monthly series (2011-2024)
        start_year = min(annual_series.keys())
        end_year = max(annual_series.keys())

        monthly_series = pd.Series(dtype=float)

        for year in range(start_year, end_year + 1):
            # Create monthly dates for this year
            dates = pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31', freq='M')

            # Get value for this year (interpolate if missing)
            if year in annual_series:
                value = annual_series[year]
            else:
                # Find nearest years with data
                prev_years = [y for y in annual_series.keys() if y < year]
                next_years = [y for y in annual_series.keys() if y > year]

                if prev_years and next_years:
                    prev_year = max(prev_years)
                    next_year = min(next_years)
                    prev_value = annual_series[prev_year]
                    next_value = annual_series[next_year]

                    # Linear interpolation
                    weight = (year - prev_year) / (next_year - prev_year)
                    value = prev_value + (next_value - prev_value) * weight
                elif prev_years:
                    value = annual_series[max(prev_years)]
                else:
                    value = annual_series[min(next_years)]

            # Create series for this year
            year_series = pd.Series(value, index=dates)
            monthly_series = pd.concat([monthly_series, year_series])

        return monthly_series

    def baseline_forecast(self, indicator_code, years_ahead=3):
        """
        Generate baseline forecast using linear regression

        Args:
            indicator_code: The indicator to forecast
            years_ahead: Number of years to forecast

        Returns:
            dict: Forecast results with confidence intervals
        """
        print(f"
📈 Generating forecast for {indicator_code}...")

        # Prepare time series
        series = self.prepare_time_series(indicator_code)

        if len(series) == 0:
            print(f"❌ Cannot forecast {indicator_code}: No data available")
            return None

        print(f"   • Time series length: {len(series)} months")
        print(f"   • Current value: {series.iloc[-1]:.2f}")

        # Prepare data for regression
        X = np.arange(len(series)).reshape(-1, 1)
        y = series.values

        # Fit linear model
        model = LinearRegression()
        model.fit(X, y)

        # Generate forecast
        future_X = np.arange(len(series), len(series) + years_ahead * 12).reshape(-1, 1)
        future_dates = pd.date_range(
            start=series.index[-1] + pd.DateOffset(months=1),
            periods=years_ahead * 12,
            freq='M'
        )

        forecast_values = model.predict(future_X)

        # Calculate confidence intervals
        residuals = y - model.predict(X)
        std_error = residuals.std()
        confidence_interval = 1.96 * std_error / np.sqrt(len(y))

        print(f"   • R-squared: {model.score(X, y):.3f}")
        print(f"   • Confidence interval: ±{confidence_interval:.3f}")

        return {
            'forecast': pd.Series(forecast_values, index=future_dates),
            'upper_bound': pd.Series(forecast_values + confidence_interval, index=future_dates),
            'lower_bound': pd.Series(forecast_values - confidence_interval, index=future_dates),
            'model': model,
            'historical': series
        }

    def scenario_forecast(self, indicator_code, years_ahead=3):
        """
        Generate optimistic, base, and pessimistic scenarios

        Returns:
            dict: Scenario forecasts
        """
        base_forecast = self.baseline_forecast(indicator_code, years_ahead)

        if base_forecast is None:
            return None

        # Scenario definitions
        scenarios = {
            'optimistic': {
                'growth_multiplier': 1.3,
                'description': 'Rapid adoption, favorable policies'
            },
            'base': {
                'growth_multiplier': 1.0,
                'description': 'Current trends continue'
            },
            'pessimistic': {
                'growth_multiplier': 0.7,
                'description': 'Slow adoption, challenges'
            }
        }

        scenario_results = {}

        for scenario_name, params in scenarios.items():
            forecast = base_forecast['forecast'].copy()
            multiplier = params['growth_multiplier']

            # Adjust growth rate
            if len(forecast) > 1:
                # Calculate trend from historical data
                historical = base_forecast['historical']
                if len(historical) >= 2:
                    historical_growth = historical.pct_change().mean()
                    if pd.isna(historical_growth):
                        historical_growth = 0.01  # Default 1% monthly growth

                    adjusted_growth = historical_growth * multiplier

                    # Apply adjusted growth
                    for i in range(1, len(forecast)):
                        forecast.iloc[i] = forecast.iloc[i-1] * (1 + adjusted_growth)

            # Store results
            scenario_results[scenario_name] = {
                'forecast': forecast,
                'description': params['description'],
                'final_value_2027': forecast[forecast.index.year == 2027].mean() if any(forecast.index.year == 2027) else None
            }

        return scenario_results

    def generate_forecast_report(self):
        """
        Generate comprehensive forecast report

        Returns:
            DataFrame: Forecast report
        """
        print("
📊 Generating forecast report...")

        indicators = {
            'ACC_OWNERSHIP': 'Account Ownership Rate (%)',
            'USG_DIGITAL_PAYMENT': 'Digital Payment Usage (%)'
        }

        report_data = []

        for indicator_code, indicator_name in indicators.items():
            # Get baseline forecast
            baseline = self.baseline_forecast(indicator_code, 3)

            if baseline is None:
                continue

            # Get scenarios
            scenarios = self.scenario_forecast(indicator_code, 3)

            if scenarios is None:
                continue

            # Extract values for each year
            for year in [2025, 2026, 2027]:
                year_data = {
                    'year': year,
                    'indicator': indicator_name,
                    'indicator_code': indicator_code
                }

                # Baseline forecast
                year_mask = baseline['forecast'].index.year == year
                if year_mask.any():
                    year_data['baseline'] = baseline['forecast'][year_mask].mean()
                    year_data['upper_bound'] = baseline['upper_bound'][year_mask].mean()
                    year_data['lower_bound'] = baseline['lower_bound'][year_mask].mean()

                # Scenario forecasts
                for scenario_name in ['optimistic', 'pessimistic']:
                    if scenario_name in scenarios:
                        scenario_forecast = scenarios[scenario_name]['forecast']
                        scenario_mask = scenario_forecast.index.year == year
                        if scenario_mask.any():
                            year_data[scenario_name] = scenario_forecast[scenario_mask].mean()

                report_data.append(year_data)

        if report_data:
            report_df = pd.DataFrame(report_data)
            print(f"✅ Report generated with {len(report_df)} records")
            return report_df
        else:
            print("⚠️ Could not generate report")
            return pd.DataFrame()
