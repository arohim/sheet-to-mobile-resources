import gspread
from google.oauth2.service_account import Credentials
from xml.etree.ElementTree import Element, SubElement, tostring, Comment
import xml.dom.minidom
import re
import os

## Configurable paths and Google Sheets details
CREDENTIALS_PATH = ".credentials/credentials.json"  # Path to Google credentials JSON
OUTPUT_PATH = ".generated"  # Output directory for generated files
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1EXU5MjWZ2bUd94f6wjWDc2OEJZz6fVprRqAFbxi0m8c"

# Key columns for Android and iOS, and language columns to process
ANDROID_KEY_COLUMN = "Identifier Android"  # Column name for Android keys
IOS_KEY_COLUMN = "Identifier iOS"  # Column name for iOS keys
LANGUAGE_COLUMNS = ["English text", "Thai text"]  # Columns with translation text


# Authenticate with Google Sheets
def authenticate_with_google():
    creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
    return gspread.authorize(creds)


# Fetch all sheet names and their data
def fetch_all_sheet_data(spreadsheet_id):
    gc = authenticate_with_google()
    spreadsheet = gc.open_by_key(spreadsheet_id)
    sheet_data = {}
    for sheet in spreadsheet.worksheets():
        sheet_name = sheet.title.replace(" ", "_").lower()  # format sheet name to be XML-compatible
        sheet_data[sheet_name] = sheet.get_all_records()
    return sheet_data


# Format string placeholders for Android
def format_android_string(text):
    return re.sub(r"\{\{[^{}]*\}\}", "%s", text)


# Format string placeholders for iOS
def format_ios_string(text):
    return re.sub(r"\{\{[^{}]*\}\}", "%@", text)


# Generate Android strings.xml content for all sheets
def create_combined_android_strings_xml(all_sheet_data, language_column):
    resources = Element("resources")
    for sheet_name, data in all_sheet_data.items():
        resources.append(Comment(""))
        resources.append(Comment(f"Sheet: {sheet_name}"))
        for entry in data:
            key_name = f"{entry[ANDROID_KEY_COLUMN]}"
            string_element = SubElement(resources, "string", name=key_name)
            formatted_text = format_android_string(entry[language_column])
            string_element.text = formatted_text
    xml_str = tostring(resources, encoding="unicode")
    return xml.dom.minidom.parseString(xml_str).toprettyxml(indent="    ")


# Generate iOS Localizable.strings content for all sheets
def create_combined_ios_localizable_strings(all_sheet_data, language_column):
    ios_strings = ""
    for sheet_name, data in all_sheet_data.items():
        ios_strings += f"\n// Sheet: {sheet_name}\n"
        for entry in data:
            key_name = f"{entry[IOS_KEY_COLUMN]}"
            formatted_text = format_ios_string(entry[language_column])
            ios_strings += f'"{key_name}" = "{formatted_text}";\n'
    return ios_strings


# Save the generated file content to the specified path
def save_to_file(content, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


# Main function to generate Android and iOS files for multiple languages
def generate_localization_files(spreadsheet_id, language_columns):
    all_sheet_data = fetch_all_sheet_data(spreadsheet_id)

    for language_column in language_columns:
        # Combined Android strings.xml
        android_xml = create_combined_android_strings_xml(all_sheet_data, language_column)
        save_to_file(android_xml, f"{OUTPUT_PATH}/android/{language_column}/strings.xml")

        # Combined iOS Localizable.strings
        ios_strings = create_combined_ios_localizable_strings(all_sheet_data, language_column)
        save_to_file(ios_strings, f"{OUTPUT_PATH}/ios/{language_column}/Localizable.strings")


# Run the generation with the given configurations
generate_localization_files(SPREADSHEET_ID, LANGUAGE_COLUMNS)
