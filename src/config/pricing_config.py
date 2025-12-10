#uses SDGE TOU(Time of Use) pricing model with demand charges 

# SDGE Energy Rates ($/kWh)
ENERGY_RATES = {
    'on_peak': 0.529,
    'off_peak': 0.214,
    'super_off_peak': 0.121
}

# SDGE Demand Charges ($/kW)
DEMAND_CHARGES = {
    'maximum_demand': 15.38,
    'on_peak_demand': 3.05
}

# Weekdays
TOU_WEEKDAY_SUMMER = {
    'on_peak': [(16, 21)],  # 4:00 PM - 9:00 PM
    'off_peak': [(6, 16), (21, 24)],  # 6:00 AM - 4:00 PM, 9:00 PM - midnight
    'super_off_peak': [(0, 6)]  # Midnight - 6:00 AM
}

TOU_WEEKDAY_WINTER = {
    'on_peak': [(16, 21)],  # 4:00 PM - 9:00 PM
    'off_peak': [(6, 16), (21, 24)],  # 6:00 AM - 4:00 PM, 9:00 PM - midnight
    'super_off_peak': [(0, 6)]  # Midnight - 6:00 AM
}

# Note: Winter has special exclusion for 10:00 AM - 2:00 PM in March and April
TOU_WEEKDAY_WINTER_MARCH_APRIL = {
    'on_peak': [(16, 21)],
    'off_peak': [(6, 10), (14, 16), (21, 24)],  # Excluding 10:00 AM - 2:00 PM
    'super_off_peak': [(0, 6), (10, 14)]  # Including 10:00 AM - 2:00 PM
}

# Weekends and Holidays
TOU_WEEKEND_SUMMER = {
    'on_peak': [(16, 21)],  # 4:00 PM - 9:00 PM
    'off_peak': [(14, 16), (21, 24)],  # 2:00 PM - 4:00 PM, 9:00 PM - midnight
    'super_off_peak': [(0, 14)]  # Midnight - 2:00 PM
}

TOU_WEEKEND_WINTER = {
    'on_peak': [(16, 21)],  # 4:00 PM - 9:00 PM
    'off_peak': [(14, 16), (21, 24)],  # 2:00 PM - 4:00 PM, 9:00 PM - midnight
    'super_off_peak': [(0, 14)]  # Midnight - 2:00 PM
}

SUMMER_MONTHS = [6, 7, 8, 9, 10]