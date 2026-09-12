# Purpose: Helper functions for Excel file to output and view  through pandas
import pandas as pd
import sqlite3 as sql
from pathlib import Path

BIKE_XLSX_IN = Path("data/BikeMinistryData.xlsx")

# Opens an excel workbook and extracts the data into a dataframe
def extractExcel(file_path: str=BIKE_XLSX_IN) -> pd.DataFrame:
    path = Path(file_path)
    excel_file = pd.ExcelFile(file_path)

    if not path.exists():
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    all_sheets = excel_file.sheet_names
    df = excel_file.parse(sheet_name=all_sheets[0])  # Read the first sheet into a DataFrame

    #print(f"df info:{"\n"}Available Sheets: {len(all_sheets):},{"\n"}{df.info()}")
    #print(f"df head:{"\n"}{df.head()},{"\n"}")
    return df

# Perform the data transformations onto the dataframe before it makes it to the database
def transformBikeData(df: pd.DataFrame) -> pd.DataFrame:
    # rename columns - Spent a lot of time on getting this right

    df = df.rename(columns={df.columns[1]: "Survey Day Time", 
                    df.columns[8]: "Donation Recipients",
                    df.columns[11]:"Organization Score", 
                    df.columns[12]: "Volunteer Num",
                    df.columns[13]:"Volunteer Name List", 
                    df.columns[14]: "Improvement Notes"}
    )
    # Standardize Column Names
    df.columns = (df.columns
                  .str.strip()
                  .str.lower()
                  .str.replace(" ", "_") # replace spaces with _
                  .str.replace(r"[^\w\s]", "", regex=True) # delete wacky bad column names
    ) 

    # Validate and cast types
    df["organization_score"] = pd.to_numeric(df["organization_score"], errors="coerce")
    df["volunteer_num"] = pd.to_numeric(df["volunteer_num"], errors="coerce")

    # drop exact duplicate rows
    df = df.drop_duplicates()
    df = df.dropna(subset=["id"])

    # fillna values
    df["donation_recipients"] = df ["donation_recipients"].fillna("N/A")
    df["volunteer_name_list"] = df ["volunteer_name_list"].fillna("N/A")
    df["improvement_notes"] = df ["improvement_notes"].fillna("N/A")
    df["organization_score"] = df ["organization_score"].fillna(0)
    df["volunteer_num"] = df ["volunteer_num"].fillna(0)

    # delete columns - alot of time on this part
    df = df.drop(df.columns[[2, 3, 4]], axis=1)

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