DATASETS = {
    # Building Loads cal_real and cal_reactive from https://github.com/sushilsilwal3/UCSD-Microgrid-Database/blob/master/Python%20Scripts/PythonBuildingLoad.py
    #columns: DateTime, RealPower, ReactivePower
    "CenterHall": {
        "filename": "BuildingLoad/CenterHall.csv",
        "type": "load",
        "cal_real": 0.5,
        "cal_reactive": 1.0
    },
    "EastCampus": {
        "filename": "BuildingLoad/EastCampus.csv",
        "type": "load",
        "cal_real": 1.0,
        "cal_reactive": 1.0
    },
    "GalbraithHall": {
        "filename": "BuildingLoad/GalbraithHall.csv",
        "type": "load",
        "cal_real": 0.5,
        "cal_reactive": 0.5
    },
    "GeiselLibrary": {
        "filename": "BuildingLoad/GeiselLibrary.csv",
        "type": "load",
        "cal_real": 0.3,
        "cal_reactive": 1.0
    },
    "Mandeville": {
        "filename": "BuildingLoad/Mandeville.csv",
        "type": "load",
        "cal_real": 0.75,
        "cal_reactive": 1.0
    },
    "MusicBuilding": {
        "filename": "BuildingLoad/MusicBuilding.csv",
        "type": "load",
        "cal_real": 0.6,
        "cal_reactive": 1.0
    },
    "OttersonHall": {
        "filename": "BuildingLoad/OttersonHall.csv",
        "type": "load",
        "cal_real": 0.35,
        "cal_reactive": 0.5
    },
    "PepperCanyon": {
        "filename": "BuildingLoad/PepperCanyon.csv",
        "type": "load",
        "cal_real": 0.7,
        "cal_reactive": 1.0
    },
    "RadyHall": {
        "filename": "BuildingLoad/RadyHall.csv",
        "type": "load",
        "cal_real": 0.7,
        "cal_reactive": 1.0
    },
    "RobinsonHall": {
        "filename": "BuildingLoad/RobinsonHall.csv",
        "type": "load",
        "cal_real": 0.4,
        "cal_reactive": 0.4
    },
    "SocialScience": {
        "filename": "BuildingLoad/SocialScience.csv",
        "type": "load",
        "cal_real": 0.7,
        "cal_reactive": 1.0
    },
    "StudentServices": {
        "filename": "BuildingLoad/StudentServices.csv",
        "type": "load",
        "cal_real": 0.5,
        "cal_reactive": 1.0
    },

    # Building Load w/ EV 
    #columns: DateTime, RealPower
    "HopkinsBuilding": {
        "filename": "BuildingLoadWithEV/HopkinsBuilding.csv",
        "type": "loadwev",
        "cal_real": 0.35,
        "cal_reactive": 0.5
    },
    # not included in UCSD-Microgrid-Database data processing scripts
    "HopkinsEV": {
        "filename": "BuildingLoadWithEV/HopkinsEV.csv",
        "type": "loadwev",
        "cal_real": 0.35,
        "cal_reactive": 0.5
    },
    "PoliceBuilding": {
        "filename": "BuildingLoadWithEV/PoliceBuilding.csv",
        "type": "loadwev",
        "cal_real": 0.4,
        "cal_reactive": 0.7
    },
    # not included in UCSD-Microgrid-Database data processing scripts
    "PoliceEV": {
        "filename": "BuildingLoadWithEV/PoliceEV.csv",
        "type": "loadwev",
        "cal_real": 0.4,
        "cal_reactive": 0.7
    },

    # PV Generators
    #columns: DateTime, RealPower
    "BioEngineeringPV": {
        "filename": "PVGenerator/BioEngineeringPV.csv",
        "type": "pv",
    },
    "CSC_BuildingPV": {
        "filename": "PVGenerator/CSC_BuildingPV.csv",
        "type": "pv",
    },
    "BSB_LibraryPV": {
        "filename": "PVGenerator/BSB_LibraryPV.csv",
        "type": "pv",
    },
    "BSB_BuildingPV": {
        "filename": "PVGenerator/BSB_BuildingPV.csv",
        "type": "pv",
    },
    "CUP_PV": {
        "filename": "PVGenerator/CUP_PV.csv",
        "type": "pv",
    },
    "EBU2_A_PV": {
        "filename": "PVGenerator/EBU2_A_PV.csv",
        "type": "pv",
    },
    "EBU2_B_PV": {
        "filename": "PVGenerator/EBU2_B_PV.csv",
        "type": "pv",
    },
    "ElectricShopPV": {
        "filename": "PVGenerator/ElectricShopPV.csv",
        "type": "pv",
    },
    "GarageFleetsPV": {
        "filename": "PVGenerator/GarageFleetsPV.csv",
        "type": "pv",
    },
    "GilmanParkingPV": {
        "filename": "PVGenerator/GilmanParkingPV.csv",
        "type": "pv",
    },
    "HopkinsParkingPV": {
        "filename": "PVGenerator/HopkinsParkingPV.csv",
        "type": "pv",
    },
    "KeelingA_PV": {
        "filename": "PVGenerator/KeelingA_PV.csv",
        "type": "pv",
    },
    "KeelingB_PV": {
        "filename": "PVGenerator/KeelingB_PV.csv",
        "type": "pv",
    },
    "KyoceraSkylinePV": {
        "filename": "PVGenerator/KyoceraSkylinePV.csv",
        "type": "pv",
    },
    "LeichtagPV": {
        "filename": "PVGenerator/LeichtagPV.csv",
        "type": "pv",
    },
    "MayerHallPV": {
        "filename": "PVGenerator/MayerHallPV.csv",
        "type": "pv",
    },
    "MESOM_PV": {
        "filename": "PVGenerator/MESOM_PV.csv",
        "type": "pv",
    },
    "OslerParkingPV": {
        "filename": "PVGenerator/OslerParkingPV.csv",
        "type": "pv",
    },
    "PriceCenterA_PV": {
        "filename": "PVGenerator/PriceCenterA_PV.csv",
        "type": "pv",
    },
    "PriceCenterB_PV": {
        "filename": "PVGenerator/PriceCenterB_PV.csv",
        "type": "pv",
    },
    "SDSC_PV": {
        "filename": "PVGenerator/SDSC_PV.csv",
        "type": "pv",
    },
    "SME_SolarPV": {
        "filename": "PVGenerator/SME_SolarPV.csv",
        "type": "pv",
    },
    "PowellPV": {
        "filename": "PVGenerator/PowellPV.csv",
        "type": "pv",
    },
    "StephenBirchPV": {
        "filename": "PVGenerator/StephenBirchPV.csv",
        "type": "pv",
    },
    "TradeStreetPV": {
        "filename": "Trade Street Off-campus Microgrid/TradeStreetPV.csv",
        "type": "pv",
    },

    #Battery Storage 
    # columns: DateTime, RealPower (negative for discharge, positve for charge)
    "TradeStreetBattery": {
        "filename": "Trade Street Off-campus Microgrid/TradeStreetBattery.csv",
        "type": "battery",
        "rating_kw": 200,
        "rating_kwh": 400
    },
    "BatteryStorage": {
        "filename": "BatteryStorage.csv",
        "type": "battery",
        "rating_kw": 2500,
        "rating_kwh": 5000
    }
}