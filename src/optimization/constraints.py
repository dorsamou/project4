"""
File: constraints.py
Description: This module defines functions to create constraints for the microgrid optimization problem, including power balance, battery power limits, SOC limits, battery dynamics, initial SOC, energy balance, and non-negativity of grid import. The main function `create_microgrid_constraints` aggregates all these constraints into a single list for use in the optimization problem.
"""
import cvxpy as cp
import numpy as np


def power_balance(grid_import: cp.Variable, battery_power: cp.Variable, load: np.ndarray, pv_generation: np.ndarray) -> list:
    return [grid_import + battery_power + pv_generation == load]

def battery_power_kw(battery_power: cp.Variable, battery_rating: float) -> list:
    return [battery_power <= battery_rating, battery_power >= -battery_rating]

def battery_soc_kwh(SOC: cp.Variable, battery_capacity: float) -> list:
    #hard limits on SOC 
    return [SOC >= 0, SOC <= battery_capacity]

def battery_dynamics(SOC: cp.Variable, battery_power: cp.Variable, round_trip_efficiency: float = 1) -> list:
    return [SOC[1:] == (SOC[:-1] + battery_power * round_trip_efficiency)]

def battery_initial_soc(SOC: cp.Variable, battery_capacity: float) -> list:
    return [SOC[0] == battery_capacity * 0.5]  # Initial SOC at 50% of capacity

def battery_energy_balance(SOC: cp.Variable) -> list:
    return [SOC[-1] == SOC[0]]  # End SOC equals initial SOC

def grid_import_nonnegative(grid_import: cp.Variable) -> list:
    return [grid_import >= 0]


def create_microgrid_constraints(grid_import: cp.Variable, battery_power: cp.Variable, SOC: cp.Variable, load: np.ndarray, pv_generation: np.ndarray,
                                battery_rating_kw: float, battery_capacity_kwh: float, round_trip_efficiency: float = 1)->list:
    constraints = []
    constraints += power_balance(grid_import, battery_power, load, pv_generation)
    constraints += battery_power_kw(battery_power, battery_rating_kw)
    constraints += battery_soc_kwh(SOC, battery_capacity_kwh)
    constraints += battery_dynamics(SOC, battery_power, round_trip_efficiency)
    constraints += battery_initial_soc(SOC, battery_capacity_kwh)
    constraints += battery_energy_balance(SOC)
    constraints += grid_import_nonnegative(grid_import)

    
    return constraints