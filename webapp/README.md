# AppScriptsLightController - Web App Component

This directory contains the Google Apps Script web app for controlling lights through Home Assistant.

## Project Structure

- `Code.js` - Main script file containing all the Google Apps Script functions
- `WebApp.html` - HTML for the standalone web app interface
- `appsscript.json` - Project manifest file

## Development Setup

This project uses [clasp](https://github.com/google/clasp) for local development and deployment to Google Apps Script.

### Prerequisites

- Node.js and npm installed
- Google account with access to Google Apps Script
- Google Cloud project with the Google Apps Script API enabled

### Setup Instructions

1. Install clasp globally (if not already installed):
   ```
   npm install -g @google/clasp
   ```

2. Login to your Google account:
   ```
   clasp login
   ```

3. Create a new Google Apps Script project:
   ```
   clasp create --title "AppScriptsLightController" --type webapp
   ```

4. Update the `.clasp.json` file with the new script ID.

5. Push your local files to Google Apps Script:
   ```
   clasp push
   ```

6. Open the project in the Google Apps Script editor:
   ```
   clasp open
   ```

### Deployment

1. Deploy the web app:
   ```
   clasp deploy --description "Light Controls Web App"
   ```

2. Get the deployment URL:
   ```
   clasp deployments
   ```

## Usage

After deployment, you can access the web app using the deployment URL. The interface allows you to:

- Select which light to control from a dropdown menu
- Turn lights on and off
- Adjust brightness with a slider
- Change light colors with a color picker
- Activate preset scenes
- Configure the Google Sheet ID through the settings panel (gear icon)

## Configuration

The web app uses script properties to store configuration:

1. **Google Sheet ID**: The ID of the Google Sheet used to store commands
   - This can be configured through the web interface by clicking the gear icon
   - No need to modify the code directly

## Sheet Structure

The web app uses two sheets in the Google Spreadsheet:

1. **Commands** - Stores the light control commands
   - Created and managed by the Python monitor script
   - Headers: Command ID, Action, Parameters, Timestamp, Status

2. **Configuration** - Stores light entity mappings
   - Created automatically by the web app if it doesn't exist
   - Format: Light Name, Entity ID (e.g., "light_name", "light.entity_id")
