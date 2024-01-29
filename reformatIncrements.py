from __future__ import print_function

import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# import time

from pprint import PrettyPrinter

months = ["Jan","Feb","Mar","Apr","May","June","July","Aug","Sept","Oct","Nov","Dec"]

# One time use script to reformat increments
# Note that some manual input and adjustments still needed to be made

from createCells import createBorderedCell, createCell

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1_DNoLWQX8jXvogVROqdu6oQSneYQy5HdavRBskHO_Os' #gym spreadsheet 2
# SPREADSHEET_ID = '1x2dVAd5YS8ifgIN9eV_kXcwRX7eXNQ1OfFiDmq5v6dg' #gym spreadsheet 1
# SPREADSHEET_ID = '13FkI3lmfiWU0oQt6uvEyXLAIw6s3RiWroA7fQOt98qI' #copy of gym spreadsheet

# For starting new spreadsheet
OFFSET = 50

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        spreadsheet = service.spreadsheets()
        sheet_metadata = spreadsheet.get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = sheet_metadata.get('sheets', '')

        # Title and id of the current sheet
        title = sheets[-1].get("properties", {}).get("title", "")
        sheet_id = sheets[-1].get("properties", {}).get("sheetId", 0)
        
        # Reading the values of the current sheet (to see what to set current weight and reps to)
        
        dataRange = title + '!D2:I37'
        
        result = spreadsheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=dataRange).execute()
        values = result.get('values', [])


        # Reading old increments and setting new increments format

        with open('increments.json', 'r') as f:
            oldIncrements = json.load(f)

        newIncrements = { name:{ 'increment': increment, 'maxReps': 10} for name,increment in oldIncrements.items()}

        currentWeights = {row[0].strip(): { 'currentReps':int(row[2]), 'currentWeight':float(row[3]) } for row in values if len(row) > 3}

        for key in currentWeights:
            if key not in newIncrements:
                newIncrements[key] = { 'increment': 5, 'maxReps': 10}
            newIncrements[key]['currentReps'] = currentWeights[key]['currentReps']
            newIncrements[key]['currentWeight'] = currentWeights[key]['currentWeight']

        with open('increments-new.json', 'w') as f:
            json.dump(newIncrements,f)


    except HttpError as err:
        print(err)


if __name__ == '__main__':
    main()