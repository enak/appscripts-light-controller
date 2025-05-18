# AppScriptsLightController - Setup Guide

This guide will walk you through setting up the AppScriptsLightController system, which connects Google Workspace with Home Assistant without exposing your Home Assistant instance to the internet.

## Step 1: Create a Google Sheet

1. Go to [Google Sheets](https://sheets.google.com) and create a new spreadsheet
2. Name it "LightController" (or any name you prefer)
3. Rename the first sheet to "Commands"
4. Note the spreadsheet ID from the URL (the long string between `/d/` and `/edit` in the URL)

## Step 2: Set Up Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use an existing one)
3. Enable the Google Sheets API and Google Drive API
4. Create a service account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Name it "light-controller"
   - Grant it the "Editor" role for the project
   - Click "Create Key" and select JSON format
   - Save the downloaded JSON file as `credentials.json` in your project directory

5. Share your Google Sheet with the service account email address (it looks like `something@project-id.iam.gserviceaccount.com`)

## Step 3: Set Up the Web App with Apps Script

1. Navigate to the webapp directory
2. Follow the instructions in the webapp/README.md file to set up and deploy the web app
3. After deployment, you'll receive a URL that can be used to access the light controls

## Step 4: Configure Home Assistant

1. Generate a long-lived access token in Home Assistant:
   - Go to your user profile (click your username in the sidebar)
   - Scroll down to "Long-Lived Access Tokens"
   - Create a token named "AppScriptsLightController"
   - Copy the token (you won't be able to see it again)

2. Make sure your lights are properly set up in Home Assistant
3. Note the entity IDs of your lights (e.g., `light.living_room`)

## Step 5: Set Up the Local Monitor

1. Navigate to the monitor directory
2. Install Python 3.6 or newer if not already installed
3. Copy the `credentials.json` file you downloaded earlier to the credentials directory
4. Copy `config.yaml.example` to `config.yaml`
5. Edit `config.yaml` with your specific settings:
   - Update the Home Assistant URL and token
   - Update the Google spreadsheet ID and sheet name
   - Set the polling interval as desired

6. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

7. Run the monitor script:
   ```
   python monitor.py
   ```

8. Consider setting up the script to run automatically on system startup:
   - For Linux, create a systemd service
   - For Windows, create a scheduled task
   - For macOS, create a LaunchAgent
   - Or use Docker as described in the monitor/README.md file

## Step 6: Test the System

1. Open the web app URL in your browser
2. Use the interface to control your lights
3. Check the monitor logs to ensure commands are being processed
4. Verify that your lights respond as expected

## Troubleshooting

### Google Sheets API Issues
- Check that the APIs are enabled in your Google Cloud project
- Verify that the service account has access to the spreadsheet
- Check the credentials file path in `config.yaml`

### Home Assistant Issues
- Verify that the Home Assistant URL is correct and accessible from your network
- Check that the access token is valid
- Confirm that the entity IDs match those in Home Assistant

### Monitor Script Issues
- Check the `monitor.log` file for error messages
- Verify that all required Python packages are installed
- Ensure the script has network access to both Google APIs and Home Assistant

## Security Considerations

This setup keeps your Home Assistant instance secure by:
1. Not exposing Home Assistant to the internet
2. Using Google's authentication for the user interface
3. Running the monitoring script only on your local network
4. Using secure API tokens for Google Drive access

Remember to keep your `credentials.json` and `config.yaml` files secure, as they contain sensitive information.
