"""
User Input Component
Collects user preferences and booking details for ML predictions
"""
import streamlit as st
from datetime import datetime

def render_user_inputs():
    """
    Render user input fields in sidebar
    Returns dict with all user inputs for ML prediction
    """
    
    st.subheader("📝 Booking Details")
    st.caption("*These inputs will be used for AI recommendations*")
    
    # Get current time for defaults
    now = datetime.now()
    current_hour = now.hour
    current_day = now.strftime('%A')
    
    # 1. Entry and Exit Time selection (simple time inputs)
    st.markdown("#### ⏰ Entry & Exit Time")

    # defaults: entry = current time rounded to hour, exit = entry + 1 hour
    from datetime import time, timedelta
    default_entry = now.replace(minute=0, second=0, microsecond=0).time()
    default_exit_dt = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
    default_exit = default_exit_dt.time()

    # Show Entry first, Exit below
    entry_time = st.time_input(
        "Entry Time",
        value=default_entry,
        help="What time do you plan to enter?"
    )

    st.markdown("---")

    exit_time = st.time_input(
        "Exit Time",
        value=default_exit,
        help="What time do you plan to exit?"
    )

    def fmt_time(t):
        # t is a datetime.time
        hour = t.hour
        if hour == 0:
            return f"12:{t.minute:02d} AM"
        elif hour < 12:
            return f"{hour}:{t.minute:02d} AM"
        elif hour == 12:
            return f"12:{t.minute:02d} PM"
        else:
            return f"{hour-12}:{t.minute:02d} PM"

    entry_time_display = fmt_time(entry_time)
    exit_time_display = fmt_time(exit_time)

    # Show entry and exit on separate lines
    st.caption(f"Selected Entry: **{entry_time_display}**")
    st.caption(f"Selected Exit: **{exit_time_display}**")

    # Compute duration (in minutes) between entry and exit, handle cross-midnight
    from datetime import datetime as _dt

    entry_dt = _dt.combine(_dt.today(), entry_time)
    exit_dt = _dt.combine(_dt.today(), exit_time)
    if exit_dt <= entry_dt:
        # Exit is next day
        exit_dt = exit_dt + timedelta(days=1)

    duration_td = exit_dt - entry_dt
    duration_minutes = int(duration_td.total_seconds() // 60)
    hours = duration_minutes // 60
    minutes = duration_minutes % 60
    if hours > 0:
        duration_str = f"{hours}h {minutes}m"
    else:
        duration_str = f"{minutes}m"

    st.markdown(f"**Duration:** {duration_str}")
    
    # 2. Day of Week selection
    st.markdown("#### 📅 Arrival Day")
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Set default to current day
    default_day_index = days.index(current_day) if current_day in days else 0
    
    day_of_week = st.selectbox(
        "Select Day of Week",
        options=days,
        index=default_day_index,
        help="Which day will you need parking?"
    )
    
    # 3. Vehicle Type selection
    st.markdown("#### 🚗 Vehicle Type")
    vehicle_types = ['Car', 'Sedan', 'SUV', 'Motorcycle', 'Electric Vehicle', 'Truck']
    
    vehicle_type = st.selectbox(
        "Select Vehicle Type",
        options=vehicle_types,
        index=1,  # Default to Sedan
        help="What type of vehicle will you be parking?"
    )
    
    # 5. Electric Vehicle checkbox
    st.markdown("#### 🔌 EV Charging")
    electric_vehicle = st.checkbox(
        "I need EV charging",
        value=False,
        help="Check if you need an electric vehicle charging station"
    )
    
    # Convert to 0/1 for ML model
    ev_value = 1 if electric_vehicle else 0
    
    # Store in session state
    if 'user_inputs' not in st.session_state:
        st.session_state.user_inputs = {}
    
    # Keep 'hour' for backwards compatibility (maps to entry hour)
    st.session_state.user_inputs = {
        'hour': entry_time.hour,
        'hour_display': entry_time_display,
        'entry_time': entry_time,
        'entry_time_display': entry_time_display,
        'exit_time': exit_time,
        'exit_time_display': exit_time_display,
        'entry_hour': entry_time.hour,
        'exit_hour': exit_time.hour,
        'duration_minutes': duration_minutes,
        'duration_str': duration_str,
        'day_of_week': day_of_week,
        'vehicle_type': vehicle_type,
        'electric_vehicle': ev_value,
        'parking_spot_id': st.session_state.get('selected_slot', None)
    }
    
    # Display summary in a nice box
    st.markdown("---")
    st.markdown("#### 📋 Summary")
    
    summary_col1, summary_col2 = st.columns(2)
    
    with summary_col1:
        st.metric("Entry", entry_time_display)
        st.metric("Vehicle", vehicle_type)
    
    with summary_col2:
        st.metric("Exit", exit_time_display)
        st.metric("Day", day_of_week[:3])  # Show abbreviated day
        st.metric("EV Charging", "Yes" if ev_value else "No")
    
    # Show selected slot if available
    if st.session_state.get('selected_slot'):
        st.success(f"🅿️ Spot: {st.session_state.selected_slot}")
    else:
        st.info("ℹ️ Select a parking spot above")
    
    return st.session_state.user_inputs


def get_user_inputs():
    """
    Get current user inputs from session state
    Returns dict or None if not set
    """
    return st.session_state.get('user_inputs', None)

