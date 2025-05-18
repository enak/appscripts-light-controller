# AppScriptsLightController

This project creates a bridge between Google Workspace and Home Assistant to control lighting without exposing Home Assistant to the internet.

## Project Structure

The project is organized into two main components:

### 1. Web App (`/webapp`)

A Google Apps Script web app that provides a user interface for controlling lights. This component:
- Creates a standalone web interface accessible via URL
- Allows selecting and controlling different lights
- Writes commands to a Google Sheet
- Can be accessed from any device with a web browser

### 2. Monitor (`/monitor`)

A Python script that runs on your local network and connects Home Assistant to Google Sheets. This component:
- Monitors the Google Sheet for new commands
- Forwards commands to Home Assistant
- Updates command status in the Google Sheet
- Runs securely on your local network

## How It Works

1. Users access the web app through a URL
2. The web app writes commands to a Google Sheet
3. The monitor script detects new commands in the sheet
4. The monitor sends commands to Home Assistant
5. Home Assistant controls the physical lights

This approach keeps your Home Assistant instance secure by:
- Not exposing Home Assistant to the internet
- Using Google's authentication for the user interface
- Running the monitoring script only on your local network
- Using secure API tokens for Google Drive access

## Setup Instructions

### Web App Setup

See the [webapp/README.md](webapp/README.md) file for detailed instructions on setting up and deploying the web app.

### Monitor Setup

See the [monitor/README.md](monitor/README.md) file for detailed instructions on setting up and running the monitor script.

## Light Configuration

Lights are configured in two places:

1. **Google Sheet**: The "Configuration" sheet contains mappings between light names and Home Assistant entity IDs
2. **config.yaml**: The monitor's configuration file also contains light entity mappings

The web app reads light configurations from the Google Sheet, while the monitor can use either the sheet or its local configuration.

## Security Considerations

This system is designed with security in mind:

- Home Assistant is never exposed to the internet
- Google's authentication secures the web interface
- The monitor script only needs outbound internet access
- API tokens are used for secure authentication
- All communication happens over HTTPS

## Requirements

### For the Web App
- Google account with access to Google Apps Script
- Google Cloud project with the Google Sheets API enabled

### For the Monitor
- Python 3.6 or newer
- Local network access to Home Assistant
- Outbound internet access for Google API calls
- Google API service account credentials
