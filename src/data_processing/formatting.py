"""
File: formatting.py
Author: adapted from @author: Sushil Silwal, ssilwal@ucsd.edu
Description: This module contains functions for formatting and cleaning datasets.
"""

import os
import pandas as pd
import numpy as np
from scipy.ndimage import gaussian_filter1d
import datetime
from typing import Optional
import holidays

#PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
#does not work in jupyter notebooks 
CURRENT_DIR = os.getcwd()
BASE_DIR = os.path.dirname(CURRENT_DIR)
RAW_DIR = BASE_DIR + "/data/raw"
FORMATTED_DIR = BASE_DIR + "/data/formatted"
#make formatted directory if it does not exist already
os.makedirs(FORMATTED_DIR, exist_ok=True)

#creates object containing US holidays with years that span the data range January 1, 2015 to February 29, 2020
US_HOLIDAYS = holidays.US(years=range(2015, 2020))


#Helper functions
# returns True if the given timestamp is a US business day (not a weekend or holiday)
def is_business_day(timestamp: pd.Timestamp) -> bool:
    day = timestamp.date()
    # Monday = 0 - Sunday = 6
    return (timestamp.weekday() < 5) and (day not in US_HOLIDAYS)

#returns the index to replace missing data with 
#passes in the current index and the full timestamps series from the dataframe
def replace_with(index: int, timestamps: pd.Series) -> int:
    #first timestamp - not enough historical data to replace missing value
    if index <= 0:
        return 0
    
    #first day - use previous time stamp to replace missing value for the first day (96 intervals since 15-min intervals)
    elif index < 96:
        return index - 1
    
    #first week - use same time stamp from previous day to replace missing value for the first week
    elif index < 96 * 7:
        return index - 96
    
    #beyond first week - replace missing value with same time stamp from a similar day(weekday, holiday, weekend)
    else :
        cur_ts = timestamps.iloc[index]
        n = 1
        while True:
            candidate_idx = index - 96 * n
            if candidate_idx < 0:
                return index - 1
            prev_ts = timestamps.iloc[candidate_idx]
            if is_business_day(cur_ts) == is_business_day(prev_ts):
                return candidate_idx
            n += 1


#fills in the missing timetsamps and fills values with NaN
def fill_missing_timestamps(df: pd.DataFrame, time_col: str = "DateTime", freq_min: int = 15) -> pd.DataFrame:
    df = df.copy()
    #converts time column to datetime format and drops rows with invalid datetime values
    df[time_col] = pd.to_datetime(df[time_col], errors="coerce")

    #sorts by time 
    df = df.dropna(subset=[time_col]).sort_values(time_col).reset_index(drop=True)

    #creates a complete datetime index from start to end with specified frequency
    start = df[time_col].iloc[0]
    end = df[time_col].iloc[-1]
    full_index = pd.date_range(start=start, end=end, freq=f"{freq_min}min")

    #reindexes the dataframe to include all timestamps, missing timestamps will have NaN values, also deals with duplicates by averaging
    df = df.groupby(time_col).mean().reindex(full_index).rename_axis(time_col).reset_index()

    return df


def save_formatted_df(df: pd.DataFrame, raw_filename: str, suffix: str = "_processed"):
    base = os.path.splitext(os.path.basename(raw_filename))[0]
    outname = f"{base}{suffix}.csv"
    outpath = os.path.join(FORMATTED_DIR, outname)
    df.to_csv(outpath, index=False)
    print(f"Saved formatted file → {outpath}")
    return outpath



class BaseFormatter:
    def __init__(self, raw_filename: str):
        self.raw_filename = raw_filename
        self.raw_path = os.path.join(RAW_DIR, raw_filename)
        if not os.path.exists(self.raw_path):
            raise FileNotFoundError(f"Raw file not found: {self.raw_path}")

    def load_raw(self) -> pd.DataFrame:
        return pd.read_csv(self.raw_path)
    
    def load_and_align(self, time_col="DateTime", freq_min: int = 15) -> pd.DataFrame:
        df = self.load_raw()

        df = fill_missing_timestamps(df, time_col=time_col, freq_min=freq_min)
        return df
    
    def aggregate_hourly_kW(self, df: pd.DataFrame) -> pd.DataFrame:
        #return the mean value for each hour as the values are in KW
        return df.resample('H').mean()


class BatteryStorageFormatter(BaseFormatter):
    def __init__(self, raw_filename: str, rating_kw: float, rating_kwh: Optional[float] = None):
        super().__init__(raw_filename)
        self.rating_kwh = rating_kwh
        self.rating_kw = rating_kw

    def run(self, save: bool = True) -> pd.DataFrame:
        df = self.load_and_align()
        #DateTime, RealPower
        if df.shape[1] < 2:
            raise ValueError("Battery file expected to contain DateRime and RealPower columns")
        power_col = df.columns[1]
        timestamps = df[df.columns[0]]

        # Fill missing values
        for i in range(len(df)):
            if pd.isna(df.at[i, power_col]):
                rep = replace_with(i, timestamps)
                df.at[i, power_col] = df.at[rep, power_col]

        # Enforce rating: replace over-limit values
        replaced = 0
        for i in range(len(df)):
            val = df.at[i, power_col]
            if pd.notna(val) and abs(val) > self.rating_kw:
                rep = replace_with(i, timestamps)
                df.at[i, power_col] = df.at[rep, power_col]
                replaced += 1

        #df = self.aggregate_hourly_kW(df)
        if save:
            save_formatted_df(df, self.raw_filename)
        return df

