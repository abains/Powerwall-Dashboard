# PGE TOU-C Total Cost of Ownership Calculator

This package provides a complete solution for calculating and tracking the Total Cost of Ownership (TCO) for your Tesla Solar and Powerwall system using PG&E's TOU-C rate plan in the Bay Area.

## Quick Start

1. **Install the pwdusage service** (see [PGE-TOU-C-SETUP.md](PGE-TOU-C-SETUP.md))
2. **Configure your rates** using `pge-tou-c-bayarea.json`
3. **Import Grafana dashboards** using the configurations in [TCO-Dashboard-PGE.md](TCO-Dashboard-PGE.md)
4. **Track your savings** and calculate payback period

## Files Included

### Configuration Files
- **pge-tou-c-bayarea.json** - Pre-configured PG&E TOU-C rate schedule for Bay Area
  - Summer rates (June-September)
  - Winter rates (October-May)
  - Peak hours: 4-9 PM daily
  - Off-peak: All other hours
  - Baseline (Tier 1) rates included

### Documentation
- **PGE-TOU-C-SETUP.md** - Complete setup guide
  - Step-by-step installation instructions
  - Rate customization guide
  - Troubleshooting section
  - Example calculations

- **TCO-Dashboard-PGE.md** - Grafana dashboard configuration
  - 15 pre-configured panels
  - InfluxDB queries
  - Dashboard layout suggestions
  - Alert configurations

- **README-PGE-TCO.md** - This file

## What You'll Track

### Financial Metrics
- **Monthly actual cost** - What you're paying PG&E
- **Baseline cost** - What you'd pay without solar/Powerwall
- **Monthly savings** - Difference between baseline and actual
- **Lifetime savings** - Total savings since installation
- **ROI progress** - Percentage of system cost recovered
- **Payback date** - Estimated date of full cost recovery
- **25-year projection** - Long-term financial benefit

### Energy Metrics
- **Peak vs off-peak usage** - Time-of-use distribution
- **Solar generation** - Daily/monthly production
- **Battery performance** - Charge/discharge patterns
- **Grid import/export** - Net energy from grid
- **Self-consumption** - Solar energy used directly

### Environmental Metrics
- **Carbon offset** - CO2 emissions avoided
- **Equivalent trees planted** - Environmental impact visualization

## Rate Information

### Current PG&E TOU-C Rates (2025)

**Peak Hours:** 4-9 PM Every Day

**Summer (June 1 - September 30):**
| Tier | Off-Peak | Peak (4-9 PM) |
|------|----------|---------------|
| Below Baseline | $0.39/kWh | $0.49/kWh |
| Above Baseline | $0.51/kWh | $0.61/kWh |

**Winter (October 1 - May 31):**
| Tier | Off-Peak | Peak (4-9 PM) |
|------|----------|---------------|
| Below Baseline | $0.35/kWh | $0.44/kWh |
| Above Baseline | $0.46/kWh | $0.56/kWh |

**Daily Service Charge:** ~$1.58/day (~$0.06575/hour)

**Note:** Rates are approximate and may vary by:
- Climate zone (P, Q, R, S, T, V, W, X, Y, Z)
- Community Choice Aggregation (EBCE, MCE, PCE, SJCE)
- Rate adjustments and temporary credits

## Prerequisites

- Powerwall Dashboard installed and running
- Docker and docker-compose
- InfluxDB with at least 30 days of data for accurate calculations
- Your PG&E account information:
  - Current rate schedule
  - Baseline allowance (kWh/day)
  - Climate zone
  - Average monthly usage before solar

## Installation

### Option 1: Automated Setup
```bash
cd ~/Powerwall-Dashboard/tools/usage-service
./build.sh
cd ~/Powerwall-Dashboard
# Add pwdusage service to powerwall.extend.yml (see setup guide)
./compose-dash.sh up -d pwdusage
```

### Option 2: Manual Setup
Follow the detailed instructions in [PGE-TOU-C-SETUP.md](PGE-TOU-C-SETUP.md)

## Configuration

### 1. Customize Rates
Edit `pge-tou-c-bayarea.json`:

```json
{
  "settings": {
    "timezone": "America/Los_Angeles",
    "cost_unit": "$",
    ...
  },
  "calendar": {
    "2025-06-01": {
      "tariffs": {
        "Peak": {
          "GRID_SUPPLY": -0.49,  // Your peak rate
          ...
        }
      }
    }
  }
}
```

### 2. Set Dashboard Variables
In Grafana, configure:
- `initial_investment` - Your system cost
- `tax_credit` - Federal ITC percentage (0.30 for 30%)
- `install_date` - System activation date
- `baseline_rate` - Estimated avg rate without solar
- `annual_maintenance` - Yearly maintenance cost

### 3. Import Dashboards
Import the pre-built dashboards or create custom panels using queries from [TCO-Dashboard-PGE.md](TCO-Dashboard-PGE.md)

## Understanding Your TCO

### Simple TCO Formula
```
Net System Cost = Initial Investment - (Federal Tax Credit + State Incentives)
Annual Savings = Baseline Annual Cost - Actual Annual Cost
Payback Period = Net System Cost / Annual Savings
25-Year Benefit = (25 × Annual Savings × Growth Factor) - Net System Cost
```

