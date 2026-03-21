import numpy as np
import pandas as pd
from src.config.carbon_config import *

#returns quarter of the year based on month in timestamp
def get_quarter(timestamp: pd.Timestamp) -> str:
    month = timestamp.month
    for quarter, months in QUARTER_MONTHS.items():
        if month in months:
            return quarter
    return 'Q1'

#returns carbon intensity based on timestamp and schedule
def get_carbon_intensity(timestamp: pd.Timestamp) -> float:
    quarter = get_quarter(timestamp)
    hour = timestamp.hour
    return CARBON_INTENSITY_BY_QUARTER[quarter].get(hour, 75.0)

#returns array of carbon intensity values for given timestamps
def get_carbon_intensity_array(timestamps: np.ndarray) -> np.ndarray:
    timestamps_pd = [pd.Timestamp(ts) for ts in timestamps]
    carbon_values = [get_carbon_intensity(ts) for ts in timestamps_pd]
    return np.array(carbon_values)

#calculates total emissions based on grid import and timestamps
def calculate_total_emissions(grid_import: np.ndarray, timestamps: np.ndarray) -> float:
    #used for after optimization to analyze emissions
    carbon_intensity = get_carbon_intensity_array(timestamps)
    
    #carbon intensity is in gCO2e/MJ, grid_import is in kW
    # Convert kW to MJ: kW * 1 hour * 3600 seconds/hour / 1000 = MJ
    energy_mj = grid_import * 3.6
    emissions_gco2 = carbon_intensity * energy_mj
    # total emissions in gCO2e
    return np.sum(emissions_gco2)

