# src/forecast_model.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings
warnings.filterwarnings('ignore')

class FinancialInclusionForecaster:
    def __init__(self, data_path='data/processed/enriched_data.csv'):
        self.data = pd.read_csv(data_path)
        self.observations = self.data[self.data['record_type'] == 'observation']
        self.events = self.data[self.data['record_type'] == 'event']
        
    def prepare_time_series(self, indicator_code):
        """Prepare time series data for forecasting"""
        
        # Get indicator data
        indicator_data = self.observations[
            self.observations['indicator_code'] == indicator_code
        ].copy()
        
        # Convert to datetime and sort
        indicator_data['observation_date'] = pd.to_datetime(indicator_data['observation_date'])
        indicator_data = indicator_data.sort_values('observation_date')
        
        # Create monthly time series
        # For annual data, interpolate to monthly
        monthly_series = pd.Series(index=pd.date_range(
            start='2011-01-01',
            end='2024-12-31',
            freq='M'
        ))
        
        for _, row in indicator_data.iterrows():
            date = row['observation_date']
            value = row['value_numeric']
            
            # If annual data, assign to all months of that year
            if row['frequency'] == 'annual':
                year = date.year
                monthly_series[monthly_series.index.year == year] = value
            else:
                # For monthly data, use actual date
                monthly_series[monthly_series.index == date] = value
        
        # Forward fill for missing values
        monthly_series = monthly_series.ffill()
        
        return monthly_series
    
    def baseline_forecast(self, indicator_code, years_ahead=3):
        """Baseline forecast using trend projection"""
        
        series = self.prepare_time_series(indicator_code)
        
        # Fit linear trend
        X = np.arange(len(series)).reshape(-1, 1)
        y = series.values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Forecast
        future_X = np.arange(len(series), len(series) + years_ahead * 12).reshape(-1, 1)
        future_dates = pd.date_range(
            start=series.index[-1] + pd.DateOffset(months=1),
            periods=years_ahead * 12,
            freq='M'
        )
        
        baseline_forecast = pd.Series(
            model.predict(future_X),
            index=future_dates
        )
        
        # Calculate confidence intervals
        residuals = y - model.predict(X)
        std_error = residuals.std()
        confidence_interval = 1.96 * std_error / np.sqrt(len(y))
        
        upper_bound = baseline_forecast + confidence_interval
        lower_bound = baseline_forecast - confidence_interval
        
        return {
            'forecast': baseline_forecast,
            'upper_bound': upper_bound,
            'lower_bound': lower_bound,
            'model': model
        }
    
    def event_augmented_forecast(self, indicator_code, years_ahead=3):
        """Forecast including event impacts"""
        
        from impact_model import ImpactModel
        
        # Get baseline forecast
        baseline = self.baseline_forecast(indicator_code, years_ahead)
        
        # Get event effects
        impact_model = ImpactModel()
        event_effects = impact_model.estimate_event_effects(indicator_code)
        
        # Project future events (based on known upcoming events)
        future_events = self._project_future_events(indicator_code, years_ahead)
        
        # Combine baseline and event effects
        augmented_forecast = baseline['forecast'].copy()
        
        for date in augmented_forecast.index:
            # Add historical event effects that are still relevant
            relevant_effects = event_effects[event_effects.index <= date].tail(24).mean()
            augmented_forecast.loc[date] += relevant_effects
            
            # Add future event effects
            for event in future_events:
                if event['date'] <= date:
                    effect = event.get('effect', 0)
                    # Gradual effect implementation
                    months_since = (date - event['date']).days // 30
                    if months_since < 18:  # 18-month effect window
                        weight = np.exp(-0.1 * months_since)
                        augmented_forecast.loc[date] += effect * weight
        
        return {
            'forecast': augmented_forecast,
            'baseline': baseline['forecast'],
            'event_effects': event_effects,
            'upper_bound': baseline['upper_bound'],
            'lower_bound': baseline['lower_bound']
        }
    
    def scenario_forecast(self, indicator_code, years_ahead=3):
        """Generate optimistic, base, and pessimistic scenarios"""
        
        base_forecast = self.event_augmented_forecast(indicator_code, years_ahead)
        
        # Scenario multipliers
        scenarios = {
            'optimistic': {
                'growth_multiplier': 1.3,
                'event_effect_multiplier': 1.5,
                'description': 'Rapid adoption, favorable policies, strong economic growth'
            },
            'base': {
                'growth_multiplier': 1.0,
                'event_effect_multiplier': 1.0,
                'description': 'Current trends continue with expected policy implementation'
            },
            'pessimistic': {
                'growth_multiplier': 0.7,
                'event_effect_multiplier': 0.5,
                'description': 'Slow adoption, regulatory challenges, economic headwinds'
            }
        }
        
        scenario_results = {}
        
        for scenario_name, params in scenarios.items():
            forecast = base_forecast['forecast'].copy()
            multiplier = params['growth_multiplier']
            
            # Apply scenario-specific adjustments
            trend_growth = forecast.pct_change().mean()
            adjusted_growth = trend_growth * multiplier
            
            # Apply growth adjustment
            for i in range(1, len(forecast)):
                forecast.iloc[i] = forecast.iloc[i-1] * (1 + adjusted_growth)
            
            scenario_results[scenario_name] = {
                'forecast': forecast,
                'params': params,
                'final_value_2027': forecast.iloc[-1]
            }
        
        return scenario_results
    
    def _project_future_events(self, indicator_code, years_ahead):
        """Project known future events and their impacts"""
        
        future_events = [
            {
                'date': pd.Timestamp('2025-07-01'),
                'event': 'NFIS-II Full Implementation',
                'indicator': 'ACC_OWNERSHIP',
                'effect': 0.02,  # 2 percentage points
                'description': 'Full implementation of National Financial Inclusion Strategy II'
            },
            {
                'date': pd.Timestamp('2026-01-01'),
                'event': 'Fayda ID National Rollout',
                'indicator': 'USG_DIGITAL_PAYMENT',
                'effect': 0.015,  # 1.5 percentage points
                'description': 'National rollout of digital ID enabling KYC simplification'
            },
            {
                'date': pd.Timestamp('2026-06-01'),
                'event': 'Interoperability Phase 2',
                'indicator': 'USG_DIGITAL_PAYMENT',
                'effect': 0.01,  # 1 percentage point
                'description': 'Enhanced interoperability between all payment providers'
            }
        ]
        
        # Filter events relevant to the indicator
        relevant_events = [
            event for event in future_events 
            if event['indicator'] == indicator_code or event['indicator'] == 'ALL'
        ]
        
        return relevant_events
    
    def generate_forecast_report(self):
        """Generate comprehensive forecast report"""
        
        indicators = {
            'ACC_OWNERSHIP': 'Account Ownership Rate (%)',
            'USG_DIGITAL_PAYMENT': 'Digital Payment Usage (%)'
        }
        
        report_data = []
        
        for indicator_code, indicator_name in indicators.items():
            # Get forecasts
            baseline = self.baseline_forecast(indicator_code, 3)
            augmented = self.event_augmented_forecast(indicator_code, 3)
            scenarios = self.scenario_forecast(indicator_code, 3)
            
            # Extract key values
            for year in [2025, 2026, 2027]:
                year_data = {
                    'year': year,
                    'indicator': indicator_name,
                    'indicator_code': indicator_code,
                    'baseline': baseline['forecast'][baseline['forecast'].index.year == year].mean(),
                    'augmented': augmented['forecast'][augmented['forecast'].index.year == year].mean(),
                    'optimistic': scenarios['optimistic']['forecast'][scenarios['optimistic']['forecast'].index.year == year].mean(),
                    'pessimistic': scenarios['pessimistic']['forecast'][scenarios['pessimistic']['forecast'].index.year == year].mean()
                }
                
                # Calculate confidence intervals
                year_mask = baseline['forecast'].index.year == year
                year_upper = baseline['upper_bound'][year_mask].mean()
                year_lower = baseline['lower_bound'][year_mask].mean()
                
                year_data['confidence_upper'] = year_upper
                year_data['confidence_lower'] = year_lower
                
                report_data.append(year_data)
        
        report_df = pd.DataFrame(report_data)
        return report_df