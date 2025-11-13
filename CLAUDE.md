# CLAUDE.md - AI Assistant Guide for Powerwall Dashboard

## Project Overview

**Powerwall Dashboard** is a comprehensive monitoring solution for Tesla Solar and Powerwall systems. It provides real-time and historical data visualization using a modern containerized stack consisting of Grafana (visualization), InfluxDB (time-series database), Telegraf (metrics collection), and pyPowerwall (Tesla API proxy).

**Key Features:**
- Real-time power flow monitoring (solar, battery, grid, home)
- Historical data with automatic downsampling
- Multiple deployment modes (Local Access, Tesla Cloud, FleetAPI, Extended TEDAPI)
- Support for Powerwall 1/2/+/3 and solar-only systems
- Optional weather data integration
- Animated power flow visualization

**Version:** Check `/VERSION` file for current version

**Repository:** https://github.com/jasonacox/Powerwall-Dashboard

---

## Technology Stack

### Core Services (Docker Containers)

1. **InfluxDB 1.8** - Time-series database
   - Port: 8086
   - Stores power metrics with multiple retention policies
   - Uses continuous queries for data downsampling

2. **pypowerwall** (v0.14.1+) - Tesla API Proxy
   - Port: 8675
   - Provides unified API for Tesla Powerwall/Solar data
   - Supports local (LAN), cloud, and TEDAPI modes
   - Repository: https://github.com/jasonacox/pypowerwall

3. **Telegraf 1.28.2** - Metrics Collection
   - Polls pypowerwall API every 5 seconds
   - Writes data to InfluxDB
   - Configurable via `telegraf.conf`

4. **Grafana 9.1.2** - Visualization Dashboard
   - Port: 9000
   - Default credentials: admin/admin
   - Pre-configured dashboards in `/dashboards/`

5. **weather411** (v0.2.3) - Optional Weather Service
   - Port: 8676
   - Integrates OpenWeatherMap data
   - Repository: https://hub.docker.com/r/jasonacox/weather411

### Languages and Tools

- **Shell Scripts** (bash) - Setup, upgrade, maintenance scripts
- **Python** - pypowerwall service, weather service, utility scripts
- **TOML** - Telegraf configuration
- **SQL** - InfluxDB queries and continuous queries
- **JSON** - Grafana dashboards, configuration
- **Docker Compose** - Container orchestration

---

## Repository Structure

```
Powerwall-Dashboard/
├── README.md              # Main documentation
├── RELEASE.md            # Release notes and changelog
├── VERSION               # Current version number
├── WINDOWS.md           # Windows-specific setup instructions
├── LICENSE              # Apache 2.0 license
│
├── *.sh                 # Main utility scripts (see below)
├── *.yml                # Docker compose configuration
├── *.conf               # Service configurations
├── *.env.sample         # Environment variable templates
│
├── .auth/               # pypowerwall authentication cache
├── backups/             # Backup scripts and tools
├── dashboards/          # Grafana dashboard JSON files
│   ├── dashboard.json              # Main animated dashboard
│   ├── dashboard-no-animation.json # No animation variant
│   ├── dashboard-simple.json       # Simple variant
│   ├── dashboard-solar-only.json   # Solar-only systems
│   └── archive/                    # Historical dashboard versions
│
├── grafana/             # Grafana data directory (gitignored except templates)
│   └── sunandmoon-template.yml    # Data source template
│
├── influxdb/            # InfluxDB configuration and data
│   ├── influxdb.sql               # Database schema and continuous queries
│   └── check_cq_health.py         # Continuous query health checker
│
├── weather/             # Weather service configuration
│   ├── server.py                  # Weather411 server
│   └── weather411.conf.sample     # Weather API configuration template
│
└── tools/               # Additional utilities and integrations
    ├── DOCKER.md                  # Docker installation guide
    ├── README.md                  # Tools overview
    ├── ecowitt-weather-history/   # Import Ecowitt weather data
    ├── energy/                    # Energy monitoring tools
    ├── export/                    # Data export utilities
    ├── fixmonthtags/             # Fix month/year tags in InfluxDB
    ├── influxdb-viewer/          # Web-based InfluxDB data viewer
    ├── influxdb2/                # InfluxDB 2.x migration tools
    ├── k3s/                      # Kubernetes deployment configs
    ├── mysql/                    # MySQL integration
    ├── pvoutput/                 # PVOutput.org integration
    ├── pwstatus/                 # Powerwall status display
    ├── solar-only/               # Solar-only system configs
    ├── switch-mode/              # Mode switching utilities
    ├── tesla-history/            # Import historical Tesla data
    ├── usage-service/            # Usage analysis tools
    └── weather-history/          # Import historical weather data
```

