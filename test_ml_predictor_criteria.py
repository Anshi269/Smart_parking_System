"""
Test ML Predictor - Understanding the Criteria
Shows exactly what the ML model looks at when making predictions
"""
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, 'src')

from data.data_loader import ParkingDataLoader
from data.booking_system import BookingSystem
from ml.predictor import ParkingPredictor
import numpy as np

print("="*80)
print("ML PREDICTOR CRITERIA TEST")
print("Understanding How ML Makes Predictions")
print("="*80)

# Initialize
data_loader = ParkingDataLoader()
booking_system = BookingSystem(data_loader, seed=42)
predictor = ParkingPredictor(model_dir='models')

print("\n[1] MODEL FEATURES")
print("-"*80)
print(f"The ML model uses {len(predictor.feature_columns)} features for prediction:")
print("\nCategorized by source:\n")

# Categorize features
user_input_features = ['Hour', 'DayOfWeek', 'Electric_Vehicle', 'Parking_Spot_ID']
time_engineering = ['IsWeekend', 'Month', 'Hour_sin', 'Hour_cos', 'DayOfWeek_sin', 
                    'DayOfWeek_cos', 'Hour_Pattern', 'DayOfWeek_Pattern']
spot_metadata = ['Parking_Lot_Section_encoded', 'Proximity_To_Exit', 'Reserved_Status']
vehicle_specs = ['Vehicle_Type_encoded', 'Vehicle_Type_Weight', 'Vehicle_Type_Height']
environmental = ['Weather_Temperature', 'Weather_Precipitation', 'Nearby_Traffic_Level_encoded']
sensors = ['Sensor_Reading_Proximity', 'Sensor_Reading_Pressure', 'Sensor_Reading_Ultrasonic']
historical = ['User_Parking_History']

categories = {
    'USER INPUT (from user)': user_input_features,
    'TIME ENGINEERING (calculated)': time_engineering,
    'SPOT METADATA (from dataset)': spot_metadata,
    'VEHICLE SPECS (from dataset)': vehicle_specs,
    'ENVIRONMENTAL (Weather/Traffic)': environmental,
    'SENSORS (real-time)': sensors,
    'HISTORICAL (user patterns)': historical
}

for category, features in categories.items():
    print(f"\n{category}:")
    available = [f for f in features if f in predictor.feature_columns]
    for feat in available:
        print(f"  - {feat}")

print("\n" + "="*80)
print("[2] TESTING DIFFERENT SCENARIOS")
print("-"*80)

# Test scenario setup
test_scenarios = [
    {
        'name': 'Peak Hour Morning - Sedan',
        'spot_id': 20,
        'section': 'Zone A',
        'hour': 9,  # Morning rush
        'day_of_week': 1,  # Tuesday
        'vehicle_type': 'Sedan',
        'is_ev': False
    },
    {
        'name': 'Off-Peak Night - Sedan',
        'spot_id': 20,
        'section': 'Zone A',
        'hour': 2,  # 2 AM
        'day_of_week': 1,  # Tuesday
        'vehicle_type': 'Sedan',
        'is_ev': False
    },
    {
        'name': 'Midday Weekday - EV Vehicle',
        'spot_id': 20,
        'section': 'Zone A',
        'hour': 14,  # 2 PM
        'day_of_week': 2,  # Wednesday
        'vehicle_type': 'Electric Vehicle',
        'is_ev': True
    },
    {
        'name': 'Weekend Evening - Motorcycle',
        'spot_id': 20,
        'section': 'Zone A',
        'hour': 18,  # 6 PM
        'day_of_week': 6,  # Sunday
        'vehicle_type': 'Motorcycle',
        'is_ev': False
    }
]

