from typing import List, Optional
from src.models.building_load import BuildingLoad
from src.models.pv_generator import PVGenerator
from src.models.battery_storage import BatteryStorage


class Microgrid:
    #optional parameters with names of loads, pv_generators, and batteries
    def __init__ (self, loads: List[str], pv_generators:Optional[List[str]] = None, batteries:Optional[List[str]] = None):
        #create lists with loads, pv_generators, and batteries objects 
        self.load_assets = []
        self.pv_generator_assets = []
        self.battery_assets = []
        if loads:
            for load in loads:
                self.load_assets.append(BuildingLoad(load))
        if pv_generators:
            for pv_generator in pv_generators:
                self.pv_generator_assets.append(PVGenerator(pv_generator))
        if batteries:
            for battery in batteries:
                self.battery_assets.append(BatteryStorage(battery))

        #need to have loads in the microgrid
        if not self.load_assets:
            raise ValueError("Microgrid must have at least one load asset.")
    
    def get_total_load(self, start=None, end=None):
        total_load = None
        for asset in self.load_assets:
            if total_load is None:
                total_load = asset.get_load_profile(start, end)
            else: 
                total_load += asset.get_load_profile(start, end)
        return total_load
    
    def get_total_pv_generation(self, start=None, end=None):
        total_generation = None
        for asset in self.pv_generator_assets:
            if total_generation is None:
                total_generation = asset.get_generation_profile(start, end)
            else: 
                total_generation += asset.get_generation_profile(start, end)
        return total_generation
    
    def get_total_battery_storage(self):
        total_kw = 0
        total_kwh = 0
        for asset in self.battery_assets:
            total_kw += asset.rating_kw
            total_kwh += asset.rating_kwh
        return total_kw, total_kwh