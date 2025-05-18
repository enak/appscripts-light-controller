#!/usr/bin/env python3
"""
AppScriptsLightController - Local Monitor Component

This script monitors a Google Sheet for light control commands and forwards them
to a local Home Assistant instance. This allows controlling Home Assistant without
exposing it to the internet.

Requirements:
- Google API credentials with access to Google Sheets
- Local network access to Home Assistant
- Python 3.6+
"""

import os
import time
import json
import yaml
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Google API libraries
import googleapiclient.discovery
from google.oauth2 import service_account

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("StageLeftMonitor")

class HomeAssistantController:
    """Controls Home Assistant lights via the local API"""
    
    def __init__(self, base_url: str, token: str, light_entities: Dict[str, str] = None):
        """
        Initialize the Home Assistant controller
        
        Args:
            base_url: Base URL for Home Assistant (e.g., http://homeassistant.local:8123)
            token: Long-lived access token for Home Assistant
            light_entities: Dictionary mapping light names to entity IDs
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.light_entities = light_entities or {}
        logger.info(f"Initialized Home Assistant controller for {base_url}")
    
    def call_service(self, domain: str, service: str, data: Dict[str, Any]) -> bool:
        """
        Call a Home Assistant service
        
        Args:
            domain: Service domain (e.g., 'light')
            service: Service name (e.g., 'turn_on')
            data: Service data (e.g., {'entity_id': 'light.stage_left'})
            
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/api/services/{domain}/{service}"
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            response.raise_for_status()
            logger.info(f"Successfully called {domain}.{service} with {data}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Home Assistant service: {e}")
            return False
    
    def process_command(self, action: str, params: Dict[str, Any]) -> bool:
        """
        Process a command from the Google Sheet
        
        Args:
            action: Command action (e.g., 'on', 'off', 'brightness', 'color', 'scene')
            params: Command parameters
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the entity_id from params, or map from light_name if provided
            entity_id = params.get("entity_id")
            light_name = params.get("light_name")
            
            if light_name and not entity_id:
                if light_name in self.light_entities:
                    entity_id = self.light_entities[light_name]
                else:
                    logger.warning(f"Unknown light name: {light_name}")
                    return False
            
            if not entity_id:
                logger.warning("No entity_id or valid light_name provided")
                return False
                
            if action == "on":
                return self.call_service("light", "turn_on", {
                    "entity_id": entity_id
                })
            elif action == "off":
                return self.call_service("light", "turn_off", {
                    "entity_id": entity_id
                })
            elif action == "brightness":
                # Convert 0-100 scale to 0-255 for Home Assistant
                brightness = int(params.get("brightness", 100) * 2.55)
                return self.call_service("light", "turn_on", {
                    "entity_id": entity_id,
                    "brightness": brightness
                })
            elif action == "color":
                # Convert hex color to RGB
                color = params.get("color", "#FFFFFF").lstrip('#')
                rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
                return self.call_service("light", "turn_on", {
                    "entity_id": entity_id,
                    "rgb_color": rgb
                })
            elif action == "scene":
                return self.call_service("scene", "turn_on", {
                    "entity_id": f"scene.{params.get('scene')}"
                })
            else:
                logger.warning(f"Unknown action: {action}")
                return False
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return False


class GoogleSheetMonitor:
    """Monitors a Google Sheet for commands"""
    
    def __init__(self, credentials_file: str, spreadsheet_id: str, sheet_name: str):
        """
        Initialize the Google Sheet monitor
        
        Args:
            credentials_file: Path to the Google API credentials JSON file
            spreadsheet_id: ID of the Google Sheet to monitor
            sheet_name: Name of the sheet within the spreadsheet
        """
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.last_processed_row = 1  # Header row
        
        # Set up Google Sheets API client
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file, scopes=scopes)
        service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)
        self.sheet = service.spreadsheets()
        
        logger.info(f"Initialized Google Sheet monitor for {spreadsheet_id}")
        
        # Ensure the sheet has the correct headers
        self._ensure_headers()
    
    def _ensure_headers(self):
        """Ensure the sheet has the correct headers"""
        headers = ["Command ID", "Action", "Parameters", "Timestamp", "Status"]
        result = self.sheet.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f"{self.sheet_name}!A1:E1"
        ).execute()
        
        values = result.get('values', [])
        if not values or values[0] != headers:
            self.sheet.values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!A1:E1",
                valueInputOption="RAW",
                body={"values": [headers]}
            ).execute()
            logger.info("Created headers in the command sheet")
    
    def get_new_commands(self) -> List[Dict[str, Any]]:
        """
        Get new commands from the Google Sheet
        
        Returns:
            List of command dictionaries
        """
        try:
            result = self.sheet.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!A{self.last_processed_row + 1}:E"
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return []
            
            commands = []
            for i, row in enumerate(values):
                if len(row) >= 5 and row[4].lower() == 'pending':
                    try:
                        commands.append({
                            'id': row[0],
                            'action': row[1],
                            'params': json.loads(row[2]) if row[2] else {},
                            'timestamp': row[3],
                            'row': self.last_processed_row + i + 1
                        })
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON in row {self.last_processed_row + i + 1}: {row[2]}")
            
            # Update the last processed row
            if values:
                self.last_processed_row += len(values)
            
            return commands
        except Exception as e:
            logger.error(f"Error getting commands from Google Sheet: {e}")
            return []
    
    def update_command_status(self, row: int, status: str):
        """
        Update the status of a command in the Google Sheet
        
        Args:
            row: Row number in the sheet
            status: New status ('completed' or 'failed')
        """
        try:
            self.sheet.values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!E{row}",
                valueInputOption="RAW",
                body={"values": [[status]]}
            ).execute()
            logger.info(f"Updated command status in row {row} to {status}")
        except Exception as e:
            logger.error(f"Error updating command status: {e}")


def main():
    """Main function to run the monitor"""
    # Load configuration
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return
    
    # Get light entity mappings from config
    light_entities = {}
    if 'home_assistant' in config and 'lights' in config['home_assistant']:
        light_entities = config['home_assistant']['lights']
    
    # Initialize controllers
    ha_controller = HomeAssistantController(
        config['home_assistant']['url'],
        config['home_assistant']['token'],
        light_entities
    )
    
    sheet_monitor = GoogleSheetMonitor(
        config['google']['credentials_file'],
        config['google']['spreadsheet_id'],
        config['google']['sheet_name']
    )
    
    logger.info("Starting monitor loop")
    
    # Main loop
    while True:
        try:
            # Get new commands
            commands = sheet_monitor.get_new_commands()
            
            # Process commands
            for command in commands:
                logger.info(f"Processing command: {command['action']} with params {command['params']}")
                success = ha_controller.process_command(command['action'], command['params'])
                status = 'completed' if success else 'failed'
                sheet_monitor.update_command_status(command['row'], status)
            
            # Sleep for a bit
            time.sleep(config.get('polling_interval', 5))
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, exiting")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(30)  # Sleep longer on error


if __name__ == "__main__":
    main()
