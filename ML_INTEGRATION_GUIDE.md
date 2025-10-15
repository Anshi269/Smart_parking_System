# 🤖 ML Integration Guide

## Overview

This guide explains how the collected user inputs will be used for ML predictions with your trained model from `model.py`.

## 📊 User Inputs Collected

The app currently collects **5 key inputs** from users:

| Field | Type | Example | Default | Purpose |
|-------|------|---------|---------|---------|
| **Hour** | Integer (0-23) | `14` (2:00 PM) | Current hour | Predict availability by time |
| **Day of Week** | String | `"Monday"` | Today | Detect weekly patterns |
| **Vehicle Type** | String | `"Sedan"` | "Sedan" | Match with spot compatibility |
| **Parking Spot ID** | Integer | `12` | From slot selection | Specific spot prediction |
| **Electric Vehicle** | Binary (0/1) | `1` (Yes) | 0 (No) | EV charging requirement |

## 🔗 Mapping to CSV Dataset

Your CSV file (`IIoT_Smart_Parking_Management.csv`) contains these fields that align with user inputs:

### Direct Matches:
- ✅ `Parking_Spot_ID` → User Input: **Parking Spot ID**
- ✅ `Electric_Vehicle` → User Input: **Electric Vehicle** (0/1)
- ✅ `Vehicle_Type` → User Input: **Vehicle Type**

### Derived Fields:
- ⏰ `Entry_Time` → Extracted from User Input: **Hour**
- 📅 `Timestamp` → Derived from User Input: **Day of Week** + **Hour**

## 🧠 How Occupied Slots Are Determined

### Current Implementation:
```python
# src/data/data_loader.py
def get_spot_info(self, spot_id, section):
    spot_data = self.df[
        (self.df['Parking_Spot_ID'] == spot_id) & 
        (self.df['Parking_Lot_Section'] == section)
    ]
    # Takes LAST record (most recent) for current status
    return spot_data.iloc[-1].to_dict()
```

**How it works:**
1. CSV contains **time-series data** - multiple records per spot over time
2. Each record has a `Timestamp` and `Occupancy_Status` (Occupied/Vacant)
3. We take the **most recent record** (last row) to show current status
4. This simulates "real-time" occupancy from historical data

### Example CSV Data:
```csv
Timestamp,Parking_Spot_ID,Occupancy_Status,Parking_Lot_Section
2021-01-01 08:00:00,20,Occupied,Zone A
2021-01-01 09:00:00,20,Vacant,Zone A    ← Most recent = Current status
```

## 🔮 Future ML Prediction Flow

When you're ready to integrate ML, here's how it will work:

### Phase 1: Prepare Input Features
```python
def prepare_prediction_input(user_inputs, data_loader):
    """
    Convert user inputs to ML model features
    """
    features = {
        # User inputs
        'Parking_Spot_ID': user_inputs['parking_spot_id'],
        'Entry_Time': user_inputs['hour'],
        'Electric_Vehicle': user_inputs['electric_vehicle'],
        'Vehicle_Type': user_inputs['vehicle_type'],
        
        # Derived features
        'DayOfWeek': convert_day_to_number(user_inputs['day_of_week']),
        
        # Historical features from CSV
        'Parking_Lot_Section': get_section_from_spot(user_inputs['parking_spot_id']),
        'Proximity_To_Exit': get_spot_metadata(...),
        'Spot_Size': get_spot_metadata(...),
        
        # Context features (you can add these)
        'Weather_Temperature': get_weather_forecast(...),
        'Nearby_Traffic_Level': get_traffic_prediction(...),
    }
    return features
```

### Phase 2: Make Predictions
```python
def predict_availability(features, model):
    """
    Predict if spot will be available at requested time
    """
    # Use your trained model from model.py
    prediction = model.predict(features)
    probability = model.predict_proba(features)
    
    return {
        'available': prediction == 0,  # 0 = Vacant, 1 = Occupied
        'confidence': probability,
        'recommendation': generate_recommendation(...)
    }
```

### Phase 3: Generate Smart Recommendations

Based on your requirements, here are the recommendation types:

#### 1. Core Predictions (Real-Time & Prebooking)
```python
recommendations = {
    'spot_availability': "Spot A12 will likely be free in 25 mins",
    'lot_occupancy': "Lot C occupancy expected: 82% at 6 PM",
    'weather_impact': "Rain likely: covered lots expected to be full earlier",
    'peak_hours': "High demand expected between 5–7 PM; book early",
    'crowd_trend': "Crowd increasing (rising trend detected)"
}
```

#### 2. Personalized Insights (User-Centric)
```python
personalized = {
    'best_match': "Recommended for you: Slot D2 (close to exit, usually free at 9 AM)",
    'optimal_time': "Least crowded between 2–3 PM",
    'ev_spots': "EV charging spots in Zone A: 85% available at your time",
    'quick_exit': "Spots near exit: A1, A5, B3 (based on your preference)"
}
```

## 📁 Suggested File Structure for ML Integration

When ready to add ML, create these files:

```
src/
├── ml/
│   ├── __init__.py
│   ├── predictor.py          # ML prediction logic
│   ├── feature_engineering.py # Feature preparation
│   └── recommender.py        # Recommendation engine
├── components/
│   └── predictions_view.py   # UI to show predictions
```

## 🎯 Next Steps (When You're Ready)

### Step 1: Load Your Trained Model
```python
# src/ml/predictor.py
import joblib
from model import best_model  # From your model.py

class ParkingPredictor:
    def __init__(self):
        # Load your trained model
        self.model = best_model
        self.scaler = scaler  # From model.py
    
    def predict(self, features):
        # Scale features
        X = self.scaler.transform([features])
        # Predict
        return self.model.predict(X)
```

### Step 2: Add Prediction Button
In `slot_selector.py`, after slot selection:
```python
if st.button("🔮 Get AI Recommendations"):
    predictions = get_predictions(user_inputs, selected_slot)
    display_recommendations(predictions)
```

### Step 3: Display Predictions
Create beautiful UI to show:
- Availability probability
- Best time to arrive
- Alternative recommendations
- Crowding predictions
- Weather-based suggestions

## 💡 Key Points

1. **User inputs are ready** - All 5 fields are collected and stored in session state
2. **No predictions yet** - Currently just collecting data (as you requested)
3. **CSV provides history** - Use historical data to train/predict future availability
4. **Modular design** - Easy to add ML module when ready
5. **Session state** - All inputs persist during navigation

## 🔧 Data Flow Summary

```
User Fills Form → Session State → Ready for ML
     ↓                                   ↓
5 Input Fields                    Feature Engineering
     ↓                                   ↓
Parking Spot ID                   Historical Data (CSV)
Hour (0-23)                             ↓
Day of Week                       Trained Model (model.py)
Vehicle Type                            ↓
EV Charging                       Predictions + Recommendations
     ↓                                   ↓
Stored in                          Display in UI
st.session_state.user_inputs      (Coming Soon)
```

## 📝 Current Status

✅ **Completed:**
- User input collection (5 fields)
- Session state management
- Data integration with CSV
- Occupancy status from historical data

⏳ **Pending (When you say):**
- ML model integration
- Prediction engine
- Recommendation system
- Real-time updates

---

**Ready for ML Integration?** Just let me know when you want to proceed with predictions!

