# =======================
# Smart Parking — Core Training Code
# =======================
import pandas as pd
import numpy as np
import kagglehub
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, matthews_corrcoef, roc_auc_score

# -------------------
# Load dataset
# -------------------
path = kagglehub.dataset_download("datasetengineer/smart-parking-management-dataset")
df = pd.read_csv(f"{path}/IIoT_Smart_Parking_Management.csv")

# -------------------
# Encode categorical and prepare target
# -------------------
for col in ['Parking_Lot_Section', 'Vehicle_Type', 'Nearby_Traffic_Level', 'User_Type']:
    if col in df.columns:
        df[col] = LabelEncoder().fit_transform(df[col].astype(str))

df = df.fillna(df.mean(numeric_only=True))

# Choose features (customize per your use)
X = df.select_dtypes(include=[np.number]).drop(columns=['Occupancy_Status_encoded'], errors='ignore')
y = LabelEncoder().fit_transform(df['Occupancy_Status'])

# -------------------
# Split + Scale
# -------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# -------------------
# Train models
# -------------------
class_weights = {0: len(y)/(2*sum(y==0)), 1: len(y)/(2*sum(y==1))}

models = {
    'Logistic Regression': LogisticRegression(max_iter=1000, class_weight='balanced', solver='saga'),
    'Random Forest': RandomForestClassifier(n_estimators=300, max_depth=15, random_state=42, class_weight='balanced', n_jobs=-1),
    'XGBoost': XGBClassifier(n_estimators=300, max_depth=7, learning_rate=0.05,
                             subsample=0.8, colsample_bytree=0.8,
                             scale_pos_weight=class_weights[1]/class_weights[0],
                             random_state=42, verbosity=0),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=300, learning_rate=0.05, max_depth=7,
                                                    min_samples_split=10, min_samples_leaf=5, random_state=42)
}

results = {}
for name, model in models.items():
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)[:, 1] if hasattr(model, 'predict_proba') else np.zeros(len(y_test))
    
    results[name] = {
        'Accuracy': accuracy_score(y_test, y_pred),
        'F1': f1_score(y_test, y_pred, average='weighted'),
        'Precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
        'Recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
        'MCC': matthews_corrcoef(y_test, y_pred),
        'AUC': roc_auc_score(y_test, y_proba),
        'Model': model
    }

# -------------------
# Evaluate & select best
# -------------------
print("\nMODEL PERFORMANCE:")
for name, r in results.items():
    print(f"{name:20s} | Acc={r['Accuracy']:.3f} | F1={r['F1']:.3f} | MCC={r['MCC']:.3f} | AUC={r['AUC']:.3f}")

best_model_name = max(results, key=lambda k: results[k]['MCC'])
best_model = results[best_model_name]['Model']
print(f"\n🏆 Best Model: {best_model_name} (MCC={results[best_model_name]['MCC']:.3f})")

# -------------------
# Cross Validation
# -------------------
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_f1 = cross_val_score(best_model, X_train_scaled, y_train, cv=skf, scoring='f1_weighted')
cv_auc = cross_val_score(best_model, X_train_scaled, y_train, cv=skf, scoring='roc_auc')
print(f"\nCross-Validation F1={cv_f1.mean():.3f} (+/-{cv_f1.std():.3f}), AUC={cv_auc.mean():.3f}")
