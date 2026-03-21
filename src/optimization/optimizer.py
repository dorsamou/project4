"""
File: optimizer.py
Description: This module defines the MicrogridOptimizer class, which defines the optimization problem for a microgrid, including decision variables, constraints, and objective function. 
It provides methods to set up and solve the optimization problem, returning results such as grid import, battery power, SOC, cost breakdown, and emissions.
"""
import cvxpy as cp
import numpy as np
import pandas as pd

from src.optimization.pricing import get_price_array, get_tou_period, calculate_total_cost
from src.optimization.carbon_intensity import get_carbon_intensity_array, calculate_total_emissions
from src.optimization.constraints import create_microgrid_constraints
from src.optimization.objectives import minimize_total_cost, minimize_emissions, weighted_objective

"""
MicrogridOptimizer class encapsulates the optimization problem for a microgrid, including decision variables, constraints, and objective function

Parameters:
- load: np.ndarray of load values (kW) for each timestamp
- pv_generation: np.ndarray of PV generation values (kW) for each timestamp (can be None or zeros if no PV)
- timestamps: np.ndarray of timestamps corresponding to load and PV generation
- battery_rating_kw: Maximum charge/discharge power of the battery (kW)
- battery_capacity_kwh: Energy capacity of the battery (kWh)
- round_trip_efficiency: Round-trip efficiency of the battery (0 to 1)
- include_soc_penalty: Whether to include a penalty in the objective for SOC outside preferred range
- min_soc: Minimum preferred SOC (as fraction of capacity, e.g. 0.20 for 20%)
- max_soc: Maximum preferred SOC (as fraction of capacity, e.g. 0.80 for 80%)

Methods:
- setup_problem(objective_type, include_soc_penalty, soc_min, soc_max, soc_penalty_weight): Set up the optimization problem with decision variables, constraints, and objective function.
- solve(solver, verbose): Solve the optimization problem and return results.
- optimize(objective_type, solver, verbose, include_soc_penalty, soc_min, soc_max, soc_penalty_weight): Complete optimization workflow: set up the problem and solve it, returning results.
"""
class MicrogridOptimizer:
    def __init__(self, load: np.ndarray, pv_generation: np.ndarray, timestamps: np.ndarray, 
                 battery_rating_kw: float, battery_capacity_kwh: float, 
                 round_trip_efficiency: float = 1.0, include_soc_penalty: bool = True, 
                 min_soc: float = 0.20, max_soc: float = 0.80):
        
        # Validate inputs
        if len(load) != len(timestamps):
            raise ValueError(f"Load length ({len(load)}) must match timestamps length ({len(timestamps)})")
        
        if pv_generation is not None and len(pv_generation) != len(load):
            raise ValueError(f"PV generation length ({len(pv_generation)}) must match load length ({len(load)})")
        
        # Handle None PV generation
        if pv_generation is None:
            pv_generation = np.zeros_like(load)
        
        self.load = np.asarray(load, dtype=float)
        self.pv_generation = np.asarray(pv_generation, dtype=float)
        self.timestamps = np.asarray(timestamps)
        self.T = len(load)  # number of timestamps
        
        # Battery parameters
        self.battery_rating_kw = float(battery_rating_kw)
        self.battery_capacity_kwh = float(battery_capacity_kwh)
        self.round_trip_efficiency = float(round_trip_efficiency)
        self.include_soc_penalty = include_soc_penalty
        self.min_soc = float(min_soc)
        self.max_soc = float(max_soc)
        
        # Get pricing and carbon intensity
        self.energy_prices = get_price_array(timestamps)
        self.carbon_intensity = get_carbon_intensity_array(timestamps)
        
        # Get on-peak hours indicator
        timestamps_pd = [pd.Timestamp(ts) for ts in timestamps]
        self.on_peak_hours = np.array([get_tou_period(ts) == 'on_peak' 
                                       for ts in timestamps_pd], dtype=float)
        
        # Declare optimization variables (initialized in setup_problem)
        self.grid_import = None
        self.battery_power = None
        self.soc = None
        self.problem = None
        self.objective = None
    
    def setup_problem(self, objective_type: str = 'cost', include_soc_penalty: bool = True, 
                     soc_min: float = 0.20, soc_max: float = 0.80, 
                     soc_penalty_weight: float = None, cost_weight: float = 0.5, emissions_weight: float = 0.5) -> None:
        # Create decision variables
        self.grid_import = cp.Variable(self.T, name="grid_import")
        self.battery_power = cp.Variable(self.T, name="battery_power")
        self.soc = cp.Variable(self.T + 1, name="soc")  # T+1 for initial and final SOC
        
        # Create constraints
        try:
            constraint_list = create_microgrid_constraints(
                self.grid_import, 
                self.battery_power, 
                self.soc, 
                self.load, 
                self.pv_generation, 
                self.battery_rating_kw, 
                self.battery_capacity_kwh, 
                self.round_trip_efficiency
            )
            
            # Verify all constraints are in a list
            if not isinstance(constraint_list, list):
                raise TypeError(f"Constraints must be a list, got {type(constraint_list)}")
            
            # Check each constraint
            for i, constraint in enumerate(constraint_list):
                if not isinstance(constraint, (cp.constraints.constraint.Constraint, 
                                              cp.constraints.zero.Equality,
                                              cp.constraints.zero.Zero,
                                              cp.constraints.nonpos.Inequality,
                                              cp.constraints.nonpos.NonPos)):
                    raise TypeError(f"Constraint {i} is not a valid CVXPY constraint: {type(constraint)}")
            
        except Exception as e:
            raise ValueError(f"Error creating constraints: {str(e)}")
        
        # Set default penalty weights if not provided
        if soc_penalty_weight is None:
            if objective_type == 'emissions':
                soc_penalty_weight = 1000.0
            else:
                soc_penalty_weight = 10.0
        
        # Create objective function
        try:
            if objective_type == 'cost':
                self.objective = minimize_total_cost(
                    self.grid_import, 
                    self.energy_prices, 
                    self.on_peak_hours, 
                    include_soc_penalty, 
                    self.soc, 
                    self.battery_capacity_kwh, 
                    soc_min, 
                    soc_max, 
                    soc_penalty_weight
                )
            elif objective_type == 'emissions':
                self.objective = minimize_emissions(
                    self.grid_import, 
                    self.carbon_intensity, 
                    self.soc, 
                    include_soc_penalty, 
                    self.battery_capacity_kwh, 
                    soc_min, 
                    soc_max, 
                    soc_penalty_weight
                )
            elif objective_type == 'weighted':
                self.objective = weighted_objective(
                    self.grid_import,
                    self.energy_prices,
                    self.carbon_intensity,
                    cost_weight =cost_weight,
                    emissions_weight = emissions_weight,
                    on_peak_hours=self.on_peak_hours,
                    SOC=self.soc,
                    battery_capacity_kwh=self.battery_capacity_kwh,
                    include_soc_penalty=include_soc_penalty,
                    soc_min=soc_min,
                    soc_max=soc_max,
                    soc_penalty_weight=soc_penalty_weight
                )
            else:
                raise ValueError(f"Unknown objective type: {objective_type}. Must be 'cost', 'emissions', or 'weighted'")
        except Exception as e:
            raise ValueError(f"Error creating objective: {str(e)}")
        
        # Create problem
        try:
            self.problem = cp.Problem(cp.Minimize(self.objective), constraint_list)
        except Exception as e:
            raise ValueError(f"Error creating optimization problem: {str(e)}")

    def solve(self, solver: str = cp.ECOS, verbose: bool = False) -> dict:
        # Solve the problem
        try:
            self.problem.solve(solver=solver, verbose=verbose)
        except Exception as e:
            raise RuntimeError(f"Solver failed: {str(e)}")
        
        # Check status
        if self.problem.status not in ['optimal', 'optimal_inaccurate']:
            raise RuntimeError(f"Optimization failed with status: {self.problem.status}")
        
        # Extract results
        grid_import_result = self.grid_import.value
        battery_power_result = self.battery_power.value
        soc_result = self.soc.value
        
        # Validate results
        if grid_import_result is None:
            raise RuntimeError("Optimization produced no solution for grid_import")
        if battery_power_result is None:
            raise RuntimeError("Optimization produced no solution for battery_power")
        if soc_result is None:
            raise RuntimeError("Optimization produced no solution for soc")
        
        # Calculate cost breakdown
        cost_breakdown = calculate_total_cost(grid_import_result, self.timestamps)
        
        # Calculate total emissions
        total_emissions_gco2 = calculate_total_emissions(grid_import_result, self.timestamps)
        
        # Package results
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
    
    def optimize(self, objective_type: str = 'cost', solver: str = cp.ECOS, 
                verbose: bool = False, include_soc_penalty: bool = True, 
                soc_min: float = 0.20, soc_max: float = 0.80, 
                soc_penalty_weight: float = None,
                cost_weight: float = 0.5, emissions_weight:float = 0.5) -> dict:
        self.setup_problem(objective_type, include_soc_penalty, soc_min, soc_max, soc_penalty_weight, cost_weight, emissions_weight)
        return self.solve(solver=solver, verbose=verbose)