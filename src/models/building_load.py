"""
File: building_load.py

Description: This file defines the BuildingLoad class, which represents a building load asset in the energy system.
It includes specific attributes for building load, such as cal_real and cal_reactive for spike detection.
"""

import numpy as np
from src.models.abstract_asset import Asset
from src.config.data_config  import DATASETS


"""
BuildingLoad class represents a building load asset in the energy system
Inherits from the Asset class and includes specific attributes for building load, such as cal_real and cal_reactive for spike detection.
Parameters:
- cal_real: A calibration factor for real power used in spike detection.
- cal_reactive: A calibration factor for reactive power used in spike detection.
"""
class BuildingLoad(Asset):
    def __init__(self, name):
        self.cal_real = DATASETS[name]['cal_real']
        self.cal_reactive = DATASETS[name]['cal_reactive']
        super().__init__(name)
    def get_load_profile(self, start=None, end=None) -> np.ndarray:
        real_power = self.get_real_power(start, end)
        return real_power