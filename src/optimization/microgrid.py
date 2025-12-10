from typing import List, Optional
import pandas as pd
import numpy as np
from src.models.building_load import BuildingLoad
from src.models.pv_generator import PVGenerator
from src.models.battery_storage import BatteryStorage
from src.optimization.optimizer import MicrogridOptimizer


class Microgrid:
    #optional parameters with names of loads, pv_generators, and batteries
    def __init__ (self, loads: List[str], pv_generators:Optional[List[str]] = None, batteries:Optional[List[str]] = None):
        #create lists with loads, pv_generators, and batteries objects 
        self.loads = []
        self.pv_generators = []
        self.batteries = []
        if loads:
            for load in loads:
                self.loads.append(BuildingLoad(load))
        if pv_generators:
            for pv_generator in pv_generators:
                self.pv_generators.append(PVGenerator(pv_generator))
        if batteries:
            for battery in batteries:
                self.batteries.append(BatteryStorage(battery))

        #need to have loads in the microgrid
        if not self.loads:
            raise ValueError("Microgrid must have at least one load asset.")

    def get_total_load(self, start=None, end=None) -> Optional[np.ndarray]:
        total_load = None
        
        for asset in self.loads:
            profile = asset.get_load_profile(start, end)

            # Convert Series → ndarray, leave ndarray unchanged
            if hasattr(profile, "to_numpy"):
                profile = profile.to_numpy()
            else:
                profile = np.asarray(profile)

            if total_load is None:
                total_load = profile.copy()
            else:
                total_load += profile

        return total_load


    def get_total_pv_generation(self, start=None, end=None) -> Optional[np.ndarray]:
        total_gen = None
        
        for asset in self.pv_generators:
            profile = asset.get_generation_profile(start, end)

            if hasattr(profile, "to_numpy"):
                profile = profile.to_numpy()
            else:
                profile = np.asarray(profile)

            if total_gen is None:
                total_gen = profile.copy()
            else:
                total_gen += profile

        return total_gen

    
    def get_total_battery_storage(self):
        total_kw = 0
        total_kwh = 0
        for asset in self.batteries:
            total_kw += asset.rating_kw
            total_kwh += asset.rating_kwh
        return total_kw, total_kwh
    
    def get_timestamps(self, start=None, end=None):
        # Create hourly timestamps from start to end
        timestamps = pd.date_range(start=start, end=end, freq='H')

        # Convert to Unix epoch seconds
        return (timestamps.astype(np.int64) // 10**9).to_numpy()
    
    def  optimize(self, start_date, end_date, objective_type='cost', round_trip_efficiency=0.95, include_soc_penalty=True, soc_min=0.20, soc_max=0.80, soc_penalty_weight=None, solver=None, verbose=False):
        optimizer = MicrogridOptimizer(
            load=self.get_total_load(start_date, end_date),
            pv_generation=self.get_total_pv_generation(start_date, end_date),
            timestamps=self.get_timestamps(start_date, end_date),
            battery_rating_kw=self.get_total_battery_storage()[0],
            battery_capacity_kwh=self.get_total_battery_storage()[1],
            round_trip_efficiency=round_trip_efficiency,
            include_soc_penalty=include_soc_penalty,
            min_soc=soc_min,
            max_soc=soc_max
        )
        return optimizer.optimize(
            objective_type=objective_type,
            include_soc_penalty=include_soc_penalty,
            soc_min=soc_min,
            soc_max=soc_max,
            soc_penalty_weight=soc_penalty_weight,
            solver=solver,
            verbose=verbose
        )
        
        
        


