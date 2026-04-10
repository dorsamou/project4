# Microgrid Optimization Tool

A microgrid optimization project that minimizes operating cost and carbon emissions across generators, battery storage, and grid imports/exports. Built around real UCSD campus load data (2018–2019), SDG&E time-of-use pricing, and CAISO carbon intensity signals, with an interactive Streamlit interface for building and simulating custom microgrids.

## Usage

Launch the Streamlit builder tool:

```bash
streamlit run run_app.py
```

From the interface you can add generators and batteries, set capacity and SOC limits, pick a date range from the UCSD dataset, choose an objective, and run the optimization. Results render as dispatch plots, SOC charts, and cost/emissions summaries.

The app can also be deployed using the following link [link text](https://project4-zxjkb7xfra9qgzsonm4yaf.streamlit.app/)