---

## Key Scripts and Their Purposes

### Main Scripts (Root Directory)

| Script | Purpose | Usage |
|--------|---------|-------|
| `setup.sh` | Interactive setup wizard | `./setup.sh` |
| `upgrade.sh` | Upgrade to latest version | `./upgrade.sh` |
| `verify.sh` | Verify installation health | `./verify.sh [--logs\|--no-logs]` |
| `compose-dash.sh` | Docker compose wrapper | `./compose-dash.sh [up\|down\|restart]` |
| `tz.sh` | Update timezone across all configs | `./tz.sh "America/Los_Angeles"` |
| `watchdog.sh` | Monitor/restart unhealthy containers | `./watchdog.sh [-enable\|-disable]` |
| `weather.sh` | Setup weather integration | `./weather.sh` |
| `add_route.sh` | Configure TEDAPI routing | `./add_route.sh [-disable]` |
| `ver.sh` | Display version information | `./ver.sh` |

### Script Details

**setup.sh** - Primary installation script
- Detects and validates Docker installation
- Prompts for deployment mode (Local/Cloud/FleetAPI/TEDAPI)
- Collects timezone, credentials, and configuration
- Creates `.env` files from samples
- Initializes InfluxDB with schema
- Auto-provisions Grafana data sources (v4.5.0+)
- Validates file permissions

**upgrade.sh** - Upgrade automation
- Backs up current configuration
- Pulls latest code from git
- Preserves user settings
- Updates Docker images
- Applies database migrations if needed
- Handles version-specific upgrade logic

**verify.sh** - Health check utility
- Tests Docker and Docker Compose availability
- Verifies container health status
- Checks port availability (8086, 8675, 9000)
- Validates pypowerwall connectivity
- Optionally displays container logs
- Provides troubleshooting guidance

**compose-dash.sh** - Docker Compose wrapper
- Determines Docker Compose version (v1 vs v2)
- Loads environment variables from `compose.env`
- Supports optional `powerwall.extend.yml` for customizations
- Pass-through for all docker-compose commands

---

## Configuration Files

### Environment Files (Created from .sample files)

**pypowerwall.env** - Tesla API configuration
```bash
PW_EMAIL=              # Tesla account email (leave blank for TEDAPI-only)
PW_PASSWORD=           # Tesla account password (leave blank for TEDAPI-only)
PW_HOST=               # Gateway IP (192.168.91.1 for TEDAPI, or LAN IP)
PW_TIMEZONE=           # Timezone (e.g., America/Los_Angeles)
PW_DEBUG=no            # Debug logging (yes/no)
PW_STYLE=grafana-dark  # Power flow animation style
PW_GW_PWD=             # Gateway WiFi password (for TEDAPI mode)
TZ=                    # Timezone (should match PW_TIMEZONE)
```

**compose.env** - Docker service configuration
```bash
INFLUXDB_PORTS=8086:8086
PYPOWERWALL_PORTS=8675:8675
GRAFANA_PORTS=9000:9000
WEATHER411_PORTS=8676:8676
PWD_USER=1000:1000     # UID:GID for container processes
```

**influxdb.env** - InfluxDB initialization (rarely modified)

**grafana.env** - Grafana configuration
```bash
GF_SERVER_HTTP_PORT=9000
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=admin
# Optional: SMTP, HTTPS, alerting configs
```

**telegraf.local** - Custom Telegraf inputs (user-defined)
- Add custom measurements here
- Not overwritten by upgrades
- TOML format

---

## Deployment Modes

The dashboard supports 4 deployment modes:

### 1. Local Access (Default)
- For Powerwall 1, 2, + with LAN gateway access
- Direct connection to Tesla Energy Gateway
- Requires gateway IP on local network
- Best performance and most metrics

### 2. Tesla Cloud (Unofficial API)
- For systems without LAN access or solar-only
- Uses unofficial Tesla Owner API
- Requires Tesla account credentials
- Less detailed than local mode

