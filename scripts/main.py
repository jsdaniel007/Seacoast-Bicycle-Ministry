# Imports
import get_latest_data as g
import etl as e

# Step 1: get the token through the Microsoft graph API

if __name__ == "__main__":
    # Step 1: Get our token and download the bike ministry data file, may need auth
    token = g.get_access_token()
    g.download_bike_ministry_file(token)

    # Step 2: Take the file and extract, file_path has a default value
    extracted_df = e.extractExcel()
    transformed_df = e.transformBikeData(extracted_df)
    load_df = e.loadBikeData(transformed_df)