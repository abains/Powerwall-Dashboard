#!/usr/bin/env python3
import os
import sys
from influxdb import InfluxDBClient
from dotenv import load_dotenv

# Load environment variables
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "../../"))

pypowerwall_env = os.path.join(project_root, "pypowerwall.env")
if os.path.exists(pypowerwall_env):
    load_dotenv(pypowerwall_env)

local_env = os.path.join(script_dir, "local.env")
if os.path.exists(local_env):
    load_dotenv(local_env)

# InfluxDB Settings
INFLUX_HOST = os.getenv("INFLUXDB_HOST", "localhost")
INFLUX_PORT = int(os.getenv("INFLUXDB_PORT", 8086))
INFLUX_DB = os.getenv("INFLUXDB_DB", "powerwall")

def main():
    print(f"Connecting to InfluxDB at {INFLUX_HOST}:{INFLUX_PORT}...")
    client = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT, database=INFLUX_DB)
    
    measurements = ["roi_stats", "roi_info", "roi_payoff_marker"]
    
    print("WARNING: This will delete all data for the following measurements:")
    for m in measurements:
        print(f" - {m}")
    
    confirm = input("Are you sure you want to continue? (yes/no): ")
    if confirm.lower() != "yes":
        print("Aborted.")
        return

    for measurement in measurements:
        print(f"Dropping measurement: {measurement}")
        client.query(f"DROP MEASUREMENT {measurement}")
    
    print("Done. All ROI data cleared.")

if __name__ == "__main__":
    main()
