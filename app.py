"""
Smart Parking Prebooking System
Main Streamlit Application
"""
import streamlit as st
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data.data_loader import ParkingDataLoader
from data.booking_system import BookingSystem
from components.map_view import render_map_view
from components.section_selector import render_section_selector
from components.slot_selector import render_slot_selector
from components.user_inputs import render_user_inputs, get_user_inputs
from utils.helpers import initialize_session_state, get_navigation_state

# Page configuration
st.set_page_config(
    page_title="Smart Parking System",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
initialize_session_state()

# Main app
def main():
    # App header
    st.title("🅿️ Smart Parking Prebooking System")
    st.markdown("*Reserve your parking spot in advance with AI-powered recommendations*")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        
        # Display current selection
        nav_state = get_navigation_state()
        
        if nav_state['area']:
            st.success(f"📍 Area: {nav_state['area']}")
        
        if nav_state['section']:
            st.success(f"🅿️ Section: {nav_state['section']}")
        
        if nav_state['slot']:
            st.success(f"🚗 Slot: {nav_state['slot']}")
        
        st.markdown("---")
        
        # User inputs section (always visible)
        user_inputs = render_user_inputs()
        
        st.markdown("---")
        
        # Display inputs ready for ML prediction
        if user_inputs and user_inputs.get('parking_spot_id'):
            with st.expander("🔮 ML Prediction Inputs Ready", expanded=False):
                st.json({
                    'hour': user_inputs['hour'],
                    'day_of_week': user_inputs['day_of_week'],
                    'vehicle_type': user_inputs['vehicle_type'],
                    'parking_spot_id': user_inputs['parking_spot_id'],
                    'electric_vehicle': user_inputs['electric_vehicle']
                })
                st.success("✅ All inputs collected! (Predictions coming soon)")
        
        st.markdown("---")
        
        # App info
        with st.expander("ℹ️ About"):
            st.markdown("""
            **Smart Parking System** helps you:
            - Find available parking spots
            - Book slots in advance
            - Get AI-powered recommendations
            - View real-time availability
            
            **Version:** 1.2.1 (Smart Spot Recommendations)
            """)
        
        # Reset button
        if st.button("🔄 Reset Selection", use_container_width=True):
            from utils.helpers import reset_navigation
            reset_navigation()
            st.rerun()
    
    # Main content area
    try:
        # Load parking data
        data_loader = ParkingDataLoader()
        
        # Initialize booking system ONCE per session (cached)
        # This ensures bookings don't change randomly when user interacts
        if 'booking_system' not in st.session_state:
            st.session_state.booking_system = BookingSystem(data_loader, seed=42)
        
        booking_system = st.session_state.booking_system
        
        # Get user inputs (especially selected hour)
        user_inputs = get_user_inputs()
        selected_hour = user_inputs.get('hour') if user_inputs else None
        
        # Navigation logic
        nav_state = get_navigation_state()
        
        # Show appropriate view based on navigation state
        if nav_state['show_slots'] and nav_state['section']:
            # Show slot selector with booking system
            spots = data_loader.get_spots_by_section(nav_state['section'])
            render_slot_selector(
                spots, 
                nav_state['section'], 
                data_loader, 
                booking_system, 
                selected_hour
            )
        
        elif nav_state['show_sections'] and nav_state['area']:
            # Show section selector with occupancy data
            sections = data_loader.get_all_sections()
            render_section_selector(
                sections, 
                nav_state['area'], 
                booking_system, 
                selected_hour
            )
        
        else:
            # Show map view (default)
            render_map_view()
        
    except FileNotFoundError as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("Please ensure the CSV file is in the 'resources' folder")
    
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()

