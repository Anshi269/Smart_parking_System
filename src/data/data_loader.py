"""
Data Loader Module
Handles loading and processing parking data from CSV file
"""
import pandas as pd
import os

class ParkingDataLoader:
    def __init__(self, csv_path="resources/IIoT_Smart_Parking_Management (2).csv"):
        """Initialize data loader with CSV path"""
        self.csv_path = csv_path
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Load parking data from CSV"""
        if os.path.exists(self.csv_path):
            self.df = pd.read_csv(self.csv_path)
            print(f"✓ Loaded {len(self.df)} records from parking dataset")
        else:
            raise FileNotFoundError(f"CSV file not found at {self.csv_path}")
    
    def get_all_sections(self):
        """Get unique parking lot sections (zones)"""
        if self.df is not None:
            return sorted(self.df['Parking_Lot_Section'].unique())
        return []
    
    def get_spots_by_section(self, section):
        """Get all parking spots in a specific section"""
        if self.df is not None:
            section_data = self.df[self.df['Parking_Lot_Section'] == section]
            spots = section_data['Parking_Spot_ID'].unique()
            return sorted(spots)
        return []
    
    def get_spot_info(self, spot_id, section):
        """Get detailed information about a specific parking spot"""
        if self.df is not None:
            spot_data = self.df[
                (self.df['Parking_Spot_ID'] == spot_id) & 
                (self.df['Parking_Lot_Section'] == section)
            ]
            if not spot_data.empty:
                return spot_data.iloc[-1].to_dict()  # Get most recent record
        return None
    
    def get_section_statistics(self, section):
        """Get statistics for a parking section"""
        if self.df is not None:
            section_data = self.df[self.df['Parking_Lot_Section'] == section]
            total_spots = len(section_data['Parking_Spot_ID'].unique())
            occupied = len(section_data[section_data['Occupancy_Status'] == 'Occupied'])
            occupancy_rate = (occupied / total_spots * 100) if total_spots > 0 else 0
            
            return {
                'total_spots': total_spots,
                'occupied': occupied,
                'available': total_spots - occupied,
                'occupancy_rate': occupancy_rate
            }
        return None