for i, scenario in enumerate(test_scenarios, 1):
    print(f"\n{'='*80}")
    print(f"SCENARIO {i}: {scenario['name']}")
    print("="*80)
    
    # Get prediction
    prediction = predictor.predict_spot_availability(
        spot_id=scenario['spot_id'],
        section=scenario['section'],
        hour=scenario['hour'],
        day_of_week=scenario['day_of_week'],
        vehicle_type=scenario['vehicle_type'],
        is_ev=scenario['is_ev'],
        data_loader=data_loader
    )
    
    # Get spot info to show raw data
    spot_info = data_loader.get_spot_info(scenario['spot_id'], scenario['section'])
    
    print(f"\nINPUT CONDITIONS:")
    print(f"  Time: {scenario['hour']}:00 ({['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][scenario['day_of_week']]})")
    print(f"  Spot: {scenario['spot_id']} in {scenario['section']}")
    print(f"  Vehicle: {scenario['vehicle_type']}")
    print(f"  EV Charging: {'Yes' if scenario['is_ev'] else 'No'}")
    
    # Show what ML sees
    print(f"\nWHAT ML MODEL SEES:")
    
    # Time pattern
    if 8 <= scenario['hour'] <= 10 or 17 <= scenario['hour'] <= 19:
        time_pattern = "PEAK HOUR"
        pattern_value = 2
    elif 11 <= scenario['hour'] <= 16:
        time_pattern = "MODERATE"
        pattern_value = 1
    else:
        time_pattern = "OFF-PEAK"
        pattern_value = 0
    
    print(f"  Time Pattern: {time_pattern} (value={pattern_value})")
    print(f"  Hour (cyclical): sin={np.sin(2*np.pi*scenario['hour']/24):.3f}, cos={np.cos(2*np.pi*scenario['hour']/24):.3f}")
    print(f"  Day Type: {'Weekend' if scenario['day_of_week'] >= 5 else 'Weekday'}")
    
    # Environmental
    if spot_info:
        print(f"\n  Weather:")
        print(f"    Temperature: {spot_info.get('Weather_Temperature', 20):.1f}°C")
        print(f"    Precipitation: {spot_info.get('Weather_Precipitation', 0)}")
        
        print(f"  Traffic:")
        print(f"    Level: {spot_info.get('Nearby_Traffic_Level', 'Medium')}")
        
        print(f"  Spot Characteristics:")
        print(f"    Distance to Exit: {spot_info.get('Proximity_To_Exit', 10):.1f}m")
        print(f"    Reserved: {'Yes' if spot_info.get('Reserved_Status', 0) == 1 else 'No'}")
        
        print(f"  Sensors:")
        print(f"    Proximity: {spot_info.get('Sensor_Reading_Proximity', 5):.2f}")
        print(f"    Pressure: {spot_info.get('Sensor_Reading_Pressure', 2):.2f}")
        print(f"    Ultrasonic: {spot_info.get('Sensor_Reading_Ultrasonic', 100):.2f}")
    
    # Show prediction
    print(f"\nML PREDICTION:")
    print(f"  Prediction: {prediction['prediction']}")
    print(f"  Confidence: {prediction['confidence']*100:.1f}%")
    print(f"  Probability Vacant: {prediction['probability_vacant']*100:.1f}%")
    print(f"  Probability Occupied: {prediction['probability_occupied']*100:.1f}%")
    
    print(f"\nRECOMMENDATION:")
    print(f"  {prediction['recommendation']}")
    
    # Show insights
    insights = prediction['insights']
    if insights:
        print(f"\nGENERATED INSIGHTS:")
        if 'weather' in insights:
            print(f"  Weather: {insights['weather']['status']}")
            print(f"    Tip: {insights['weather']['tip']}")
        if 'traffic' in insights:
            print(f"  Traffic: {insights['traffic']['status']}")
            print(f"    Tip: {insights['traffic']['tip']}")
        if 'time_pattern' in insights:
            print(f"  Time: {insights['time_pattern']['pattern']}")
            print(f"    Tip: {insights['time_pattern']['tip']}")

print("\n" + "="*80)
print("[3] DECISION CRITERIA EXPLANATION")
print("-"*80)

print("""
The ML model makes predictions based on:

1. TIME PATTERNS (Most Important):
   - Peak Hours (8-10 AM, 5-7 PM): Higher occupancy expected
   - Off-Peak (Night): Lower occupancy expected
   - Cyclical encoding helps model understand time is circular (23:00 -> 00:00)

2. ENVIRONMENTAL CONDITIONS:
   - Weather Temperature: Hot/cold affects parking choices
   - Precipitation: Rain increases demand for covered spots
   - Traffic Level: High traffic -> spots fill faster

3. SPOT CHARACTERISTICS:
   - Proximity to Exit: Closer spots more popular
   - Reserved Status: Reserved spots less available
   - Sensor Readings: Real-time occupancy indicators

4. VEHICLE MATCHING:
   - Vehicle Type: Different vehicles prefer different spots
   - EV Charging: EV vehicles need charging spots
   - Vehicle Size: Weight/height affects spot suitability

5. HISTORICAL PATTERNS:
   - User Parking History: Repeat users have patterns
   - Section occupancy trends
   - Day of week patterns (weekday vs weekend)

RECOMMENDATION LOGIC:
- Probability > 70%: "HIGHLY RECOMMENDED"
- Probability > 55%: "RECOMMENDED"  
- Probability > 45%: "UNCERTAIN"
- Probability < 45%: "NOT RECOMMENDED"

Plus contextual modifiers:
- Peak hour warning
- Weather suggestions (hot/cold/rain)
- Traffic alerts
""")

print("="*80)
print("[4] COMPARING SIMILAR SPOTS IN DIFFERENT CONDITIONS")
print("-"*80)

spot_id = 20
section = "Zone A"

