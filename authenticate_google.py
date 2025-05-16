# authenticate_google.py
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os.path

# --- CONFIGURATION ---
# !!! CHOOSE YOUR PORT AND SET IT HERE !!!
# This port MUST be added to your "Authorized redirect URIs" in Google Cloud Console.
# Example: if DESIRED_PORT = 8080, add "http://localhost:8080/"
DESIRED_PORT = 8080  # <<< CHANGE THIS TO YOUR DESIRED PORT (e.g., 8080, 8090)

# Path to your client secrets file downloaded from Google Cloud Console.
# Make sure this file ("credentials.json" or your chosen name) is in the same directory.
CLIENT_SECRETS_FILE = "credentials.json"

# The scopes required by your application (must match your agent's needs)
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# The file where the token will be stored
TOKEN_FILE = "token.json"
# --- END CONFIGURATION ---

def authenticate():
    creds = None
    if os.path.exists(TOKEN_FILE):
        print(f"Loading existing credentials from {TOKEN_FILE}")
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"Error loading token file {TOKEN_FILE}: {e}. Will attempt to re-authenticate.")
            creds = None # Ensure re-authentication if token file is corrupt

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Credentials expired, refreshing...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}. Need to re-authenticate.")
                if os.path.exists(TOKEN_FILE): # Remove problematic token file
                    os.remove(TOKEN_FILE)
                creds = None # Force re-authentication
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                print(f"ERROR: Client secrets file '{CLIENT_SECRETS_FILE}' not found.")
                print("Please download it from Google Cloud Console and place it in the current directory.")
                return None

            print(f"No valid credentials found, initiating OAuth flow on port {DESIRED_PORT}...")
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            # Run the local server on the DESIRED_PORT
            creds = flow.run_local_server(
                port=DESIRED_PORT,
                prompt='consent', # Ensures user is prompted for consent
                # You can customize the message shown in the console before opening the browser
                # authorization_prompt_message="Please authorize access via your browser: {url}"
            )
        # Save the credentials for the next run
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
        print(f"Credentials saved to {TOKEN_FILE}")
    else:
        print("Credentials are valid and loaded from token.json.")

    return creds

if __name__ == "__main__":
    print("-" * 50)
    print("Google OAuth 2.0 Authentication Helper")
    print("-" * 50)
    print(f"This script will attempt to authenticate with Google and generate '{TOKEN_FILE}'.")
    print(f"It will use the redirect URI: http://localhost:{DESIRED_PORT}/")
    print("\nIMPORTANT:")
    print(f"1. Ensure you have downloaded your 'OAuth 2.0 Client ID' JSON file and named it '{CLIENT_SECRETS_FILE}' in this directory.")
    print(f"2. In your Google Cloud Console (https://console.cloud.google.com/), for that Client ID,")
    print(f"   you MUST add 'http://localhost:{DESIRED_PORT}/' to the 'Authorized redirect URIs' list.")
    print("-" * 50)
    input("Press Enter to continue after verifying the above steps...")

    credentials = authenticate()
    if credentials:
        print("\nAuthentication successful or existing token loaded and valid.")
        print(f"Your '{TOKEN_FILE}' should now be ready for your LangChain agent.")
    else:
        print("\nAuthentication failed. Please check the console messages and your setup.")