# Purpose: Helper functions for Excel file to output and view  through pandas
import pandas as pd
import sqlite3 as sql
import datetime
from pathlib import Path
from settings import LOG_COLUMNS, LOG_FOLDER, BIKE_XLSX_IN

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Helper Functions
def dfLogInfo(df: pd.DataFrame, headerText: str, firstRun: bool=False) -> None:
    # log for viewing later
    if firstRun:
        with open(LOG_COLUMNS, "w") as l:
            logStr = [f"{headerText}: {"\n"} {df.columns}", f"{df.describe().T}"]
            l.write(f"\nLength of Columns: {len(df.columns)}")
            for i in range(len(logStr)):
                l.write(logStr[i])
    else:
        with open(LOG_COLUMNS, "a") as l:
                logStr = [f"{headerText}: {"\n"} {df.columns}", f"{df.describe().T}"]
                l.write(f"\nLength of Columns: {len(df.columns)}")
                for i in range(len(logStr)):
                    l.write(logStr[i])

# Functions
# Opens an excel workbook and extracts the data into a dataframe
def extractExcel(file_path: str=BIKE_XLSX_IN) -> pd.DataFrame:
    path = Path(file_path)
    excel_file = pd.ExcelFile(path)

    if not path.exists():
        raise FileNotFoundError(f"The file '{path}' does not exist.")

    all_sheets = excel_file.sheet_names
    df = excel_file.parse(sheet_name=all_sheets[0])  # Read the first sheet into a DataFrame

    dfLogInfo(df, "exiting extractExcel df...", True)

    return df

# Perform the data transformations onto the dataframe before it makes it to the database
def transformBikeData(df: pd.DataFrame) -> pd.DataFrame:
    # drop complete duplicate columns first
    df = df.drop_duplicates()
    df = df.drop(columns=[
        "Id", "Completion time", "Email", "Name"
        ])

    # Standardize Column Names
    df.columns = (df.columns
                  .str.strip()
                  .str.lower()
                  .str.replace(" ", "_") # replace spaces with _
                  .str.replace(r"[^\w\s]", "", regex=True) # delete wacky bad column names
    ) 

    dfLogInfo(df, "before rename on transformBikeData")

    # rename columns manually because I'm tired
    df = df.rename(columns={
                    "start_time": "survey_date",
                    "bike_ministry_date": "event_date", 
                    "bike_donations_received": "donations_received",
                    "bikes_given_away": "donations_given",
                    "bike_repairs": "repairs_count", 
                    "bikes_that_were_scrapped": "scrapped_num",
                    "number_of_volunteers": "volunteer_num", 
                    "how_organized_was_today": "organization_score",
                    "names_of_donation_recipients": "recipient_list",
                    "list_any_names_of_people_that_attended_that_may_not_have_signed_in": "volunteer_name_list",
                    "what_can_we_do_to_improve_next_time": "improvement_notes"
                })

    # Validate and cast types

    # Have be UTC so that clean conversions/timezone locales can happen in the power bi dashboard
    df["survey_date"] = pd.to_datetime(df["survey_date"], format='%m-%d-%Y', utc=True, errors='coerce')
    df["event_date"] = pd.to_datetime(df["event_date"], format='%m-%d-%Y', utc=True, errors='coerce')

    # to_numeric phase
    # TODO: Have a null value before/after check to see if pd.to_numeric is wiping out values silently like strings
    # TODO: research CoW optimizations with pandas
    # think of .to_numeric as a null value handler, while .astype is a caster
    df["donations_received"] = pd.to_numeric(df["donations_received"], errors='coerce').astype("Int64") # handle nulls 
    df["donations_given"] = pd.to_numeric(df["donations_given"], errors='coerce').astype("Int64")
    df["repairs_count"] = pd.to_numeric(df["repairs_count"], errors='coerce').astype("Int64")
    df["scrapped_num"] = pd.to_numeric(df["scrapped_num"], errors='coerce').astype("Int64")
    df["volunteer_num"] = pd.to_numeric(df["volunteer_num"], errors='coerce').astype("Int64")
    df["organization_score"] = pd.to_numeric(df["organization_score"], errors='coerce').astype("Int64")

    # the rest are just objects

    # TODO: fillna values
    df["recipient_list"] = df ["recipient_list"].fillna("N/A")
    df["volunteer_name_list"] = df ["volunteer_name_list"].fillna("N/A")
    df["improvement_notes"] = df ["improvement_notes"].fillna("N/A")

    # Integer values, can't accept N/A
    df["donations_received"] = pd.to_numeric(df["donations_received"], errors='coerce').astype("Int64") # handle nulls 
    df["donations_given"] = pd.to_numeric(df["donations_given"], errors='coerce').astype("Int64")
    df["repairs_count"] = pd.to_numeric(df["repairs_count"], errors='coerce').astype("Int64")
    df["scrapped_num"] = pd.to_numeric(df["scrapped_num"], errors='coerce').astype("Int64")
    df["volunteer_num"] = pd.to_numeric(df["volunteer_num"], errors='coerce').astype("Int64")
    df["organization_score"] = pd.to_numeric(df["organization_score"], errors='coerce').astype("Int64")

    # TODO: for statistical preservation, keep the 
    df["donations_received"] = df["donations_received"].astype('Int64').fillna(round(df["donations_received"].mean()))
    df["donations_given"] = df["donations_given"].astype('Int64').fillna(round(df["donations_given"].mean()))
    df["repairs_count"] = df["repairs_count"].astype('Int64').fillna(round(df["repairs_count"].mean()))
    df["scrapped_num"] = df["scrapped_num"].astype('Int64').fillna(round(df["scrapped_num"].mean()))
    df["volunteer_num"] = df ["volunteer_num"].astype('Int64').fillna(round(df["volunteer_num"].mean()))
    df["organization_score"] = df ["organization_score"].astype('Int64').fillna(round(df["organization_score"].median()))

    return df

# Load the cleaned and prepared data into the Database
def loadBikeData(df:pd.DataFrame) -> None:
    with sql.connect("data/bikeministrydata.db") as conn:
        with open("sql/rebuild_schema.sql", "r") as f: 
            sql_script = f.read()

        # Create the table structure, no data yet
        conn.executescript(sql_script)

    # Load data now
    df.to_sql("bike_stats", con=conn, if_exists="append", index=False)

if __name__ == "_main_":
    testfilepath = Path(BIKE_XLSX_IN)

    # Clean terminal settings for viewing
    pd.set_option('display.max_columns', None)  # Show all columns
    pd.set_option('display.max_rows', None)     # Show all rows

    try:
        extracted_df = extractExcel(testfilepath)
        transformed_df = transformBikeData(extracted_df)
        load_df = loadBikeData(transformed_df)

    except FileNotFoundError as e:
        print(f"Error: {e}")