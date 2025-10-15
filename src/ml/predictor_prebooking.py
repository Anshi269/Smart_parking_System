"""
ML Predictor for PREBOOKING System
Fixed for real-world prebooking scenarios
- Removes sensor dependency for future bookings
- Predicts traffic from historical patterns
- Integrates weather API for forecast
- Better vehicle-to-spot matching
"""
import joblib
import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta

class PrebookingPredictor:
    """
    AI-powered parking predictor optimized for PREBOOKING
    Does NOT rely on real-time sensors for future predictions
    """
    
    def __init__(self, model_dir='models', data_loader=None):
        """
        Initialize predictor for prebooking
        
        Args:
            model_dir: Directory containing saved model files
            data_loader: ParkingDataLoader to analyze historical patterns
        """
        self.model_dir = model_dir
        self.data_loader = data_loader
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.label_encoders = None
        self.is_loaded = False
        
        # Historical pattern caches (learned from dataset)
        self.traffic_patterns = None
        self.sensor_patterns = None
        
        self._load_model()
        if data_loader:
            self._learn_patterns()
    
    def _load_model(self):
        """Load trained model and associated files"""
        try:
            model_path = os.path.join(self.model_dir, 'parking_predictor.pkl')
            scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
            features_path = os.path.join(self.model_dir, 'feature_columns.pkl')
            encoders_path = os.path.join(self.model_dir, 'label_encoders.pkl')
            
            if not all(os.path.exists(p) for p in [model_path, scaler_path, features_path, encoders_path]):
                print("[WARNING] ML model files not found. Predictions will be disabled.")
                return
            
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.feature_columns = joblib.load(features_path)
            self.label_encoders = joblib.load(encoders_path)
            self.is_loaded = True
            
            print("[OK] Prebooking ML model loaded successfully")
        
        except Exception as e:
            print(f"[ERROR] Failed to load ML model: {e}")
            self.is_loaded = False
    
    def _learn_patterns(self):
        """
        Learn historical patterns from dataset for predictions
        - Traffic patterns by hour and weekday
        - Sensor patterns by hour
        - Weather patterns by hour/month
        """
        if not self.data_loader or not self.data_loader.df is not None:
            return
        
        df = self.data_loader.df
        
        # Learn traffic patterns (hour + weekday)
        if 'Timestamp' not in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        
        df['Hour'] = df['Entry_Time']
        df['DayOfWeek'] = pd.to_datetime(df['Timestamp']).dt.dayofweek
        
        # Average traffic level by hour and weekday
        self.traffic_patterns = df.groupby(['Hour', 'DayOfWeek'])['Nearby_Traffic_Level'].agg(
            lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Medium'
        ).to_dict()
        
        # Average sensor readings by hour (fallback for when we can't get real-time)
        self.sensor_patterns = {
            'proximity': df.groupby('Hour')['Sensor_Reading_Proximity'].mean().to_dict(),
            'pressure': df.groupby('Hour')['Sensor_Reading_Pressure'].mean().to_dict(),
            'ultrasonic': df.groupby('Hour')['Sensor_Reading_Ultrasonic'].mean().to_dict()
        }
        
        print("[OK] Learned historical patterns from dataset")
        print(f"  - Traffic patterns: {len(self.traffic_patterns)} hour-day combinations")
        print(f"  - Sensor patterns: {len(self.sensor_patterns['proximity'])} hourly averages")
    
    def _predict_traffic_level(self, hour, day_of_week):
        """
        Predict traffic level based on historical patterns
        NOT from static dataset value
        
        Args:
            hour: Hour of day (0-23)
            day_of_week: Day of week (0=Monday, 6=Sunday)
        
        Returns:
            str: Predicted traffic level (Low/Medium/High)
        """
        if self.traffic_patterns is None:
            # Fallback to rule-based if no patterns learned
            if 8 <= hour <= 10 or 17 <= hour <= 19:
                if day_of_week < 5:  # Weekday
                    return 'High'
                else:  # Weekend
                    return 'Medium'
            elif 11 <= hour <= 16:
                return 'Medium'
            else:
                return 'Low'
        
        # Use learned patterns
        key = (hour, day_of_week)
        if key in self.traffic_patterns:
            return self.traffic_patterns[key]
        
        # Fallback to same hour, different day
        same_hour = [v for k, v in self.traffic_patterns.items() if k[0] == hour]
        if same_hour:
            return max(set(same_hour), key=same_hour.count)  # Most common
        
        return 'Medium'  # Default
    
    def _get_weather_forecast(self, hour, day_of_week, location="default"):
        """
        Get weather forecast for future booking time
        TODO: Integrate real weather API
        
        Args:
            hour: Target hour
            day_of_week: Target day
            location: Location for forecast
        
        Returns:
            dict: Weather forecast data
        """
        # TODO: Replace with actual weather API call
        # Example: OpenWeatherMap, WeatherAPI, etc.
        
        # For now, use historical averages from dataset
        if self.data_loader and self.data_loader.df is not None:
            df = self.data_loader.df
            if 'Hour' not in df.columns:
                df['Hour'] = df['Entry_Time']
            
            hour_data = df[df['Hour'] == hour]
            if len(hour_data) > 0:
                avg_temp = hour_data['Weather_Temperature'].mean()
                avg_precip = hour_data['Weather_Precipitation'].mean()
                
                return {
                    'temperature': avg_temp,
                    'precipitation': 1 if avg_precip > 0.5 else 0,
                    'source': 'historical_average'
                }
        
        # Default fallback
        return {
            'temperature': 20.0,
            'precipitation': 0,
            'source': 'default'
        }
    
    def _get_historical_sensor_average(self, hour):
        """
        Get historical average sensor readings for an hour
        Used for prebooking since we can't know future sensor values
        
        Args:
            hour: Hour of day
        
        Returns:
            dict: Average sensor readings
        """
        if self.sensor_patterns:
            return {
                'proximity': self.sensor_patterns['proximity'].get(hour, 5.0),
                'pressure': self.sensor_patterns['pressure'].get(hour, 2.0),
                'ultrasonic': self.sensor_patterns['ultrasonic'].get(hour, 100.0)
            }
        
        # Defaults if no patterns
        return {
            'proximity': 5.0,
            'pressure': 2.0,
            'ultrasonic': 100.0
        }
    
    def _get_spot_size_for_vehicle(self, vehicle_type):
        """
        Map vehicle type to recommended spot size
        
        Args:
            vehicle_type: Vehicle type from user
        
        Returns:
            str: Recommended spot size
        """
        vehicle_to_size = {
            'Motorcycle': 'Compact',
            'Sedan': 'Standard',
            'Car': 'Standard',
            'SUV': 'Large',
            'Truck': 'Large',
            'Electric Vehicle': 'Standard'
        }
        return vehicle_to_size.get(vehicle_type, 'Standard')
    
    def predict_for_prebooking(self, spot_id, section, booking_datetime,
                               vehicle_type='Sedan', is_ev=False):
        """
        Predict spot availability for PREBOOKING
        Optimized for future time slots (not real-time)
        
        Args:
            spot_id: Parking spot ID
            section: Parking section (Zone A, B, C, D)
            booking_datetime: datetime object for booking time
            vehicle_type: Vehicle type from user
            is_ev: Electric vehicle flag
        
        Returns:
            dict: Prediction with insights
        """
        if not self.is_loaded:
            return self._get_default_prediction()
        
        try:
            hour = booking_datetime.hour
            day_of_week = booking_datetime.weekday()
            
            # Get spot metadata (static info)
            spot_info = self.data_loader.get_spot_info(spot_id, section) if self.data_loader else {}
            
            # PREDICT traffic (not read from dataset)
            predicted_traffic = self._predict_traffic_level(hour, day_of_week)
            
            # GET weather forecast (will use API in future)
            weather_forecast = self._get_weather_forecast(hour, day_of_week)
            
            # GET historical sensor averages (not real-time)
            sensor_averages = self._get_historical_sensor_average(hour)
            
            # Check vehicle-spot compatibility
            recommended_size = self._get_spot_size_for_vehicle(vehicle_type)
            actual_size = spot_info.get('Spot_Size', 'Standard') if spot_info else 'Standard'
            size_compatible = (recommended_size == actual_size or actual_size == 'Standard')
            
            # Build features
            features = self._build_prebooking_features(
                hour, day_of_week, is_ev, spot_id, section,
                vehicle_type, spot_info, predicted_traffic,
                weather_forecast, sensor_averages
            )
            
            # Make prediction
            feature_df = pd.DataFrame([features])[self.feature_columns]
            feature_scaled = self.scaler.transform(feature_df)
            
            prediction = self.model.predict(feature_scaled)[0]
            probabilities = self.model.predict_proba(feature_scaled)[0]
            
            prob_vacant = probabilities[0]
            prob_occupied = probabilities[1]
            confidence = max(prob_vacant, prob_occupied)
            
            # Calculate time until booking
            now = datetime.now()
            hours_until = (booking_datetime - now).total_seconds() / 3600
            
            # Generate recommendation
            recommendation = self._generate_prebooking_recommendation(
                prob_vacant, hour, day_of_week, predicted_traffic,
                weather_forecast, size_compatible, hours_until
            )
            
            # Extract insights
            insights = self._extract_prebooking_insights(
                hour, day_of_week, predicted_traffic, weather_forecast,
                spot_info, hours_until, size_compatible, recommended_size
            )
            
            return {
                'prediction': 'Vacant' if prediction == 0 else 'Occupied',
                'confidence': confidence,
                'probability_vacant': prob_vacant,
                'probability_occupied': prob_occupied,
                'recommendation': recommendation,
                'insights': insights,
                'predicted_traffic': predicted_traffic,
                'weather_forecast': weather_forecast,
                'size_compatible': size_compatible,
                'recommended_size': recommended_size,
                'hours_until_booking': hours_until
            }
        
        except Exception as e:
            print(f"[ERROR] Prebooking prediction failed: {e}")
            import traceback
            traceback.print_exc()
            return self._get_default_prediction()
    
    def _build_prebooking_features(self, hour, day_of_week, is_ev, spot_id, section,
                                   vehicle_type, spot_info, predicted_traffic,
                                   weather_forecast, sensor_averages):
        """Build features for prebooking prediction"""
        
        # Time features
        month = datetime.now().month
        is_weekend = 1 if day_of_week >= 5 else 0
        
        # Cyclical encoding
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)
        day_sin = np.sin(2 * np.pi * day_of_week / 7)
        day_cos = np.cos(2 * np.pi * day_of_week / 7)
        
        # Patterns
        if 8 <= hour <= 10 or 17 <= hour <= 19:
            hour_pattern = 2  # Peak
        elif 11 <= hour <= 16:
            hour_pattern = 1  # Moderate
        else:
            hour_pattern = 0  # Off-peak
        
        day_pattern = 1 if day_of_week < 5 else 0
        
        # Encode categorical
        section_encoded = self.label_encoders['Parking_Lot_Section'].transform([section])[0]
        
        # Map vehicle type to dataset format
        vehicle_type_map = {
            'Sedan': 'Car', 'SUV': 'Car', 'Truck': 'Car', 'Car': 'Car',
            'Motorcycle': 'Motorcycle', 'Electric Vehicle': 'Electric Vehicle'
        }
        vehicle_mapped = vehicle_type_map.get(vehicle_type, 'Car')
        vehicle_encoded = self.label_encoders['Vehicle_Type'].transform([vehicle_mapped])[0]
        
        # Encode PREDICTED traffic (not from dataset)
        traffic_encoded = self.label_encoders['Nearby_Traffic_Level'].transform([predicted_traffic])[0]
        
        return {
            'Hour': hour,
            'DayOfWeek': day_of_week,
            'Electric_Vehicle': 1 if is_ev else 0,
            'Parking_Spot_ID': spot_id,
            'IsWeekend': is_weekend,
            'Month': month,
            'Hour_sin': hour_sin,
            'Hour_cos': hour_cos,
            'DayOfWeek_sin': day_sin,
            'DayOfWeek_cos': day_cos,
            'Hour_Pattern': hour_pattern,
            'DayOfWeek_Pattern': day_pattern,
            'Parking_Lot_Section_encoded': section_encoded,
            'Vehicle_Type_encoded': vehicle_encoded,
            'Proximity_To_Exit': spot_info.get('Proximity_To_Exit', 10.0) if spot_info else 10.0,
            'Reserved_Status': spot_info.get('Reserved_Status', 0) if spot_info else 0,
            
            # Weather FORECAST (not static dataset value)
            'Weather_Temperature': weather_forecast['temperature'],
            'Weather_Precipitation': weather_forecast['precipitation'],
            
            # PREDICTED traffic (not static dataset value)
            'Nearby_Traffic_Level_encoded': traffic_encoded,
            
            # Historical sensor AVERAGES (not real-time)
            'Sensor_Reading_Proximity': sensor_averages['proximity'],
            'Sensor_Reading_Pressure': sensor_averages['pressure'],
            'Sensor_Reading_Ultrasonic': sensor_averages['ultrasonic'],
            
            # Vehicle specs (from dataset averages for vehicle type)
            'Vehicle_Type_Weight': spot_info.get('Vehicle_Type_Weight', 1500.0) if spot_info else 1500.0,
            'Vehicle_Type_Height': spot_info.get('Vehicle_Type_Height', 4.0) if spot_info else 4.0,
            'User_Parking_History': spot_info.get('User_Parking_History', 5.0) if spot_info else 5.0
        }
    
    def _generate_prebooking_recommendation(self, prob_vacant, hour, day_of_week,
                                           predicted_traffic, weather_forecast,
                                           size_compatible, hours_until):
        """Generate recommendation for prebooking"""
        
        if prob_vacant > 0.7:
            base = "HIGHLY RECOMMENDED - Good availability expected"
        elif prob_vacant > 0.55:
            base = "RECOMMENDED - Likely available"
        elif prob_vacant > 0.45:
            base = "UNCERTAIN - Consider alternatives"
        else:
            base = "NOT RECOMMENDED - Likely occupied, check alternatives"
        
        # Add prebooking-specific context
        if hours_until > 24:
            base += f" (Booking {hours_until:.0f}h in advance)"
        elif hours_until > 2:
            base += f" (Booking {hours_until:.1f}h ahead)"
        
        # Time-based
        if 8 <= hour <= 10 or 17 <= hour <= 19:
            base += " (Peak hour)"
        
        # Weather-based (FORECAST, not current)
        temp = weather_forecast['temperature']
        precip = weather_forecast['precipitation']
        
        if temp > 30:
            base += " - Hot weather forecast, covered spots recommended"
        elif temp < 5:
            base += " - Cold weather forecast, covered spots recommended"
        
        if precip > 0:
            base += " - Rain expected, covered parking essential"
        
        # Traffic-based (PREDICTED, not current)
        if predicted_traffic == 'High':
            base += " - High traffic expected"
        
        # Size compatibility
        if not size_compatible:
            base += " - Warning: Spot size may not match your vehicle"
        
        return base
    
    def _extract_prebooking_insights(self, hour, day_of_week, predicted_traffic,
                                     weather_forecast, spot_info, hours_until,
                                     size_compatible, recommended_size):
        """Extract insights for prebooking"""
        
        insights = {}
        
        # Weather FORECAST insights
        temp = weather_forecast['temperature']
        precip = weather_forecast['precipitation']
        
        if temp > 30:
            weather_status = f"Hot ({temp:.0f}°C forecast)"
            weather_tip = "Shaded or covered parking recommended"
        elif temp < 10:
            weather_status = f"Cold ({temp:.0f}°C forecast)"
            weather_tip = "Covered parking recommended"
        else:
            weather_status = f"Pleasant ({temp:.0f}°C forecast)"
            weather_tip = "Good parking conditions expected"
        
        if precip > 0:
            weather_status += ", Rain expected"
            weather_tip = "Covered parking strongly recommended"
        
        insights['weather'] = {
            'temperature': temp,
            'precipitation': precip,
            'status': weather_status,
            'tip': weather_tip,
            'source': weather_forecast.get('source', 'forecast')
        }
        
        # PREDICTED traffic insights
        if predicted_traffic == 'High':
            traffic_tip = "High traffic expected - spot may fill quickly"
        elif predicted_traffic == 'Low':
            traffic_tip = "Low traffic expected - easy access"
        else:
            traffic_tip = "Moderate traffic expected"
        
        insights['traffic'] = {
            'level': predicted_traffic,
            'status': f"{predicted_traffic} traffic predicted",
            'tip': traffic_tip,
            'source': 'historical_pattern'
        }
        
        # Time pattern
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        if 8 <= hour <= 10:
            time_pattern = "Morning Rush"
            time_tip = "High demand period"
        elif 17 <= hour <= 19:
            time_pattern = "Evening Rush"
            time_tip = "High demand period"
        elif 11 <= hour <= 16:
            time_pattern = "Midday"
            time_tip = "Moderate demand"
        else:
            time_pattern = "Off-Peak"
            time_tip = "Low demand, good availability"
        
        insights['time_pattern'] = {
            'pattern': time_pattern,
            'hour': hour,
            'day': days[day_of_week],
            'tip': time_tip,
            'hours_until': hours_until
        }
        
        # Spot characteristics
        proximity = spot_info.get('Proximity_To_Exit', 10.0) if spot_info else 10.0
        insights['spot_characteristics'] = {
            'distance_to_exit': proximity,
            'tip': f"Only {proximity:.1f}m from exit" if proximity < 10 else f"{proximity:.1f}m from exit"
        }
        
        # Vehicle compatibility
        insights['vehicle_compatibility'] = {
            'compatible': size_compatible,
            'recommended_size': recommended_size,
            'spot_size': spot_info.get('Spot_Size', 'Standard') if spot_info else 'Standard',
            'tip': "Good match for your vehicle" if size_compatible else f"Your vehicle needs {recommended_size} spot"
        }
        
        return insights
    
    def _get_default_prediction(self):
        """Return default prediction when model unavailable"""
        return {
            'prediction': 'Unknown',
            'confidence': 0.5,
            'probability_vacant': 0.5,
            'probability_occupied': 0.5,
            'recommendation': 'ML model not available',
            'insights': {},
            'predicted_traffic': 'Medium',
            'weather_forecast': {'temperature': 20, 'precipitation': 0},
            'size_compatible': True,
            'recommended_size': 'Standard',
            'hours_until_booking': 0
        }

