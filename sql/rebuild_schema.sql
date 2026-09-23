-- Teardown code: necessary for making sure there's no conflicts with creating tables
DROP INDEX IF EXISTS idx_bike_ministry_date;
DROP TABLE IF EXISTS bike_stats;

-- Rebuild
CREATE TABLE bike_stats (
    stat_id INTEGER PRIMARY KEY,
    survey_date TEXT NOT NULL, -- UTC - ISO 8601 Date String (YYYY-MM-DD)
    event_date TEXT NOT NULL, -- UTC - ISO 8601 Date String (YYYY-MM-DD)
    donations_received INTEGER DEFAULT 0,
    donations_given INTEGER DEFAULT 0,
    repairs_count INTEGER DEFAULT 0,
    scrapped_num INTEGER DEFAULT 0,
    volunteer_num INTEGER DEFAULT 0,
    organization_score INTEGER DEFAULT 0,
    recipient_list TEXT,
    volunteer_name_list TEXT,
    improvement_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    
);

-- Create an Index for Optimization: Re-apply indices on slice/filter columns in order to give power bi performance increases
CREATE INDEX idx_bike_ministry_date ON bike_stats(event_date)