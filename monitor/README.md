# AppScriptsLightController - Monitor Component

This directory contains the Python monitor component of the AppScriptsLightController system. The monitor watches a Google Sheet for commands and forwards them to Home Assistant.

## Components

- `monitor.py` - Main script that monitors the Google Sheet and sends commands to Home Assistant
- `create_sheet_template.py` - Utility script to create a new Google Sheet with the proper structure
- `config.yaml.example` - Example configuration file (copy to `config.yaml` and update)
- `Dockerfile` and `docker-compose.yml` - Docker configuration for containerized deployment

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Google API Credentials

1. Create a Google Cloud project
2. Enable the Google Sheets API and Google Drive API
3. Create a service account with appropriate permissions
4. Download the service account credentials as JSON
5. Save the credentials file in a secure location (e.g., `./credentials/credentials.json`)

### 3. Create a Google Sheet

You can create a Google Sheet template using the included utility script:

```bash
python create_sheet_template.py --credentials ./credentials/credentials.json --name "LightController"
```

This will:
- Create a new Google Sheet with the name "LightController"
- Set up the Commands sheet with proper headers
- Set up the Configuration sheet with initial data
- Print the spreadsheet ID for use in your configuration

### 4. Configure the Monitor

1. Copy the example configuration file:
   ```bash
   cp config.yaml.example config.yaml
   ```

2. Edit `config.yaml` with your specific settings:
   - Update the Home Assistant URL and token
   - Update the Google spreadsheet ID and credentials path
   - Configure your light entity mappings

### 5. Run the Monitor

```bash
python monitor.py
```

The monitor will:
1. Connect to your Google Sheet
2. Check for new commands periodically
3. Send commands to Home Assistant when detected
4. Update the command status in the sheet

## Docker Deployment

For a containerized deployment:

1. Build and start the container:
   ```bash
   docker-compose up -d
   ```

2. View logs:
   ```bash
   docker-compose logs -f
   ```

3. Stop the container:
   ```bash
   docker-compose down
   ```

## Troubleshooting

- Check `monitor.log` for detailed error messages
- Ensure your Home Assistant instance is accessible from the monitor
- Verify that your Google API credentials have the necessary permissions
- Make sure you've shared the Google Sheet with the service account email
