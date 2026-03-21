"""
File: pv_generator.py

Description: This module defines the PVGenerator class, which represents a photovoltaic (solar) generator in the energy system. 
 
"""


from src.models.abstract_asset import Asset
import numpy as np

class PVGenerator (Asset):
    def __init__(self, name):
        super().__init__(name)\
    #returns a numpy array of the generation profile for the PV generator
    def get_generation_profile(self, start=None, end=None) -> np.ndarray:
        real_power = self.get_real_power(start, end) 
        # Clip negative values to 0 (solar can't generate negative power)
        real_power = np.clip(real_power, 0, None)   
        return real_power