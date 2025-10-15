"""
ML Predictor Module
Loads trained model and makes predictions for parking spots
Combines ML predictions with database availability
"""
import joblib
import numpy as np
import pandas as pd
import os
from datetime import datetime

class ParkingPredictor:
    """
    AI-powered parking predictor
    Uses trained ML model to provide intelligent suggestions
    """
    
    def __init__(self, model_dir='models'):
        """
        Initialize predictor by loading trained model
        
        Args:
            model_dir: Directory containing saved model files
        """
        self.model_dir = model_dir
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.label_encoders = None
        self.is_loaded = False
        
        self._load_model()
    
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
            
            print("[OK] ML model loaded successfully")
        
        except Exception as e:
            print(f"[ERROR] Failed to load ML model: {e}")
            self.is_loaded = False
    
    def predict_spot_availability(self, spot_id, section, hour, day_of_week, 
                                  vehicle_type='Sedan', is_ev=False, 
                                  data_loader=None):
        """
        Predict if a parking spot will be available
        
        Args:
            spot_id: Parking spot ID
            section: Parking section (Zone A, B, C, D)
            hour: Hour of day (0-23)
            day_of_week: Day of week (0=Monday, 6=Sunday) or day name
            vehicle_type: Vehicle type (Sedan, SUV, Truck, Motorcycle)
            is_ev: Electric vehicle (True/False)
            data_loader: ParkingDataLoader instance for spot metadata
        
        Returns:
            dict: {
                'prediction': 'Vacant' or 'Occupied',
                'confidence': float (0-1),
                'probability_vacant': float,
                'probability_occupied': float,
                'recommendation': str,
                'insights': dict
            }
        """
        if not self.is_loaded:
            return {
                'prediction': 'Unknown',
                'confidence': 0.5,
                'probability_vacant': 0.5,
                'probability_occupied': 0.5,
                'recommendation': 'ML model not available',
                'insights': {}
            }
        
        try:
            # Convert day name to number if needed
            if isinstance(day_of_week, str):
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                day_of_week = days.index(day_of_week) if day_of_week in days else 0
            
            # Get spot metadata from data loader
            spot_info = data_loader.get_spot_info(spot_id, section) if data_loader else {}
            
            if not spot_info:
                # Use defaults if spot not found
                spot_info = {
                    'Proximity_To_Exit': 10.0,
                    'Weather_Temperature': 20.0,
                    'Weather_Precipitation': 0,
                    'Nearby_Traffic_Level': 'Medium',
                    'Sensor_Reading_Proximity': 5.0,
                    'Sensor_Reading_Pressure': 2.0,
                    'Sensor_Reading_Ultrasonic': 100.0,
                    'Vehicle_Type_Weight': 1500.0,
                    'Vehicle_Type_Height': 4.0,
                    'User_Parking_History': 5.0,
                    'Reserved_Status': 0
                }
            
            # Build feature dictionary
            features = self._build_features(
                hour, day_of_week, is_ev, spot_id, section,
                vehicle_type, spot_info
            )
            
            # Make prediction
            feature_df = pd.DataFrame([features])[self.feature_columns]
            feature_scaled = self.scaler.transform(feature_df)
            
            prediction = self.model.predict(feature_scaled)[0]
            probabilities = self.model.predict_proba(feature_scaled)[0]
            
            prob_vacant = probabilities[0]
            prob_occupied = probabilities[1]
            confidence = max(prob_vacant, prob_occupied)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                prob_vacant, hour, spot_info
            )
            
            # Extract insights
            insights = self._extract_insights(spot_info, hour, day_of_week)
            
            return {
                'prediction': 'Vacant' if prediction == 0 else 'Occupied',
                'confidence': confidence,
                'probability_vacant': prob_vacant,
                'probability_occupied': prob_occupied,
                'recommendation': recommendation,
                'insights': insights
            }
        
        except Exception as e:
            print(f"[ERROR] Prediction failed: {e}")
            return {
                'prediction': 'Unknown',
                'confidence': 0.5,
                'probability_vacant': 0.5,
                'probability_occupied': 0.5,
                'recommendation': f'Prediction error: {str(e)}',
                'insights': {}
            }
    
    def _build_features(self, hour, day_of_week, is_ev, spot_id, section,
                       vehicle_type, spot_info):
        """Build feature dictionary for prediction"""
        
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
        
        day_pattern = 1 if day_of_week < 5 else 0  # Weekday/Weekend
        
        # Encode section and vehicle type
        section_encoded = self.label_encoders['Parking_Lot_Section'].transform([section])[0]
        
        # Map vehicle type to CSV format
        vehicle_type_map = {
            'Sedan': 'Car',
            'SUV': 'Car',
            'Truck': 'Car',
            'Car': 'Car',
            'Motorcycle': 'Motorcycle',
            'Electric Vehicle': 'Electric Vehicle'
        }
        vehicle_mapped = vehicle_type_map.get(vehicle_type, 'Car')
        vehicle_encoded = self.label_encoders['Vehicle_Type'].transform([vehicle_mapped])[0]
        
        # Traffic level encoding
        traffic_level = spot_info.get('Nearby_Traffic_Level', 'Medium')
        traffic_encoded = self.label_encoders['Nearby_Traffic_Level'].transform([traffic_level])[0]
        
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
            'Proximity_To_Exit': spot_info.get('Proximity_To_Exit', 10.0),
            'Reserved_Status': spot_info.get('Reserved_Status', 0),
            'Weather_Temperature': spot_info.get('Weather_Temperature', 20.0),
            'Weather_Precipitation': spot_info.get('Weather_Precipitation', 0),
            'Nearby_Traffic_Level_encoded': traffic_encoded,
            'Sensor_Reading_Proximity': spot_info.get('Sensor_Reading_Proximity', 5.0),
            'Sensor_Reading_Pressure': spot_info.get('Sensor_Reading_Pressure', 2.0),
            'Sensor_Reading_Ultrasonic': spot_info.get('Sensor_Reading_Ultrasonic', 100.0),
            'Vehicle_Type_Weight': spot_info.get('Vehicle_Type_Weight', 1500.0),
            'Vehicle_Type_Height': spot_info.get('Vehicle_Type_Height', 4.0),
            'User_Parking_History': spot_info.get('User_Parking_History', 5.0)
        }
    
    def _generate_recommendation(self, prob_vacant, hour, spot_info):
        """Generate human-readable recommendation"""
        
        if prob_vacant > 0.7:
            base = "HIGHLY RECOMMENDED - Good availability expected"
        elif prob_vacant > 0.55:
            base = "RECOMMENDED - Likely available"
        elif prob_vacant > 0.45:
            base = "UNCERTAIN - Consider alternatives"
        else:
            base = "NOT RECOMMENDED - Likely occupied, check alternatives"
        
        # Add time-based context
        if 8 <= hour <= 10 or 17 <= hour <= 19:
            base += " (Peak hour - book quickly)"
        
        # Add weather context
        temp = spot_info.get('Weather_Temperature', 20)
        if temp > 30:
            base += " (Hot weather - consider covered spots)"
        elif temp < 5:
            base += " (Cold weather - covered spots recommended)"
        
        # Add traffic context
        traffic = spot_info.get('Nearby_Traffic_Level', 'Medium')
        if traffic == 'High':
            base += " (High traffic - allow extra time)"
        
        return base
    
    def _extract_insights(self, spot_info, hour, day_of_week):
        """Extract contextual insights from spot data"""
        
        insights = {}
        
        # Weather insights
        temp = spot_info.get('Weather_Temperature', 20.0)
        precip = spot_info.get('Weather_Precipitation', 0)
        
        if temp > 30:
            weather_status = f"Hot ({temp:.0f}°C)"
            weather_tip = "Consider shaded or covered parking"
        elif temp < 10:
            weather_status = f"Cold ({temp:.0f}°C)"
            weather_tip = "Covered parking recommended"
        else:
            weather_status = f"Pleasant ({temp:.0f}°C)"
            weather_tip = "Good parking conditions"
        
        if precip > 0:
            weather_status += ", Rain expected"
            weather_tip = "Covered parking strongly recommended"
        
        insights['weather'] = {
            'temperature': temp,
            'precipitation': precip,
            'status': weather_status,
            'tip': weather_tip
        }
        
        # Traffic insights
        traffic = spot_info.get('Nearby_Traffic_Level', 'Medium')
        insights['traffic'] = {
            'level': traffic,
            'status': f"{traffic} traffic conditions",
            'tip': "Easy access" if traffic == 'Low' else "Allow extra time"
        }
        
        # Time pattern insights
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
            'day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][day_of_week],
            'tip': time_tip
        }
        
        # Spot characteristics
        proximity = spot_info.get('Proximity_To_Exit', 10.0)
        insights['spot_characteristics'] = {
            'distance_to_exit': proximity,
            'tip': f"Only {proximity:.1f}m from exit" if proximity < 10 else f"{proximity:.1f}m from exit"
        }
        
        return insights
    
    def get_alternative_suggestions(self, section, hour, day_of_week, 
                                   vehicle_type, is_ev, data_loader, 
                                   booking_system, exclude_spot=None, top_n=3):
        """
        Find best alternative spots using ML predictions
        
        Args:
            section: Current section
            hour: Hour of day
            day_of_week: Day of week
            vehicle_type: Vehicle type
            is_ev: Electric vehicle flag
            data_loader: Data loader instance
            booking_system: Booking system instance
            exclude_spot: Spot to exclude (current selection)
            top_n: Number of alternatives to return
        
        Returns:
            list: Top alternative spots with predictions
        """
        if not self.is_loaded:
            return []
        
        try:
            # Get all available spots in section
            available_spots = booking_system.get_available_spots_in_section(section, hour)
            
            if exclude_spot and exclude_spot in available_spots:
                available_spots.remove(exclude_spot)
            
            # Predict for each available spot
            spot_predictions = []
            for spot_id in available_spots[:20]:  # Limit to 20 for performance
                prediction = self.predict_spot_availability(
                    spot_id, section, hour, day_of_week,
                    vehicle_type, is_ev, data_loader
                )
                
                spot_info = data_loader.get_spot_info(spot_id, section)
                
                spot_predictions.append({
                    'spot_id': spot_id,
                    'section': section,
                    'confidence': prediction['probability_vacant'],
                    'distance_to_exit': spot_info.get('Proximity_To_Exit', 10.0) if spot_info else 10.0,
                    'prediction': prediction
                })
            
            # Sort by confidence (descending)
            spot_predictions.sort(key=lambda x: x['confidence'], reverse=True)
            
            return spot_predictions[:top_n]
        
        except Exception as e:
            print(f"[ERROR] Failed to get alternatives: {e}")
            return []