class BuildingLoadFormatter(BaseFormatter):
    def __init__(self, raw_filename: str, cal_real: float = 0.4, cal_reactive: float = 0.4):
        super().__init__(raw_filename)
        #calibration factors convert raw meter readings into real world kW/kVAR values
        self.cal_real = cal_real
        self.cal_reactive = cal_reactive

    def run(self, save: bool = True) -> pd.DataFrame:
        df = self.load_and_align(freq_min=15)
        # DateTime, RealPower, ReactivePower
        if df.shape[1] < 2:
            raise ValueError("Load file must have at least DateTime and one power column")

        timestamps = df[df.columns[0]]
        power_cols = df.columns[1:]
        n = len(df)

        for col in power_cols:
            for i in range(n):
                if pd.isna(df.at[i, col]):
                    rep = replace_with(i, timestamps)
                    df.at[i, col] = df.at[rep, col]

        df_smooth = df.copy()
        for col in power_cols:
            series = df[col].ffill().bfill().values.astype(float)
            df_smooth[col] = gaussian_filter1d(series, sigma=2)

        error_real = 0
        error_reactive = 0

        # Spike detection: use sliding 672-sample (~7 days * 96) window avg as original script did
        for j in range(n):
            for col in power_cols:
                # window average safe calc
                if j < n - 672:
                    window_vals = df_smooth[col].iloc[j:j+672]
                else:
                    start_idx = max(0, j-672)
                    window_vals = df[col].iloc[start_idx:j].astype(float) if j > 0 else pd.Series([0.0])
                window_avg = np.mean(np.abs(window_vals)) if len(window_vals) > 0 else 0.0
                if window_avg == 0:
                    window_avg = 1e-6
                # determine threshold: real vs reactive heuristics
                if ("Real" in col) or ("real" in col.lower()) or (len(power_cols) == 1):
                    thresh = self.cal_real * window_avg
                else:
                    thresh = self.cal_reactive * window_avg

                if abs(df.at[j, col] - df_smooth.at[j, col]) > thresh:
                    rep = replace_with(j, timestamps)
                    df.at[j, col] = df.at[rep, col]
                    if ("Real" in col) or ("real" in col.lower()) or (len(power_cols) == 1):
                        error_real += 1
                    else:
                        error_reactive += 1
        #df = self.aggregate_hourly_kW(df)

        if save:
            save_formatted_df(df, self.raw_filename)
        return df

class PVGeneratorFormatter(BaseFormatter):
    #DateTime, RealPower
    def __init__(self, raw_filename: str):
        super().__init__(raw_filename)

    def run(self, save: bool = True) -> pd.DataFrame:
        df = self.load_and_align()
        if df.shape[1] < 2: #should return 2 columns (1, 2)
            raise ValueError("PV file must have DateTime + RealPower columns")
        real_power = df.columns[1]
        timestamps = df[df.columns[0]]

        # from algorithm given in https://pubs.aip.org/aip/jrse/article/13/2/025301/926842/Open-source-multi-year-power-generation
        smooth = gaussian_filter1d(df[real_power].fillna(0).values, sigma=1)
        pMax = np.max(smooth)

        for i in range(1, min(96, len(df))):
            val = df.at[i, real_power]
            hour = timestamps.iloc[i].hour

            if pd.isna(val) or val < -3 or val > 1.1 * pMax:
                df.at[i, real_power] = df.at[i - 1, real_power]

            if val > 1 and hour in [21, 22, 23, 0, 1, 2, 3, 4]:
                df.at[i, real_power] = df.at[i - 1, real_power]


        for i in range(96, len(df)):
            val = df.at[i, real_power]
            hour = timestamps.iloc[i].hour

            if pd.isna(val) or val < -3 or val > 1.1 * pMax:
                df.at[i, real_power] = df.at[i - 96, real_power]

            if val is not None and val > 1 and hour in [21, 22, 23, 0, 1, 2, 3, 4]:
                df.at[i, real_power] = df.at[i - 96, real_power]

            if hour == 0 and timestamps.iloc[i].minute == 0:
                if i >= 96 * 2:
                    prev_day_range = df[real_power].iloc[i - 96:i]
                    if prev_day_range.max() <= 0.1:
                        df.loc[i - 96:i, real_power] = df.loc[i - 192:i - 96, real_power].values

        #df = self.aggregate_hourly_kW(df)

        if save:
            save_formatted_df(df, self.raw_filename)

        return df

