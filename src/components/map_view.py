"""
Map View Component
Displays a temporary satellite-style map with parking area markers
"""
import streamlit as st
import pandas as pd

def render_map_view():
    """Render a dummy satellite map with parking area markers"""
    
    st.markdown("### 🗺️ Parking Area Map")
    st.markdown("*Select a parking area to view available sections*")
    
    # Dummy parking area data (coordinates for visual representation)
    parking_areas = [
        {
            'name': 'Downtown Parking Complex',
            'location': 'City Center',
            'lat': 40.7580,
            'lon': -73.9855,
            'zones': ['Zone A', 'Zone B', 'Zone C', 'Zone D'],
            'total_capacity': 200
        }
    ]
    
    # Create a simple map visualization using folium-like approach
    # For now, we'll use a simple card-based UI that simulates a map
    
    st.markdown("""
    <style>
    .map-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        margin: 20px 0;
    }
    .parking-marker {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        cursor: pointer;
        transition: transform 0.2s;
    }
    .parking-marker:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display parking area as clickable cards
    st.markdown('<div class="map-container">', unsafe_allow_html=True)
    
    for area in parking_areas:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown(f"""
            <div class="parking-marker">
                <h3>📍 {area['name']}</h3>
                <p><strong>Location:</strong> {area['location']}</p>
                <p><strong>Zones Available:</strong> {', '.join(area['zones'])}</p>
                <p><strong>Total Capacity:</strong> {area['total_capacity']} spots</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Button to select this parking area
            if st.button(f"Select {area['name']}", key=f"area_{area['name']}", use_container_width=True):
                st.session_state.selected_area = area['name']
                st.session_state.show_section_selector = True
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display map legend
    with st.expander("ℹ️ Map Legend"):
        st.markdown("""
        - 🟢 **Available** - Parking area with free spots
        - 🟡 **Limited** - Parking area with few spots remaining
        - 🔴 **Full** - Parking area at capacity
        - 📍 **Location Marker** - Click to view parking sections
        """)
    
    return st.session_state.get('selected_area', None)

