# Data Dictionary

## 1. Bluebikes Trip Data

**Source:** [Bluebikes System Data](https://bluebikes.com/system-data)
**License:** [Bluebikes Data License Agreement](https://bluebikes.com/data-license-agreement)
**Format:** CSV (zipped)
**Period:** September–December 2025
**Location:** `data/raw/bluebikes/`
**Files:**
- `202509-bluebikes-tripdata.csv` (134MB)
- `202510-bluebikes-tripdata.csv` (117MB)
- `202511-bluebikes-tripdata.csv` (79MB)
- `202512-bluebikes-tripdata.csv` (43MB)

### Schema

| Column | Type | Description |
|--------|------|-------------|
| ride_id | string | Unique trip identifier |
| rideable_type | string | Bike type: `classic_bike` or `electric_bike` |
| started_at | timestamp | Trip start time (YYYY-MM-DD HH:MM:SS.mmm) |
| ended_at | timestamp | Trip end time (YYYY-MM-DD HH:MM:SS.mmm) |
| start_station_name | string | Name of departure station |
| start_station_id | string | ID of departure station |
| end_station_name | string | Name of arrival station |
| end_station_id | string | ID of arrival station |
| start_lat | float | Latitude of trip start |
| start_lng | float | Longitude of trip start |
| end_lat | float | Latitude of trip end |
| end_lng | float | Longitude of trip end |
| member_casual | string | Rider type: `member` or `casual` |

### Selected Stations

| Station ID | Station Name | Role |
|------------|-------------|------|
| M32004 | Kendall T | Station A — near Kendall/MIT Red Line station |
| M32042 | MIT Vassar St | Station B — near Westgate dormitory |

### Arrival Definition

An "arrival" is defined as a **trip end (bike return)** at one of the selected stations. The `ended_at` timestamp is used as the arrival time.

---

## 2. MBTA LAMP Subway Performance Data

**Source:** [MBTA LAMP Public Data](https://performancedata.mbta.com/)
**License:** Public domain (MBTA open data)
**Format:** Apache Parquet
**Period:** September–December 2025 (122 daily files)
**Location:** `data/raw/mbta/`
**Files:** `YYYY-MM-DD-subway-on-time-performance-v1.parquet`
**Total size:** ~219MB

### Schema

| Column | Type | Description |
|--------|------|-------------|
| stop_sequence | int | Stop order within the trip |
| stop_id | string | Platform-level stop identifier |
| parent_station | string | Station-level identifier (e.g., `place-knncl`) |
| move_timestamp | float | Unix timestamp when train departed previous stop |
| stop_timestamp | float | Unix timestamp when train arrived at this stop |
| travel_time_seconds | float | Travel time from previous stop (seconds) |
| dwell_time_seconds | float | Time spent at this stop (seconds) |
| headway_trunk_seconds | float | Time since previous train on trunk (seconds) |
| headway_branch_seconds | float | Time since previous train on branch (seconds) |
| service_date | int | Service date (YYYYMMDD format) |
| route_id | string | Line identifier (e.g., `Red`, `Orange`, `Green-B`) |
| direction_id | bool | Direction (True/False) |
| start_time | int | Trip start time (seconds from midnight) |
| vehicle_id | string | Vehicle identifier |
| branch_route_id | string | Branch route (if applicable) |
| trunk_route_id | string | Trunk route |
| stop_count | int | Number of stops in trip |
| trip_id | string | Trip identifier |
| vehicle_label | string | Vehicle label |
| vehicle_consist | string | Vehicle consist (car numbers) |
| direction | string | Direction name (e.g., `North`, `South`) |
| direction_destination | string | Terminal station name |
| scheduled_arrival_time | float | Scheduled arrival (seconds from midnight) |
| scheduled_departure_time | float | Scheduled departure (seconds from midnight) |
| scheduled_travel_time | float | Scheduled travel time (seconds) |
| scheduled_headway_branch | float | Scheduled branch headway (seconds) |
| scheduled_headway_trunk | float | Scheduled trunk headway (seconds) |

### Selected Station

| Station ID | Station Name | Route |
|------------|-------------|-------|
| place-knncl | Kendall/MIT | Red Line |

### Arrival Definition

An "arrival" is defined as a **train arrival** at Kendall/MIT station (`parent_station = 'place-knncl'`). The `stop_timestamp` (Unix epoch) is used as the arrival time. Both directions (Alewife-bound and Braintree/Ashmont-bound) are included.

### Disruption Flagging

Records where actual headway deviates significantly from scheduled headway will be flagged. Flagged periods will be excluded from primary analysis.
