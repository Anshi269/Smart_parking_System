# 🚀 Quick Start Guide

## First Time Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify Data File
Make sure the CSV file is in the correct location:
```
parking/
└── resources/
    └── IIoT_Smart_Parking_Management (2).csv
```

### 3. Run the Application
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 🎯 How to Use the UI

### Step 1: Select Parking Area (Map View)
- View the satellite-style map
- Click on "Downtown Parking Complex" 
- Click "Select Downtown Parking Complex" button

### Step 2: Choose Parking Section
- You'll see 4 zones: Zone A, B, C, D
- Click on any zone to view available slots
- Use "Back to Map" to return

### Step 3: Select Your Slot
- View the 2D grid of parking slots
- **Green slots** = Available
- **Red slots** = Occupied
- Click on any available slot to select it
- View detailed slot information
- Click "Proceed to Booking" (feature coming soon)

### Step 4: Fill User Inputs (Sidebar)
The sidebar now collects important booking details:
1. **⏰ Arrival Time**: Select hour (0-23, defaults to current hour)
2. **📅 Arrival Day**: Choose day of week (defaults to today)
3. **🚗 Vehicle Type**: Car, Sedan, SUV, Motorcycle, Electric Vehicle, Truck
4. **🔌 EV Charging**: Check if you need EV charging
5. **🅿️ Parking Spot ID**: Auto-filled from your slot selection

## 🎨 UI Navigation Flow

```
Map View
    ↓ (Select Area)
Section Selector
    ↓ (Select Zone)
Slot Selector
    ↓ (Select Slot)
User Inputs (Sidebar - Always Visible)
    ↓
ML Prediction Ready! (Coming Soon)
```

## 📱 Current Features

✅ **Working Now:**
- Interactive map view
- Section selection (Zones A-D)
- Slot selection grid
- Real-time availability display
- Slot details (size, EV charging, distance to exit)
- **User input collection (5 fields)**
  - Hour selection with AM/PM display
  - Day of week selection
  - Vehicle type dropdown
  - EV charging checkbox
  - Auto-populated parking spot ID
- Input summary display
- ML prediction inputs ready notification

🔨 **Coming Next:**
- ML model integration for predictions
- AI recommendations based on inputs
- Booking confirmation
- User authentication
- Payment integration

## 🔄 How User Inputs Work

1. **Always Visible**: User inputs are always shown in the sidebar
2. **Smart Defaults**: Hour and day default to current time
3. **Auto-Update**: Parking spot ID updates when you select a slot
4. **Summary Display**: See all your inputs at a glance
5. **ML Ready**: When all inputs are filled (including slot selection), you'll see a "🔮 ML Prediction Inputs Ready" expandable section

## 📊 Understanding the Data

### Occupied Slots
- The app reads the CSV file which has **time-series data**
- Each spot has multiple records over time
- We take the **most recent record** (last entry) to determine current status
- Green = Vacant, Red = Occupied

### User Input Fields (for ML Prediction)
All 5 fields are collected and will be used for:
- Predicting spot availability at your desired time
- Recommending best spots based on your preferences
- Estimating parking duration
- Dynamic pricing (future feature)

## 🐛 Troubleshooting

### CSV File Not Found
- Ensure the file is in `resources/` folder
- Check the exact filename: `IIoT_Smart_Parking_Management (2).csv`

### App Not Loading
- Check if Streamlit is installed: `streamlit --version`
- Reinstall dependencies: `pip install -r requirements.txt`

### Slots Not Showing
- Verify the CSV file has data
- Check the console for error messages

### User Inputs Not Saving
- Make sure you've selected a parking slot first
- Check the sidebar summary section
- Use the "🔄 Reset Selection" button if needed

## 💡 Tips

1. **Use the sidebar** to see your current selection and fill booking details
2. **Back buttons** are available at each step
3. **Hover over slots** to see interactive effects
4. **Fill user inputs** at any time - they persist during navigation
5. **Check ML Prediction Inputs** expandable to see what data is ready
6. **Reset** if you want to start over (clears all selections and inputs)

## 📝 What Happens Next

Once you're comfortable with the UI and inputs, the next phase will be:
1. **ML Model Integration**: Use collected inputs with your `model.py`
2. **Predictions**: 
   - "Spot A12 will likely be free in 25 mins"
   - "Lot C occupancy expected: 82% at 6 PM"
3. **Recommendations**:
   - "Recommended for you: Slot D2 (close to exit, usually free at 9 AM)"
   - "Least crowded between 2–3 PM"
4. **Booking System**: Save prebookings with user details
5. **Multi-user Support**: Handle concurrent bookings

## 🎯 Current Version: 1.1.0

**New in this version:**
- ⏰ Hour selection (0-23 with AM/PM display)
- 📅 Day of week selection
- 🚗 Vehicle type dropdown
- 🔌 EV charging preference
- 🅿️ Auto-populated parking spot ID
- 📋 Input summary with metrics
- 🔮 ML prediction readiness indicator
