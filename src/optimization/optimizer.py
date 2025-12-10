import cvxpy as cp
import numpy as np
import pandas as pd

from src.optimization.pricing import get_price_array, get_tou_period, calculate_total_cost
from src.optimization.carbon_intensity import get_carbon_intensity_array, calculate_total_emissions
from src.optimization.constraints import create_microgrid_constraints
from src.optimization.objectives import minimize_total_cost, minimize_emissions

class MicrogridOptimizer:
    def __init__(self, load: np.ndarray, pv_generation: np.ndarray, timestamps: np.ndarray, battery_rating_kw: float, battery_capacity_kwh: float, round_trip_efficiency: float = 1.0, include_soc_penalty: bool = True, min_soc: float = 0.20, max_soc: float = 0.80):
        self.load = load
        self.pv_generation = pv_generation
        self.timestamps = timestamps
        self.T = len(load) #number of timestamps
        
        # Battery parameters
        self.battery_rating_kw = battery_rating_kw
        self.battery_capacity_kwh = battery_capacity_kwh
        self.round_trip_efficiency = round_trip_efficiency
        self.include_soc_penalty = include_soc_penalty
        self.min_soc = min_soc
        self.max_soc = max_soc
        
        self.energy_prices = get_price_array(timestamps)
        self.carbon_intensity = get_carbon_intensity_array(timestamps)
        timestamps_pd = [pd.Timestamp(ts) for ts in timestamps]
        self.on_peak_hours = np.array([get_tou_period(ts) == 'on_peak' 
                                       for ts in timestamps_pd], dtype=float)
        
        # declare optimization variables
        self.grid_import = None
        self.battery_power = None
        self.soc = None
        self.problem = None
        self.objective = None
    
    def setup_problem(self, objective_type: str = 'cost', include_soc_penalty: bool = True, soc_min: float = 0.20, soc_max: float = 0.80, soc_penalty_weight: float = None) -> None:
        # Create decision variables
        self.grid_import = cp.Variable(self.T, name="grid_import")
        self.battery_power = cp.Variable(self.T, name="battery_power")
        self.soc = cp.Variable(self.T + 1, name="soc")
        
        # Create constraints
        constraint_list = create_microgrid_constraints(self.grid_import, self.battery_power, self.soc, self.load, self.pv_generation, self.battery_rating_kw, self.battery_capacity_kwh, self.round_trip_efficiency)
        
        # Set default penalty weights if not provided
        if soc_penalty_weight is None:
            if objective_type == 'emissions':
                soc_penalty_weight = 1000.0
            else:
                soc_penalty_weight = 10.0
        
        if objective_type == 'cost':
            self.objective = minimize_total_cost(self.grid_import, self.energy_prices, self.on_peak_hours, self.include_soc_penalty, self.soc, self.battery_capacity_kwh, soc_min, soc_max, soc_penalty_weight)
        elif objective_type == 'emissions':
            self.objective = minimize_emissions(self.grid_import, self.carbon_intensity, self.soc, self.include_soc_penalty, self.battery_capacity_kwh, soc_min, soc_max, soc_penalty_weight)
        else:
            raise ValueError(f"Unknown objective type: {objective_type}")
        
        # Create problem
        self.problem = cp.Problem(cp.Minimize(self.objective), constraint_list)

    def solve(self, solver: str = cp.ECOS, verbose: bool = False) -> dict:
        self.problem.solve(solver=solver, verbose=verbose)
        
        # Check status
        if self.problem.status not in ['optimal', 'optimal_inaccurate']:
            print(f"Warning: Optimization status is {self.problem.status}")
        
        grid_import_result = self.grid_import.value
        battery_power_result = self.battery_power.value
        soc_result = self.soc.value
        
        cost_breakdown = calculate_total_cost(grid_import_result, self.timestamps)
        total_emissions_gco2 = calculate_total_emissions(grid_import_result, self.timestamps)
        
        results = {
            'status': self.problem.status,
            'optimal_value': self.problem.value,
            'grid_import': grid_import_result,
            'battery_power': battery_power_result,
            'soc': soc_result,
            'cost_breakdown': cost_breakdown,
            'total_emissions_gco2': total_emissions_gco2,
            'timestamps': self.timestamps
        }
        
        return results
    
    def optimize(self, objective_type: str = 'cost', solver: str = cp.ECOS, verbose: bool = False, include_soc_penalty: bool = True, soc_min: float = 0.20, soc_max: float = 0.80, soc_penalty_weight: float = None) -> dict:
        self.setup_problem(objective_type, include_soc_penalty, soc_min, soc_max, soc_penalty_weight)
        return self.solve(solver=solver, verbose=verbose)