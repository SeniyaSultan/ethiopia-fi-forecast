
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

class ImpactModel:
    def __init__(self, data_path='data/processed/enriched_data.csv'):
        """
        Initialize the Impact Model

        Args:
            data_path: Path to the enriched data CSV file
        """
        try:
            # Load data
            self.data = pd.read_csv(data_path)
            print(f"✅ Data loaded successfully: {len(self.data)} records")

            # Extract different record types
            self.events = self.data[self.data['record_type'] == 'event'].copy()
            self.observations = self.data[self.data['record_type'] == 'observation'].copy()
            self.impacts = self.data[self.data['record_type'] == 'impact_link'].copy()

            # Convert dates
            self.events['observation_date'] = pd.to_datetime(self.events['observation_date'])
            self.observations['observation_date'] = pd.to_datetime(self.observations['observation_date'])
            self.impacts['observation_date'] = pd.to_datetime(self.impacts['observation_date'])

            print(f"   • Events: {len(self.events)}")
            print(f"   • Observations: {len(self.observations)}")
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
            'id': [1, 2, 3, 4, 5, 6, 7, 8, 9],
            'record_type': ['observation', 'observation', 'observation', 'event', 'event', 
                          'impact_link', 'impact_link', 'impact_link', 'impact_link'],
            'indicator': ['Account Ownership', 'Account Ownership', 'Account Ownership',
                         'Telebirr Launch', 'M-Pesa Entry',
                         'Telebirr Impact', 'Telebirr Impact', 'M-Pesa Impact', 'NFIS Impact'],
            'indicator_code': ['ACC_OWNERSHIP', 'ACC_OWNERSHIP', 'ACC_OWNERSHIP',
                              None, None, None, None, None, None],
            'value_numeric': [35.0, 46.0, 49.0, None, None, None, None, None, None],
            'observation_date': ['2017-12-31', '2021-12-31', '2024-12-31',
                                '2021-05-11', '2023-08-15',
                                '2021-05-11', '2021-05-11', '2023-08-15', '2022-01-01'],
            'parent_id': [None, None, None, None, None, 4, 4, 5, 4],
            'related_indicator': [None, None, None, None, None,
                                 'ACC_MM_ACCOUNT', 'USG_DIGITAL_PAYMENT', 'USG_DIGITAL_PAYMENT', 'ACC_OWNERSHIP'],
            'impact_direction': [None, None, None, None, None, 'positive', 'positive', 'positive', 'positive'],
            'impact_magnitude': [None, None, None, None, None, 'high', 'medium', 'low', 'high']
        }

        self.data = pd.DataFrame(sample_data)
        self.events = self.data[self.data['record_type'] == 'event'].copy()
        self.observations = self.data[self.data['record_type'] == 'observation'].copy()
        self.impacts = self.data[self.data['record_type'] == 'impact_link'].copy()

        # Convert dates
        self.events['observation_date'] = pd.to_datetime(self.events['observation_date'])
        self.observations['observation_date'] = pd.to_datetime(self.observations['observation_date'])
        self.impacts['observation_date'] = pd.to_datetime(self.impacts['observation_date'])

        print("   ✅ Sample data created")

    def create_impact_matrix(self):
        """
        Create event-indicator impact matrix

        Returns:
            DataFrame: Impact matrix
        """
        print("
📊 Creating impact matrix...")

        # Define key indicators
        indicators = [
            'ACC_OWNERSHIP',
            'ACC_MM_ACCOUNT', 
            'USG_DIGITAL_PAYMENT',
            'USG_ACC_WAGES',
            'INF_ATM_PER_100K',
            'INF_AGENT_PER_100K',
            'ENB_SMARTPHONE'
        ]

        # Get unique event names
        if len(self.events) == 0:
            print("⚠️ No events found")
            return pd.DataFrame()

        event_names = self.events['indicator'].unique()

        # Create empty matrix
        impact_matrix = pd.DataFrame(
            index=event_names,
            columns=indicators,
            dtype=float
        ).fillna(0)

        print(f"   • Events: {len(event_names)}")
        print(f"   • Indicators: {len(indicators)}")

        # Fill matrix from impact links
        if len(self.impacts) == 0:
            print("⚠️ No impact links found")
            return impact_matrix

        for _, impact in self.impacts.iterrows():
            event_id = impact['parent_id']

            if pd.isna(event_id):
                continue

            try:
                # Get event
                event_row = self.events[self.events['id'] == event_id]
                if len(event_row) == 0:
                    continue

                event_name = event_row['indicator'].iloc[0]
                indicator = impact['related_indicator']

                if indicator in indicators:
                    # Convert impact magnitude to score
                    magnitude_map = {
                        'very_high': 3.0,
                        'high': 2.0,
                        'medium': 1.0,
                        'low': 0.5,
                        'very_low': 0.2
                    }

                    direction_map = {'positive': 1, 'negative': -1}

                    magnitude_val = str(impact.get('impact_magnitude', 'medium'))
                    magnitude = magnitude_map.get(magnitude_val, 1.0)

                    direction_val = str(impact.get('impact_direction', 'positive'))
                    direction = direction_map.get(direction_val, 1)

                    # Calculate impact score
                    impact_score = magnitude * direction

                    # Add to matrix
                    current = impact_matrix.loc[event_name, indicator]
                    impact_matrix.loc[event_name, indicator] = current + impact_score

            except Exception as e:
                print(f"⚠️ Error processing impact: {e}")
                continue

        print(f"✅ Impact matrix created: {impact_matrix.shape}")
        return impact_matrix

    def estimate_event_effects(self, indicator_code='ACC_OWNERSHIP'):
        """
        Estimate historical event effects

        Args:
            indicator_code: Indicator to analyze

        Returns:
            Series: Monthly effect estimates
        """
        print(f"
📈 Estimating event effects for {indicator_code}...")

        # Get impacts for this indicator
        effects = self.impacts[self.impacts['related_indicator'] == indicator_code].copy()

        if len(effects) == 0:
            print(f"⚠️ No impacts found for {indicator_code}")
            return pd.Series()

        print(f"   • Found {len(effects)} impact links")

        # Create timeline (2011-2024)
        timeline = pd.date_range(start='2011-01-01', end='2024-12-31', freq='M')
        effect_series = pd.Series(0.0, index=timeline)

        # Process each impact
        for _, effect in effects.iterrows():
            event_id = effect['parent_id']

            if pd.isna(event_id):
                continue

            try:
                # Get event
                event_row = self.events[self.events['id'] == event_id]
                if len(event_row) == 0:
                    continue

                event_date = event_row['observation_date'].iloc[0]
                magnitude_val = str(effect.get('impact_magnitude', 'medium'))

                # Map magnitude to effect size
                magnitude_map = {
                    'very_high': 0.015,  # 1.5pp per month
                    'high': 0.010,       # 1.0pp per month
                    'medium': 0.006,     # 0.6pp per month
                    'low': 0.003,        # 0.3pp per month
                    'very_low': 0.001     # 0.1pp per month
                }

                magnitude = magnitude_map.get(magnitude_val, 0.006)
                direction = 1 if str(effect.get('impact_direction', 'positive')) == 'positive' else -1

                # Get lag (default 0)
                lag_months = effect.get('lag_months', 0)
                if pd.isna(lag_months):
                    lag_months = 0

                # Calculate effect start
                effect_start = event_date + pd.DateOffset(months=int(lag_months))

                # Apply effect over 18 months (exponential decay)
                for month_offset in range(0, 18):
                    effect_date = effect_start + pd.DateOffset(months=month_offset)

                    if effect_date in effect_series.index:
                        weight = np.exp(-0.1 * month_offset)
                        monthly_effect = magnitude * direction * weight
                        effect_series.loc[effect_date] += monthly_effect

            except Exception as e:
                print(f"⚠️ Error processing effect: {e}")
                continue

        # Calculate summary
        non_zero = effect_series[effect_series != 0]
        print(f"   • Non-zero months: {len(non_zero)}")
        print(f"   • Total effect: {effect_series.sum():.4f} pp")

        return effect_series

    def validate_impacts(self):
        """
        Validate impact estimates

        Returns:
            dict: Validation results
        """
        print("
🔍 Validating impacts...")

        validation_results = {}

        # Validate Telebirr impact on mobile money
        try:
            mm_data = self.observations[self.observations['indicator_code'] == 'ACC_MM_ACCOUNT'].copy()

            if len(mm_data) >= 2:
                mm_data = mm_data.sort_values('observation_date')

                # Find values before and after Telebirr launch (May 2021)
                telebirr_date = pd.Timestamp('2021-05-11')
                pre_telebirr = mm_data[mm_data['observation_date'] < telebirr_date]
                post_telebirr = mm_data[mm_data['observation_date'] > telebirr_date]

                if len(pre_telebirr) > 0 and len(post_telebirr) > 0:
                    pre_value = pre_telebirr['value_numeric'].iloc[-1]
                    post_value = post_telebirr['value_numeric'].iloc[0]
                    actual_change = post_value - pre_value

                    validation_results['telebirr_mm_accounts'] = {
                        'actual_change': actual_change,
                        'expected_change': 0.06,  # 6pp from model
                        'difference': actual_change - 0.06,
                        'relative_error': abs(actual_change - 0.06) / 0.06,
                        'notes': f'Pre: {pre_value:.2f}%, Post: {post_value:.2f}%'
                    }

                    print(f"✅ Telebirr validation: {actual_change:.2f}pp change")

        except Exception as e:
            print(f"⚠️ Telebirr validation failed: {e}")

        return validation_results
