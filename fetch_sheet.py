import gspread
from google.oauth2.service_account import Credentials
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom

# Define the Google Sheets scope
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Authenticate with Google Sheets
def authenticate_with_google():
    creds = Credentials.from_service_account_file(".credentials/sheet-to-resources-ae525d0998dd.json", scopes=SCOPES)
    return gspread.authorize(creds)

# Fetch sheet data
def fetch_sheet_data(spreadsheet_id, sheet_name):
    gc = authenticate_with_google()
    sheet = gc.open_by_key(spreadsheet_id).worksheet(sheet_name)
    return sheet.get_all_records()

def create_strings_xml(data, language_column):
    resources = Element("resources")
    for entry in data:
        string_element = SubElement(resources, "string", name=entry["Identifier Android"])
        string_element.text = entry[language_column]
    xml_str = tostring(resources, encoding="unicode")
    pretty_xml = xml.dom.minidom.parseString(xml_str).toprettyxml()
    return pretty_xml

# Write the generated XML to file
def save_xml_to_file(content, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

spreadsheet_id = "1EXU5MjWZ2bUd94f6wjWDc2OEJZz6fVprRqAFbxi0m8c"
sheet_name = "Common"
data = fetch_sheet_data(spreadsheet_id, sheet_name)
print(data)

language_column = "English text"  # Change for other languages
xml_content = create_strings_xml(data, language_column)
save_xml_to_file(xml_content, ".generated/strings.xml")
