"""
Booking System Module
Generates and manages dummy booking data (will be replaced with database later)
"""
import random
import pandas as pd
from datetime import datetime, timedelta

class BookingSystem:
    """
    Handles parking spot bookings
    Currently generates dummy data - will be replaced with database queries later
    
    IMPORTANT: Uses a fixed random seed to ensure bookings are consistent
    across page refreshes and interactions within the same session.
    """
    
    def __init__(self, data_loader, seed=42):
        """
        Initialize booking system with reference to parking data
        
        Args:
            data_loader: ParkingDataLoader instance
            seed: Random seed for consistent booking generation (default: 42)
        """
        self.data_loader = data_loader
        self.seed = seed
        self.bookings = self._generate_dummy_bookings()
    
    def _generate_dummy_bookings(self):
        """
        Generate dummy booking data for each hour (0-23) and each parking spot
        This simulates real user bookings from a database
        
        USES FIXED SEED: Ensures bookings are consistent and don't change
        randomly when user interacts with the app (selecting spots, etc.)
        
        Returns:
            dict: {(spot_id, section, hour): booking_status}
        """
        # Set random seed for consistent bookings
        random.seed(self.seed)
        
        bookings = {}
        
        # Get all sections and spots
        sections = self.data_loader.get_all_sections()
        
        for section in sections:
            spots = self.data_loader.get_spots_by_section(section)
            
            for spot_id in spots:
                for hour in range(24):  # 0-23 hours
                    # Generate occupancy pattern based on typical parking behavior
                    occupancy_probability = self._get_occupancy_probability(hour)
                    
                    # Randomly decide if spot is booked at this hour
                    is_booked = random.random() < occupancy_probability
                    
                    bookings[(spot_id, section, hour)] = {
                        'is_booked': is_booked,
                        'booked_by': f"User_{random.randint(1000, 9999)}" if is_booked else None,
                        'booking_time': datetime.now() - timedelta(hours=random.randint(1, 48)) if is_booked else None
                    }
        
        # Reset random seed to avoid affecting other random operations
        random.seed()
        
        return bookings
    
    def _get_occupancy_probability(self, hour):
        """
        Get probability of a spot being occupied based on hour
        Simulates realistic parking patterns
        
        Peak hours (8-10 AM, 5-7 PM): Higher occupancy
        Off-peak (11 PM - 6 AM): Lower occupancy
        """
        if 8 <= hour <= 10 or 17 <= hour <= 19:  # Peak hours
            return 0.75  # 75% occupancy
        elif 11 <= hour <= 16:  # Midday
            return 0.60  # 60% occupancy
        elif 20 <= hour <= 22:  # Evening
            return 0.50  # 50% occupancy
        else:  # Night/early morning
            return 0.25  # 25% occupancy
    
    def is_spot_booked(self, spot_id, section, hour):
        """
        Check if a specific spot is booked at a given hour
        
        Args:
            spot_id: Parking spot ID
            section: Parking section (Zone A, B, C, D)
            hour: Hour of day (0-23)
        
        Returns:
            bool: True if booked, False if available
        """
        key = (spot_id, section, hour)
        return self.bookings.get(key, {}).get('is_booked', False)
    
    def get_section_occupancy(self, section, hour):
        """
        Calculate occupancy percentage for a section at a given hour
        
        Args:
            section: Parking section (Zone A, B, C, D)
            hour: Hour of day (0-23)
        
        Returns:
            dict: {
                'total_spots': int,
                'booked_spots': int,
                'available_spots': int,
                'occupancy_percentage': float
            }
        """
        spots = self.data_loader.get_spots_by_section(section)
        total_spots = len(spots)
        
        booked_spots = sum(
            1 for spot_id in spots 
            if self.is_spot_booked(spot_id, section, hour)
        )
        
        available_spots = total_spots - booked_spots
        occupancy_percentage = (booked_spots / total_spots * 100) if total_spots > 0 else 0
        
        return {
            'total_spots': total_spots,
            'booked_spots': booked_spots,
            'available_spots': available_spots,
            'occupancy_percentage': round(occupancy_percentage, 1)
        }
    
    def get_all_sections_occupancy(self, hour):
        """
        Get occupancy data for all sections at a given hour
        
        Args:
            hour: Hour of day (0-23)
        
        Returns:
            dict: {section_name: occupancy_data}
        """
        sections = self.data_loader.get_all_sections()
        return {
            section: self.get_section_occupancy(section, hour)
            for section in sections
        }
    
    def get_least_occupied_section(self, hour):
        """
        Find the least occupied section at a given hour
        
        Args:
            hour: Hour of day (0-23)
        
        Returns:
            tuple: (section_name, occupancy_percentage)
        """
        all_occupancy = self.get_all_sections_occupancy(hour)
        
        least_occupied = min(
            all_occupancy.items(),
            key=lambda x: x[1]['occupancy_percentage']
        )
        
        return (least_occupied[0], least_occupied[1]['occupancy_percentage'])
    
    def get_available_spots_in_section(self, section, hour):
        """
        Get list of available (not booked) spots in a section at a given hour
        Sorted by spot ID for consistency
        
        Args:
            section: Parking section
            hour: Hour of day (0-23)
        
        Returns:
            list: List of available spot IDs (sorted)
        """
        spots = self.data_loader.get_spots_by_section(section)
        
        available = [
            spot_id for spot_id in spots
            if not self.is_spot_booked(spot_id, section, hour)
        ]
        
        return sorted(available)
    
    def get_best_available_spot(self, section, hour, data_loader, prefer_close_to_exit=True):
        """
        Get the best available spot in a section based on criteria
        
        Args:
            section: Parking section
            hour: Hour of day (0-23)
            data_loader: ParkingDataLoader to get spot details
            prefer_close_to_exit: If True, prefer spots closer to exit
        
        Returns:
            int or None: Best available spot ID, or None if all booked
        """
        available_spots = self.get_available_spots_in_section(section, hour)
        
        if not available_spots:
            return None
        
        # If we want closest to exit, evaluate each spot
        if prefer_close_to_exit:
            best_spot = None
            min_distance = float('inf')
            
            for spot_id in available_spots:
                spot_info = data_loader.get_spot_info(spot_id, section)
                if spot_info:
                    distance = spot_info.get('Proximity_To_Exit', float('inf'))
                    if distance < min_distance:
                        min_distance = distance
                        best_spot = spot_id
            
            return best_spot if best_spot else available_spots[0]
        
        # Otherwise, just return the first available
        return available_spots[0]
    
    def get_occupancy_trend(self, section, current_hour):
        """
        Detect if occupancy is rising or falling
        
        Args:
            section: Parking section
            current_hour: Current hour (0-23)
        
        Returns:
            str: 'rising', 'falling', or 'stable'
        """
        if current_hour == 0:
            prev_hour = 23
        else:
            prev_hour = current_hour - 1
        
        current_occupancy = self.get_section_occupancy(section, current_hour)['occupancy_percentage']
        prev_occupancy = self.get_section_occupancy(section, prev_hour)['occupancy_percentage']
        
        diff = current_occupancy - prev_occupancy
        
        if diff > 5:
            return 'rising'
        elif diff < -5:
            return 'falling'
        else:
            return 'stable'
    
    def book_spot(self, spot_id, section, hour, user_id="User"):
        """
        Book a parking spot (for future use when booking is implemented)
        
        Args:
            spot_id: Parking spot ID
            section: Parking section
            hour: Hour to book (0-23)
            user_id: User making the booking
        
        Returns:
            bool: True if booking successful, False if already booked
        """
        key = (spot_id, section, hour)
        
        # Check if spot is available
        if key in self.bookings and self.bookings[key]['is_booked']:
            return False  # Already booked
        
        # Book the spot
        self.bookings[key] = {
            'is_booked': True,
            'booked_by': user_id,
            'booking_time': datetime.now()
        }
        
        return True

