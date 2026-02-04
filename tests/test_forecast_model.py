# tests/test_forecast_model.py
import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from forecast_model import FinancialInclusionForecaster

class TestForecastModel:
    @pytest.fixture
    def forecaster(self):
        return FinancialInclusionForecaster()
    
    def test_prepare_time_series(self, forecaster):
        series = forecaster.prepare_time_series('ACC_OWNERSHIP')
        assert len(series) > 0
        assert series.index[0].year == 2011
        assert series.index[-1].year == 2024
    
    def test_baseline_forecast(self, forecaster):
        forecast = forecaster.baseline_forecast('ACC_OWNERSHIP', years_ahead=3)
        assert 'forecast' in forecast
        assert 'upper_bound' in forecast
        assert 'lower_bound' in forecast
        assert len(forecast['forecast']) == 36  # 3 years * 12 months
    
    def test_event_augmented_forecast(self, forecaster):
        forecast = forecaster.event_augmented_forecast('ACC_OWNERSHIP', years_ahead=3)
        assert 'forecast' in forecast
        assert 'baseline' in forecast
        assert 'event_effects' in forecast
        # Event-augmented should differ from baseline
        assert not np.allclose(forecast['forecast'].values, forecast['baseline'].values)
    
    def test_scenario_forecast(self, forecaster):
        scenarios = forecaster.scenario_forecast('ACC_OWNERSHIP', years_ahead=3)
        assert 'optimistic' in scenarios
        assert 'base' in scenarios
        assert 'pessimistic' in scenarios
        # Optimistic should be higher than pessimistic
        assert scenarios['optimistic']['final_value_2027'] > scenarios['pessimistic']['final_value_2027']
    
    def test_generate_forecast_report(self, forecaster):
        report = forecaster.generate_forecast_report()
        assert not report.empty
        assert 'year' in report.columns
        assert 'indicator' in report.columns
        assert 'augmented' in report.columns
        # Should have data for 2025-2027
        assert set(report['year'].unique()) == {2025, 2026, 2027}

# tests/test_impact_model.py
import pytest
from impact_model import ImpactModel

class TestImpactModel:
    @pytest.fixture
    def impact_model(self):
        return ImpactModel()
    
    def test_create_impact_matrix(self, impact_model):
        matrix = impact_model.create_impact_matrix()
        assert not matrix.empty
        # Should have events as rows and indicators as columns
        assert len(matrix.index) > 0
        assert len(matrix.columns) > 0
    
    def test_estimate_event_effects(self, impact_model):
        effects = impact_model.estimate_event_effects('ACC_OWNERSHIP')
        assert len(effects) > 0
        assert effects.index[0].year == 2011
        assert effects.index[-1].year == 2024
    
    def test_validate_impacts(self, impact_model):
        validation = impact_model.validate_impacts()
        assert isinstance(validation, dict)
        # Should have at least Telebirr validation
        if 'telebirr' in validation:
            assert 'actual_change' in validation['telebirr']
            assert 'expected_change' in validation['telebirr']