"""
PROPERLY TRAINED PARKING PREDICTION MODEL
Uses only features available at prediction time
Includes feature engineering as per model features.txt
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
import joblib
import os

print("="*70)
print("SMART PARKING - PROPER MODEL TRAINING")
print("="*70)

# Load dataset
df = pd.read_csv('resources/IIoT_Smart_Parking_Management (2).csv')
print(f"\n[OK] Loaded {len(df)} records")

# Parse timestamp to extract time features
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['DayOfWeek'] = df['Timestamp'].dt.dayofweek  # 0=Monday, 6=Sunday
df['Month'] = df['Timestamp'].dt.month
df['IsWeekend'] = (df['DayOfWeek'] >= 5).astype(int)

# Use Entry_Time as Hour (already in dataset)
df['Hour'] = df['Entry_Time']

print("\n[1] FEATURE ENGINEERING")
print("-" * 70)

# Cyclical encoding for time features
df['Hour_sin'] = np.sin(2 * np.pi * df['Hour'] / 24)
df['Hour_cos'] = np.cos(2 * np.pi * df['Hour'] / 24)
df['DayOfWeek_sin'] = np.sin(2 * np.pi * df['DayOfWeek'] / 7)
df['DayOfWeek_cos'] = np.cos(2 * np.pi * df['DayOfWeek'] / 7)

# Hour patterns (peak/off-peak)
def get_hour_pattern(hour):
    if 8 <= hour <= 10 or 17 <= hour <= 19:
        return 2  # Peak
    elif 11 <= hour <= 16:
        return 1  # Moderate
    else:
        return 0  # Off-peak

df['Hour_Pattern'] = df['Hour'].apply(get_hour_pattern)

# Day patterns (weekday/weekend)
df['DayOfWeek_Pattern'] = (df['DayOfWeek'] < 5).astype(int)  # 1=Weekday, 0=Weekend

# Encode categorical variables
label_encoders = {}
categorical_cols = ['Parking_Lot_Section', 'Vehicle_Type', 'Nearby_Traffic_Level', 'User_Type']
for col in categorical_cols:
    if col in df.columns:
        le = LabelEncoder()
        df[col + '_encoded'] = le.fit_transform(df[col].astype(str))
        label_encoders[col] = le

# Target variable
df['Occupancy_Status_encoded'] = LabelEncoder().fit_transform(df['Occupancy_Status'])

print(f"  [OK] Cyclical time features created")
print(f"  [OK] Hour/Day patterns created")
print(f"  [OK] Categorical variables encoded")

# Select features - ONLY those available at prediction time!
print("\n[2] FEATURE SELECTION (Available at Prediction Time)")
print("-" * 70)

feature_columns = [
    # User inputs (collected from user)
    'Hour', 'DayOfWeek', 'Electric_Vehicle', 'Parking_Spot_ID',
    
    # Engineered time features
    'IsWeekend', 'Month', 'Hour_sin', 'Hour_cos', 
    'DayOfWeek_sin', 'DayOfWeek_cos', 'Hour_Pattern', 'DayOfWeek_Pattern',
    
    # From dataset (historical data for that spot/section)
    'Parking_Lot_Section_encoded', 'Vehicle_Type_encoded',
    'Proximity_To_Exit', 'Reserved_Status',
    
    # Weather & Traffic (available from forecast/sensors)
    'Weather_Temperature', 'Weather_Precipitation', 'Nearby_Traffic_Level_encoded',
    
    # Sensor readings (available in real-time)
    'Sensor_Reading_Proximity', 'Sensor_Reading_Pressure', 'Sensor_Reading_Ultrasonic',
    
    # Vehicle specifications (from user vehicle type)
    'Vehicle_Type_Weight', 'Vehicle_Type_Height',
    
    # User history (if available)
    'User_Parking_History'
]

# Verify all features exist
available_features = [f for f in feature_columns if f in df.columns]
missing_features = [f for f in feature_columns if f not in df.columns]

if missing_features:
    print(f"  [WARNING] Missing features: {missing_features}")

print(f"  [OK] Using {len(available_features)} features")
for i, feat in enumerate(available_features, 1):
    print(f"     {i:2d}. {feat}")

# EXCLUDED FEATURES (not available at prediction time)
excluded_features = ['Exit_Time', 'Parking_Duration', 'Payment_Amount', 
                     'Parking_Violation', 'Occupancy_Rate']
print(f"\n  [INFO] Excluded {len(excluded_features)} features (not available at prediction):")
for feat in excluded_features:
    print(f"     X {feat}")

# Prepare training data
X = df[available_features].copy()
y = df['Occupancy_Status_encoded'].copy()

# Handle any missing values
X = X.fillna(X.mean())

print(f"\n[3] DATASET PREPARATION")
print("-" * 70)
print(f"  Total samples: {len(X)}")
print(f"  Features: {X.shape[1]}")
print(f"  Occupied: {sum(y==1)} ({sum(y==1)/len(y)*100:.1f}%)")
print(f"  Vacant: {sum(y==0)} ({sum(y==0)/len(y)*100:.1f}%)")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"  Training set: {len(X_train)} samples")
print(f"  Test set: {len(X_test)} samples")

# Train models
print(f"\n[4] MODEL TRAINING")
print("-" * 70)

models = {
    'Random Forest': RandomForestClassifier(
        n_estimators=200, max_depth=15, min_samples_split=10,
        random_state=42, class_weight='balanced', n_jobs=-1
    ),
    'Gradient Boosting': GradientBoostingClassifier(
        n_estimators=200, learning_rate=0.1, max_depth=7,
        min_samples_split=10, random_state=42
    ),
    'XGBoost': XGBClassifier(
        n_estimators=200, max_depth=7, learning_rate=0.1,
        subsample=0.8, colsample_bytree=0.8,
        random_state=42, eval_metric='logloss'
    )
}

results = {}
for name, model in models.items():
    print(f"\n  Training {name}...")
    model.fit(X_train_scaled, y_train)
    
    # Predictions
    y_pred_train = model.predict(X_train_scaled)
    y_pred_test = model.predict(X_test_scaled)
    
    # Metrics
    train_acc = accuracy_score(y_train, y_pred_train)
    test_acc = accuracy_score(y_test, y_pred_test)
    test_f1 = f1_score(y_test, y_pred_test, average='weighted')
    
    results[name] = {
        'model': model,
        'train_acc': train_acc,
        'test_acc': test_acc,
        'f1': test_f1,
        'predictions': y_pred_test
    }
    
    print(f"    Train Accuracy: {train_acc:.3f}")
    print(f"    Test Accuracy:  {test_acc:.3f}")
    print(f"    F1 Score:       {test_f1:.3f}")

# Select best model
print(f"\n[5] MODEL SELECTION")
print("-" * 70)

best_model_name = max(results, key=lambda k: results[k]['test_acc'])
best_model = results[best_model_name]['model']
best_acc = results[best_model_name]['test_acc']
best_f1 = results[best_model_name]['f1']

print(f"  [BEST] {best_model_name}")
print(f"    Accuracy: {best_acc:.3f}")
print(f"    F1 Score: {best_f1:.3f}")

# Detailed evaluation
print(f"\n[6] DETAILED EVALUATION")
print("-" * 70)

y_pred_best = results[best_model_name]['predictions']
print("\nClassification Report:")
print(classification_report(y_test, y_pred_best, target_names=['Vacant', 'Occupied']))

print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred_best)
print(f"  True Vacant, Predicted Vacant:    {cm[0][0]}")
print(f"  True Vacant, Predicted Occupied:  {cm[0][1]}")
print(f"  True Occupied, Predicted Vacant:  {cm[1][0]}")
print(f"  True Occupied, Predicted Occupied: {cm[1][1]}")

# Feature importance (if available)
if hasattr(best_model, 'feature_importances_'):
    print(f"\n[7] TOP 10 IMPORTANT FEATURES")
    print("-" * 70)
    
    importances = best_model.feature_importances_
    feature_importance = sorted(zip(available_features, importances), 
                                key=lambda x: x[1], reverse=True)
    
    for i, (feat, imp) in enumerate(feature_importance[:10], 1):
        print(f"  {i:2d}. {feat:30s} {imp:.4f}")

# Save model
print(f"\n[8] SAVING MODEL")
print("-" * 70)

model_dir = 'models'
os.makedirs(model_dir, exist_ok=True)

model_path = os.path.join(model_dir, 'parking_predictor.pkl')
scaler_path = os.path.join(model_dir, 'scaler.pkl')
features_path = os.path.join(model_dir, 'feature_columns.pkl')
encoders_path = os.path.join(model_dir, 'label_encoders.pkl')

joblib.dump(best_model, model_path)
joblib.dump(scaler, scaler_path)
joblib.dump(available_features, features_path)
joblib.dump(label_encoders, encoders_path)

print(f"  [OK] Model saved to: {model_path}")
print(f"  [OK] Scaler saved to: {scaler_path}")
print(f"  [OK] Features saved to: {features_path}")
print(f"  [OK] Encoders saved to: {encoders_path}")

# Test prediction example
print(f"\n[9] TEST PREDICTION")
print("-" * 70)

print("\n  Example: User wants to book Spot 20 on Wednesday at 2 PM")
print("  Vehicle: Sedan, EV: No")

# Get sample data for spot 20
spot_20 = df[df['Parking_Spot_ID'] == 20].iloc[0]

test_input = {
    'Hour': 14,
    'DayOfWeek': 2,  # Wednesday
    'Electric_Vehicle': 0,
    'Parking_Spot_ID': 20,
    'IsWeekend': 0,
    'Month': spot_20['Month'],
    'Hour_sin': np.sin(2 * np.pi * 14 / 24),
    'Hour_cos': np.cos(2 * np.pi * 14 / 24),
    'DayOfWeek_sin': np.sin(2 * np.pi * 2 / 7),
    'DayOfWeek_cos': np.cos(2 * np.pi * 2 / 7),
    'Hour_Pattern': get_hour_pattern(14),
    'DayOfWeek_Pattern': 1,
    'Parking_Lot_Section_encoded': spot_20['Parking_Lot_Section_encoded'],
    'Vehicle_Type_encoded': spot_20['Vehicle_Type_encoded'],
    'Proximity_To_Exit': spot_20['Proximity_To_Exit'],
    'Reserved_Status': 0,
    'Weather_Temperature': 20.0,  # Example
    'Weather_Precipitation': 0,
    'Nearby_Traffic_Level_encoded': spot_20['Nearby_Traffic_Level_encoded'],
    'Sensor_Reading_Proximity': spot_20['Sensor_Reading_Proximity'],
    'Sensor_Reading_Pressure': spot_20['Sensor_Reading_Pressure'],
    'Sensor_Reading_Ultrasonic': spot_20['Sensor_Reading_Ultrasonic'],
    'Vehicle_Type_Weight': spot_20['Vehicle_Type_Weight'],
    'Vehicle_Type_Height': spot_20['Vehicle_Type_Height'],
    'User_Parking_History': 5.0
}

test_df = pd.DataFrame([test_input])[available_features]
test_scaled = scaler.transform(test_df)
prediction = best_model.predict(test_scaled)[0]
probability = best_model.predict_proba(test_scaled)[0]

print(f"\n  Prediction: {'OCCUPIED' if prediction == 1 else 'VACANT'}")
print(f"  Confidence: {probability[prediction]*100:.1f}%")
print(f"  Probability Vacant: {probability[0]*100:.1f}%")
print(f"  Probability Occupied: {probability[1]*100:.1f}%")

if probability[0] > 0.7:
    print(f"\n  [RECOMMENDATION] HIGHLY AVAILABLE - Good choice!")
elif probability[0] > 0.5:
    print(f"\n  [RECOMMENDATION] Likely available - Consider booking")
else:
    print(f"\n  [RECOMMENDATION] Likely occupied - Try another spot")

print("\n" + "="*70)
print("MODEL TRAINING COMPLETE!")
print("="*70)
print(f"\nModel can now be used for:")
print("  - Weather-aware predictions")
print("  - Traffic-based recommendations")
print("  - Time-pattern analysis")
print("  - Smart spot suggestions")
print("\nReady for integration into the app!")
print("="*70)

