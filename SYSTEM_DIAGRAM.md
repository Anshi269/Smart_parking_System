# 🏗️ Smart Parking System Architecture - v1.2.0

## 📊 Complete System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SMART PARKING SYSTEM v1.2.0                      │
└─────────────────────────────────────────────────────────────────────┘

┌───────────────────┐
│   USER INPUTS     │
│   (Sidebar)       │
│                   │
│ ⏰ Hour: 14       │───────┐
│ 📅 Day: Monday    │       │
│ 🚗 Vehicle: Sedan │       │
│ 🔌 EV: No         │       │
│ 🅿️ Spot: (auto)  │       │
└───────────────────┘       │
                            │
                            ↓
┌────────────────────────────────────────────────────────────┐
│                    BOOKING SYSTEM                           │
│                                                             │
│  Generate Dummy Bookings (24 hours × all spots)            │
│  ┌──────────────────────────────────────────────┐         │
│  │ Hour 0:  25% occupancy (Night)               │         │
│  │ Hour 9:  75% occupancy (Morning Peak)        │         │
│  │ Hour 14: 60% occupancy (Midday)              │         │
│  │ Hour 18: 75% occupancy (Evening Peak)        │         │
│  │ Hour 23: 50% occupancy (Late Evening)        │         │
│  └──────────────────────────────────────────────┘         │
│                                                             │
│  Booking Data Structure:                                   │
│  (spot_id, section, hour) → {is_booked, booked_by}        │
│                                                             │
└────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌────────────────────────────────────────────────────────────┐
│                    NAVIGATION FLOW                          │
└────────────────────────────────────────────────────────────┘

Step 1: MAP VIEW
┌─────────────────────────────────────┐
│  🗺️ Satellite Map                  │
│  ┌───────────────────────────────┐ │
│  │ 📍 Downtown Parking Complex   │ │
│  │ Location: City Center         │ │
│  │ Zones: A, B, C, D             │ │
│  │ Capacity: 200 spots           │ │
│  │ [Select]                      │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
                  │
                  ↓
Step 2: SECTION SELECTOR (WITH OCCUPANCY)
┌─────────────────────────────────────────────────────────────┐
│  📊 Showing occupancy for 2:00 PM                           │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ 🅿️ Zone A   │  │ 🅿️ Zone B   │  │ 🅿️ Zone C   │  ... │
│  │ 75% Occupied │  │ 62% Occupied │  │ 45% Occupied │     │
│  │ 5 available  │  │ 8 available  │  │ 14 available │     │
│  │ High 🔴      │  │ Medium 🟠    │  │ Low 🟢       │     │
│  │ [Select]     │  │ [Select]     │  │ [Select]     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                  │
                  ↓ (User clicks Zone A - 75% busy)
                  │
┌─────────────────────────────────────────────────────────────┐
│  ⚠️ SMART SUGGESTION                                        │
│  Zone A is 75% occupied.                                    │
│  Consider Zone C instead - only 45% occupied!               │
│  [Switch to Zone C]  [Stay in Zone A]                      │
└─────────────────────────────────────────────────────────────┘
                  │
                  ↓ (User stays in Zone A)
                  │
Step 3: SLOT SELECTOR (TIME-BASED AVAILABILITY)
┌─────────────────────────────────────────────────────────────┐
│  🚗 Select Parking Slot - Zone A                            │
│  🟢 Available  🔴 Occupied  🔵 Selected                      │
│                                                              │
│  Slot Grid (10 per row):                                    │
│  ┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐      │
│  │ 1  │ 2  │ 3  │ 4  │ 5  │ 6  │ 7  │ 8  │ 9  │ 10 │      │
│  │🟢  │🔴  │🟢  │🔴  │🟢  │🔴  │🔴  │🟢  │🔴  │🟢  │      │
│  └────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘      │
│  ┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐      │
│  │ 11 │ 12 │ 13 │ 14 │ 15 │ 16 │ 17 │ 18 │ 19 │ 20 │      │
│  │🟢  │🔴  │🟢  │🔴  │🟢  │🔴  │🟢  │🔴  │🔴  │🟢  │      │
│  └────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘      │
│                                                              │
│  Red = Booked at 2:00 PM by other users                    │
│  Green = Available to book at 2:00 PM                      │
└─────────────────────────────────────────────────────────────┘
                  │
                  ↓ (User clicks Slot 5)
                  │
┌─────────────────────────────────────────────────────────────┐
│  ✅ Selected Slot Information                               │
│  ┌─────────────┬─────────────┬─────────────┐              │
│  │ Slot ID: 5  │ Section: A  │ Size: Std   │              │
│  └─────────────┴─────────────┴─────────────┘              │
│                                                              │
│  Details:                                                    │
│  • Proximity to Exit: 8.5m                                  │
│  • Spot Type: Standard                                      │
│  • EV Charging: No                                          │
│                                                              │
│  [📅 Proceed to Booking] (Coming Soon)                     │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow Architecture

