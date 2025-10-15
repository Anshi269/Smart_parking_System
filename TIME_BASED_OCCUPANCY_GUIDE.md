# ⏰ Time-Based Occupancy System - Documentation

## 🎯 Overview

The parking app now features **time-based occupancy** that shows real-time booking status based on the hour selected by the user. This simulates a multi-user system where spots are pre-booked by other users.

## 🏗️ Architecture

### Booking System (`src/data/booking_system.py`)

A new module that manages parking spot bookings:

```
BookingSystem
├── Generate dummy bookings (24 hours × all spots)
├── Check if spot is booked at specific hour
├── Calculate section occupancy percentage
├── Find least occupied section
├── Detect occupancy trends (rising/falling)
└── Get available spots for time period
```

### Data Flow

```
User selects hour in sidebar (e.g., 14 = 2:00 PM)
         ↓
BookingSystem loads dummy bookings for all hours
         ↓
Zone Selection Page: Shows occupancy % for each zone at hour 14
         ↓
User selects Zone A (75% occupied)
         ↓
System suggests Zone B (45% occupied) - less crowded
         ↓
Slot Selection: Shows red/green based on hour 14 bookings
         ↓
User can only book available (green) slots
```

## 📊 Features Implemented

### 1. Time-Based Booking Generation

**File**: `src/data/booking_system.py`

```python
def _generate_dummy_bookings(self):
    """
    Generates bookings for:
    - All parking spots (50+)
    - All zones (A, B, C, D)
    - All hours (0-23)
    
    Uses realistic patterns:
    - Peak hours (8-10 AM, 5-7 PM): 75% occupancy
    - Midday (11 AM - 4 PM): 60% occupancy
    - Evening (8-10 PM): 50% occupancy
    - Night (11 PM - 6 AM): 25% occupancy
    """
```

### 2. Zone Occupancy Display

**File**: `src/components/section_selector.py`

**What it does:**
- Shows occupancy percentage for each zone
- Color-coded borders:
  - 🟢 Green (< 50%): Low occupancy
  - 🟠 Orange (50-75%): Medium occupancy
  - 🔴 Red (> 75%): High occupancy
- Displays available spots count
- Shows time context ("Showing occupancy for 2:00 PM")

**Example Display:**
```
┌─────────────────────┐
│  🅿️ Zone A          │
│  75% Occupied       │  ← Red border
│  6 spots available  │
│  Occupancy: High    │
└─────────────────────┘
```

### 3. Smart Zone Suggestions

**When triggered:**
- User selects a zone with > 60% occupancy
- There's another zone with at least 15% less occupancy

**What happens:**
```
⚠️ Zone A is 75% occupied.
Consider Zone B instead - only 45% occupied!

[Switch to Zone B]  [Stay Here]
```

User can click "Switch to Zone B" to automatically navigate to the less crowded zone.

### 4. Time-Based Slot Availability

**File**: `src/components/slot_selector.py`

**What changed:**
- Slots are now checked against booking system
- Red (occupied) = Spot is booked at selected hour
- Green (available) = Spot is free at selected hour
- User can only select green slots

**Example:**
```
User selects Hour: 14 (2:00 PM)
Spot #12 booking status:
  - Hour 13: Available
  - Hour 14: Booked      ← Shows as RED
  - Hour 15: Available
```

## 🔧 Technical Implementation

### Booking Data Structure

```python
bookings = {
    (spot_id, section, hour): {
        'is_booked': bool,           # True if booked
        'booked_by': str,            # User ID (dummy)
        'booking_time': datetime     # When booking was made
    }
}

# Example:
(12, "Zone A", 14): {
    'is_booked': True,
    'booked_by': "User_1234",
    'booking_time': datetime(2024, 10, 13, 10, 30)
}
```

### Occupancy Calculation

```python
def get_section_occupancy(self, section, hour):
    """
    For Zone A at 2:00 PM:
    - Total spots: 20
    - Booked spots: 15 (count from booking system)
    - Available: 5
    - Occupancy %: 75%
    """
    return {
        'total_spots': 20,
        'booked_spots': 15,
        'available_spots': 5,
        'occupancy_percentage': 75.0
    }
```

### Peak Hour Patterns

Simulates realistic parking behavior:

| Time Period | Hours | Occupancy | Reason |
|------------|-------|-----------|---------|
| Morning Rush | 8-10 AM | 75% | People arriving at work |
| Midday | 11 AM-4 PM | 60% | Steady traffic |
| Evening Rush | 5-7 PM | 75% | Peak demand |
| Evening | 8-10 PM | 50% | Some people leaving |
| Night | 11 PM-6 AM | 25% | Low demand |

## 🎨 User Experience Flow

### Scenario 1: User Selects Peak Hour

