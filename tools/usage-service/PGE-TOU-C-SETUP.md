# PGE TOU-C Total Cost of Ownership (TCO) Setup Guide

This guide helps you calculate the Total Cost of Ownership (TCO) for your Tesla Solar and Powerwall system using PG&E's TOU-C rate plan in the Bay Area.

## Overview

The **pwdusage** microservice integrates with Powerwall Dashboard to provide detailed cost and usage analysis based on your specific utility rate plan. This allows you to:

- Calculate actual energy costs with your solar/Powerwall system
- Estimate costs without the system (baseline scenario)
- Track savings over time
- Understand ROI and payback period
- Optimize battery charging/discharging schedules

## Prerequisites

- Powerwall Dashboard already installed and running
- Docker and docker-compose installed
- Access to your PG&E account to verify exact rates
- Knowledge of your baseline allowance (found on your PG&E bill)

## Step 1: Install pwdusage Service

### Option A: Using Docker (Recommended)

1. **Navigate to the usage-service directory:**
   ```bash
   cd ~/Powerwall-Dashboard/tools/usage-service
   ```

2. **Build the Docker image:**
   ```bash
   ./build.sh
   ```

3. **Update your docker-compose configuration:**

   Edit `~/Powerwall-Dashboard/powerwall.extend.yml` (create if it doesn't exist):
   ```yaml
   services:
     pwdusage:
       image: pwdusage:latest
       container_name: pwdusage
       hostname: pwdusage
       restart: unless-stopped
       volumes:
         - type: bind
           source: ./tools/usage-service/pge-tou-c-bayarea.json
           target: /app/usage_config.json
           read_only: true
       ports:
         - "8677:8677"
       environment:
         - CONFIG_FILE=/app/usage_config.json
       depends_on:
         - influxdb
       networks:
         - default
   ```

4. **Start the service:**
   ```bash
   cd ~/Powerwall-Dashboard
   ./compose-dash.sh up -d pwdusage
   ```

5. **Verify the service is running:**
   ```bash
   docker logs pwdusage
   curl http://localhost:8677/usage
   ```

## Step 2: Customize Rate Configuration

The provided `pge-tou-c-bayarea.json` configuration uses baseline (Tier 1) rates. You need to customize it based on your actual usage and baseline allowance.

### Find Your Baseline Allowance

1. Check your PG&E bill for your "Baseline Allowance" (typically 9-15 kWh/day for Bay Area)
2. Determine your climate zone (P, Q, R, S, T, V, W, X, Y, or Z)
3. Note whether you have gas or electric heating

### Adjust Rates for Above-Baseline Usage

If your monthly usage exceeds your baseline allowance, you'll need to configure Tier 2 rates:

**Summer (June-September):**
- Tier 1 (Below Baseline): $0.39 off-peak / $0.49 peak
- Tier 2 (Above Baseline): $0.51 off-peak / $0.61 peak

**Winter (October-May):**
- Tier 1: Approximately 10-15% lower than summer
- Tier 2: Approximately 10-15% lower than summer

### Update Configuration File

Edit `pge-tou-c-bayarea.json` and update:

1. **Timezone** - Verify it's set to `America/Los_Angeles`
2. **Supply Charge** - Check your PG&E bill for exact daily service charge (currently ~$0.06575/hour = $1.578/day)
3. **Export Rates** - Adjust `GRID_EXPORT` to match your net metering credit (often same as import rate)
4. **Seasonal Rates** - Update based on latest PG&E tariff schedule

Example for Tier 2 (Above Baseline) Summer rates:
```json
"2025-06-01": {
    "plan": "PGE-TOU-C-BayArea",
    "season": "Summer",
    "tariffs": {
        "Peak": {
            "GRID_SUPPLY": -0.61,
            "GRID_EXPORT": 0.49,
            "SELF_PW_NET_OF_GRID": 0.61,
            "SELF_SOLAR_PLUS_RES": 0.61,
            "SUPPLY_CHARGE": -0.06575
        },
        "Off-Peak": {
            "GRID_SUPPLY": -0.51,
            "GRID_EXPORT": 0.39,
            "SELF_PW_NET_OF_GRID": 0.51,
            "SELF_SOLAR_PLUS_RES": 0.51,
            "SUPPLY_CHARGE": -0.06575
        }
    }
}
```

## Step 3: Configure Grafana Data Source

1. **Open Grafana** at `http://your-server:9000`

2. **Add pwdusage data source:**
   - Go to Configuration → Data Sources
   - Click "Add data source"
   - Select "JSON API"
   - Configure:
     - Name: `pwdusage`
     - URL: `http://pwdusage:8677`
     - Access: Server (default)
   - Click "Save & test"

## Step 4: Import Dashboards

The usage-service directory includes pre-built Grafana dashboards:

1. **Usage Summary Dashboard:**
   - Go to Dashboards → Import
   - Upload `Usage Summary v2 dashboard.json`
   - Select your data sources (InfluxDB and pwdusage)
   - Click Import

2. **Usage Detail Dashboard:**
   - Import `Usage Detail Dashboard.json`
   - Shows hourly/daily breakdowns by rate period

3. **Savings Panel:**
   - Import `Savings panel.json`
   - Add to your main dashboard for quick savings view

## Step 5: Calculate Total Cost of Ownership (TCO)

### Understanding TCO Components

TCO calculation involves comparing two scenarios:

**Scenario A: With Solar + Powerwall (Actual)**
- Grid import costs (reduced by solar/battery)
- Solar export credits
- System maintenance costs (minimal for Tesla)
- Initial investment cost

**Scenario B: Without Solar + Powerwall (Baseline)**
- Full grid import for all home consumption
- No export credits
- No system costs

### TCO Formula

```
Total Savings = (Baseline Cost - Actual Cost) - (Annual System Cost)

ROI = Total Savings / Initial Investment
Payback Period = Initial Investment / Annual Savings
```

### Create TCO Tracking Dashboard

Create a new Grafana dashboard with these panels:

#### Panel 1: Monthly Cost Comparison
```sql
Query 1 (Baseline - estimated):
SELECT mean("home") * 0.45 as "Estimated Without Solar"
FROM "kwh"."http"
WHERE $timeFilter
GROUP BY time(1d)

Query 2 (Actual - from pwdusage):
http://pwdusage:8677/usage?period=daily&metric=total_cost
```

#### Panel 2: Cumulative Savings
Track cumulative savings since installation:
```sql
SELECT cumulative_sum(mean("savings")) as "Total Savings"
FROM (
  SELECT (baseline_cost - actual_cost) as "savings"
  FROM ...
)
WHERE time > 'YYYY-MM-DD'  -- Your installation date
```

#### Panel 3: Payback Progress
```
Payback % = (Cumulative Savings / Initial Investment) * 100
```

### Setting System Parameters

Create a Grafana dashboard variable for:
- `initial_investment` - Total cost of your solar + Powerwall system
- `installation_date` - When your system was activated
- `avg_baseline_rate` - Estimated average rate without solar (use $0.45/kWh as starting point)
- `annual_maintenance` - Estimated annual maintenance (typically $0-500 for Tesla systems)

## Step 6: Advanced TCO Analysis

### Account for Rate Increases

PG&E rates typically increase 3-7% annually. To project long-term savings:

```sql
Year 1 Savings: Actual calculation
Year 2 Savings: Year 1 * 1.05 (assuming 5% rate increase)
Year 3 Savings: Year 2 * 1.05
...
25-Year Savings: Sum of all years
```

### Include Federal Tax Credit

If you received the federal solar Investment Tax Credit (ITC):
- 30% of system cost (for systems installed 2022-2032)
- Reduces effective system cost for ROI calculation

```
Effective Investment = Initial Investment - (Initial Investment * 0.30)
```

### Battery Replacement Cost

Powerwall warranty is 10 years. For 25-year TCO analysis:
- Include estimated battery replacement cost (~$10,000-15,000 in year 11)
- Tesla batteries often exceed warranty period

### Carbon Offset Value

Optional: Calculate environmental value
- Track kWh solar generated
- Multiply by regional carbon intensity (0.2-0.5 kg CO2/kWh for California)
- Value at social cost of carbon (~$50/ton CO2)

## Step 7: Optimize for Better ROI

### Peak Shaving Strategy

Configure your Powerwall to:
1. Charge from solar during off-peak
2. Discharge during peak hours (4-9 PM)
3. Avoid charging from grid unless necessary

### Monitor and Adjust

Review monthly:
1. Are you exceeding baseline allowance?
   - If yes, focus on reducing peak usage
   - Consider switching to EV2-A if you have an EV
2. Is battery cycling optimally?
   - Should discharge fully during peak
   - Should charge fully from solar when available
3. Are solar exports optimized?
   - Maximize self-consumption first
   - Export excess during peak for best credit

## Troubleshooting

### pwdusage service not responding
```bash
docker logs pwdusage
docker restart pwdusage
```

### Rates don't match your bill
1. Verify your exact rate schedule on PG&E website
2. Check for temporary rate adjustments or credits
3. Ensure Community Choice Aggregation (CCA) rates if applicable (EBCE, MCE, PCE, SJCE, etc.)

### Missing data in dashboards
1. Verify InfluxDB has data:
   ```bash
   docker exec -it influxdb influx -execute "SELECT * FROM powerwall.kwh.http LIMIT 10"
   ```
2. Check pwdusage can access InfluxDB:
   ```bash
   docker exec -it pwdusage curl http://influxdb:8086/health
   ```

## Additional Resources

- **pwdusage Documentation**: https://github.com/BuongiornoTexas/pwdusage
- **PG&E Rate Plans**: https://www.pge.com/en/account/rate-plans.html
- **PG&E TOU-C Tariff**: https://www.pge.com/tariffs/assets/pdf/tariffbook/ELEC_SCHEDS_E-TOU-C.pdf
- **Baseline Allowance Calculator**: https://www.pge.com/en/account/rate-plans/how-rates-work/baseline-allowance.html
- **Tesla App**: Monitor your system performance and battery modes

## Example TCO Calculation

Assuming:
- System Cost: $40,000
- Federal Tax Credit: $12,000 (30%)
- Net Cost: $28,000
- Average Monthly Bill Before: $250
- Average Monthly Bill After: $50
- Monthly Savings: $200
- Annual Savings: $2,400

**Payback Period:**
```
$28,000 / $2,400 = 11.7 years
```

**25-Year Savings (with 5% annual rate increases):**
```
Year 1: $2,400
Year 2: $2,520
...
Year 25: $7,651
Total: ~$109,000
```

**Net 25-Year Benefit:**
```
$109,000 - $28,000 = $81,000
```

## Notes for Bay Area Residents

- **CCA Programs**: If you're in a Community Choice Aggregation area (EBCE, MCE, PCE, SJCE), rates may differ
- **SGIP Rebate**: Check if you qualified for Self-Generation Incentive Program rebates
- **Peak Hours**: PG&E's 4-9 PM peak coincides with dinner time - optimal battery usage window
- **Summer Impact**: June-September rates are significantly higher - where solar provides maximum value
- **PG&E PSPS**: Public Safety Power Shutoffs make battery backup especially valuable

## Updates and Maintenance

1. **Check rates quarterly** - PG&E adjusts rates periodically
2. **Update configuration** - Modify `pge-tou-c-bayarea.json` when rates change
3. **Restart service** - After configuration changes:
   ```bash
   ./compose-dash.sh restart pwdusage
   ```
4. **Monitor accuracy** - Compare dashboard calculations to actual PG&E bills monthly

---

**Last Updated:** 2025-11-13
**For:** PG&E E-TOU-C Rate Plan
**Region:** Bay Area, California
