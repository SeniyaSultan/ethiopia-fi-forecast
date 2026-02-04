
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

class ImpactModel:
    def __init__(self, data_path="../data/processed/enriched_data.csv"):
        """
        Initialize the Impact Model with data

        Args:
            data_path: Path to the enriched data CSV file
        """
        try:
            # Try to load the data
            self.data = pd.read_csv(data_path)
            print(f"✅ Data loaded successfully from {data_path}")
            print(f"   Total records: {len(self.data)}")

            # Extract different record types
            self.events = self.data[self.data["record_type"] == "event"].copy()
            self.observations = self.data[self.data["record_type"] == "observation"].copy()
            self.impacts = self.data[self.data["record_type"] == "impact_link"].copy()

            print(f"   Events: {len(self.events)}")
            print(f"   Observations: {len(self.observations)}")
            print(f"   Impact links: {len(self.impacts)}")

            # Convert dates
            if len(self.events) > 0:
                self.events["observation_date"] = pd.to_datetime(self.events["observation_date"])
            if len(self.observations) > 0:
                self.observations["observation_date"] = pd.to_datetime(self.observations["observation_date"])
            if len(self.impacts) > 0:
                self.impacts["observation_date"] = pd.to_datetime(self.impacts["observation_date"])

        except FileNotFoundError:
            print(f"❌ File not found: {data_path}")
            print("   Creating sample data for demonstration...")
            self._create_sample_data()
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            print("   Creating sample data for demonstration...")
            self._create_sample_data()

    def _create_sample_data(self):
        """Create sample data for testing/demonstration"""
        print("   Creating sample data structure...")

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
        self.events = self.data[self.data["record_type"] == "event"].copy()
        self.observations = self.data[self.data["record_type"] == "observation"].copy()
        self.impacts = self.data[self.data["record_type"] == "impact_link"].copy()

        # Convert dates
        self.events["observation_date"] = pd.to_datetime(self.events["observation_date"])
        self.observations["observation_date"] = pd.to_datetime(self.observations["observation_date"])
        self.impacts["observation_date"] = pd.to_datetime(self.impacts["observation_date"])

        print("   ✅ Sample data created successfully")

    def create_impact_matrix(self):
        """
        Create event-indicator impact matrix

        Returns:
            DataFrame: Impact matrix with events as rows and indicators as columns
        """
        print("
📊 Creating impact matrix...")

        # Define key indicators
        indicators = [
            "ACC_OWNERSHIP",
            "ACC_MM_ACCOUNT", 
            "USG_DIGITAL_PAYMENT",
            "USG_ACC_WAGES",
            "INF_ATM_PER_100K",
            "INF_AGENT_PER_100K",
            "ENB_SMARTPHONE"
        ]

        # Get unique event names
        if len(self.events) == 0:
            print("   ⚠️ No events found in data")
            return pd.DataFrame()

        event_names = self.events["indicator"].unique()

        # Create empty matrix
        impact_matrix = pd.DataFrame(
            index=event_names,
            columns=indicators,
            dtype=float
        )

        # Initialize with zeros
        impact_matrix = impact_matrix.fillna(0)

        print(f"   Found {len(event_names)} events and {len(indicators)} indicators")

        # Fill matrix based on impact_link records
        if len(self.impacts) == 0:
            print("   ⚠️ No impact links found")
            return impact_matrix

        print(f"   Processing {len(self.impacts)} impact links...")

        for idx, impact in self.impacts.iterrows():
            event_id = impact["parent_id"]

            # Skip if no parent_id
            if pd.isna(event_id):
                continue

            # Find the corresponding event
            try:
                event_id = int(event_id)
                event_row = self.events[self.events["id"] == event_id]

                if len(event_row) == 0:
                    print(f"   ⚠️ Event ID {event_id} not found")
                    continue

                event_name = event_row["indicator"].iloc[0]
                indicator = impact["related_indicator"]

                if indicator and indicator in impact_matrix.columns:
                    # Convert impact magnitude to numeric score
                    magnitude_map = {
                        "very_high": 3.0,
                        "high": 2.0,
                        "medium": 1.0,
                        "low": 0.5,
                        "very_low": 0.2
                    }

                    direction_map = {"positive": 1, "negative": -1}

                    magnitude_val = str(impact.get("impact_magnitude", "medium"))
                    magnitude = magnitude_map.get(magnitude_val, 1.0)

                    direction_val = str(impact.get("impact_direction", "positive"))
                    direction = direction_map.get(direction_val, 1)

                    # Calculate impact score
                    impact_score = magnitude * direction

                    # Add to matrix (accumulate if multiple impacts for same event-indicator)
                    current_value = impact_matrix.loc[event_name, indicator]
                    impact_matrix.loc[event_name, indicator] = current_value + impact_score

                    # Print debug info
                    print(f"   ➕ {event_name[:20]:20} -> {indicator[:15]:15}: {impact_score:+.2f}")

            except Exception as e:
                print(f"   ❌ Error processing impact link {idx}: {e}")
                continue

        print("   ✅ Impact matrix created successfully")
        return impact_matrix

    def estimate_event_effects(self, indicator_code="ACC_OWNERSHIP"):
        """
        Estimate historical event effects for a specific indicator

        Args:
            indicator_code: The indicator code to analyze

        Returns:
            Series: Monthly effect estimates
        """
        print(f"
📈 Estimating event effects for {indicator_code}...")

        # Get impacts for this indicator
        effects = self.impacts[self.impacts["related_indicator"] == indicator_code].copy()

        if len(effects) == 0:
            print(f"   ⚠️ No impact links found for {indicator_code}")
            return pd.Series()

        print(f"   Found {len(effects)} impact links for {indicator_code}")

        # Create timeline (2011-2024)
        timeline = pd.date_range(start="2011-01-01", end="2024-12-31", freq="M")
        effect_series = pd.Series(0.0, index=timeline, name="effect")

        # Process each impact
        for idx, effect in effects.iterrows():
            event_id = effect["parent_id"]

            if pd.isna(event_id):
                continue

            try:
                # Get event details
                event_id = int(event_id)
                event_row = self.events[self.events["id"] == event_id]

                if len(event_row) == 0:
                    continue

                event_date = pd.to_datetime(event_row["observation_date"].iloc[0])
                magnitude_val = str(effect.get("impact_magnitude", "medium"))

                # Map magnitude to effect size (percentage points per month)
                magnitude_map = {
                    "very_high": 0.015,  # 1.5pp per month
                    "high": 0.010,       # 1.0pp per month
                    "medium": 0.006,     # 0.6pp per month
                    "low": 0.003,        # 0.3pp per month
                    "very_low": 0.001     # 0.1pp per month
                }

                magnitude = magnitude_map.get(magnitude_val, 0.006)
                direction = 1 if str(effect.get("impact_direction", "positive")) == "positive" else -1

                # Get lag months (default 0)
                lag_months = effect.get("lag_months", 0)
                if pd.isna(lag_months):
                    lag_months = 0

                # Calculate effect start date
                effect_start = event_date + pd.DateOffset(months=int(lag_months))

                # Apply effect over 18-month window
                print(f"   📅 Event at {event_date.date()}, effect starts at {effect_start.date()}")

                for month_offset in range(0, 18):
                    effect_date = effect_start + pd.DateOffset(months=month_offset)

                    # Check if date is in our timeline
                    if effect_date in effect_series.index:
                        # Gradually decreasing effect (exponential decay)
                        weight = np.exp(-0.1 * month_offset)
                        monthly_effect = magnitude * direction * weight
                        effect_series.loc[effect_date] += monthly_effect

            except Exception as e:
                print(f"   ❌ Error processing effect {idx}: {e}")
                continue

        # Filter out zero effects for cleaner output
        non_zero_effects = effect_series[effect_series != 0]
        print(f"   ✅ Created effect series with {len(non_zero_effects)} non-zero months")
        print(f"   📊 Total cumulative effect: {effect_series.sum():.4f} percentage points")

        return effect_series

    def validate_impacts(self):
        """
        Validate impact estimates against historical data

        Returns:
            dict: Validation results
        """
        print("
🔍 Validating impacts...")

        validation_results = {}

        # Validation 1: Telebirr impact on mobile money accounts
        try:
            mm_data = self.observations[self.observations["indicator_code"] == "ACC_MM_ACCOUNT"].copy()

            if len(mm_data) >= 2:
                mm_data = mm_data.sort_values("observation_date")
                mm_values = mm_data["value_numeric"].values

                # Calculate actual change around Telebirr launch (May 2021)
                telebirr_date = pd.Timestamp("2021-05-11")

                # Find values before and after Telebirr
                pre_telebirr = mm_data[mm_data["observation_date"] < telebirr_date]
                post_telebirr = mm_data[mm_data["observation_date"] > telebirr_date]

                if len(pre_telebirr) > 0 and len(post_telebirr) > 0:
                    pre_value = pre_telebirr["value_numeric"].iloc[-1]
                    post_value = post_telebirr["value_numeric"].iloc[0]
                    actual_change = post_value - pre_value

                    # Expected change from our model (high impact = 2.0 magnitude)
                    expected_change = 0.06  # 6 percentage points

                    validation_results["telebirr_mm_accounts"] = {
                        "actual_change": actual_change,
                        "expected_change": expected_change,
                        "difference": actual_change - expected_change,
                        "relative_error": abs(actual_change - expected_change) / expected_change,
                        "notes": f"Pre: {pre_value:.2f}%, Post: {post_value:.2f}%"
                    }

                    print(f"   ✅ Telebirr validation: Actual change {actual_change:.2f}pp, Expected {expected_change:.2f}pp")

        except Exception as e:
            print(f"   ⚠️ Telebirr validation failed: {e}")

        # Validation 2: Overall trend consistency
        try:
            account_data = self.observations[self.observations["indicator_code"] == "ACC_OWNERSHIP"].copy()

            if len(account_data) >= 2:
                account_data = account_data.sort_values("observation_date")
                values = account_data["value_numeric"].values

                # Calculate average annual growth
                annual_growth_rates = []
                for i in range(1, len(values)):
                    growth = values[i] - values[i-1]
                    annual_growth_rates.append(growth)

                avg_growth = np.mean(annual_growth_rates) if annual_growth_rates else 0

                validation_results["trend_consistency"] = {
                    "average_annual_growth": avg_growth,
                    "data_points": len(values),
                    "notes": f"From {values[0]:.1f}% to {values[-1]:.1f}% over {len(values)-1} periods"
                }

                print(f"   ✅ Trend consistency: Average annual growth {avg_growth:.2f}pp")

        except Exception as e:
            print(f"   ⚠️ Trend validation failed: {e}")

        print("   🔍 Validation complete")
        return validation_results

    def get_event_summary(self):
        """
        Get summary of events and their impacts

        Returns:
            DataFrame: Event summary
        """
        print("
📋 Generating event summary...")

        if len(self.events) == 0:
            print("   ⚠️ No events found")
            return pd.DataFrame()

        summary_data = []

        for _, event in self.events.iterrows():
            event_id = event["id"]
            event_name = event["indicator"]
            event_date = event["observation_date"]

            # Get impacts for this event
            event_impacts = self.impacts[self.impacts["parent_id"] == event_id]

            # Calculate total impact score
            total_impact = 0
            impact_details = []

            for _, impact in event_impacts.iterrows():
                magnitude_map = {
                    "very_high": 3.0, "high": 2.0, "medium": 1.0,
                    "low": 0.5, "very_low": 0.2
                }

                magnitude_val = str(impact.get("impact_magnitude", "medium"))
                magnitude = magnitude_map.get(magnitude_val, 1.0)

                direction = 1 if str(impact.get("impact_direction", "positive")) == "positive" else -1

                impact_score = magnitude * direction
                total_impact += abs(impact_score)

                indicator = impact.get("related_indicator", "Unknown")
                impact_details.append(f"{indicator}: {impact_score:+.2f}")

            summary_data.append({
                "event_id": event_id,
                "event_name": event_name,
                "date": event_date.strftime("%Y-%m-%d") if not pd.isna(event_date) else "Unknown",
                "total_impact_score": total_impact,
                "num_impacts": len(event_impacts),
                "impact_details": "; ".join(impact_details) if impact_details else "None"
            })

        summary_df = pd.DataFrame(summary_data)
        summary_df = summary_df.sort_values("total_impact_score", ascending=False)

        print(f"   ✅ Generated summary for {len(summary_df)} events")
        return summary_df
