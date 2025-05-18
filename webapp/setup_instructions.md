# Stage Left Light Control - Web App Setup Instructions

Follow these steps to set up and deploy the Stage Left Light Control web app using clasp.

## Step 1: Install and Configure Clasp

1. Make sure you have Node.js and npm installed.

2. Navigate to the webapp directory:
   ```
   cd /home/enak/Code/stage-left-light/webapp
   ```

3. Log in to your Google account with clasp:
   ```
   npm run login
   ```
   This will open a browser window where you need to authorize clasp to access your Google account.

## Step 2: Enable the Google Apps Script API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Search for "Google Apps Script API" and enable it
4. Make sure your Google account has permission to use the API

## Step 3: Create a New Google Apps Script Project

1. Create a new Google Apps Script project:
   ```
   npm run create
   ```

2. When prompted, select "standalone" as the script type.

3. This will update your `.clasp.json` file with the new script ID.

## Step 4: Push Your Code to Google Apps Script

1. Push your local files to Google Apps Script:
   ```
   npm run push
   ```

2. Open the project in the Google Apps Script editor:
   ```
   npm run open
   ```

3. In the editor, verify that all files were uploaded correctly:
   - `Code.js`
   - `WebApp.html`
   - `appsscript.json`

## Step 5: Update the Spreadsheet ID

1. In the Google Apps Script editor, open `Code.js`
2. Update the `CONTROL_SPREADSHEET_ID` constant with your Google Sheet ID
3. Save the file

## Step 6: Deploy as a Web App

1. Deploy the web app:
   ```
   npm run deploy
   ```

2. In the deployment dialog:
   - Set "Execute as" to "User accessing the web app"
   - Set "Who has access" to the appropriate access level (e.g., "Anyone" or "Anyone within [your organization]")
   - Click "Deploy"

3. Copy the web app URL that is provided after deployment

## Step 7: Access the Web App

1. Open the web app URL in your browser
2. If prompted, authorize the app to access your Google account
3. You should now see the Theater Light Controls interface

## Step 8: Create Shortcuts for Easy Access

### On Mobile Devices:
1. Open the web app URL in your mobile browser
2. Add the page to your home screen:
   - iOS (Safari): Tap the share icon and select "Add to Home Screen"
   - Android (Chrome): Tap the menu button and select "Add to Home Screen"

### On Desktop:
1. Create a bookmark to the web app URL
2. For even quicker access, create a desktop shortcut that links to the URL

## Troubleshooting

### Authorization Issues
- If you see "This app isn't verified" message, click "Advanced" and then "Go to [App Name] (unsafe)"
- Make sure you've enabled the Google Apps Script API in your Google Cloud project

### Deployment Issues
- If you get errors during deployment, check the error message in the console
- Make sure your Google account has permission to create and deploy Apps Script projects

### Script ID Issues
- If your `.clasp.json` file doesn't have a script ID, run `npm run create` again
- If you want to use an existing script, update the script ID in `.clasp.json` manually

## Updating the Web App

1. Make changes to the local files
2. Push changes to Google Apps Script:
   ```
   npm run push
   ```
3. Deploy a new version:
   ```
   npm run deploy
   ```
4. The web app URL will remain the same, but it will now serve the updated version
