"""
File: pricing.py
Description: This module defines functions to determine time-of-use (TOU) periods, calculate energy prices based on TOU schedules, and compute total costs for grid import considering both energy charges and demand charges.
"""
import pandas as pd
import numpy as np
from src.data_formatting.formatting import is_business_day
from src.config.pricing_config import *

#returns off-peak, mid_peak, or on-peak based on timestamp and schedule
def get_tou_period(timestamp: pd.Timestamp) -> str:
    hour = timestamp.hour
    month = timestamp.month
    is_summer = month in SUMMER_MONTHS
    is_weekend = not is_business_day(timestamp)

    #creates schedule based on month, season, and day type
    if is_weekend:
        schedule = TOU_WEEKEND_SUMMER if is_summer else TOU_WEEKEND_WINTER
    else:
        # Check for March/April special case
        if month in [3, 4] and not is_summer:
            schedule = TOU_WEEKDAY_WINTER_MARCH_APRIL
        else:
            schedule = TOU_WEEKDAY_SUMMER if is_summer else TOU_WEEKDAY_WINTER
    
    for period, time_ranges in schedule.items():
        for start_hour, end_hour in time_ranges:
            if start_hour <= hour < end_hour:
                return period
    
    return 'off_peak'
    
#returns energy price based on timestamp and schedule
def get_energy_price(timestamp: pd.Timestamp) -> float:
    period = get_tou_period(timestamp)
    return ENERGY_RATES[period]

#returns array of energy prices for given timestamps
def get_price_array(timestamps: np.ndarray) -> np.ndarray:
    #convert to pd.Timestamp since functions use pd.Timestamp
    timestamps_pd = [pd.Timestamp(ts, unit='s') for ts in timestamps]
    prices = [get_energy_price(ts) for ts in timestamps_pd]
    return np.array(prices)

#calculates total cost based on grid import, timestamps, and whether to include demand charges
def calculate_total_cost(grid_import: np.ndarray, timestamps: np.ndarray, 
                         include_demand_charges: bool = True,
                         simulation_days: int = 1) -> dict:
    energy_prices = get_price_array(timestamps)
    energy_charges = np.sum(energy_prices * grid_import)
    
    total_cost = energy_charges
    demand_charge_total = 0.0
    max_demand = 0.0
    on_peak_demand = 0.0

    # Demand charges are a monthly billing concept — only apply for full month simulations
    apply_demand_charges = include_demand_charges and simulation_days >= 28

    if apply_demand_charges and len(grid_import) > 0:
        max_demand = np.max(grid_import)
        max_demand_charge = max_demand * DEMAND_CHARGES['maximum_demand']

        timestamps_pd = [pd.Timestamp(ts, unit='s') for ts in timestamps]
        on_peak_mask = np.array([get_tou_period(ts) == 'on_peak' for ts in timestamps_pd])

        if np.any(on_peak_mask):
            on_peak_demand = np.max(grid_import[on_peak_mask])
            on_peak_demand_charge = on_peak_demand * DEMAND_CHARGES['on_peak_demand']
        else:
            on_peak_demand_charge = 0.0

        demand_charge_total = max_demand_charge + on_peak_demand_charge
        total_cost += demand_charge_total

    return {
        'total_cost': total_cost,
        'energy_charges': energy_charges,
        'demand_charges': demand_charge_total,
        'max_demand': max_demand,
        'on_peak_demand': on_peak_demand,
        'demand_charges_applied': apply_demand_charges 
    }