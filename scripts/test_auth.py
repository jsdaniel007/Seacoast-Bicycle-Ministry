from msal import PublicClientApplication

TENANT_ID = "b8af498a-467e-44aa-bdb3-4fb952a3b14f"
CLIENT_ID = "78106273-9a6f-4f5d-a645-f464a3e58e7e"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

app = PublicClientApplication(
    client_id=CLIENT_ID, authority=AUTHORITY
    )

result = app.acquire_token_interactive(
    scopes=["Files.Read.All"]
    )

if "access_token" in result:
    print("Auth successful!")
else:
    print(result)