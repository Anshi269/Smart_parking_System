# 🧪 Testing the Zone Notification System

## How to Test the Notification

### ✅ Step-by-Step Test

**Refresh your browser first!** Then follow these exact steps:

#### 1. **Set the Hour to Peak Time**
   - In sidebar, set **Hour to 18** (6:00 PM)
   - This ensures zones will be busy

#### 2. **Navigate to Zone Selection**
   - Click on "Downtown Parking Complex"
   - You should see occupancy % on each zone card
   - **Look for a RED zone** (>75% occupied)

#### 3. **Click the Busy Zone**
   - Click "Select Zone A" (or whichever is most occupied)
   
#### 4. **Check for Notification**
   - **At the TOP** of the slot page, you should see:
     - 🔍 Debug line showing occupancy
     - ⚠️ RED WARNING BOX if zone is >60% occupied
     - 💡 BLUE RECOMMENDATION BOX with alternative spot

---

## 🔍 What You Should See

### If Notification Appears:
```
🚗 Select Parking Slot - Zone A
🔍 Debug: This zone is 75% occupied at hour 18

⚠️ WARNING: Zone A is 75% occupied!
Finding a spot here might be difficult. Consider a less crowded alternative.

💡 Smart Recommendation:
Spot 12 in Zone D is a better choice:
- ✅ Only 45% occupied (30% less crowded)
- ✅ 14 spots available (vs 5 here)
- ✅ Distance to exit: 8.5m
- ✅ Easier to find and park

[🚀 Switch to Spot 12 in Zone D]  [Dismiss & Stay Here]
```

### If NO Notification:
```
🚗 Select Parking Slot - Zone A
🔍 Debug: This zone is 45% occupied at hour 18

✅ Zone A is only 45% occupied - Plenty of spaces!
```

---

## 🐛 Troubleshooting

### Issue 1: "I don't see the debug line"
**Cause:** Hour not set in sidebar or booking_system not loaded

**Fix:** 
1. Check sidebar - is an hour selected?
2. Refresh the page completely
3. Make sure you see "Loaded 1000 records" in terminal

### Issue 2: "Debug shows low occupancy (like 25%)"
**Cause:** Wrong hour selected (off-peak time)

**Fix:**
1. In sidebar, change hour to **9** (morning rush) or **18** (evening rush)
2. Go back and re-select the zone
3. Should now show higher occupancy

### Issue 3: "Debug shows 65% but no notification"
**Cause:** No other zone is 15%+ less occupied

**Conditions for notification:**
- ✅ Current zone > 60% occupied
- ✅ Another zone exists with 15%+ less occupancy
- ✅ Not dismissed previously

**To check:**
1. Go back to zone selection
2. Look at ALL zone occupancy %
3. Is there a zone with significantly lower %?

### Issue 4: "I see notification once, then it's gone"
**Cause:** You clicked "Dismiss & Stay Here"

**Fix:**
1. Click "Reset Selection" in sidebar
2. Or change the hour slightly (e.g., 18 → 17 → 18)
3. Navigate back to the zone

---

## 🎯 Guaranteed Test Case

Follow this EXACT sequence to see the notification:

```
1. Refresh browser (Ctrl+F5)
2. Sidebar: Set Hour = 18
3. Click parking area
4. Look at zone cards:
   - Find the zone with HIGHEST % (red border)
   - Note its % (e.g., Zone A: 75%)
5. Click that zone
6. 💥 You SHOULD see:
   - Debug line at top
   - Red warning box
   - Blue recommendation
   - Two buttons
```

If you don't see it after this, there might be an issue with the hour selection or zone occupancy generation.

---

## 📊 Check Occupancy Levels

To verify zones are actually busy, before selecting a zone:

**On Zone Selection Page:**
```
Zone A: 🔴 75% occupied  ← BUSY
Zone B: 🟠 62% occupied  ← BUSY
Zone C: 🟢 48% occupied  ← OK
Zone D: 🟢 35% occupied  ← OK
```

- **Red zones** (>75%): Should trigger notification
- **Orange zones** (50-75%): Should trigger notification if big difference exists
- **Green zones** (<50%): Should NOT trigger notification

---

## 🧪 Test Different Hours

| Hour | Expected Occupancy | Should Trigger? |
|------|-------------------|-----------------|
| 2 AM (2) | ~25% all zones | ❌ No (all zones empty) |
| 9 AM (9) | ~75% busy zones | ✅ Yes |
| 2 PM (14) | ~60% busy zones | ✅ Maybe |
| 6 PM (18) | ~75% busy zones | ✅ Yes |
| 11 PM (23) | ~50% busy zones | ⚠️ Maybe |

---

## 🔧 Quick Debug Commands

If you want to manually check what's happening:

**Check if booking system is loaded:**
- You should see "Loaded 1000 records" repeating in terminal

**Check current state:**
- Sidebar should show your selected hour
- Zone selection page should show % on cards
- Slot page should show debug line at top

---

## ✅ Success Criteria

The notification system is working if:

1. ✅ Debug line appears at top of slot selector
2. ✅ Shows correct occupancy %
3. ✅ Red warning appears when zone >60% AND better alternative exists
4. ✅ Blue recommendation shows specific spot and zone
5. ✅ Buttons work (Switch or Dismiss)
6. ✅ After dismissing, warning doesn't show again for same zone/hour

---

## 📝 What to Report

If it's still not working, please tell me:

1. **What hour did you select?** (e.g., 18)
2. **What does the debug line say?** (e.g., "This zone is 75% occupied")
3. **Which zone did you select?** (e.g., Zone A)
4. **Do you see ANY warning/recommendation box?** (Yes/No)
5. **Screenshot if possible**

This will help me identify the exact issue!

---

**Quick Test Command:**
```
Hour: 18
Zone: Zone A (or highest % zone)
Expected: See red warning + blue recommendation at TOP
```