### 3. FleetAPI Cloud (Official API)
- Uses Tesla's official Fleet API
- Requires Tesla account and API registration
- Similar to Tesla Cloud mode

### 4. Extended Metrics (TEDAPI)
- For Powerwall 2/+/3 with WiFi access point connection
- Accesses TEDAPI endpoint at 192.168.91.1
- Requires direct WiFi connection to Powerwall
- Needs Gateway WiFi password (from QR code)
- Provides additional device vitals and metrics
- **Powerwall 3**: Must use this mode (full TEDAPI)

**Important TEDAPI Notes:**
- Firmware 25.10.1+ requires direct WiFi AP connection
- Gateway 1 systems incompatible (requires power toggle)
- Powerwall 3 password is on the PW3 itself, not Gateway
- Test access: `curl -k --head https://192.168.91.1`

---

## InfluxDB Schema

### Retention Policies

| Policy | Duration | Purpose |
|--------|----------|---------|
| raw | 3 days | High-frequency raw data (5s interval) |
| autogen | infinite | 1-minute aggregates |
| kwh | infinite | Hourly energy totals |
| daily | infinite | Daily energy totals |
| monthly | infinite | Monthly energy totals |
| strings | infinite | Solar string metrics |
| pwtemps | infinite | Powerwall temperatures |
| vitals | infinite | Device vitals (voltage, frequency, current) |
| grid | infinite | Grid status |
| alerts | infinite | System alerts |
| pod | infinite | Pod-level metrics |
| fans | infinite | Fan status |

### Continuous Queries (CQ)

InfluxDB uses continuous queries to automatically downsample data:
- `cq_autogen`: Raw → 1-minute averages
- `cq_kwh`: 1-minute → hourly kWh
- `cq_daily`: hourly → daily kWh
- `cq_monthly`: daily → monthly kWh
- `cq_strings`: String metrics downsampling
- `cq_vitals*`: Device vitals downsampling
- `cq_pw_temps*`: Temperature downsampling

**Location:** `/influxdb/influxdb.sql`

**Timezone:** All CQs use timezone specified during setup (default: America/Los_Angeles)

---

## Development Workflows

### Making Configuration Changes

1. **Environment Variables:**
   ```bash
   # Edit the appropriate .env file
   vim pypowerwall.env

   # Restart affected container
   ./compose-dash.sh restart pypowerwall
   ```

2. **Timezone Changes:**
   ```bash
   # Use the timezone update script
   ./tz.sh "America/New_York"

   # Manually verify changes in:
   # - pypowerwall.env (PW_TIMEZONE, TZ)
   # - telegraf.conf (if timezone-specific configs)
   # - influxdb.sql (continuous queries)
   # - Grafana dashboards (import with new timezone)
   ```

3. **Telegraf Custom Metrics:**
   ```bash
   # Edit telegraf.local (created from telegraf.local.sample)
   vim telegraf.local

   # Restart telegraf
   ./compose-dash.sh restart telegraf
   ```

### Modifying Dashboards

1. Make changes in Grafana UI
2. Export dashboard as JSON
3. Save to `/dashboards/` directory
4. Commit to git for version control
5. Users import via Grafana UI after pulling updates

**Dashboard Guidelines:**
- Use variables for customization (timezone, cost per kWh)
- Include timezone prompt during import
- Test with different time ranges
- Validate queries against available retention policies

### Adding New Tools

1. Create subdirectory in `/tools/`
2. Add README.md with:
   - Purpose and description
   - Prerequisites
   - Setup instructions
   - Usage examples
   - Known limitations
3. Update `/tools/README.md` with entry
4. Include sample configuration files (*.sample)
5. Add to `.gitignore` if generates data files

---

## Docker Conventions

### Container Naming
- Containers use `container_name` for easy reference
- Names: `influxdb`, `pypowerwall`, `telegraf`, `grafana`, `weather411`

### User Permissions
- Containers run as `${PWD_USER:-1000:1000}` (non-root)
- Ensures file permissions match host user
- Override in `compose.env` if needed

### Volume Bindings
- Configuration files: read-only bind mounts
- Data directories: read-write bind mounts
- Allows editing configs on host without container rebuild