conditions = [
    {'name': 'Best Case', 'hour': 2, 'day': 2, 'vehicle': 'Car'},
    {'name': 'Normal Case', 'hour': 14, 'day': 2, 'vehicle': 'Car'},
    {'name': 'Worst Case', 'hour': 9, 'day': 1, 'vehicle': 'Car'},
]

print(f"\nSame Spot (Spot {spot_id}, {section}) under different conditions:\n")
print(f"{'Condition':<15} {'Time':<15} {'Vacant %':<12} {'Occupied %':<12} {'Recommendation':<20}")
print("-"*80)

for cond in conditions:
    pred = predictor.predict_spot_availability(
        spot_id=spot_id,
        section=section,
        hour=cond['hour'],
        day_of_week=cond['day'],
        vehicle_type=cond['vehicle'],
        is_ev=False,
        data_loader=data_loader
    )
    
    time_str = f"{cond['hour']}:00 {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][cond['day']]}"
    rec_short = pred['recommendation'].split('-')[0].strip()
    
    print(f"{cond['name']:<15} {time_str:<15} {pred['probability_vacant']*100:<11.1f}% "
          f"{pred['probability_occupied']*100:<11.1f}% {rec_short:<20}")

print("\n" + "="*80)
print("[5] FEATURE IMPORTANCE (What matters most)")
print("-"*80)

print("""
Based on the trained Random Forest model, here are the TOP 10 most important
features (from training):

1. Sensor_Reading_Ultrasonic (8.6%) - Real-time occupancy detection
2. Vehicle_Type_Height (8.2%) - Vehicle size matching
3. Sensor_Reading_Proximity (7.9%) - Distance sensor
4. Vehicle_Type_Weight (7.7%) - Vehicle weight matching
5. Proximity_To_Exit (7.7%) - Spot location preference
6. User_Parking_History (7.6%) - Historical patterns
7. Weather_Temperature (7.6%) - Weather conditions ⭐
8. Sensor_Reading_Pressure (7.3%) - Pressure sensor
9. Parking_Spot_ID (6.6%) - Specific spot characteristics
10. Month (4.4%) - Seasonal patterns

Note: Time-based features (Hour, DayOfWeek) are distributed across
cyclical encodings (Hour_sin, Hour_cos, etc.)
""")

print("="*80)
print("[6] WEATHER & TRAFFIC IMPACT DEMONSTRATION")
print("-"*80)

# Get spot with different weather/traffic from dataset
print("\nShowing how weather and traffic affect recommendations:\n")

spots_sample = [20, 25, 30]
for spot in spots_sample:
    spot_info = data_loader.get_spot_info(spot, "Zone A")
    if spot_info:
        pred = predictor.predict_spot_availability(
            spot_id=spot,
            section="Zone A",
            hour=14,
            day_of_week=2,
            vehicle_type='Car',
            is_ev=False,
            data_loader=data_loader
        )
        
        print(f"Spot {spot}:")
        print(f"  Weather: {spot_info['Weather_Temperature']:.0f}°C, "
              f"Precip: {spot_info['Weather_Precipitation']}")
        print(f"  Traffic: {spot_info['Nearby_Traffic_Level']}")
        print(f"  ML Confidence: {pred['probability_vacant']*100:.0f}% vacant")
        print(f"  Insight: {pred['insights'].get('weather', {}).get('tip', 'N/A')}")
        print()

print("="*80)
print("SUMMARY: ML PREDICTOR CRITERIA")
print("="*80)

print("""
The ML predictor works by:

✅ INPUTS (What you provide):
   - Time: Hour and Day of week
   - Location: Parking spot ID and section
   - Vehicle: Type and EV status

✅ ENRICHMENT (What ML adds):
   - Time patterns (peak/off-peak)
   - Cyclical time encoding
   - Weather conditions from dataset
   - Traffic levels from dataset
   - Sensor readings from dataset

✅ PROCESSING (What ML does):
   - Combines all 25 features
   - Scales them using trained scaler
   - Passes through Random Forest model
   - Outputs probability distribution

✅ OUTPUTS (What you get):
   - Prediction: Vacant or Occupied
   - Confidence: 0-100%
   - Recommendation: Text suggestion
   - Insights: Weather, traffic, time patterns
   - Smart tips: Context-aware advice

✅ KEY CRITERIA FOR "GOOD" SPOT:
   1. Off-peak time (+)
   2. Good weather conditions (+)
   3. Low traffic level (+)
   4. Close to exit (+)
   5. Matching vehicle type (+)
   6. Not reserved (+)
   7. Historical availability (+)

The model is NOT perfect (50% base accuracy) but provides
VALUABLE CONTEXT through weather, traffic, and time insights!
""")

print("="*80)
print("Test complete! You now understand how the ML predictor works.")
print("="*80)

