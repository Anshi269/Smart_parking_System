# 🅿️ Smart Parking Prebooking System

A smart parking management system with AI-powered recommendations and real-time availability tracking.

## 📁 Project Structure

```
parking/
├── app.py                          # Main Streamlit application
├── model.py                        # ML model training script
├── requirements.txt                # Python dependencies
├── resources/                      # Data files
│   └── IIoT_Smart_Parking_Management (2).csv
└── src/                           # Source code
    ├── components/                # UI components
    │   ├── map_view.py           # Satellite map view
    │   ├── section_selector.py   # Section selection UI
    │   └── slot_selector.py      # Slot selection grid
    ├── data/                      # Data handling
    │   └── data_loader.py        # CSV data loader
    └── utils/                     # Utilities
        └── helpers.py            # Helper functions
```

## 🚀 Getting Started

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser at `http://localhost:8501`

## 📋 Current Features (UI + Time-Based Occupancy Phase)

### ✅ Implemented
- **Map View**: Satellite-style map showing parking areas
- **Section Selector**: Visual selection of parking zones (A, B, C, D)
  - 📊 **Real-time occupancy % for each zone** based on selected time
  - Color-coded indicators (Green/Orange/Red)
  - Shows available spots count
- **Slot Selector**: 2D grid layout for slot selection (bus booking style)
  - Time-based availability (slots booked by other users)
  - Smart suggestions when selecting busy zones
- **User Input Collection**: 5 fields for ML predictions
  - ⏰ Hour (0-23, with AM/PM display, defaults to current hour)
  - 📅 Day of Week (Monday-Sunday, defaults to today)
  - 🚗 Vehicle Type (Car, Sedan, SUV, Motorcycle, Electric Vehicle, Truck)
  - 🔌 Electric Vehicle (Yes/No checkbox for EV charging)
  - 🅿️ Parking Spot ID (auto-populated from slot selection)
- **Booking System**: Dummy booking data for each hour (will be replaced with DB)
  - Simulates real user bookings
  - Peak hour patterns (8-10 AM, 5-7 PM: 75% occupancy)
  - Off-peak patterns (Night: 25% occupancy)
- **Smart Recommendations**:
  - Suggests less crowded zones when user picks busy zones
  - "Switch to Zone B" button if current zone >60% occupied
- **Data Integration**: Real-time data from CSV dataset + booking system
- **Navigation**: Smooth transitions between views
- **Session State Management**: Maintains all user selections and inputs
- **Input Summary**: Visual display of all collected inputs

### 🔨 Coming Soon
- ML model integration for predictions
- AI-powered slot recommendations (using collected inputs)
- Time-based availability predictions
- Multi-user booking system
- Payment integration
- User authentication

## 📊 Data Structure

The system uses the IIoT Smart Parking Management dataset with the following key fields:
- **Parking_Lot_Section**: Zone A, B, C, D
- **Parking_Spot_ID**: Unique spot identifiers
- **Occupancy_Status**: Occupied/Vacant
- **Spot_Size**: Standard/Compact/Oversized
- **Electric_Vehicle**: EV charging availability
- **Proximity_To_Exit**: Distance to exit

## 🎨 UI Components

### Map View
- Shows parking area locations
- Displays total capacity
- Clickable area selection

### Section Selector
- Grid layout of parking zones
- Visual section cards
- Quick zone information

### Slot Selector
- 2D grid (10 slots per row)
- Color-coded availability:
  - 🟢 Green: Available
  - 🔴 Red: Occupied
  - 🔵 Blue: Selected
- Detailed spot information

## 📝 Development Notes

- Built with Streamlit for rapid UI development
- Clean codebase with modular components
- Organized folder structure for scalability
- Ready for ML model integration
- Designed for thin vertical slice development

## 🔄 Version History

**v1.2.1 - Smart Spot Recommendations** ✨ LATEST
- **Spot-level recommendations** when you select a spot in busy zone
- Recommends best alternative spot (closest to exit) in less crowded zone
- One-click switch to recommended spot
- Shows occupancy comparison and spot details
- Intelligent algorithm: only suggests if >15% improvement
- Consistent bookings (fixed seed) - no random changes

**v1.2.0 - Time-Based Occupancy System**
- Booking system with dummy data (24 hours × all spots)
- Real-time occupancy percentage on zone cards
- Color-coded zone indicators (Green/Orange/Red)
- Time-based slot availability
- Smart zone suggestions when >60% occupied
- "Switch to less crowded zone" feature
- Peak hour patterns (realistic occupancy simulation)
- All based on user's selected hour

**v1.1.0 - UI + User Inputs Phase**
- Added user input collection (5 fields)
- Hour selection with AM/PM display
- Day of week selection with smart defaults
- Vehicle type dropdown
- EV charging preference checkbox
- Auto-populated parking spot ID
- Input summary display with metrics
- ML prediction inputs readiness indicator
- Session state management for all inputs

**v1.0.0 - UI Phase**
- Initial UI implementation
- Map, section, and slot selection
- Data loader integration

