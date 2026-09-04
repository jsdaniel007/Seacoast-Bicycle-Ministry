# Seacoast-Bicycle-Ministry
Code and Programming for Seacoast Bicycle Ministry

# Diary
## Major Development Phases
### Phase 1: Automate retrieving Excel file through Microsoft Graph API
**get_latest_data.py:** handles authentication, caching of token through Oauth, and retrieving the excel sheet based on the ID of the file.
**settings.py:** has variables for various configuration of GraphAPI

### Phase 2: Extract, Transform, Load from excel
**etl.py:** contains logic for ETL process including data extraction from Excel, cleaning, and sqlite preperation
- Uses a "Full Rebuild" approach to table creation and teardown


Dataflow 


─────────────────────────────────┐
│     Microsoft Organization      │  <-- Where the files live
│           OneDrive              │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│     get_latest_data.py         │  <-- Fetching and Saving
│      (Microsoft Graph API)      │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────┐
│   BikeMinistryData.xlsx │  <-- Raw Source Files
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│    Python ETL Pipeline  │  <-- Automated Processing
│   • get_latest_data.py  │
│   • etl.py              │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   sql/rebuild_schema.sql│  <-- Database DDL Execution
└────────────┬────────────┘      (Runs DROP & CREATE via executescript)
             │
             ▼
┌─────────────────────────┐
│     SQLite Database     │  <-- Stored Target Data
│    (bike_stats table)   │      (Appended via Pandas to_sql)
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│    Power BI Dashboard   │  <-- Final Reporting Source
└─────────────────────────┘