#!/usr/bin/env python3
import os
import sys
import datetime
from influxdb import InfluxDBClient
from dateutil import parser
import time
from dotenv import load_dotenv

# Configuration
# Load environment variables
# We look for pypowerwall.env in the project root (two levels up)
# and local.env in the same directory as this script.

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
INSTALL_COST = float(os.getenv('PW_INSTALL_COST', 0))
INSTALL_DATE = os.getenv('PW_INSTALL_DATE', '2021-01-01')

# Rates (PG&E TOU-C 2024 approx)
RATE_SUMMER_PEAK = float(os.getenv('PW_ROI_RATE_SUMMER_PEAK', 0.62))
RATE_SUMMER_OFFPEAK = float(os.getenv('PW_ROI_RATE_SUMMER_OFFPEAK', 0.53))
RATE_WINTER_PEAK = float(os.getenv('PW_ROI_RATE_WINTER_PEAK', 0.52))
RATE_WINTER_OFFPEAK = float(os.getenv('PW_ROI_RATE_WINTER_OFFPEAK', 0.49))

def get_rate(dt):
    """Return the rate for a given datetime."""
    # Summer: June 1 - Sep 30
    is_summer = 6 <= dt.month <= 9
    
    # Peak: 4pm - 9pm (16:00 - 21:00)
    is_peak = 16 <= dt.hour < 21
    
    if is_summer:
        return RATE_SUMMER_PEAK if is_peak else RATE_SUMMER_OFFPEAK
    else:
        return RATE_WINTER_PEAK if is_peak else RATE_WINTER_OFFPEAK

def main():
    print(f"Connecting to InfluxDB at {INFLUX_HOST}:{INFLUX_PORT}...")
    client = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT, database=INFLUX_DB)
    
    # Check connection
    try:
        client.ping()
    except Exception as e:
        print(f"Error connecting to InfluxDB: {e}")
        sys.exit(1)

    print("Calculating ROI...")
    
    # Query hourly solar generation
    # Integral of Watts (W) over 1h gives Watt-hours (Wh). Divide by 1000 for kWh.
    # InfluxDB integral returns area under curve (value * seconds).
    # So integral(W) = Joules. 1 kWh = 3,600,000 Joules.
    query = f"SELECT integral(solar) / 3600000 AS energy_kwh FROM http WHERE time >= '{INSTALL_DATE}' GROUP BY time(1h) fill(0)"
    
    result = client.query(query)
    points = list(result.get_points())
    
    cumulative_savings = 0.0
    roi_points = []
    
    last_dt = None
    payoff_date_past = None
    
    for point in points:
        dt = parser.parse(point['time'])
        energy = point['energy_kwh']
        
        if energy is None:
            energy = 0
            
        rate = get_rate(dt)
        savings = energy * rate
        cumulative_savings += savings
        
        # Check if we just passed the payoff threshold
        if INSTALL_COST > 0 and payoff_date_past is None and cumulative_savings >= INSTALL_COST:
            payoff_date_past = dt
        
        roi_points.append({
            "measurement": "roi_stats",
            "time": point['time'],
            "fields": {
                "savings": float(savings),
                "cumulative_savings": float(cumulative_savings),
                "net_savings": float(cumulative_savings - INSTALL_COST),
                "rate_applied": float(rate),
                "energy_kwh": float(energy)
            }
        })
        last_dt = dt

    print(f"Total Savings to date: ${cumulative_savings:.2f}")
    
    if INSTALL_COST > 0:
        print(f"Installation Cost: ${INSTALL_COST:.2f}")
        remaining = INSTALL_COST - cumulative_savings
        
        payoff_str = ""
        days_remaining = 0
        
        if remaining > 0:
            print(f"Remaining to payoff: ${remaining:.2f}")
            
            # Project future
            # Calculate average daily savings over last 365 days (or available duration)
            days_available = (last_dt - parser.parse(INSTALL_DATE)).days
            if days_available > 0:
                avg_daily_savings = cumulative_savings / days_available
                days_to_payoff = remaining / avg_daily_savings
                payoff_date = last_dt + datetime.timedelta(days=days_to_payoff)
                payoff_str = payoff_date.strftime('%Y-%m-%d')
                days_remaining = days_to_payoff
                print(f"Estimated Payoff Date: {payoff_str}")
                
                # Generate future points for graph
                current_sim_savings = cumulative_savings
                current_sim_date = last_dt
                
                # Step by day for projection
                while current_sim_savings < INSTALL_COST * 1.2: # Go a bit past payoff
                    current_sim_date += datetime.timedelta(days=1)
                    current_sim_savings += avg_daily_savings
                    
                    roi_points.append({
                        "measurement": "roi_stats",
                        "time": current_sim_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        "fields": {
                            "cumulative_savings": float(current_sim_savings),
                            "net_savings": float(current_sim_savings - INSTALL_COST),
                            "projected": True
                        }
                    })
        else:
            print("Paid off!")
            if payoff_date_past:
                payoff_str = f"Paid Off: {payoff_date_past.strftime('%Y-%m-%d')}"
                print(payoff_str)
            else:
                payoff_str = "Paid Off"

        # Write payoff info (always write if cost is set)
        roi_points.append({
            "measurement": "roi_info",
            "time": datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            "fields": {
                "payoff_date_str": payoff_str,
                "days_remaining": float(days_remaining)
            }
        })

        # Write Payoff Marker for Annotation
        marker_date = payoff_date_past if payoff_date_past else (payoff_date if 'payoff_date' in locals() else None)
        if marker_date:
            roi_points.append({
                "measurement": "roi_payoff_marker",
                "time": marker_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "fields": {
                    "value": 1,
                    "text": "Payoff Date"
                }
            })
    
    # Write to InfluxDB
    print(f"Writing {len(roi_points)} points to InfluxDB...")
    # Write in batches
    batch_size = 1000
    for i in range(0, len(roi_points), batch_size):
        client.write_points(roi_points[i:i+batch_size])
    
    print("Done.")

if __name__ == "__main__":
    main()