### Example Calculation
- System Cost: $40,000
- Federal Tax Credit: $12,000 (30%)
- Net Cost: $28,000
- Monthly baseline (without solar): $250
- Monthly actual (with solar): $50
- Monthly savings: $200
- Annual savings: $2,400

**Results:**
- Payback Period: 11.7 years
- 25-Year Savings: ~$109,000
- Net 25-Year Benefit: ~$81,000

## Optimization Tips

### Maximize Savings
1. **Peak Shaving** - Use battery during 4-9 PM to avoid expensive peak rates
2. **Load Shifting** - Run appliances during off-peak hours
3. **Self-Consumption** - Use solar directly rather than export/import
4. **Baseline Management** - Stay under baseline allowance when possible

### Battery Strategy for TOU-C
```
Off-Peak (12 AM - 4 PM):
  - Charge from solar (free)
  - Don't charge from grid unless necessary

Peak (4 PM - 9 PM):
  - Discharge to power home
  - Avoid grid import at $0.49-0.61/kWh
  - Maximize savings

Late Evening (9 PM - 12 AM):
  - Allow battery to rest
  - Use remaining solar if available
```

## Monitoring and Maintenance

### Weekly
- Check battery discharge during peak hours
- Verify solar production is as expected
- Review any anomalies in usage patterns

### Monthly
- Compare dashboard to actual PG&E bill
- Verify cost calculations are accurate
- Adjust baseline rate if needed
- Track savings trend

### Quarterly
- Update rates if PG&E has adjusted them
- Check for new incentives or programs
- Review optimization opportunities
- Calculate YTD ROI

### Annually
- Update annual projections
- Review long-term performance
- Consider system upgrades if beneficial
- File tax documents for ITC

## Troubleshooting

### Dashboard shows $0 cost
- Check pwdusage service is running: `docker logs pwdusage`
- Verify InfluxDB has data for selected time range
- Confirm rate configuration has dates in correct format

### Savings seem too high/low
- Verify baseline_rate matches your pre-solar average
- Check if you're in a CCA area (different rates)
- Confirm peak/off-peak periods are correct
- Compare to actual PG&E bills

### Payback date seems wrong
- Double-check initial_investment amount
- Verify tax_credit percentage (0.30 = 30%)
- Ensure install_date is correct
- Confirm annual savings calculation

## Bay Area Specific Considerations

### Community Choice Aggregation
If you're served by a CCA, adjust rates:
- **EBCE** (East Bay) - Often 1-2¢ less than PG&E
- **MCE** (Marin/Napa) - Competitive with PG&E
- **PCE** (Peninsula) - Similar to PG&E
- **SJCE** (San Jose) - Often slightly less than PG&E

### Climate Zones
Bay Area includes multiple zones:
- **Zone P** (San Francisco) - Lower baseline
- **Zone R** (Peninsula) - Moderate baseline
- **Zone X** (East Bay) - Moderate to high baseline

Check your PG&E bill for your specific zone.

### PSPS Events
Public Safety Power Shutoffs make battery backup especially valuable:
- Track outage frequency
- Calculate backup value (~$50-100 per avoided outage)
- Include in TCO calculation as "insurance benefit"

## Advanced Features

### Time-of-Use Optimization
Use Grafana alerts to optimize battery usage:
- Alert when battery isn't discharging during peak
- Notify if charging from grid during peak
- Track missed savings opportunities

### Rate Forecast
Model future savings with rate increases:
```python
Year N = Base Savings × (1 + rate_increase)^N
# PG&E historically increases 3-7% annually
```

### Solar Production Tracking
Compare actual vs expected:
```sql
Expected Daily = System Size (kW) × 4-5 hours × 365 days
Actual = sum(solar) from InfluxDB
Performance Ratio = Actual / Expected
```

## Resources

### Official PG&E
- Rate Plans: https://www.pge.com/en/account/rate-plans.html
- TOU-C Details: https://www.pge.com/tariffs/assets/pdf/tariffbook/ELEC_SCHEDS_E-TOU-C.pdf
- Baseline Allowance: https://www.pge.com/en/account/rate-plans/how-rates-work/baseline-allowance.html

### Tools
- Location/Climate Zone Finder: https://jasonacox.github.io/Powerwall-Dashboard/location.html
- pwdusage GitHub: https://github.com/BuongiornoTexas/pwdusage
- Tesla App: Monitor system performance

### Community
- Powerwall Dashboard: https://github.com/jasonacox/Powerwall-Dashboard
- Issues/Discussions: https://github.com/jasonacox/Powerwall-Dashboard/discussions

## Support

For questions or issues:
1. Check the troubleshooting section
2. Review [PGE-TOU-C-SETUP.md](PGE-TOU-C-SETUP.md)
3. Search existing GitHub issues
4. Post in GitHub Discussions

## Updates

This configuration is based on 2025 PG&E TOU-C rates. Update when:
- PG&E adjusts rates (typically 2-3 times per year)
- You switch rate plans
- Your CCA changes rates
- Federal/state incentives change

---

**Version:** 1.0
**Last Updated:** 2025-11-13
**Rate Schedule:** PG&E E-TOU-C 2025
**Region:** San Francisco Bay Area, California
