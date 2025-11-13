# TCO Dashboard Configuration Guide

This guide provides InfluxDB queries and Grafana panel configurations for tracking Total Cost of Ownership.

## Dashboard Variables

First, create these dashboard variables in Grafana (Dashboard Settings → Variables):

### Variable 1: Initial Investment
- Name: `initial_investment`
- Type: Constant
- Value: `40000` (Change to your actual system cost)

### Variable 2: Federal Tax Credit
- Name: `tax_credit`
- Type: Constant
- Value: `0.30` (30% ITC)

### Variable 3: Installation Date
- Name: `install_date`
- Type: Constant
- Value: `2024-01-01` (Your actual installation date)

### Variable 4: Baseline Rate (avg $/kWh without solar)
- Name: `baseline_rate`
- Type: Constant
- Value: `0.45` (Estimated average PG&E rate)

### Variable 5: Annual Maintenance Cost
- Name: `annual_maintenance`
- Type: Constant
- Value: `200` (Estimated annual maintenance)

## Panel 1: Current Month Actual Cost

**Data Source:** pwdusage
**Visualization:** Stat
**Query:**
```
Endpoint: /usage
Parameters: period=monthly&metric=total_cost
```

**Panel Options:**
- Unit: currency (USD)
- Decimals: 2
- Title: "Current Month Energy Cost"
- Description: "Actual electricity cost this month"

## Panel 2: Current Month Baseline (Without Solar)

**Data Source:** InfluxDB
**Visualization:** Stat
**Query:**
```sql
SELECT sum("home") * ${baseline_rate} as "Baseline Cost"
FROM "powerwall"."kwh"."http"
WHERE time >= now() - 30d
GROUP BY time(1M)
```

**Panel Options:**
- Unit: currency (USD)
- Decimals: 2
- Title: "Est. Cost Without Solar"
- Description: "What you'd pay without solar/Powerwall"

## Panel 3: Current Month Savings

**Data Source:** Mixed (InfluxDB + calculation)
**Visualization:** Stat
**Query:**
```sql
SELECT
  (sum("home") * ${baseline_rate}) - actual_cost as "Monthly Savings"
FROM "powerwall"."kwh"."http"
WHERE time >= now() - 30d
```

**Panel Options:**
- Unit: currency (USD)
- Decimals: 2
- Color: Green if positive
- Title: "This Month Savings"
- Description: "Baseline - Actual"

## Panel 4: Year-to-Date Savings

**Data Source:** InfluxDB
**Visualization:** Stat
**Query:**
```sql
SELECT
  sum("home") * ${baseline_rate} as "YTD Baseline"
FROM "powerwall"."kwh"."http"
WHERE time >= now() - 1y
GROUP BY time(1y)
```

**Calculation:**
Subtract YTD actual costs from pwdusage service.

**Panel Options:**
- Unit: currency (USD)
- Decimals: 0
- Title: "Year-to-Date Savings"

## Panel 5: Lifetime Savings

**Data Source:** InfluxDB
**Visualization:** Stat
**Query:**
```sql
SELECT
  sum("home") * ${baseline_rate} as "Lifetime Baseline"
FROM "powerwall"."kwh"."http"
WHERE time >= '${install_date}'
```

**Panel Options:**
- Unit: currency (USD)
- Decimals: 0
- Title: "Lifetime Savings"
- Description: "Total savings since installation"

## Panel 6: Net Investment

**Data Source:** N/A (calculated value)
**Visualization:** Stat
**Value:**
```
${initial_investment} * (1 - ${tax_credit})
```

**Panel Options:**
- Unit: currency (USD)
- Decimals: 0
- Title: "Net System Cost"
- Description: "After federal tax credit"

## Panel 7: Payback Progress

**Data Source:** Mixed
**Visualization:** Gauge
**Query:**
```sql
SELECT
  (lifetime_savings / (${initial_investment} * (1 - ${tax_credit}))) * 100
  as "Payback Percentage"
```

**Panel Options:**
- Unit: percent (0-100)
- Max: 100
- Thresholds:
  - 0-25%: Red
  - 25-75%: Yellow
  - 75-100%: Green
- Title: "ROI Progress"

## Panel 8: Estimated Payback Date

**Data Source:** Mixed
**Visualization:** Stat
**Calculation:**
```
Net Investment = ${initial_investment} * (1 - ${tax_credit})
Monthly Savings = (Current Month Baseline - Current Month Actual)
Months to Payback = Net Investment / Monthly Savings
Payback Date = Install Date + Months to Payback
```

**Panel Options:**
- Display: Date format
- Title: "Estimated Payback Date"

## Panel 9: Monthly Cost Comparison (Time Series)

**Data Source:** InfluxDB + pwdusage
**Visualization:** Time series
**Queries:**

Query A (Baseline):
```sql
SELECT sum("home") * ${baseline_rate} as "Without Solar"
FROM "powerwall"."kwh"."http"
WHERE $timeFilter
GROUP BY time(1M)
```

Query B (Actual):
```
Endpoint: /usage
Parameters: period=monthly&metric=total_cost
```

**Panel Options:**
- Unit: currency (USD)
- Legend: Bottom
- Title: "Monthly Cost Comparison"
- Y-axis: $0 to auto

## Panel 10: Daily Energy Flow & Cost

**Data Source:** InfluxDB
**Visualization:** Time series (stacked)
**Queries:**

Query A (Grid Import):
```sql
SELECT sum("from_grid") as "Grid Import"
FROM "powerwall"."kwh"."http"
WHERE $timeFilter
GROUP BY time(1d)
```

