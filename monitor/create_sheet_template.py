#!/usr/bin/env python3
"""
AppScriptsLightController - Sheet Template Creator

This script creates a Google Sheet template for the AppScriptsLightController system.
It sets up the necessary headers and formatting for the command sheet.
"""

import os
import yaml
import argparse
from googleapiclient.discovery import build
from google.oauth2 import service_account

def create_sheet_template(credentials_file, spreadsheet_name="LightController"):
    """
    Create a Google Sheet template for the Stage Left Light Control system
    
    Args:
        credentials_file: Path to the Google API credentials JSON file
        spreadsheet_name: Name for the new spreadsheet
        
    Returns:
        The ID of the created spreadsheet
    """
    # Set up Google Sheets API client
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    credentials = service_account.Credentials.from_service_account_file(
        credentials_file, scopes=scopes)
    
    # Create the spreadsheet
    drive_service = build('drive', 'v3', credentials=credentials)
    sheets_service = build('sheets', 'v4', credentials=credentials)
    
    # Create a new spreadsheet
    spreadsheet = {
        'properties': {
            'title': spreadsheet_name
        },
        'sheets': [
            {
                'properties': {
                    'title': 'Commands',
                    'gridProperties': {
                        'frozenRowCount': 1
                    }
                }
            }
        ]
    }
    
    spreadsheet = sheets_service.spreadsheets().create(body=spreadsheet).execute()
    spreadsheet_id = spreadsheet['spreadsheetId']
    print(f"Created spreadsheet with ID: {spreadsheet_id}")
    
    # Add headers to the Commands sheet
    headers = [["Command ID", "Action", "Parameters", "Timestamp", "Status"]]
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="Commands!A1:E1",
        valueInputOption="RAW",
        body={"values": headers}
    ).execute()
    
    # Format the headers (make them bold and add background color)
    requests = [
        {
            'repeatCell': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': 0,
                    'endRowIndex': 1,
                    'startColumnIndex': 0,
                    'endColumnIndex': 5
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {
                            'red': 0.2,
                            'green': 0.2,
                            'blue': 0.2
                        },
                        'textFormat': {
                            'bold': True,
                            'foregroundColor': {
                                'red': 1.0,
                                'green': 1.0,
                                'blue': 1.0
                            }
                        }
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat)'
            }
        },
        {
            'autoResizeDimensions': {
                'dimensions': {
                    'sheetId': 0,
                    'dimension': 'COLUMNS',
                    'startIndex': 0,
                    'endIndex': 5
                }
            }
        }
    ]
    
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()
    
    print("Formatted headers in the Commands sheet")
    
    # Create Configuration sheet
    requests = [
        {
            'addSheet': {
                'properties': {
                    'title': 'Configuration',
                    'gridProperties': {
                        'frozenRowCount': 1
                    }
                }
            }
        }
    ]
    
    response = sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()
    
    config_sheet_id = response['replies'][0]['addSheet']['properties']['sheetId']
    
    # Add headers and initial data to Configuration sheet
    config_data = [
        ["Light Name", "Entity ID"],
        ["stage_right", "light.stage_right"]
    ]
    
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="Configuration!A1:B2",
        valueInputOption="RAW",
        body={"values": config_data}
    ).execute()
    
    # Format the config headers
    requests = [
        {
            'repeatCell': {
                'range': {
                    'sheetId': config_sheet_id,
                    'startRowIndex': 0,
                    'endRowIndex': 1,
                    'startColumnIndex': 0,
                    'endColumnIndex': 2
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {
                            'red': 0.2,
                            'green': 0.2,
                            'blue': 0.2
                        },
                        'textFormat': {
                            'bold': True,
                            'foregroundColor': {
                                'red': 1.0,
                                'green': 1.0,
                                'blue': 1.0
                            }
                        }
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat)'
            }
        },
        {
            'autoResizeDimensions': {
                'dimensions': {
                    'sheetId': config_sheet_id,
                    'dimension': 'COLUMNS',
                    'startIndex': 0,
                    'endIndex': 2
                }
            }
        }
    ]
    
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()
    
    print("Created and formatted Configuration sheet")
    
    # Update the config file with the new spreadsheet ID
    if os.path.exists('config.yaml.example') and not os.path.exists('config.yaml'):
        with open('config.yaml.example', 'r') as f:
            config = yaml.safe_load(f)
        
        config['google']['spreadsheet_id'] = spreadsheet_id
        
        with open('config.yaml', 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print("Updated config.yaml with the new spreadsheet ID")
    
    return spreadsheet_id

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a Google Sheet template for AppScriptsLightController")
    parser.add_argument('--credentials', default='credentials.json', help='Path to the Google API credentials JSON file')
    parser.add_argument('--name', default='LightController', help='Name for the new spreadsheet')
    
    args = parser.parse_args()
    
    spreadsheet_id = create_sheet_template(args.credentials, args.name)
    print(f"\nNext steps:")
    print(f"1. Share the spreadsheet with your Google account")
    print(f"2. Update your config.yaml with the spreadsheet ID: {spreadsheet_id}")
    print(f"3. Run the monitor.py script to start monitoring for commands")
