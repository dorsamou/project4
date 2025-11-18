DATASETS = {
    # Building Loads cal_real and cal_reactive from https://github.com/sushilsilwal3/UCSD-Microgrid-Database/blob/master/Python%20Scripts/PythonBuildingLoad.py
    #columns: DateTime, RealPower, ReactivePower
    "CenterHall": {
        "raw_filename": "BuildingLoad/CenterHall.csv",
        "formatted_filename": "CenterHall_formatted.csv",
        "type": "load",
        "cal_real": 0.5,
        "cal_reactive": 1.0
    },
    "EastCampus": {
        "raw_filename": "BuildingLoad/EastCampus.csv",
        "formatted_filename": "EastCampus_formatted.csv",
        "type": "load",
        "cal_real": 1.0,
        "cal_reactive": 1.0
    },
    "GalbraithHall": {
        "raw_filename": "BuildingLoad/GalbraithHall.csv",
        "formatted_filename": "GalbraithHall_formatted.csv",
        "type": "load",
        "cal_real": 0.5,
        "cal_reactive": 0.5
    },
    "GeiselLibrary": {
        "raw_filename": "BuildingLoad/GeiselLibrary.csv",
        "formatted_filename": "GeiselLibrary_formatted.csv",
        "type": "load",
        "cal_real": 0.3,
        "cal_reactive": 1.0
    },
    "Mandeville": {
        "raw_filename": "BuildingLoad/Mandeville.csv",
        "formatted_filename": "Mandeville_formatted.csv",
        "type": "load",
        "cal_real": 0.75,
        "cal_reactive": 1.0
    },
    "MusicBuilding": {
        "raw_filename": "BuildingLoad/MusicBuilding.csv",
        "formatted_filename": "MusicBuilding_formatted.csv",
        "type": "load",
        "cal_real": 0.6,
        "cal_reactive": 1.0
    },
    "OttersonHall": {
        "raw_filename": "BuildingLoad/OttersonHall.csv",
        "formatted_filename": "OttersonHall_formatted.csv",
        "type": "load",
        "cal_real": 0.35,
        "cal_reactive": 0.5
    },
    "PepperCanyon": {
        "raw_filename": "BuildingLoad/PepperCanyon.csv",
        "formatted_filename": "PepperCanyon_formatted.csv",
        "type": "load",
        "cal_real": 0.7,
        "cal_reactive": 1.0
    },
    "RadyHall": {
        "raw_filename": "BuildingLoad/RadyHall.csv",
        "formatted_filename": "RadyHall_formatted.csv",
        "type": "load",
        "cal_real": 0.7,
        "cal_reactive": 1.0
    },
    "RobinsonHall": {
        "raw_filename": "BuildingLoad/RobinsonHall.csv",
        "formatted_filename": "RobinsonHall_formatted.csv",
        "type": "load",
        "cal_real": 0.4,
        "cal_reactive": 0.4
    },
    "SocialScience": {
        "raw_filename": "BuildingLoad/SocialScience.csv",
        "formatted_filename": "SocialScience_formatted.csv",
        "type": "load",
        "cal_real": 0.7,
        "cal_reactive": 1.0
    },
    "StudentServices": {
        "raw_filename": "BuildingLoad/StudentServices.csv",
        "formatted_filename": "StudentServices_formatted.csv",
        "type": "load",
        "cal_real": 0.5,
        "cal_reactive": 1.0
    },

    # Building Load w/ EV 
    #columns: DateTime, RealPower
    "HopkinsBuilding": {
        "raw_filename": "BuildingLoadWithEV/HopkinsBuilding.csv",
        "raw_ev_filename": "BuildingLoadWithEV/HopkinsEV.csv",
        "formatted_filename": "HopkinsBuilding_with_ev_formatted.csv",
        "type": "loadwev",
        "cal_real": 0.35,
        "cal_reactive": 0.5
    },
    "PoliceBuilding": {
        "raw_filename": "BuildingLoadWithEV/PoliceBuilding.csv",
        "raw_ev_filename": "BuildingLoadWithEV/PoliceEV.csv",
        "formatted_filename": "PoliceBuilding_with_ev_formatted.csv",
        "type": "loadwev",
        "cal_real": 0.4,
        "cal_reactive": 0.7
    },

    # PV Generators
    #columns: DateTime, RealPower
    "BioEngineeringPV": {
        "raw_filename": "PVGenerator/BioEngineeringPV.csv",
        "formatted_filename": "BioEngineeringPV_formatted.csv",
        "type": "pv",
    },
    "CSC_BuildingPV": {
        "raw_filename": "PVGenerator/CSC_BuildingPV.csv",
        "formatted_filename": "CSC_BuildingPV_formatted.csv",
        "type": "pv",
    },
    "BSB_LibraryPV": {
        "raw_filename": "PVGenerator/BSB_LibraryPV.csv",
        "formatted_filename": "BSB_LibraryPV_formatted.csv",
        "type": "pv",
    },
    "BSB_BuildingPV": {
        "raw_filename": "PVGenerator/BSB_BuildingPV.csv",
        "formatted_filename": "BSB_BuildingPV_formatted.csv",
        "type": "pv",
    },
    "CUP_PV": {
        "raw_filename": "PVGenerator/CUP_PV.csv",
        "formatted_filename": "CUP_PV_formatted.csv",
        "type": "pv",
    },
    "EBU2_A_PV": {
        "raw_filename": "PVGenerator/EBU2_A_PV.csv",
        "formatted_filename": "EBU2_A_PV_formatted.csv",
        "type": "pv",
    },
    "EBU2_B_PV": {
        "raw_filename": "PVGenerator/EBU2_B_PV.csv",
        "formatted_filename": "EBU2_B_PV_formatted.csv",
        "type": "pv",
    },
    "ElectricShopPV": {
        "raw_filename": "PVGenerator/ElectricShopPV.csv",
        "formatted_filename": "ElectricShopPV_formatted.csv",
        "type": "pv",
    },
    "GarageFleetsPV": {
        "raw_filename": "PVGenerator/GarageFleetsPV.csv",
        "formatted_filename": "GarageFleetsPV_formatted.csv",
        "type": "pv",
    },
    "GilmanParkingPV": {
        "raw_filename": "PVGenerator/GilmanParkingPV.csv",
        "formatted_filename": "GilmanParkingPV_formatted.csv",
        "type": "pv",
    },
    "HopkinsParkingPV": {
        "raw_filename": "PVGenerator/HopkinsParkingPV.csv",
        "formatted_filename": "HopkinsParkingPV_formatted.csv",
        "type": "pv",
    },
    "KeelingA_PV": {
        "raw_filename": "PVGenerator/KeelingA_PV.csv",
        "formatted_filename": "KeelingA_PV_formatted.csv",
        "type": "pv",
    },
    "KeelingB_PV": {
        "raw_filename": "PVGenerator/KeelingB_PV.csv",
        "formatted_filename": "KeelingB_PV_formatted.csv",
        "type": "pv",
    },
    "KyoceraSkylinePV": {
        "raw_filename": "PVGenerator/KyoceraSkylinePV.csv",
        "formatted_filename": "KyoceraSkylinePV_formatted.csv",
        "type": "pv",
    },
    "LeichtagPV": {
        "raw_filename": "PVGenerator/LeichtagPV.csv",
        "formatted_filename": "LeichtagPV_formatted.csv",
        "type": "pv",
    },
    "MayerHallPV": {
        "raw_filename": "PVGenerator/MayerHallPV.csv",
        "formatted_filename": "MayerHallPV_formatted.csv",
        "type": "pv",
    },
    "MESOM_PV": {
        "raw_filename": "PVGenerator/MESOM_PV.csv",
        "formatted_filename": "MESOM_PV_formatted.csv",
        "type": "pv",
    },
    "OslerParkingPV": {
        "raw_filename": "PVGenerator/OslerParkingPV.csv",
        "formatted_filename": "OslerParkingPV_formatted.csv",
        "type": "pv",
    },
    "PriceCenterA_PV": {
        "raw_filename": "PVGenerator/PriceCenterA_PV.csv",
        "formatted_filename": "PriceCenterA_PV_formatted.csv",
        "type": "pv",
    },
    "PriceCenterB_PV": {
        "raw_filename": "PVGenerator/PriceCenterB_PV.csv",
        "formatted_filename": "PriceCenterB_PV_formatted.csv",
        "type": "pv",
    },
    "SDSC_PV": {
        "raw_filename": "PVGenerator/SDSC_PV.csv",
        "formatted_filename": "SDSC_PV_formatted.csv",
        "type": "pv",
    },
    "SME_SolarPV": {
        "raw_filename": "PVGenerator/SME_SolarPV.csv",
        "formatted_filename": "SME_SolarPV_formatted.csv",
        "type": "pv",
    },
    "PowellPV": {
        "raw_filename": "PVGenerator/PowellPV.csv",
        "formatted_filename": "PowellPV_formatted.csv",
        "type": "pv",
    },
    "StephenBirchPV": {
        "raw_filename": "PVGenerator/StephenBirchPV.csv",
        "formatted_filename": "StephenBirchPV_formatted.csv",
        "type": "pv",
    },
    "TradeStreetPV": {
        "raw_filename": "Trade Street Off-campus Microgrid/TradeStreetPV.csv",
        "formatted_filename": "TradeStreetPV_formatted.csv",
        "type": "pv",
    },

    #Battery Storage 
    # columns: DateTime, RealPower (negative for discharge, positve for charge)
    "TradeStreetBattery": {
        "raw_filename": "Trade Street Off-campus Microgrid/TradeStreetBattery.csv",
        "formatted_filename": "TradeStreetBattery_formatted.csv",
        "type": "battery",
        "rating_kw": 200,
        "rating_kwh": 400
    },
    "BatteryStorage": {
        "raw_filename": "BatteryStorage.csv",
        "formatted_filename": "BatteryStorage_formatted.csv",
        "type": "battery",
        "rating_kw": 2500,
        "rating_kwh": 5000
    }
}