### Health Checks
All services implement health checks:
- **InfluxDB:** `curl -f http://influxdb:8086/health`
- **pypowerwall:** `wget --spider -q http://pypowerwall:8675/api/site_info`
- **Telegraf:** `pgrep telegraf`
- **Grafana:** `curl -f http://grafana:9000/api/health`
- **weather411:** `wget --spider -q http://weather411:8676/stats`

Health check parameters:
- Interval: 30s
- Timeout: 10s
- Retries: 3
- Start period: 30-60s (varies by service)

### Networking
- Default bridge network
- Services communicate via container names (Docker DNS)
- Ports exposed only for external access

### Image Updates
```bash
# Pull latest images
./compose-dash.sh pull

# Recreate containers with new images
./compose-dash.sh up -d
```

---

## Testing and Verification

### Health Verification

```bash
# Run comprehensive health check
./verify.sh

# Check specific container
docker logs -f pypowerwall

# Verify all containers running
docker ps

# Check container health status
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### API Testing

```bash
# Test pypowerwall proxy endpoints
curl http://localhost:8675/api/status       # Powerwall status
curl http://localhost:8675/api/meters/aggregates  # Power metrics
curl http://localhost:8675/soe              # Battery state of energy
curl http://localhost:8675/vitals           # Device vitals (if available)
curl http://localhost:8675/temps            # Temperatures
curl http://localhost:8675/strings          # String data (if Powerwall+)
curl http://localhost:8675/csv              # CSV export

# Test weather411 (if configured)
curl http://localhost:8676/                 # Current weather
curl http://localhost:8676/json             # JSON format
curl http://localhost:8676/stats            # Service stats
```

### Database Verification

```bash
# Access InfluxDB CLI
docker exec -it influxdb influx

# Inside InfluxDB CLI:
USE powerwall
SHOW RETENTION POLICIES
SHOW CONTINUOUS QUERIES
SELECT * FROM http ORDER BY time DESC LIMIT 10
SELECT COUNT(*) FROM autogen.http WHERE time > now() - 1h
```

### Continuous Query Health

```bash
# Run health check script
docker exec -it influxdb python3 /var/lib/influxdb/check_cq_health.py

