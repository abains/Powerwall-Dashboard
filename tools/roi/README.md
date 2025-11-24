# Solar ROI Calculator

This tool calculates the Return on Investment (ROI) for your solar panel installation based on PG&E TOU-C rates.

## Features
- Calculates cumulative savings from historical data in InfluxDB.
- Applies seasonal and time-of-use (TOU) rates.
- Projects future savings to estimate a payoff date.
- Writes data to InfluxDB for visualization in Grafana.

## Setup

1.  **Configuration**:
    Create a `local.env` file in this directory (`tools/roi/local.env`) with your specific settings:
    ```bash
    # InfluxDB Connection
    INFLUXDB_HOST=raspberrypi.local
    INFLUXDB_PORT=8086
    INFLUXDB_DB=powerwall

    # Installation Details
    PW_INSTALL_COST=15500           # Your installation cost
    PW_INSTALL_DATE=2021-11-11      # Your installation date
    ```

2.  **Requirements**:
    Ensure you have the necessary Python packages installed. You can install them via pip:
    ```bash
    pip install influxdb python-dotenv python-dateutil
    ```

3.  **Run the Script**:
    Run the script to calculate ROI and backfill data:
    ```bash
    python3 roi.py
    ```
    The script will automatically load configuration from `local.env`.

4.  **Grafana Dashboard**:
    - Open Grafana (http://localhost:9000).
    - Go to **Dashboards > Import**.
    - Upload `dashboards/dashboard-roi.json` (located in the project root `dashboards` folder).
    - The dashboard visualizes "Net Savings" and indicates the Break Even point.

## Automation
To keep the ROI data up to date, you can run this script periodically (e.g., via cron) or manually whenever you want to check the progress.
