# get_latest_data.py
import json
import token

from msal import PublicClientApplication, SerializableTokenCache
import os
import requests
import settings

TENANT_ID = settings.config["tenant_id"]
CLIENT_ID = settings.config["client_id"]
CACHE_FILE = "token_cache.json"

from msal import PublicClientApplication

# authentication aka Phase 1, with cache function
def get_access_token() -> dict:
    cache = SerializableTokenCache()

    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache.deserialize(f.read())

    app = PublicClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        token_cache=cache
    )

    accounts = app.get_accounts()

    result = None

    if accounts:
        result = app.acquire_token_silent(["User.Read"], account=accounts[0])
    if not result:
        flow = app.initiate_device_flow(
            scopes=["User.Read"]
        )

        print(flow["message"])

        result = app.acquire_token_by_device_flow(flow)

    if cache.has_state_changed:
        with open(CACHE_FILE, "w") as f:
            f.write(cache.serialize())

    return result["access_token"]

def download_bike_ministry_file(token: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    file_id = settings.config["file_id"]
    response = requests.get(
        f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content",
        headers=headers)
    with open("data/BikeMinistryData.xlsx", "wb") as f:
        f.write(response.content)

if __name__=="__main__":
    # How to use this
    token = get_access_token()
    download_bike_ministry_file(token)

