"""
File: microgrid.py

Description: This file defines the microgrid class which is used in optimization to represent a microgrid with 
loads, PV generators, and battery storage modeled by BuildingLoad, PVGenerator, and BatteryStorage classes.
"""

from typing import List, Optional
import pandas as pd
import numpy as np
from src.models.building_load import BuildingLoad
from src.models.pv_generator import PVGenerator
from src.models.battery_storage import BatteryStorage
from src.optimization.optimizer import MicrogridOptimizer


"""
Microgrid class represents a microgrid with loads, PV generators, and battery storage. It provides methods to
aggregate load and generation profiles, calculate total battery capacity, and run optimization.

Parameters:
- loads: List of load asset identifiers (e.g., building names)
- pv_generators: Optional list of PV generator asset identifiers
- batteries: Optional list of battery storage asset identifiers
Methods:
- get_total_load(start, end): Get aggregated load profile across all load assets for the specified time range.
- get_total_pv_generation(start, end): Get aggregated PV generation profile across all PV assets for the specified time range.
- get_total_battery_storage(): Get total battery power and energy capacity.
- get_timestamps(start, end): Create hourly timestamps from start to end (inclusive of start, exclusive of end).
- optimize(start_date, end_date, objective_type, round_trip_efficiency, include_soc_penalty, soc_min, soc_max, soc_penalty_weight, solver, verbose): Run optimization for the microgrid with specified parameters.
"""
class Microgrid: 
    def __init__(self, loads: List[str], pv_generators: Optional[List[str]] = None, 
                 batteries: Optional[List[str]] = None):
        # Create lists with loads, pv_generators, and batteries objects 
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

        # Need to have loads in the microgrid
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
        if not self.pv_generators:
            return None
            
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
    
    def get_timestamps(self, start=None, end=None) -> np.ndarray:
        # Create hourly timestamps from start to end (exclusive)
        # The 'H' frequency creates hourly timestamps at the start of each hour
        timestamps = pd.date_range(start=start, end=end, freq='h', inclusive='left')
        
        # Convert to Unix epoch seconds
        return (timestamps.astype(np.int64) // 10**9).to_numpy()
    
    def optimize(self, start_date, end_date, objective_type='cost', 
                round_trip_efficiency=0.95, include_soc_penalty=True, 
                soc_min=0.20, soc_max=0.80, soc_penalty_weight=None, 
                cost_weight=0.5, emissions_weight=0.5,
                solver=None, verbose=False) -> dict:
        # Get data
        load = self.get_total_load(start_date, end_date)
        pv_gen = self.get_total_pv_generation(start_date, end_date)
        timestamps = self.get_timestamps(start_date, end_date)
        battery_kw, battery_kwh = self.get_total_battery_storage()
        
        # Debug: print shapes of the data arrays to verify they are consistent
        print(f"Debug: Load shape: {load.shape}, PV shape: {pv_gen.shape if pv_gen is not None else 'None'}, Timestamps shape: {timestamps.shape}")
        
        # Validate dimensions match
        if len(load) != len(timestamps):
            raise ValueError(
                f"Data dimension mismatch: Load has {len(load)} values but "
                f"timestamps has {len(timestamps)} values. "
                f"Date range: {start_date} to {end_date}"
            )
        
        # Create optimizer
        optimizer = MicrogridOptimizer(
            load=load,
            pv_generation=pv_gen,
            timestamps=timestamps,
            battery_rating_kw=battery_kw,
            battery_capacity_kwh=battery_kwh,
            round_trip_efficiency=round_trip_efficiency,
            include_soc_penalty=include_soc_penalty,
            min_soc=soc_min,
            max_soc=soc_max
        )
        
        # Run optimization
        return optimizer.optimize(
            objective_type=objective_type,
            include_soc_penalty=include_soc_penalty,
            soc_min=soc_min,
            soc_max=soc_max,
            soc_penalty_weight=soc_penalty_weight,
            solver=solver,
            verbose=verbose,
            cost_weight=cost_weight,
            emissions_weight=emissions_weight
        )