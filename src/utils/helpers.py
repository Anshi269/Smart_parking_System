"""
Helper Utilities
Common utility functions for the parking app
"""
import streamlit as st

def initialize_session_state():
    """Initialize all session state variables"""
    if 'selected_area' not in st.session_state:
        st.session_state.selected_area = None
    
    if 'selected_section' not in st.session_state:
        st.session_state.selected_section = None
    
    if 'selected_slot' not in st.session_state:
        st.session_state.selected_slot = None
    
    if 'show_section_selector' not in st.session_state:
        st.session_state.show_section_selector = False
    
    if 'show_slot_selector' not in st.session_state:
        st.session_state.show_slot_selector = False
    
    if 'user_inputs' not in st.session_state:
        st.session_state.user_inputs = {}
    
    # Note: booking_system is initialized separately in app.py
    # to ensure it persists throughout the session

def reset_navigation():
    """Reset all navigation states (but keep booking_system intact)"""
    st.session_state.selected_area = None
    st.session_state.selected_section = None
    st.session_state.selected_slot = None
    st.session_state.show_section_selector = False
    st.session_state.show_slot_selector = False
    st.session_state.user_inputs = {}
    # Note: We don't reset booking_system so bookings remain consistent

def get_navigation_state():
    """Get current navigation state"""
    return {
        'area': st.session_state.get('selected_area'),
        'section': st.session_state.get('selected_section'),
        'slot': st.session_state.get('selected_slot'),
        'show_sections': st.session_state.get('show_section_selector', False),
        'show_slots': st.session_state.get('show_slot_selector', False)
    }

