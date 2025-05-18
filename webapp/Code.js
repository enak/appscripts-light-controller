/**
 * AppScriptsLightController - Google Apps Script Web App Component
 * 
 * This script creates a standalone web app to control lights through 
 * Home Assistant without exposing it to the internet. Commands are written 
 * to a Google Sheet that is monitored by a local script.
 */

// Sheet names
const SHEET_NAME = 'Commands'; // Name of the sheet within the spreadsheet
const CONFIG_SHEET_NAME = 'Configuration'; // Name of the configuration sheet

// Cache for light configurations
let lightConfigCache = null;
let lightConfigLastFetch = null;
const CONFIG_CACHE_TTL = 5 * 60 * 1000; // 5 minutes in milliseconds

/**
 * Gets the control spreadsheet ID from script properties.
 * If not set, returns a default value.
 * 
 * @return {string} The spreadsheet ID
 */
function getControlSpreadsheetId() {
  const scriptProperties = PropertiesService.getScriptProperties();
  const spreadsheetId = scriptProperties.getProperty('CONTROL_SPREADSHEET_ID');
  
  if (!spreadsheetId) {
    Logger.log('Warning: CONTROL_SPREADSHEET_ID not set in script properties');
    return '1gXKvJWPFknqdi9QeyCAXqiC4MqaDJoKQvn130hVe6_c'; // Default fallback ID
  }
  
  return spreadsheetId;
}

/**
 * Sets the control spreadsheet ID in script properties.
 * 
 * @param {string} spreadsheetId - The ID of the spreadsheet to use
 */
function setControlSpreadsheetId(spreadsheetId) {
  const scriptProperties = PropertiesService.getScriptProperties();
  scriptProperties.setProperty('CONTROL_SPREADSHEET_ID', spreadsheetId);
  Logger.log('Updated CONTROL_SPREADSHEET_ID in script properties');
  
  // Clear the cache to force reload from the new spreadsheet
  lightConfigCache = null;
  lightConfigLastFetch = null;
  
  return { success: true, message: 'Spreadsheet ID updated successfully' };
}

/**
 * Serves the web app - this is the function that responds to HTTP GET requests
 * when the script is deployed as a web app.
 * 
 * @param {object} e - The event parameter (not used in this implementation)
 * @return {HtmlOutput} The HTML page to display
 */
function doGet(e) {
  return HtmlService.createHtmlOutputFromFile('WebApp')
      .setTitle('Light Controls')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * Fetches light configuration from the configuration sheet
 * @return {object} Light configuration mapping names to entity IDs
 */
function getLightConfig() {
  // Check if we have a valid cached config
  const now = new Date().getTime();
  if (lightConfigCache && lightConfigLastFetch && (now - lightConfigLastFetch < CONFIG_CACHE_TTL)) {
    return lightConfigCache;
  }
  
  try {
    const spreadsheetId = getControlSpreadsheetId();
    const spreadsheet = SpreadsheetApp.openById(spreadsheetId);
    let configSheet = spreadsheet.getSheetByName(CONFIG_SHEET_NAME);
    
    // Create config sheet if it doesn't exist
    if (!configSheet) {
      configSheet = spreadsheet.insertSheet(CONFIG_SHEET_NAME);
      configSheet.appendRow(['Light Name', 'Entity ID']);
      configSheet.appendRow(['light_1', 'light.entity_id_1']);
      configSheet.setFrozenRows(1);
    }
    
    // Read configuration
    const configData = configSheet.getDataRange().getValues();
    const config = {};
    
    // Skip header row
    for (let i = 1; i < configData.length; i++) {
      if (configData[i][0] && configData[i][1]) {
        config[configData[i][0]] = configData[i][1];
      }
    }
    
    // Update cache
    lightConfigCache = config;
    lightConfigLastFetch = now;
    
    return config;
  } catch (error) {
    Logger.log('Error fetching light config: ' + error.toString());
    // Return default config if there's an error
    return { 'light_1': 'light.entity_id_1' };
  }
}

/**
 * Sends a command to control the lights by writing to a Google Sheet.
 * The sheet is monitored by a local script that communicates with Home Assistant.
 * 
 * @param {string} action - The action to perform (e.g., "on", "off", "dim")
 * @param {object} params - Additional parameters for the action (e.g., brightness level)
 * @return {object} Status of the operation
 */
function sendLightCommand(action, params = {}) {
  try {
    // Open the control spreadsheet
    const spreadsheetId = getControlSpreadsheetId();
    const spreadsheet = SpreadsheetApp.openById(spreadsheetId);
    const sheet = spreadsheet.getSheetByName(SHEET_NAME);
    
    // Prepare the command data
    const timestamp = new Date().toISOString();
    const commandId = Utilities.getUuid();
    const command = {
      id: commandId,
      action: action,
      params: params,
      timestamp: timestamp,
      status: 'pending'
    };
    
    // Write the command to the sheet
    sheet.appendRow([
      commandId,
      action,
      JSON.stringify(params),
      timestamp,
      'pending'
    ]);
    
    return {
      success: true,
      message: `Command ${action} sent successfully`,
      commandId: commandId
    };
  } catch (error) {
    Logger.log('Error sending command: ' + error.toString());
    return {
      success: false,
      message: 'Error: ' + error.toString()
    };
  }
}

/**
 * Get available lights from configuration
 * @return {array} Array of light names
 */
function getAvailableLights() {
  const config = getLightConfig();
  return Object.keys(config);
}

/**
 * Turn on a light
 * @param {string} lightName - Name of the light to control
 */
function turnOnLight(lightName) {
  const config = getLightConfig();
  if (!config[lightName]) {
    return {
      success: false,
      message: `Unknown light: ${lightName}`
    };
  }
  
  return sendLightCommand('on', { 
    light_name: lightName,
    entity_id: config[lightName]
  });
}

/**
 * Turn off a light
 * @param {string} lightName - Name of the light to control
 */
function turnOffLight(lightName) {
  const config = getLightConfig();
  if (!config[lightName]) {
    return {
      success: false,
      message: `Unknown light: ${lightName}`
    };
  }
  
  return sendLightCommand('off', { 
    light_name: lightName,
    entity_id: config[lightName]
  });
}

/**
 * Set the brightness of a light
 * @param {string} lightName - Name of the light to control
 * @param {number} brightness - Brightness level (0-100)
 */
function dimLight(lightName, brightness) {
  const config = getLightConfig();
  if (!config[lightName]) {
    return {
      success: false,
      message: `Unknown light: ${lightName}`
    };
  }
  
  return sendLightCommand('brightness', { 
    light_name: lightName,
    entity_id: config[lightName],
    brightness: brightness
  });
}

/**
 * Set the color of a light
 * @param {string} lightName - Name of the light to control
 * @param {string} color - Color in hex format (e.g., "#FF0000" for red)
 */
function setLightColor(lightName, color) {
  const config = getLightConfig();
  if (!config[lightName]) {
    return {
      success: false,
      message: `Unknown light: ${lightName}`
    };
  }
  
  return sendLightCommand('color', { 
    light_name: lightName,
    entity_id: config[lightName],
    color: color
  });
}

/**
 * Activate a preset scene
 * @param {string} scene - The scene name to activate
 */
function activateScene(scene) {
  return sendLightCommand('scene', { scene: scene });
}