# Check for CQ execution errors
docker exec -it influxdb influx -execute "SHOW QUERIES"
```

---

## Common Tasks for AI Assistants

### When Helping with Setup Issues

1. **Check Docker installation:**
   ```bash
   docker --version
   docker compose version  # or docker-compose --version
   ```

2. **Verify user permissions:**
   ```bash
   groups $USER  # Should include 'docker'
   ls -la  # Check write permissions
   ```

3. **Check if ports are available:**
   ```bash
   netstat -tuln | grep -E ':(8086|8675|9000)'
   ```

4. **Verify environment files exist:**
   ```bash
   ls -la *.env
   ```

### When Troubleshooting Connectivity

1. **Check pypowerwall logs for auth issues:**
   ```bash
   docker logs pypowerwall | grep -i error
   ```

2. **Verify Powerwall IP is reachable:**
   ```bash
   ping 192.168.91.1  # Or configured IP
   curl -k https://192.168.91.1  # For TEDAPI
   ```

3. **Test TEDAPI access (if applicable):**
   ```bash
   python3 -m pypowerwall scan
   python3 -m pypowerwall.tedapi  # Interactive test
   ```

### When Adding New Features

1. **Check if similar functionality exists in `/tools/`**
2. **Review RELEASE.md for recent changes**
3. **Ensure backward compatibility with existing configs**
4. **Test with both local and cloud modes if applicable**
5. **Update relevant documentation**
6. **Consider impact on upgrade.sh**

### When Modifying InfluxDB Schema

1. **Create migration script in `/influxdb/`**
2. **Name it `run-once-<description>.sql`**
3. **setup.sh automatically runs `run-once-*.sql` files**
4. **Mark as executed with `.done` suffix**
5. **Test with empty database AND existing data**
6. **Update upgrade.sh if schema changes affect existing data**

### When Working with Grafana Dashboards

1. **Import dashboard to Grafana for testing**
2. **Make changes in Grafana UI**
3. **Export and save to `/dashboards/`**
4. **Ensure variables are properly configured**
5. **Test with different timezones and date ranges**
6. **Update dashboard version/title if significant changes**

---

## File Permissions and Security

### Expected Ownership
- Configuration files: Owned by host user running setup
- Data directories: Owned by `PWD_USER` (default 1000:1000)
- Scripts: Executable permission for .sh files

### Sensitive Files (.gitignored)
- `*.env` - Environment variables with credentials
- `.auth/.pypowerwall.auth` - Tesla login session
- `.auth/.pypowerwall.site` - Site data cache
- `weather/weather411.conf` - Weather API keys
- `grafana/grafana.db` - Grafana database
- `influxdb/{data,wal,meta}/` - InfluxDB data

### Required Readable Files
```bash
chmod 644 *.conf *.env telegraf.local
chmod 755 *.sh
```

---

## Git Workflow Conventions

### Protected Files
Never commit:
- `*.env` files (use `*.env.sample` templates)
- Authentication cache (`.auth/`)
- Database data (`influxdb/data/`, `grafana/grafana.db`)
- Backup archives (`backups/*.tgz`)

### Branch Strategy
- `main` - Stable releases
- Feature branches - New functionality
- Release tags - Version markers (e.g., `v4.8.5`)

### Commit Message Style
Review recent commits for style:
```bash
git log --oneline -20
```

Typical format:
- Start with action verb (Add, Update, Fix, Remove)
- Be specific about what changed
- Reference issue numbers if applicable
- Examples:
  - "Update README.md with Powerwall 3 password location"
  - "Fix upgrade version #682"
  - "Add timezone validation in setup.sh"

---

## Timezone Handling

Timezones are critical for accurate data aggregation. They must be consistent across all components.

### Timezone Locations

1. **pypowerwall.env:**
   - `PW_TIMEZONE=America/Los_Angeles`
   - `TZ=America/Los_Angeles`

2. **influxdb.sql:**
   - Continuous queries use `tz('America/Los_Angeles')`

3. **Grafana Dashboards:**
   - Import-time variable prompt
   - User enters timezone when importing

### Valid Timezone Format
- IANA timezone database format
- Find yours: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
- Examples: `America/New_York`, `Europe/London`, `Asia/Tokyo`

### Changing Timezone
```bash
# Preferred method (updates all configs):
./tz.sh "America/Chicago"

# Manual method (update all locations above and restart):
./compose-dash.sh restart
```

---

## Upgrade Strategy

### User Upgrade Path
```bash
./upgrade.sh
```

### What upgrade.sh Does
1. Checks git status (warns if uncommitted changes)
2. Backs up current VERSION to `upgrade.log`
3. Pulls latest code from GitHub
4. Preserves existing `.env` files
5. Updates Docker images
6. Runs database migrations (run-once-*.sql)
7. Restarts containers
8. Displays changelog

### Handling Breaking Changes
- Review RELEASE.md before upgrading
- Major version changes may require manual steps
- Check for new `.sample` files indicating new configs
- Test in non-production environment if possible

### Rollback Procedure
```bash
# Stop containers
./compose-dash.sh down

# Restore from backup
cd backups/
# Extract backup archive (if available)

# Checkout previous version
git log --oneline
git checkout <previous-version-tag>

# Restart
./compose-dash.sh up -d
```

---

## pypowerwall Proxy API Reference

The pypowerwall container exposes these endpoints (port 8675):

### Core Endpoints
- `/api/status` - System status and firmware version
- `/api/meters/aggregates` - Current power metrics
- `/api/system_status/soe` - Battery state of energy (%)
- `/api/system_status/grid_status` - Grid connection status
- `/api/site_info` - Site configuration

### Extended Endpoints (if available)
- `/temps` - Powerwall temperatures
- `/vitals` - Device vitals (voltage, frequency, current)
- `/strings` - Solar string data (Powerwall+ only)
- `/alerts` - System alerts

### Utility Endpoints
- `/stats` - Proxy statistics
- `/csv` - Power data in CSV format
- `/help` - API documentation
- `/health` - Health check (with detailed stats)

### Aggregates Format
```json
{
  "site": {
    "instant_power": 1234,      // Grid power (negative = export)
    "instant_total_current": 5.2
  },
  "battery": {
    "instant_power": -500,      // Battery power (negative = charging)
    "instant_total_current": 2.1,
    "percentage": 85.5
  },
  "load": {
    "instant_power": 2000,      // Home consumption
    "instant_total_current": 8.3
  },
  "solar": {
    "instant_power": 3000,      // Solar production
    "instant_total_current": 12.5
  }
}
```

---

## Powerwall 3 Specific Notes

Powerwall 3 has significant differences from previous generations:

### Requirements
- **Must** use TEDAPI mode (option 4 in setup)
- Direct WiFi connection to Powerwall AP at 192.168.91.1
- Gateway WiFi password (found on PW3 unit, NOT Gateway)
- Leave `PW_EMAIL` and `PW_PASSWORD` blank in `pypowerwall.env`
- Set `PW_GW_PWD` to Powerwall 3 password

### Password Location
- **Powerwall 3:** On label under glass cover (visible during install)
- **NOT** the Gateway password
- If multiple PW3 units, use primary Powerwall password

### Connectivity
- Ethernet cable must connect to PW3, not Gateway 2
- Firmware 25.10.1+ blocks network routing to TEDAPI
- Must connect directly to WiFi AP
- See: https://github.com/jasonacox/Powerwall-Dashboard/discussions/607

### Limitations
- No legacy local APIs available
- All data comes from TEDAPI endpoint
- Some metrics calculated rather than direct from API

---

## Weather Integration

### Setup
1. Register at https://openweathermap.org (free tier available)
2. Verify email and generate API key
3. Copy `weather/weather411.conf.sample` to `weather/weather411.conf`
4. Edit configuration:
   ```ini
   [OpenWeatherMap]
   APIKEY = your_api_key_here
   LAT = 37.7749    # Your latitude
   LON = -122.4194  # Your longitude
   ```
5. Find coordinates: https://jasonacox.github.io/Powerwall-Dashboard/location.html
6. Run `./weather.sh` or restart containers

### Weather Data in Grafana
- Uses "Sun and Moon" data source
- Configure with your coordinates in Grafana
- Provides sunrise/sunset times, moon phase
- weather411 adds current conditions, forecasts

---

## Watchdog Service

Monitors container health and auto-restarts if unhealthy.

### Enable
```bash
./watchdog.sh -enable
# Adds cron job running every 5 minutes
```

### Disable
```bash
./watchdog.sh -disable
```

### What it Monitors
- Container running status
- Docker health check results
- Restarts only if container is unhealthy or stopped

### Logs
Check cron/syslog for watchdog activity:
```bash
grep watchdog /var/log/syslog
```

---

## Backups

Location: `/backups/`

### Available Backup Tools
- Manual backup scripts for InfluxDB data
- Automated backup suggestions in `/backups/README.md`

### Recommended Backup Strategy
1. **Configuration Files:**
   ```bash
   tar -czf config-backup-$(date +%Y%m%d).tgz *.env telegraf.local
   ```

2. **InfluxDB Data:**
   ```bash
   docker exec influxdb influxd backup -portable /var/lib/influxdb/backup
   docker cp influxdb:/var/lib/influxdb/backup ./backups/influxdb-backup-$(date +%Y%m%d)
   ```

3. **Grafana Dashboards:**
   - Already in git at `/dashboards/`
   - Optionally export custom dashboards from UI

### Restore
See individual backup script documentation in `/backups/`

---

## Common Error Scenarios

### "Invalid Powerwall Login"
- **Cause:** Incorrect credentials or password
- **Solution:** Try last 5 characters of password from QR code
- **For PW3:** Use password from PW3 unit, not Gateway

### "Cannot connect to 192.168.91.1"
- **Cause:** Not connected to Powerwall WiFi AP
- **Solution:** Connect directly to Powerwall WiFi or setup bridge
- **Firmware 25.10.1+:** Network routing disabled by Tesla

### "Docker permission denied"
- **Cause:** User not in docker group
- **Solution:**
  ```bash
  sudo usermod -aG docker $USER
  # Log out and back in
  ```

### "Port already in use"
- **Cause:** Another service using 8086, 8675, or 9000
- **Solution:**
  - Find conflicting service: `netstat -tuln | grep PORT`
  - Stop conflicting service or change port in `compose.env`

### "Influxdb error 139"
- **Cause:** InfluxDB incompatible with older Raspberry Pi models
- **Solution:** Use more recent hardware or try InfluxDB 2.x (see `/tools/influxdb2/`)

### "No data in Grafana"
- **Cause:** Multiple possible issues
- **Solution:**
  1. Check pypowerwall connectivity: `curl http://localhost:8675/api/status`
  2. Check Telegraf logs: `docker logs telegraf`
  3. Verify InfluxDB has data: `docker exec -it influxdb influx -execute "SELECT COUNT(*) FROM powerwall.raw.http"`
  4. Check Grafana data source configuration

### Gateway 1 Systems with TEDAPI
- **Issue:** Gateway 1 requires power toggle for TEDAPI access
- **Solution:** Use Local or Cloud mode instead
- **Reference:** https://github.com/jasonacox/Powerwall-Dashboard/issues/536

---

## Platform-Specific Notes

### Windows 11
- Requires WSL 2 (Windows Subsystem for Linux)
- Install Docker Desktop for Windows
- Run setup within WSL Ubuntu environment
- See `WINDOWS.md` for detailed instructions

### Synology NAS
- May have git version conflicts (`/usr/bin/git` vs `/opt/bin/git`)
- Adjust PATH to prioritize `/usr/bin/git`
- File permission issues common - ensure readable configs
- See: https://github.com/jasonacox/Powerwall-Dashboard/issues/22

### Rootless Docker
- Modify `PWD_USER` in `compose.env` to match rootless UID mapping
- May require custom volume paths
- See: https://github.com/jasonacox/Powerwall-Dashboard/issues/22#issuecomment-1254699603

### Raspberry Pi
- Use recent models (Pi 4+ recommended)
- Older models may have InfluxDB compatibility issues
- Monitor for SD card wear with frequent writes
- Consider USB SSD for database storage

---

## AI Assistant Best Practices

### Before Making Changes

1. **Read relevant documentation:**
   - README.md for user-facing info
   - RELEASE.md for recent changes
   - Related tool README in `/tools/`

2. **Check existing issues/discussions:**
   - Review GitHub issues for similar problems
   - Check discussions for community solutions

3. **Understand deployment mode:**
   - Local, Cloud, FleetAPI, or TEDAPI?
   - Different modes have different capabilities

### When Modifying Code

1. **Preserve user data:**
   - Never delete `.env` files
   - Don't modify `influxdb/data/` contents
   - Preserve `.auth/` directory

2. **Maintain backward compatibility:**
   - Don't break existing configurations
   - Support migration from previous versions
   - Update upgrade.sh if needed

3. **Test thoroughly:**
   - Test with fresh install (`./setup.sh`)
   - Test upgrade path (`./upgrade.sh`)
   - Verify with `./verify.sh`

4. **Follow conventions:**
   - Use existing code style
   - Match commit message format
   - Update VERSION file if releasing
   - Update RELEASE.md with changes

### When Helping Users

1. **Gather information:**
   - Docker version (`docker --version`)
   - Platform (Linux, Windows WSL, Synology, etc.)
   - Deployment mode (Local, Cloud, TEDAPI)
   - Powerwall model (1, 2, +, 3)
   - Error messages and logs

2. **Provide context-aware solutions:**
   - Different solutions for different modes
   - Platform-specific guidance
   - Version-specific issues

3. **Reference documentation:**
   - Link to relevant README sections
   - Point to GitHub issues/discussions
   - Cite specific configuration examples

4. **Suggest verification steps:**
   - Always recommend `./verify.sh` after changes
   - Suggest checking logs for specific containers
   - Provide test commands to confirm fixes

---

## Related Projects and Integrations

### Official Related Projects
- **pypowerwall:** https://github.com/jasonacox/pypowerwall
- **weather411:** https://hub.docker.com/r/jasonacox/weather411
- **Powerwall-Display:** https://github.com/jasonacox/Powerwall-Display (ESP32)

### Community Tools (in /tools/)
- **PVOutput Integration:** Upload to PVOutput.org
- **MySQL Export:** Replicate data to MySQL
- **Tesla History Import:** Import historical data
- **Usage Service:** Advanced usage analysis
- **InfluxDB2 Migration:** Move to InfluxDB 2.x

### Third-Party Apps
- **NetZero App:** iOS/Android monitoring app
- **Tesla App:** Official Tesla mobile app (limited data)

---

## Quick Reference Commands

### Service Management
```bash
# Start all services
./compose-dash.sh up -d

# Stop all services
./compose-dash.sh down

# Restart specific service
./compose-dash.sh restart pypowerwall

# View logs
docker logs -f pypowerwall
docker logs --tail 100 telegraf

# Check status
./verify.sh
docker ps
```

### Database Operations
```bash
# Access InfluxDB CLI
docker exec -it influxdb influx

# Import SQL file
docker exec -it influxdb influx -import -path=/var/lib/influxdb/influxdb.sql

# Backup database
docker exec influxdb influxd backup -portable /var/lib/influxdb/backup

# Check continuous query health
docker exec influxdb python3 /var/lib/influxdb/check_cq_health.py
```

### Configuration Updates
```bash
# Change timezone
./tz.sh "America/Denver"

# Re-run setup (preserves data)
./setup.sh

# Upgrade to latest
./upgrade.sh

# Update weather configuration
vim weather/weather411.conf
./compose-dash.sh restart weather411
```

### Troubleshooting
```bash
# Full verification
./verify.sh --logs

# Test pypowerwall connection
curl http://localhost:8675/api/status | jq

# Check InfluxDB for recent data
docker exec influxdb influx -execute "SELECT * FROM powerwall.raw.http ORDER BY time DESC LIMIT 5"

# Test TEDAPI access
curl -k --head https://192.168.91.1

# Restart unhealthy containers
docker ps --filter health=unhealthy
./compose-dash.sh restart <container_name>
```

---

## Version Information

- **Current Version:** See `/VERSION` file
- **Version Format:** `v4.8.5` (major.minor.patch)
- **Release Notes:** See `RELEASE.md`
- **Changelog:** Full history in git commits

### Version Compatibility
- **InfluxDB:** 1.8.x (migration to 2.x available in `/tools/influxdb2/`)
- **Grafana:** 9.1.2
- **Telegraf:** 1.28.2
- **pypowerwall:** v0.14.1+ (see RELEASE.md for minimum version)
- **Python:** 3.x (in containers)

---

## Support and Contributions

### Getting Help
1. Review this CLAUDE.md file
2. Check README.md and RELEASE.md
3. Search GitHub Issues: https://github.com/jasonacox/Powerwall-Dashboard/issues
4. Check Discussions: https://github.com/jasonacox/Powerwall-Dashboard/discussions
5. Open new issue with detailed information

### Contributing
1. Fork repository
2. Create feature branch
3. Make changes following conventions in this document
4. Test thoroughly (setup, upgrade, verify)
5. Submit pull request with clear description
6. Reference related issues

### Testing Contributions
- Test with different deployment modes
- Verify upgrade path works
- Check on different platforms if possible
- Ensure documentation is updated
- Validate against current VERSION

---

## Glossary

**TEDAPI** - Tesla Energy Device API, accessed at 192.168.91.1 on Powerwall WiFi AP

**Gateway** - Tesla Energy Gateway, the central controller for Powerwall systems

**Powerwall+** - Integrated Powerwall with Tesla solar inverter (provides string data)

**String Data** - Individual solar panel string metrics (voltage, current, power)

**SOE** - State of Energy, battery charge percentage

**CQ** - Continuous Query, automatic data aggregation in InfluxDB

**Retention Policy** - InfluxDB data lifecycle rule (duration, replication)

**Downsampling** - Aggregating high-frequency data into lower-frequency summaries

**FleetAPI** - Tesla's official fleet management API

**Local Access** - Direct connection to Powerwall via LAN (not cloud)

**Cloud Mode** - Data retrieved from Tesla servers instead of local gateway

---

## Document Maintenance

This CLAUDE.md file should be updated when:
- Major version releases occur
- New deployment modes are added
- Docker service versions change significantly
- New configuration files are introduced
- Breaking changes affect workflows
- New tools are added to `/tools/`

**Last Updated:** 2025-11-13
**For Version:** v4.8.5+
**Maintainer:** AI Assistant generated, community maintained

---

## Additional Resources

- **Main Documentation:** README.md
- **Release History:** RELEASE.md
- **Windows Setup:** WINDOWS.md
- **Docker Guide:** tools/DOCKER.md
- **Tools Overview:** tools/README.md
- **Location Finder:** https://jasonacox.github.io/Powerwall-Dashboard/location.html
- **Project Repository:** https://github.com/jasonacox/Powerwall-Dashboard
- **pypowerwall Docs:** https://github.com/jasonacox/pypowerwall