```
┌────────────────────┐
│   CSV Dataset      │
│   (1000 records)   │
│                    │
│ • Parking Sections │
│ • Spot IDs         │
│ • Occupancy Status │
│ • Features         │
└────────────────────┘
         │
         ↓
┌────────────────────┐
│  ParkingDataLoader │
│                    │
│ • get_all_sections │
│ • get_spots()      │
│ • get_spot_info()  │
└────────────────────┘
         │
         ├──────────────────────────────┐
         ↓                              ↓
┌────────────────────┐         ┌────────────────────┐
│  BookingSystem     │         │   UI Components    │
│                    │         │                    │
│ • Generate dummy   │         │ • map_view.py      │
│   bookings         │         │ • section_sel.py   │
│ • Calculate occ%   │         │ • slot_selector.py │
│ • Find least occ   │         │ • user_inputs.py   │
│ • Check if booked  │         │                    │
└────────────────────┘         └────────────────────┘
         │                              │
         └───────────┬──────────────────┘
                     ↓
         ┌────────────────────┐
         │   Session State    │
         │                    │
         │ • selected_area    │
         │ • selected_section │
         │ • selected_slot    │
         │ • user_inputs      │
         │ • suggestions      │
         └────────────────────┘
                     ↓
         ┌────────────────────┐
         │   Streamlit UI     │
         │   (app.py)         │
         └────────────────────┘
```

## 🎯 Occupancy Calculation Flow

```
User Input: Hour = 14 (2:00 PM), Section = "Zone A"
                     ↓
┌──────────────────────────────────────────────────────────┐
│  BookingSystem.get_section_occupancy("Zone A", 14)      │
└──────────────────────────────────────────────────────────┘
                     ↓
         ┌───────────────────────┐
         │ Get all spots in      │
         │ Zone A from CSV       │
         │ Result: [1,2,3...20]  │
         └───────────────────────┘
                     ↓
         ┌───────────────────────┐
         │ Check each spot's     │
         │ booking status at     │
         │ hour 14:              │
         │                       │
         │ Spot 1:  ✅ Booked   │
         │ Spot 2:  ❌ Free     │
         │ Spot 3:  ✅ Booked   │
         │ ...                   │
         │ Total: 15/20 booked   │
         └───────────────────────┘
                     ↓
         ┌───────────────────────┐
         │ Calculate:            │
         │ occupancy = 15/20     │
         │ percentage = 75%      │
         │ available = 5         │
         └───────────────────────┘
                     ↓
         ┌───────────────────────┐
         │ Determine color:      │
         │ 75% > 75% → RED 🔴    │
         └───────────────────────┘
                     ↓
         ┌───────────────────────┐
         │ Display on UI:        │
         │ Zone A: 75% Occupied  │
         │ 5 spots available     │
         │ Occupancy: High       │
         └───────────────────────┘
```

## 🧠 Smart Suggestion Logic

```
User selects Zone A (75% occupied)
                ↓
┌────────────────────────────────────────┐
│  Is occupancy > 60%?                   │
│  75% > 60% → YES                       │
└────────────────────────────────────────┘
                ↓
┌────────────────────────────────────────┐
│  Find least occupied zone at hour 14:  │
│  • Zone A: 75%                         │
│  • Zone B: 68%                         │
│  • Zone C: 45% ← LEAST                 │
│  • Zone D: 52%                         │
└────────────────────────────────────────┘
                ↓
┌────────────────────────────────────────┐
│  Is difference > 15%?                  │
│  75% - 45% = 30% > 15% → YES           │
└────────────────────────────────────────┘
                ↓
┌────────────────────────────────────────┐
│  Show suggestion:                       │
│  "Zone A is 75% occupied.              │
│   Consider Zone C - only 45%!"         │
│                                         │
│  Store in session_state:               │
│  {                                      │
│    'current_zone': 'Zone A',           │
│    'current_occupancy': 75,            │
│    'suggested_zone': 'Zone C',         │
│    'suggested_occupancy': 45           │
│  }                                      │
└────────────────────────────────────────┘
                ↓
┌────────────────────────────────────────┐
│  Display in Slot Selector:             │
│  ⚠️ Warning message with buttons       │
│  [Switch to Zone C] [Stay Here]        │
└────────────────────────────────────────┘
```

## 📊 Time-Based Occupancy Patterns

