# PG&E EV2-A Rate Configuration

This file contains a sample configuration for the PG&E EV2-A (Home Charging EV2-A) time-of-use rate plan covering years 2020-2025.

## Rate Structure

The PG&E EV2-A plan has the following time-of-use structure that applies **every day** including weekends and holidays:

### Time Periods
- **Off-Peak**: 12:00 AM - 3:00 PM (15 hours)
- **Part-Peak**: 3:00 PM - 4:00 PM and 9:00 PM - 12:00 AM (4 hours)
- **Peak**: 4:00 PM - 9:00 PM (5 hours)

### Seasonal Definitions
- **Summer Season**: June 1 - September 30
- **Winter Season**: October 1 - May 31

## File Overview

The `pge_ev2a_usage.json` file includes:

1. **Settings**: Configured for Pacific timezone (America/Los_Angeles) with standard Powerwall Dashboard integration
2. **Plan Definition**: PGE-EV2A plan with proper time periods for both Summer and Winter seasons
3. **Calendar Entries**: Rate data for each year from 2020 through 2025, with seasonal transitions

## Rate Values

The rates in this file are based on historical PG&E EV2-A pricing and include estimated values for:
- Grid supply costs (negative values representing money spent)
- Grid export credits (positive values representing money earned)
- Self-consumption values (positive values representing savings)
- Supply charges ($15/month = $0.4838709677/day)

### Important Notes

1. **Verify Rates**: The rates included are approximate and based on public PG&E data. You should verify these against your actual PG&E bills and update them accordingly.

2. **Grid Export Rates**: The export rate (NEM/Net Energy Metering) of $0.03/kWh is a conservative estimate. Your actual export credit may vary based on:
   - Your NEM status (NEM 2.0, NEM 3.0, etc.)
   - Time-of-use export rates
   - Your specific service agreement

3. **Rate Updates**: PG&E rates change periodically. Check your bills for rate changes and update the configuration accordingly.

4. **Supply Charge**: The daily supply charge is calculated as $15/month ÷ 31 days = $0.4838709677/day

## Usage

1. Copy or rename `pge_ev2a_usage.json` to `usage.json` in your pwdusage configuration directory
2. Update the rates to match your actual PG&E bills
3. Adjust the `influx_url` and other settings as needed for your setup
4. Restart the pwdusage service to apply the new configuration

## Configuration Details

### Timezone
Set to `America/Los_Angeles` for Pacific Time. Adjust if you're in a different timezone.

### Year Anchor
Set to `JAN` to align with calendar year. This can be adjusted if you prefer fiscal year reporting.

### Supply Priority
The configuration prioritizes grid supply over battery and solar, which is standard for cost calculations. Adjust based on your preferences.

## Additional Resources

- [PG&E EV Rate Plans](https://www.pge.com/en/account/rate-plans/electric-vehicles.html)
- [pwdusage Documentation](https://github.com/BuongiornoTexas/pwdusage)
- [Powerwall Dashboard](https://github.com/jasonacox/Powerwall-Dashboard)

## Rate History Coverage

This configuration provides calendar entries for:
- **2020**: Full year with seasonal transitions
- **2021**: Full year with seasonal transitions
- **2022**: Full year with seasonal transitions
- **2023**: Full year with seasonal transitions
- **2024**: Full year with seasonal transitions (based on current 2024 rates)
- **2025**: Full year with projected rates

Each year includes:
- Winter season start (January 1 or October 1)
- Summer season start (June 1)
- Updated tariff rates reflecting approximate annual rate increases

## Customization

To customize this configuration:

1. **Update Rates**: Modify the GRID_SUPPLY, GRID_EXPORT, and other tariff values in the calendar section
2. **Add Future Years**: Follow the same pattern to add entries for years beyond 2025
3. **Adjust Time Periods**: Modify the periods in the plans section if PG&E changes their time-of-use structure
4. **Change Seasons**: Update season definitions if PG&E modifies their seasonal boundaries
