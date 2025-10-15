"""
Slot Selector Component
Displays parking slots in a 2D grid (bus booking style)
Shows time-based availability from booking system
"""
import streamlit as st
import math

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
                        st.markdown(f"""
                        <div class="slot {slot_class}">
                            {spot_id}
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
            
            # Additional spot details
            with st.expander("📋 Detailed Spot Information"):
                st.write(f"**Proximity to Exit:** {selected_spot_info.get('Proximity_To_Exit', 'N/A'):.2f} meters")
                st.write(f"**Spot Type:** {spot_size}")
                st.write(f"**EV Charging:** {'Yes' if selected_spot_info.get('Electric_Vehicle', 0) == 1 else 'No'}")
            
            # Proceed to booking button
            if st.button("📅 Proceed to Booking", type="primary", use_container_width=True):
                st.success(f"✅ Slot {st.session_state.selected_slot} selected! (Booking flow coming soon)")
                # This is where booking logic will be added later

