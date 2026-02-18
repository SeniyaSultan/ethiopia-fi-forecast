import pytest
import pandas as pd
import numpy as np
from src.forecast import generate_forecast, calculate_confidence_interval

def test_generate_forecast_baseline():
    """Test baseline forecast generation."""
    # Setup
    historical_data = pd.Series([46, 49], index=[2021, 2024])
    
    # Execute
    forecast = generate_forecast(historical_data, years=[2025, 2026, 2027])
    
    # Assert
    assert len(forecast) == 3
    assert forecast.iloc[0] > 49  # Should increase
    assert isinstance(forecast, pd.Series)

def test_calculate_confidence_interval():
    """Test confidence interval calculation."""
    forecast = pd.Series([52, 54, 55])
    lower, upper = calculate_confidence_interval(forecast, confidence=0.8)
    
    assert lower < forecast.iloc[0]
    assert upper > forecast.iloc[-1]
    assert len(lower) == len(forecast)

def test_event_impact_integration():
    """Test that events properly influence forecasts."""
    # Setup
    base_forecast = pd.Series([52, 54, 55])
    event_impact = {'2025': 2.0, '2026': 3.0, '2027': 4.0}
    
    # Execute
    adjusted = apply_event_impacts(base_forecast, event_impact)
    
    # Assert
    assert adjusted[2025] == 54.0
    assert adjusted[2026] == 57.0