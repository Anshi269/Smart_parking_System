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
    
    # 1. Hour selection (0-23 with AM/PM display)
    st.markdown("#### ⏰ Arrival Time")
    hour = st.slider(
        "Select Hour",
        min_value=0,
        max_value=23,
        value=current_hour,
        format="%d:00",
        help="What time do you plan to arrive?"
    )
    
    # Display in 12-hour format for user clarity
    if hour == 0:
        hour_display = "12:00 AM"
    elif hour < 12:
        hour_display = f"{hour}:00 AM"
    elif hour == 12:
        hour_display = "12:00 PM"
    else:
        hour_display = f"{hour-12}:00 PM"
    
    st.caption(f"Selected: **{hour_display}**")
    
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
    
    st.session_state.user_inputs = {
        'hour': hour,
        'hour_display': hour_display,
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
        st.metric("Time", hour_display)
        st.metric("Vehicle", vehicle_type)
    
    with summary_col2:
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

