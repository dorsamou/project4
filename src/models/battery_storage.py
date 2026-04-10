"""
File: battery_storage.py

Description: This file defines the BatteryStorage class, which represents a battery storage asset in the energy system.
It includes specific attributes for battery storage, such as rating in kW and kWh.
"""

from src.models.abstract_asset import Asset
from src.config.data_config  import DATASETS

"""
BatteryStorage class represents a battery storage asset in the energy system
Inherits from the Asset class and includes specific attributes for battery storage, such as rating in kW and kWh.
Parameters:
- rating_kw: The power rating of the battery storage in kilowatts (kW).
- rating_kwh: The energy capacity of the battery storage in kilowatt-hours (kWh).
"""
class BatteryStorage(Asset):
    def __init__(self, name):
        self.rating_kw = DATASETS[name]['rating_kw']
        self.rating_kwh = DATASETS[name]['rating_kwh']
        super().__init__(name)