Query B (Solar Generation):
```sql
SELECT sum("solar") as "Solar"
FROM "powerwall"."kwh"."http"
WHERE $timeFilter
GROUP BY time(1d)
```

Query C (Battery Discharge):
```sql
SELECT sum("from_pw") as "Battery"
FROM "powerwall"."kwh"."http"
WHERE $timeFilter
GROUP BY time(1d)
```

**Panel Options:**
- Unit: kWh
- Stack: Normal
- Title: "Daily Energy Mix"

## Panel 11: Peak vs Off-Peak Usage

**Data Source:** pwdusage
**Visualization:** Pie chart
**Query:**
```
Endpoint: /usage
Parameters: period=monthly&breakdown=time_of_use
```

**Panel Options:**
- Legend: Values + Percentages
- Title: "Peak vs Off-Peak Distribution"

## Panel 12: 25-Year Projection

**Data Source:** Calculated
**Visualization:** Table
**Calculation:**

For each year 1-25:
```
Year N Savings = Year 1 Savings * (1.05)^(N-1)
// Assuming 5% annual rate increase
```

Cumulative Savings = Sum of all years
Net Benefit = Cumulative Savings - Net Investment

**Panel Options:**
- Columns: Year, Annual Savings, Cumulative Savings
- Format: Currency
- Title: "Long-term Savings Projection"

## Panel 13: Carbon Offset

**Data Source:** InfluxDB
**Visualization:** Stat
**Query:**
```sql
SELECT
  sum("solar") * 0.35 as "CO2 Avoided (kg)"
FROM "powerwall"."kwh"."http"
WHERE time >= '${install_date}'
```

**Panel Options:**
- Unit: kg
- Decimals: 0
- Title: "Lifetime CO2 Offset"
- Description: "Based on California grid carbon intensity"

## Panel 14: Monthly Savings Trend

**Data Source:** InfluxDB + pwdusage
**Visualization:** Bar gauge
**Query:**
```sql
SELECT
  (sum("home") * ${baseline_rate}) - actual_cost as "Savings"
FROM "powerwall"."kwh"."http"
WHERE time >= now() - 12M
GROUP BY time(1M)
```

**Panel Options:**
- Orientation: Horizontal
- Display mode: Gradient
- Title: "12-Month Savings Trend"

## Panel 15: Export Credits Summary

**Data Source:** InfluxDB
**Visualization:** Stat
**Query:**
```sql
SELECT
  sum("to_grid") * 0.45 as "Export Credits"
FROM "powerwall"."kwh"."http"
WHERE time >= now() - 1M
GROUP BY time(1M)
```

**Panel Options:**
- Unit: currency (USD)
- Decimals: 2
- Title: "This Month Export Credits"
- Description: "Net metering credits"

## Complete Dashboard Layout Suggestion

```
Row 1 (Stats):
[Net Investment] [Payback Progress] [Lifetime Savings] [Estimated Payback Date]

Row 2 (Current Month):
[Current Month Cost] [Baseline Cost] [Monthly Savings] [Export Credits]

Row 3 (Time Series):
[Monthly Cost Comparison - Full Width]

Row 4 (Details):
[Daily Energy Flow & Cost - 2/3 width] [Peak vs Off-Peak Usage - 1/3 width]

Row 5 (Trends):
[Monthly Savings Trend - Full Width]

Row 6 (Projections):
[25-Year Projection - 3/4 width] [Carbon Offset - 1/4 width]
```

## Alerts to Configure

### Alert 1: High Peak Usage
Trigger when peak usage exceeds threshold:
```sql
SELECT sum("from_grid") as "Peak Import"
FROM "powerwall"."raw"."http"
WHERE time >= now() - 1h AND time >= '16:00' AND time < '21:00'
HAVING sum > 5
```

### Alert 2: Low Solar Production
Trigger when daily solar is below expected:
```sql
SELECT sum("solar")
FROM "powerwall"."kwh"."http"
WHERE time >= now() - 1d
HAVING sum < 20  // Adjust based on your system size
```

### Alert 3: Battery Not Discharging During Peak
Check if battery is being utilized during expensive peak hours:
```sql
SELECT mean("from_pw")
FROM "powerwall"."raw"."http"
WHERE time >= now() - 1h AND time >= '16:00' AND time < '21:00'
HAVING mean < 0.5  // Battery should be discharging
```

## Tips for Accuracy

1. **Verify baseline rate** - Calculate your actual average rate from pre-solar bills
2. **Update rates seasonally** - PG&E rates change with seasons
3. **Account for CCA rates** - If you're served by EBCE, MCE, PCE, or SJCE
4. **Include all fees** - Don't forget transmission charges and taxes
5. **Track rate changes** - PG&E adjusts rates several times per year
6. **Compare to bills** - Validate calculations against actual PG&E bills monthly

## Exporting Data

To export TCO data for spreadsheet analysis:

```bash
# Export monthly savings data
docker exec -it influxdb influx -database powerwall -execute \
  "SELECT sum(home) * 0.45 as baseline, time
   FROM kwh.http
   WHERE time > '2024-01-01'
   GROUP BY time(1M)" \
  -format csv > tco_data.csv
```

## Integration with Tesla App

Compare dashboard data with Tesla app:
- Tesla App shows: Solar production, home consumption, grid import/export
- Dashboard adds: Cost calculations, savings, ROI tracking
- Use both for complete picture

---

**Note:** All calculations are estimates. Actual savings depend on:
- Actual PG&E rates and rate changes
- Your specific rate schedule and baseline allowance
- Seasonal variations
- System performance
- Usage patterns
- Grid reliability and PSPS events