```
1. User sets hour to 18 (6:00 PM) in sidebar
2. Navigates to Zone Selection
3. Sees:
   Zone A: 🔴 82% occupied (2 spots)
   Zone B: 🟠 68% occupied (8 spots)
   Zone C: 🟢 45% occupied (14 spots)
   Zone D: 🟢 38% occupied (16 spots)
4. User clicks "Zone A" (busy)
5. System shows warning: "Consider Zone D - only 38% occupied!"
6. User can switch or stay
```

### Scenario 2: User Selects Off-Peak Hour

```
1. User sets hour to 2 (2:00 AM) in sidebar
2. Navigates to Zone Selection
3. Sees:
   Zone A: 🟢 20% occupied (18 spots)
   Zone B: 🟢 28% occupied (16 spots)
   Zone C: 🟢 22% occupied (17 spots)
   Zone D: 🟢 25% occupied (17 spots)
4. User clicks any zone - no warnings (all zones available)
5. Proceeds to slot selection - most slots are green
```

## 📈 Occupancy Statistics API

### Get Section Occupancy
```python
booking_system.get_section_occupancy("Zone A", 14)
# Returns: {'total_spots': 20, 'booked_spots': 15, ...}
```

### Get All Sections
```python
booking_system.get_all_sections_occupancy(14)
# Returns: {
#   "Zone A": {...},
#   "Zone B": {...},
#   ...
# }
```

### Find Least Occupied
```python
booking_system.get_least_occupied_section(14)
# Returns: ("Zone D", 38.5)
```

### Check Specific Spot
```python
booking_system.is_spot_booked(12, "Zone A", 14)
# Returns: True or False
```

## 🔄 Database Migration (Future)

Currently using **dummy generated data**. When ready for database:

### What to Replace:

**Current (Dummy)**:
```python
def _generate_dummy_bookings(self):
    # Generates random bookings
    bookings = {}
    ...
    return bookings
```

**Future (Database)**:
```python
def _load_bookings_from_db(self):
    # Query real bookings from database
    query = """
        SELECT spot_id, section, hour, user_id, booking_time
        FROM bookings
        WHERE booking_date = ?
    """
    return db.execute(query, date)
```

### Database Schema Suggestion:

```sql
CREATE TABLE bookings (
    id INT PRIMARY KEY,
    spot_id INT,
    section VARCHAR(10),
    user_id INT,
    booking_date DATE,
    booking_hour INT,  -- 0-23
    duration INT,      -- hours
    created_at TIMESTAMP,
    FOREIGN KEY (spot_id, section) REFERENCES parking_spots(id, section),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_bookings_time ON bookings(booking_date, booking_hour);
```

## 🎯 Benefits of This System

### For Users:
- ✅ See real-time availability before navigating
- ✅ Get smart suggestions to save time
- ✅ Avoid going to full zones
- ✅ Know exactly which spots are available

### For System:
- ✅ Distributes users across zones
- ✅ Reduces congestion in popular zones
- ✅ Better user experience
- ✅ Ready for ML predictions

### For Future ML:
- ✅ Historical booking patterns available
- ✅ Peak hour detection
- ✅ Trend analysis (rising/falling occupancy)
- ✅ Can predict future availability

## 📝 Code Examples

### Check Occupancy at Different Times

```python
# Morning
morning_occ = booking_system.get_section_occupancy("Zone A", 9)
print(f"Morning: {morning_occ['occupancy_percentage']}%")

# Afternoon
afternoon_occ = booking_system.get_section_occupancy("Zone A", 14)
print(f"Afternoon: {afternoon_occ['occupancy_percentage']}%")

# Night
night_occ = booking_system.get_section_occupancy("Zone A", 2)
print(f"Night: {night_occ['occupancy_percentage']}%")
```

### Find Best Time to Park

```python
occupancy_by_hour = {}
for hour in range(24):
    occ = booking_system.get_section_occupancy("Zone A", hour)
    occupancy_by_hour[hour] = occ['occupancy_percentage']

best_hour = min(occupancy_by_hour, key=occupancy_by_hour.get)
print(f"Best time: {best_hour}:00 ({occupancy_by_hour[best_hour]}%)")
```

## 🚀 Future Enhancements

Based on your requirements, next additions could be:

### Core Predictions:
- [ ] "Spot A12 will likely be free in 25 mins"
- [ ] "Rain likely: covered lots expected to be full earlier"
- [ ] "High demand expected between 5–7 PM; book early"

### Personalized Insights:
- [ ] "Recommended: Slot D2 (close to exit, usually free at 9 AM)"
- [ ] "Least crowded between 2–3 PM"
- [ ] "Based on your history, you prefer spots near exit"

### Trend Detection:
- [x] Rising/falling occupancy (implemented in `get_occupancy_trend()`)
- [ ] Display trends in UI
- [ ] Predict next hour's occupancy

---

**Status**: ✅ Time-Based Occupancy System Complete!
**Next**: ML Predictions & Personalized Recommendations

