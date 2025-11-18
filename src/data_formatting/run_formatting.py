import os 
from src.data_formatting.formatting import (
    BatteryStorageFormatter,
    BuildingLoadFormatter,
    PVGeneratorFormatter,
    combine_power,
    save_formatted_df
)
from src.config.config import DATASETS
from src.config.paths import FORMATTED_DATA_PATH

def run_formatting():
    for asset, data_info in DATASETS.items():
        ftype = data_info["type"]
        filename = data_info["raw_filename"]

        #if the formatted file name in data_info["formatted_filename"] already exists in the path FORMATTED_DATA_PATH, skip formatting
        formatted_filepath = os.path.join(FORMATTED_DATA_PATH, data_info["formatted_filename"])
        if os.path.exists(formatted_filepath):
            print(f"Formatted file for asset '{asset}' already exists. Skipping formatting.")
            continue

        elif ftype == "load":
            formatter = BuildingLoadFormatter(
                filename,
                cal_real=data_info["cal_real"],
                cal_reactive=data_info["cal_reactive"],
            )
            df = formatter.run(save=True)

        elif ftype == "pv":
            formatter = PVGeneratorFormatter(
                filename
            )
            df = formatter.run(save=True)

        elif ftype == "battery":
            formatter = BatteryStorageFormatter(
                filename,
                rating_kw=data_info["rating_kw"],
            )
            df = formatter.run(save=True)

        elif ftype == "loadwev":
            building_formatter = BuildingLoadFormatter(
                filename,
                cal_real=data_info["cal_real"],
                cal_reactive=data_info["cal_reactive"],
            )
            df_building = building_formatter.run(save=False)

            ev_filename = data_info["raw_ev_filename"]

            ev_formatter = BuildingLoadFormatter(
                ev_filename,
                cal_real=data_info["cal_real"],
                cal_reactive=data_info["cal_reactive"],
            )
            df_ev = ev_formatter.run(save=False)

            df = combine_power(df_building, df_ev)
            # Save the combined dataframe
            save_formatted_df(df=df, raw_filename=filename, suffix="_with_ev_formatted")


        else:
            print(f"Unknown type '{ftype}' for asset '{asset}'.")
            continue

if __name__ == "__main__":
    run_formatting()
