"""
Section Selector Component
Displays parking sections (zones) in a popup-style interface
Shows real-time occupancy percentage for each zone based on selected time
"""
import streamlit as st

def render_section_selector(sections, area_name, booking_system=None, selected_hour=None):
    """
    Render section selector as a popup-style interface with occupancy data
    
    Args:
        sections: List of available sections (e.g., ['Zone A', 'Zone B', ...])
        area_name: Name of the selected parking area
        booking_system: BookingSystem instance for occupancy data
        selected_hour: Hour selected by user (0-23) for time-based occupancy
    """
    
    st.markdown(f"### 🅿️ Select Parking Section - {area_name}")
    
    # Custom CSS for popup-style cards
    st.markdown("""
    <style>
    .section-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin: 20px 0;
    }
    .section-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 30px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        cursor: pointer;
        transition: all 0.3s;
        border: 2px solid transparent;
    }
    .section-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        border-color: #667eea;
    }
    .section-title {
        font-size: 24px;
        font-weight: bold;
        color: #2d3748;
        margin-bottom: 10px;
    }
    .section-info {
        font-size: 14px;
        color: #4a5568;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Map", key="back_to_map"):
        st.session_state.show_section_selector = False
        st.session_state.selected_area = None
        st.rerun()
    
    st.markdown("---")
    
    # Get occupancy data for all sections at selected hour
    occupancy_data = {}
    if booking_system and selected_hour is not None:
        occupancy_data = booking_system.get_all_sections_occupancy(selected_hour)
        
        # Show time context
        hour_display = f"{selected_hour}:00" if selected_hour < 12 or selected_hour == 0 else f"{selected_hour-12 if selected_hour > 12 else selected_hour}:00 {'AM' if selected_hour < 12 else 'PM'}"
        st.info(f"📊 Showing occupancy for **{hour_display}**")
    
    # Display sections in a grid layout
    cols = st.columns(min(len(sections), 4))
    
    for idx, section in enumerate(sections):
        col_idx = idx % len(cols)
        
        with cols[col_idx]:
            # Get occupancy info for this section
            if section in occupancy_data:
                occ_info = occupancy_data[section]
                occ_pct = occ_info['occupancy_percentage']
                available = occ_info['available_spots']
                
                # Determine color based on occupancy
                if occ_pct < 50:
                    color = "#48bb78"  # Green
                    status = "Low"
                elif occ_pct < 75:
                    color = "#ed8936"  # Orange
                    status = "Medium"
                else:
                    color = "#f56565"  # Red
                    status = "High"
                
                # Create a visually appealing card with occupancy info
                st.markdown(f"""
                <div class="section-card" style="border-left: 5px solid {color};">
                    <div class="section-title">🅿️ {section}</div>
                    <div class="section-info">
                        <strong style="color: {color};">{occ_pct}% Occupied</strong><br>
                        {available} spots available<br>
                        <small>Occupancy: {status}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Fallback if no occupancy data
                st.markdown(f"""
                <div class="section-card">
                    <div class="section-title">🅿️ {section}</div>
                    <div class="section-info">Click to view slots</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Button to select section
            if st.button(f"Select {section}", key=f"section_{section}", use_container_width=True):
                st.session_state.selected_section = section
                st.session_state.show_slot_selector = True
                
                # Check if this is a busy zone and suggest alternatives
                if section in occupancy_data and booking_system:
                    occ_pct = occupancy_data[section]['occupancy_percentage']
                    if occ_pct > 60:  # If more than 60% occupied
                        least_occupied, least_pct = booking_system.get_least_occupied_section(selected_hour)
                        if least_occupied != section and least_pct < occ_pct - 15:
                            # Store suggestion to show later
                            st.session_state.occupancy_suggestion = {
                                'current_zone': section,
                                'current_occupancy': occ_pct,
                                'suggested_zone': least_occupied,
                                'suggested_occupancy': least_pct
                            }
                
                st.rerun()
    
    # Section information panel
    st.markdown("---")
    with st.expander("📊 Section Information"):
        st.markdown("""
        **Available Sections:**
        - **Zone A**: Ground level parking, close to main entrance
        - **Zone B**: Level 1, covered parking with easy access
        - **Zone C**: Level 2, premium covered spots
        - **Zone D**: Rooftop parking, open-air spots
        
        *Select a zone to view real-time availability and book your spot*
        """)

