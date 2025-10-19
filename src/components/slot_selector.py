"""
Slot Selector Component
Displays parking slots in a 2D grid (bus booking style)
Shows time-based availability from booking system
Integrated with ML predictor for intelligent suggestions
"""
import streamlit as st
import math
from datetime import datetime, timedelta

def render_slot_selector(spots, section_name, data_loader, booking_system=None, selected_hour=None):
    """
    Render parking slots in a 2D grid layout similar to bus booking UI
    Shows real-time booking status based on selected time
    
    Args:
        spots: List of parking spot IDs
        section_name: Name of the selected section
        data_loader: ParkingDataLoader instance for getting spot info
        booking_system: BookingSystem instance for time-based availability
        selected_hour: Hour selected by user (0-23)
    """
    
    st.markdown(f"### 🚗 Select Parking Slot - {section_name}")
    
    # Debug info to show occupancy (temporary - for testing)
    if booking_system and selected_hour is not None:
        current_occ = booking_system.get_section_occupancy(section_name, selected_hour)
        st.caption(f"🔍 Debug: This zone is {current_occ['occupancy_percentage']:.0f}% occupied at hour {selected_hour}")
    
    # Custom CSS for slot grid
    st.markdown("""
    <style>
    .slot-container {
        background: #f7fafc;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    .slot-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
        gap: 10px;
        margin: 20px 0;
    }
    .slot {
        aspect-ratio: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 14px;
        position: relative;
    }
    .slot-available {
        background: #48bb78;
        color: white;
        border: 2px solid #38a169;
    }
    .slot-available:hover {
        background: #38a169;
        transform: scale(1.1);
        box-shadow: 0 0 10px rgba(56, 161, 105, 0.5);
    }
    .slot-occupied {
        background: #fc8181;
        color: white;
        border: 2px solid #f56565;
        cursor: not-allowed;
        opacity: 0.6;
    }
    .slot-occupied:hover {
        opacity: 0.8;
    }
    .slot-selected {
        background: #4299e1;
        color: white;
        border: 3px solid #2b6cb0;
        transform: scale(1.1);
        box-shadow: 0 0 15px rgba(66, 153, 225, 0.6);
    }
    .ev-icon {
        position: absolute;
        top: 6px;
        right: 6px;
        font-size: 12px;
        background: rgba(255,255,255,0.15);
        padding: 2px 6px;
        border-radius: 6px;
        color: #fff;
        display: inline-block;
    }
    .slot-available .ev-icon { background: rgba(255,255,255,0.15); color: #065f46; }
    .slot-selected .ev-icon { background: rgba(255,255,255,0.18); color: #055a8c; }
    .legend {
        display: flex;
        gap: 20px;
        margin: 20px 0;
        justify-content: center;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .legend-box {
        width: 30px;
        height: 30px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Floating panel CSS
    st.markdown("""
    <style>
    .floating-panel {
        position: fixed;
        top: 80px;
        right: 20px;
        width: 320px;
        background: #ffffff;
        border-radius: 10px;
        padding: 16px 18px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        z-index: 9999;
        border-left: 6px solid #4299e1;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
    }
    .floating-panel h4 { margin: 0 0 8px 0; }
    .floating-panel .meta { font-size: 13px; color: #4a5568; margin-bottom: 6px; }
    .floating-panel .close-note { font-size: 12px; color: #718096; margin-top: 8px; }
    </style>
    """, unsafe_allow_html=True)
    
    # Back button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Back to Sections", key="back_to_sections"):
            st.session_state.show_slot_selector = False
            st.session_state.selected_section = None
            st.session_state.selected_slot = None
            if 'occupancy_suggestion' in st.session_state:
                del st.session_state.occupancy_suggestion
            st.rerun()
    
    # Show occupancy warning if current zone is busy (unless user dismissed it)
    dismiss_key = f"dismiss_{section_name}_{selected_hour}"
    if booking_system and selected_hour is not None:
        current_occupancy = booking_system.get_section_occupancy(section_name, selected_hour)
        current_occ_pct = current_occupancy['occupancy_percentage']
        
        # If zone is busy (>60%), show prominent warning with suggestion
        if current_occ_pct > 60 and not st.session_state.get(dismiss_key, False):
            least_occupied_section, least_occ_pct = booking_system.get_least_occupied_section(selected_hour)
            
            # Only suggest if there's a significant difference (>15%)
            if least_occupied_section != section_name and least_occ_pct < current_occ_pct - 15:
                # Get best spot in the better zone
                recommended_spot = booking_system.get_best_available_spot(
                    least_occupied_section, 
                    selected_hour,
                    data_loader,
                    prefer_close_to_exit=True
                )
                
                if recommended_spot:
                    rec_spot_info = data_loader.get_spot_info(recommended_spot, least_occupied_section)
                    available_count = booking_system.get_section_occupancy(least_occupied_section, selected_hour)['available_spots']
                    
                    st.error(f"""
                    ⚠️ **WARNING: {section_name} is {current_occ_pct:.0f}% occupied!**
                    
                    Finding a spot here might be difficult. Consider a less crowded alternative.
                    """)
                    
                    st.info(f"""
                    💡 **Smart Recommendation:**
                    
                    **Spot {recommended_spot}** in **{least_occupied_section}** is a better choice:
                    - ✅ Only **{least_occ_pct:.0f}% occupied** ({current_occ_pct - least_occ_pct:.0f}% less crowded)
                    - ✅ **{available_count} spots available** (vs {current_occupancy['available_spots']} here)
                    - ✅ Distance to exit: **{rec_spot_info.get('Proximity_To_Exit', 0):.1f}m**
                    - ✅ Easier to find and park
                    
                    *We strongly recommend switching to avoid congestion!*
                    """)
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(f"🚀 Switch to Spot {recommended_spot} in {least_occupied_section}", 
                                   key="switch_zone_top",
                                   type="primary",
                                   use_container_width=True):
                            st.session_state.selected_section = least_occupied_section
                            st.session_state.selected_slot = recommended_spot
                            if 'occupancy_suggestion' in st.session_state:
                                del st.session_state.occupancy_suggestion
                            st.rerun()
                    with col_b:
                        if st.button("Dismiss & Stay Here", 
                                   key="stay_zone_top",
                                   use_container_width=True):
                            # Dismiss the suggestion for this zone/hour combo
                            st.session_state[dismiss_key] = True
                            st.rerun()
        
        # Show zone status info
        if current_occ_pct > 60:
            if st.session_state.get(dismiss_key, False):
                st.warning(f"📊 **{section_name}** is {current_occ_pct:.0f}% occupied ({current_occupancy['available_spots']} spots available)")
            # else: already shown warning above
        elif current_occ_pct > 40:
            st.warning(f"📊 **{section_name}** is {current_occ_pct:.0f}% occupied - Moderate traffic")
        else:
            st.success(f"✅ **{section_name}** is only {current_occ_pct:.0f}% occupied - Plenty of spaces!")
    
    st.markdown("---")
    
    # Legend
    st.markdown("""
    <div class="legend">
        <div class="legend-item">
            <div class="legend-box" style="background: #48bb78;"></div>
            <span>Available</span>
        </div>
        <div class="legend-item">
            <div class="legend-box" style="background: #fc8181;"></div>
            <span>Occupied</span>
        </div>
        <div class="legend-item">
            <div class="legend-box" style="background: #4299e1;"></div>
            <span>Selected</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize selected slot in session state
    if 'selected_slot' not in st.session_state:
        st.session_state.selected_slot = None
    
    # Calculate grid dimensions (e.g., 10 slots per row)
    slots_per_row = 10
    num_rows = math.ceil(len(spots) / slots_per_row)
    
    # Display slots in grid format
    st.markdown('<div class="slot-container">', unsafe_allow_html=True)
    
    for row in range(num_rows):
        cols = st.columns(slots_per_row)
        
        for col_idx in range(slots_per_row):
            spot_idx = row * slots_per_row + col_idx
            
            if spot_idx < len(spots):
                spot_id = spots[spot_idx]
                
                # Get spot information
                spot_info = data_loader.get_spot_info(spot_id, section_name)
                
                if spot_info:
                    # Check if spot is booked at selected hour (from booking system)
                    if booking_system and selected_hour is not None:
                        is_occupied = booking_system.is_spot_booked(spot_id, section_name, selected_hour)
                    else:
                        # Fallback to CSV data
                        is_occupied = spot_info.get('Occupancy_Status', 'Vacant') == 'Occupied'
                    
                    is_selected = st.session_state.selected_slot == spot_id
                    
                    with cols[col_idx]:
                        # Determine slot class
                        if is_selected:
                            slot_class = "slot-selected"
                        elif is_occupied:
                            slot_class = "slot-occupied"
                        else:
                            slot_class = "slot-available"
                        
                        # Display slot
                        # Prepare tooltip for available/selected slots
                        tooltip_text = ""
                        try:
                            if slot_class in ("slot-available", "slot-selected") and spot_info:
                                ev = 'Yes' if spot_info.get('Electric_Vehicle', 0) == 1 else 'No'
                                size = spot_info.get('Spot_Size', 'Standard')
                                # Use a concise one-line tooltip (browser title) for hover and focus
                                tooltip_text = f"✅ Selected Slot Information | Slot ID: {spot_id} | Section: {section_name} | Spot Size: {size} | EV Charging: {ev}"
                        except Exception:
                            tooltip_text = ""

                        title_attr = f' title="{tooltip_text}"' if tooltip_text else ""

                        # EV icon markup when available
                        ev_html = ""
                        try:
                            if spot_info and spot_info.get('Electric_Vehicle', 0) == 1:
                                # small lightning bolt emoji as EV indicator
                                ev_html = f"<span class='ev-icon'>⚡ EV</span>"
                        except Exception:
                            ev_html = ""

                        st.markdown(f"""
                        <div class="slot {slot_class}"{title_attr}>
                            {spot_id}
                            {ev_html}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Button for slot selection (only if available)
                        if not is_occupied:
                            if st.button(
                                f"Slot {spot_id}", 
                                key=f"slot_{spot_id}",
                                use_container_width=True,
                                type="primary" if is_selected else "secondary"
                            ):
                                st.session_state.selected_slot = spot_id
                                # Update user inputs with selected slot
                                if 'user_inputs' in st.session_state:
                                    st.session_state.user_inputs['parking_spot_id'] = spot_id
                                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display selected slot information
    if st.session_state.selected_slot:
        st.markdown("---")
        st.markdown("### ✅ Selected Slot Information")
        
        selected_spot_info = data_loader.get_spot_info(
            st.session_state.selected_slot, 
            section_name
        )
        
        if selected_spot_info:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Slot ID", st.session_state.selected_slot)
            
            with col2:
                st.metric("Section", section_name)
            
            with col3:
                spot_size = selected_spot_info.get('Spot_Size', 'Standard')
                st.metric("Spot Size", spot_size)
            
            # Show reminder about the recommendation at the bottom
            if booking_system and selected_hour is not None:
                current_occupancy = booking_system.get_section_occupancy(section_name, selected_hour)
                current_occ_pct = current_occupancy['occupancy_percentage']
                
                # If zone is still busy, show a gentle reminder
                if current_occ_pct > 60:
                    least_occupied_section, least_occ_pct = booking_system.get_least_occupied_section(selected_hour)
                    if least_occupied_section != section_name and least_occ_pct < current_occ_pct - 15:
                        st.caption(f"💡 Reminder: {least_occupied_section} has {least_occ_pct:.0f}% occupancy (less crowded). See recommendation above.")
            
            # ML-Powered Insights (NEW!)
            st.markdown("---")
            st.markdown("### 🤖 AI-Powered Insights")
            
            # Get ML prediction
            ml_prediction = _get_ml_insights(
                st.session_state.selected_slot,
                section_name,
                selected_hour,
                data_loader
            )
            
            if ml_prediction and ml_prediction.get('available'):
                _display_ml_insights(ml_prediction, section_name, selected_hour, booking_system, data_loader)
            
            # Additional spot details
            with st.expander("📋 Detailed Spot Information"):
                st.write(f"**Proximity to Exit:** {selected_spot_info.get('Proximity_To_Exit', 'N/A'):.2f} meters")
                st.write(f"**Spot Type:** {spot_size}")
                st.write(f"**EV Charging:** {'Yes' if selected_spot_info.get('Electric_Vehicle', 0) == 1 else 'No'}")
            
            # Proceed to booking button
            if st.button("📅 Proceed to Booking", type="primary", use_container_width=True):
                st.success(f"✅ Slot {st.session_state.selected_slot} selected! (Booking flow coming soon)")
                # This is where booking logic will be added later

        # Floating info panel (also shows when a slot is selected)
        try:
            ev = 'Yes' if selected_spot_info.get('Electric_Vehicle', 0) == 1 else 'No'
            size = selected_spot_info.get('Spot_Size', 'Standard')
            proximity = selected_spot_info.get('Proximity_To_Exit', 0.0)

            panel_html = f"""
            <div class='floating-panel' id='floating_slot_info'>
                <h4>✅ Selected Slot Information</h4>
                <div class='meta'><strong>Slot ID:</strong> {st.session_state.selected_slot}</div>
                <div class='meta'><strong>Section:</strong> {section_name}</div>
                <div class='meta'><strong>Spot Size:</strong> {size}</div>
                <div class='meta'><strong>EV Charging:</strong> {ev}</div>
                <div class='meta'><strong>Proximity to Exit:</strong> {proximity:.1f} m</div>
                <div class='close-note'>Click the button below to close this panel.</div>
            </div>
            """

            st.markdown(panel_html, unsafe_allow_html=True)

            if st.button("Close Info", key="close_floating_info"):
                st.session_state.selected_slot = None
                # Also clear parking_spot_id in user inputs when closing
                if 'user_inputs' in st.session_state and 'parking_spot_id' in st.session_state.user_inputs:
                    st.session_state.user_inputs['parking_spot_id'] = None
                st.experimental_rerun()

        except Exception:
            # If any data missing, silently skip floating panel
            pass


def _get_ml_insights(spot_id, section, hour, data_loader):
    """Get ML insights for selected spot"""
    try:
        # Import predictor
        from ml.predictor_prebooking import PrebookingPredictor
        
        # Initialize predictor (cached in session state)
        if 'ml_predictor' not in st.session_state:
            st.session_state.ml_predictor = PrebookingPredictor(
                model_dir='models',
                data_loader=data_loader
            )
        
        predictor = st.session_state.ml_predictor
        
        # Get user inputs
        user_inputs = st.session_state.get('user_inputs', {})
        day_of_week = user_inputs.get('day_of_week', datetime.now().strftime('%A'))
        vehicle_type = user_inputs.get('vehicle_type', 'Sedan')
        is_ev = user_inputs.get('electric_vehicle', 0) == 1
        
        # Calculate booking datetime (current day at selected hour)
        now = datetime.now()
        booking_datetime = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        # If selected hour is in the past today, assume next day
        if booking_datetime < now:
            booking_datetime += timedelta(days=1)
        
        # Get prediction
        prediction = predictor.predict_for_prebooking(
            spot_id=spot_id,
            section=section,
            booking_datetime=booking_datetime,
            vehicle_type=vehicle_type,
            is_ev=is_ev
        )
        
        prediction['available'] = True
        return prediction
    
    except Exception as e:
        print(f"[ERROR] ML insights failed: {e}")
        return {'available': False, 'error': str(e)}


def _display_ml_insights(prediction, section, hour, booking_system, data_loader):
    """Display ML insights in a beautiful format"""
    
    insights = prediction.get('insights', {})
    
    # Main prediction card
    col1, col2, col3 = st.columns(3)
    
    with col1:
        confidence = prediction.get('probability_vacant', 0.5) * 100
        st.metric(
            "AI Confidence", 
            f"{confidence:.0f}%",
            "Likely Available" if confidence > 55 else "Uncertain",
            delta_color="normal" if confidence > 55 else "inverse"
        )
    
    with col2:
        traffic = prediction.get('predicted_traffic', 'Medium')
        traffic_emoji = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(traffic, "🟡")
        st.metric(
            "Traffic Prediction",
            f"{traffic_emoji} {traffic}",
            insights.get('traffic', {}).get('tip', '')
        )
    
    with col3:
        weather = insights.get('weather', {})
        temp = weather.get('temperature', 20)
        st.metric(
            "Weather Forecast",
            f"{temp:.0f}°C",
            weather.get('tip', 'Good conditions')
        )
    
    # Detailed insights in expandable sections
    with st.expander("🌤️ Weather & Environmental Conditions", expanded=True):
        weather_info = insights.get('weather', {})
        st.write(f"**Status:** {weather_info.get('status', 'N/A')}")
        st.write(f"**Temperature:** {weather_info.get('temperature', 20):.1f}°C")
        st.write(f"**Precipitation:** {'Rain expected' if weather_info.get('precipitation', 0) > 0 else 'No rain'}")
        st.info(f"💡 **Tip:** {weather_info.get('tip', 'Good parking conditions expected')}")
        
        # Weather source indicator
        source = weather_info.get('source', 'historical_average')
        if source == 'historical_average':
            st.caption("ℹ️ Using historical weather average (Live API coming soon)")
    
    with st.expander("🚗 Traffic & Timing Insights"):
        traffic_info = insights.get('traffic', {})
        time_info = insights.get('time_pattern', {})
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.write("**Traffic Prediction:**")
            st.write(f"- Level: {traffic_info.get('level', 'Medium')}")
            st.write(f"- {traffic_info.get('tip', 'N/A')}")
            st.caption(f"Source: {traffic_info.get('source', 'Pattern-based')}")
        
        with col_b:
            st.write("**Time Pattern:**")
            st.write(f"- Pattern: {time_info.get('pattern', 'N/A')}")
            st.write(f"- {time_info.get('tip', 'N/A')}")
            hours_until = prediction.get('hours_until_booking', 0)
            if hours_until > 0:
                st.caption(f"⏰ Booking {hours_until:.1f} hours ahead")
    
    with st.expander("🚙 Vehicle Compatibility"):
        vehicle_info = insights.get('vehicle_compatibility', {})
        compatible = vehicle_info.get('compatible', True)
        
        if compatible:
            st.success(f"✅ {vehicle_info.get('tip', 'Good match for your vehicle')}")
        else:
            st.warning(f"⚠️ {vehicle_info.get('tip', 'Spot size may not match')}")
            st.write(f"**Your vehicle needs:** {vehicle_info.get('recommended_size', 'Standard')} spot")
            st.write(f"**This spot is:** {vehicle_info.get('spot_size', 'Standard')}")
    
    # Overall recommendation
    recommendation = prediction.get('recommendation', '')
    
    if prediction.get('probability_vacant', 0.5) > 0.7:
        st.success(f"✅ **Recommendation:** {recommendation}")
    elif prediction.get('probability_vacant', 0.5) > 0.55:
        st.info(f"💡 **Recommendation:** {recommendation}")
    elif prediction.get('probability_vacant', 0.5) > 0.45:
        st.warning(f"⚠️ **Recommendation:** {recommendation}")
    else:
        st.error(f"❌ **Recommendation:** {recommendation}")
    
    # Smart alternatives suggestion
    if prediction.get('probability_vacant', 0.5) < 0.6:
        with st.expander("🎯 Smart Alternative Suggestions"):
            st.write("Looking for better options with higher availability confidence...")
            
            # Get user inputs
            user_inputs = st.session_state.get('user_inputs', {})
            day_of_week = user_inputs.get('day_of_week', datetime.now().strftime('%A'))
            vehicle_type = user_inputs.get('vehicle_type', 'Sedan')
            is_ev = user_inputs.get('electric_vehicle', 0) == 1
            
            # Calculate booking time
            now = datetime.now()
            booking_datetime = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if booking_datetime < now:
                booking_datetime += timedelta(days=1)
            
            # Get alternatives
            try:
                predictor = st.session_state.ml_predictor
                
                # Get available spots from booking system
                available_spots = booking_system.get_available_spots_in_section(section, hour)
                
                # Get ML predictions for alternatives
                alternatives = []
                for spot_id in available_spots[:10]:  # Check top 10 available spots
                    if spot_id == st.session_state.selected_slot:
                        continue  # Skip currently selected spot
                    
                    alt_pred = predictor.predict_for_prebooking(
                        spot_id=spot_id,
                        section=section,
                        booking_datetime=booking_datetime,
                        vehicle_type=vehicle_type,
                        is_ev=is_ev
                    )
                    
                    spot_info = data_loader.get_spot_info(spot_id, section)
                    
                    alternatives.append({
                        'spot_id': spot_id,
                        'confidence': alt_pred.get('probability_vacant', 0.5),
                        'distance': spot_info.get('Proximity_To_Exit', 10.0) if spot_info else 10.0,
                        'size': spot_info.get('Spot_Size', 'Standard') if spot_info else 'Standard',
                        'compatible': alt_pred.get('size_compatible', True)
                    })
                
                # Sort by confidence (descending)
                alternatives.sort(key=lambda x: x['confidence'], reverse=True)
                
                # Display top 3 alternatives
                if alternatives:
                    st.write("**Top 3 Alternative Spots:**")
                    
                    for i, alt in enumerate(alternatives[:3], 1):
                        col_1, col_2, col_3, col_4 = st.columns([1, 2, 2, 1])
                        
                        with col_1:
                            st.write(f"**#{i}**")
                        
                        with col_2:
                            st.write(f"**Spot {alt['spot_id']}**")
                            st.caption(f"{alt['size']} {'✓' if alt['compatible'] else '⚠️'}")
                        
                        with col_3:
                            st.write(f"{alt['confidence']*100:.0f}% confidence")
                            st.caption(f"{alt['distance']:.1f}m from exit")
                        
                        with col_4:
                            if st.button("Select", key=f"alt_{alt['spot_id']}"):
                                st.session_state.selected_slot = alt['spot_id']
                                if 'user_inputs' in st.session_state:
                                    st.session_state.user_inputs['parking_spot_id'] = alt['spot_id']
                                st.rerun()
                else:
                    st.write("No better alternatives found at this time.")
            
            except Exception as e:
                st.write(f"Unable to load alternatives: {str(e)}")

