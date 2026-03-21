"""
File: objectives.py
Description: This module defines the objective functions for the optimization problem, including cost minimization and emissions minimization. 
It also includes a penalty function to encourage maintaining the battery's state of charge (SOC) within a specified range.
"""

import cvxpy as cp
import numpy as np
from src.config.pricing_config import DEMAND_CHARGES


def soc_penalty(SOC: cp.Variable, battery_capacity_kwh: float, soc_min: float = 0.20, soc_max: float = 0.80, penalty_weight: float = 10.0) -> cp.Expression:
    soc_min_kwh = soc_min * battery_capacity_kwh
    soc_max_kwh = soc_max * battery_capacity_kwh
    # Penalty for going below 20% , adds to objective that is being minimizing
    below_min = cp.sum(cp.pos(soc_min_kwh - SOC))
    # Penalty for going above 80%
    above_max = cp.sum(cp.pos(SOC - soc_max_kwh))
    return penalty_weight * (below_min + above_max)


#returns the cost functions to be minimized for cost 
def minimize_total_cost(grid_import: cp.Variable, energy_prices: np.ndarray, on_peak_hours: np.ndarray = None, include_soc_penalty: bool = True, SOC: cp.Variable = None, 
                        battery_capacity_kwh: float = None, soc_min: float = 0.20, soc_max: float = 0.80, soc_penalty_weight: float = 10.0 ) -> cp.Expression:
    energy_cost = cp.sum(cp.multiply(energy_prices, grid_import))
    max_demand_cost = cp.max(grid_import) * DEMAND_CHARGES['maximum_demand']
    
    if on_peak_hours is not None and np.any(on_peak_hours):
        on_peak_demand_cost = cp.max(cp.multiply(on_peak_hours, grid_import)) * DEMAND_CHARGES['on_peak_demand']
    else:
        on_peak_demand_cost = 0
    
    total_cost = energy_cost + max_demand_cost + on_peak_demand_cost
    
    if include_soc_penalty and SOC is not None and battery_capacity_kwh is not None:
        total_cost += soc_penalty(SOC, battery_capacity_kwh, soc_min, soc_max, soc_penalty_weight)
    
    return total_cost

#returns the cost functions to be minimized for emissions
def minimize_emissions(grid_import: cp.Variable, carbon_intensity: np.ndarray, SOC: cp.Variable = None, include_soc_penalty: bool = True, battery_capacity_kwh: float = None,
                      soc_min: float = 0.20, soc_max: float = 0.80, soc_penalty_weight: float = 10.0) -> cp.Expression:
    energy_mj = grid_import * 3.6
    emissions = cp.sum(cp.multiply(carbon_intensity, energy_mj))
    
    # Add SOC penalty if requested (converted to emission units)
    if include_soc_penalty and SOC is not None and battery_capacity_kwh is not None:
        emissions += soc_penalty(SOC, battery_capacity_kwh, soc_min, soc_max, soc_penalty_weight)
    
    return emissions

def weighted_objective(
    grid_import: cp.Variable,
    energy_prices: np.ndarray,
    carbon_intensity: np.ndarray,
    cost_weight: float = 0.5,                  # weight on cost
    emissions_weight: float = 0.5,                   # weight on emissions
    on_peak_hours: np.ndarray = None,
    SOC: cp.Variable = None,
    battery_capacity_kwh: float = None,
    include_soc_penalty: bool = True,
    soc_min: float = 0.20,
    soc_max: float = 0.80,
    soc_penalty_weight: float = 10.0,
) -> cp.Expression:
    cost_expr = minimize_total_cost(
        grid_import, energy_prices, on_peak_hours,
        include_soc_penalty=False,       # add penalty once at the end
        SOC=None, battery_capacity_kwh=None
    )
    emissions_expr = minimize_emissions(
        grid_import, carbon_intensity,
        include_soc_penalty=False,
        SOC=None, battery_capacity_kwh=None
    )
    objective = cost_weight * cost_expr + emissions_weight * emissions_expr

    if include_soc_penalty and SOC is not None and battery_capacity_kwh is not None:
        objective += soc_penalty(SOC, battery_capacity_kwh, soc_min, soc_max, soc_penalty_weight)

    return objective