```
Occupancy Over 24 Hours:

100% ┤
 90% ┤
 80% ┤      ██         ██
 70% ┤      ██   ██    ██
 60% ┤      ██   ██    ██
 50% ┤      ██   ██    ██    ██
 40% ┤      ██   ██    ██    ██
 30% ┤   ██ ██   ██    ██    ██
 20% ┤   ██ ██   ██    ██    ██ ██
 10% ┤   ██ ██   ██    ██    ██ ██
  0% ┼───┴┴─┴┴───┴┴────┴┴────┴┴─┴┴────────
     0  4  8  12  16   20   24
     │  │  │   │   │    │    │
     │  │  │   │   │    │    └─ Night (25%)
     │  │  │   │   │    └─ Evening (50%)
     │  │  │   │   └─ Peak PM (75%)
     │  │  │   └─ Midday (60%)
     │  │  └─ Peak AM (75%)
     │  └─ Early (25%)
     └─ Night (25%)
```

## 🔌 API Functions Available

```python
# BookingSystem API

# 1. Check if specific spot is booked
is_booked = booking_system.is_spot_booked(
    spot_id=12,
    section="Zone A",
    hour=14
)
→ True/False

# 2. Get section occupancy
occupancy = booking_system.get_section_occupancy(
    section="Zone A",
    hour=14
)
→ {
    'total_spots': 20,
    'booked_spots': 15,
    'available_spots': 5,
    'occupancy_percentage': 75.0
}

# 3. Get all sections occupancy
all_occ = booking_system.get_all_sections_occupancy(hour=14)
→ {
    "Zone A": {...},
    "Zone B": {...},
    "Zone C": {...},
    "Zone D": {...}
}

# 4. Find least occupied section
least = booking_system.get_least_occupied_section(hour=14)
→ ("Zone C", 45.0)

# 5. Get available spots list
available = booking_system.get_available_spots_in_section(
    section="Zone A",
    hour=14
)
→ [1, 3, 5, 8, 15, 20]

# 6. Detect occupancy trend
trend = booking_system.get_occupancy_trend(
    section="Zone A",
    current_hour=14
)
→ "rising" | "falling" | "stable"
```

## 🗂️ File Structure

```
parking/
│
├── 📄 app.py                    # Main application
│   └─ Integrates BookingSystem
│   └─ Passes selected_hour to components
│
├── 📂 src/
│   │
│   ├── 📂 data/
│   │   ├── data_loader.py       # CSV data handling
│   │   └── booking_system.py    # ✨ NEW: Time-based bookings
│   │
│   ├── 📂 components/
│   │   ├── map_view.py          # Satellite map
│   │   ├── section_selector.py  # ✨ UPDATED: Shows occupancy %
│   │   ├── slot_selector.py     # ✨ UPDATED: Time-based slots
│   │   └── user_inputs.py       # User input form
│   │
│   └── 📂 utils/
│       └── helpers.py            # Session state helpers
│
├── 📂 resources/
│   └── IIoT_Smart_Parking_Management (2).csv
│
└── 📚 Documentation/
    ├── README.md
    ├── QUICKSTART.md
    ├── ML_INTEGRATION_GUIDE.md
    ├── TIME_BASED_OCCUPANCY_GUIDE.md  # ✨ NEW
    ├── WHATS_NEW_v1.2.0.md            # ✨ NEW
    └── SYSTEM_DIAGRAM.md              # ✨ NEW (This file)
```

## 🎯 Key Connections

### 1. User Input → Occupancy Display
```
Sidebar: User selects Hour = 14
    ↓
app.py: selected_hour = user_inputs.get('hour')
    ↓
section_selector.py: Shows occupancy for hour 14
```

### 2. Zone Selection → Smart Suggestion
```
User clicks "Zone A"
    ↓
Check: occupancy > 60%?
    ↓
Yes: Find least occupied zone
    ↓
Store suggestion in session_state
    ↓
slot_selector.py: Display warning with switch button
```

### 3. Slot Display → Booking Status
```
User in slot selector, hour = 14
    ↓
For each spot: Check is_spot_booked(spot_id, section, 14)
    ↓
True: Display RED (occupied)
False: Display GREEN (available)
```

## 📈 Scalability

### Current (v1.2.0):
```python
# Dummy data in memory
bookings = generate_dummy_bookings()  # All hours × all spots
```

### Future (Database):
```python
# Query from database
def get_bookings_for_hour(hour):
    return db.query("""
        SELECT spot_id, section, hour
        FROM bookings
        WHERE booking_hour = ? AND booking_date = ?
    """, hour, today)
```

### Migration Path:
1. ✅ Current: In-memory dummy data
2. → SQLite: Local database file
3. → PostgreSQL: Production database
4. → Redis: Caching layer
5. → API: Microservice architecture

---

**Version:** 1.2.0
**Architecture:** Clean, Modular, Scalable
**Ready for:** ML Integration & Real Database

