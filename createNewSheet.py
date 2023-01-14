from __future__ import print_function

import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import time
months = ["Jan","Feb","Mar","Apr","May","June","July","Aug","Sept","Oct","Nov","Dec"]

from createCells import createBorderedCell, createCell

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1x2dVAd5YS8ifgIN9eV_kXcwRX7eXNQ1OfFiDmq5v6dg' #gym spreadsheet
# SPREADSHEET_ID = '13FkI3lmfiWU0oQt6uvEyXLAIw6s3RiWroA7fQOt98qI' #copy of gym spreadsheet

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
        # Id of the previous week's sheet
        sheet_id = sheets[-1].get("properties", {}).get("sheetId", 0)
        
        
        # Creating the new blanksheet
        
        today = time.localtime()
        # Name of the new sheet
        name = f'week {len(sheets) + 1} - {months[today.tm_mon-1]} {today.tm_mday}, {today.tm_year}'
        
        body = {
            'requests': [
                {
                    'addSheet':{
                        'properties': {
                            'title': name
                        },
                        
                    },
                }
            ]
        }
        
        request = spreadsheet.batchUpdate(
            spreadsheetId=SPREADSHEET_ID, body=body)
        response = request.execute()
        new_sheet_id = response['replies'][0]['addSheet']['properties']['sheetId']
        
        # Copying previous sheet and resizing columns
        
        body = {
            'requests': [
                {
                    'copyPaste':{
                        'source':{
                            'sheet_id':sheet_id,
                            'startRowIndex': 0,
                            'endRowIndex': 33,
                            'startColumnIndex': 0,
                            'endColumnIndex': 9,
                        },
                        'destination':{
                            'sheet_id':new_sheet_id,
                            'startRowIndex': 0,
                            'endRowIndex': 33,
                            'startColumnIndex': 0,
                            'endColumnIndex': 9,
                        }
                        
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                        "sheetId": new_sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 7,
                        "endIndex": 8
                        },
                        "properties": {
                        "pixelSize": 816
                        },
                        "fields": "pixelSize"
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                        "sheetId": new_sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 3,
                        "endIndex": 4
                        },
                        "properties": {
                        "pixelSize": 164
                        },
                        "fields": "pixelSize"
                    }
                },
            ]
        }
        
        request = spreadsheet.batchUpdate(
            spreadsheetId=SPREADSHEET_ID, body=body)
        response = request.execute()
        
        
        # Reading the values of the old sheet (to see what to increment)
        
        dataRange = name + '!D2:I33'
        
        
        result = spreadsheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=dataRange).execute()
        values = result.get('values', [])
        
        new = {}
        
        # Load increment values
        
        with open("increments.json", 'r') as f:
            increments = json.load(f)
        
        # Set new reps and weights in dictionary
        
        for row in values[::-1]:
            if len(row) == 0: continue
            
            exerciseName = row[0].strip()
            
            if exerciseName in new or exerciseName == 'Max Incline walk': continue
            
            reps = int(row[2])
            weight = int(row[3])
            goNext = len(row) > 5
            
            if goNext and reps == 8:
                new[exerciseName] = ("12", str(weight))
            elif goNext:
                new[exerciseName] = ("8", str(weight + increments[exerciseName]))
            else:
                new[exerciseName] = (str(reps), str(weight))
                
        # Updating sheet
        
        body = {
            'requests': [
                {
                    'updateCells':{
                        'rows':[
                        ],
                        'fields':'*',
                        'start':{
                            'sheet_id':new_sheet_id,
                            'rowIndex': 1,
                            'columnIndex': 5
                        }
                    },
                },
            ]
        }
        
        for row in values:
            if len(row) > 0 and row[0].strip() != 'Max Incline walk':
                exerciseName = row[0].strip()
                body['requests'][0]['updateCells']['rows'].append(
                    {
                        'values':[
                            createBorderedCell(new[exerciseName][0]),
                            createBorderedCell(new[exerciseName][1]),
                            createCell(''),
                            createCell(''),
                        ]
                    }
                )
            else:
                body['requests'][0]['updateCells']['rows'].append({})
                
                
        request = spreadsheet.batchUpdate(
            spreadsheetId=SPREADSHEET_ID, body=body)
        response = request.execute()
    except HttpError as err:
        print(err)


if __name__ == '__main__':
    main()
    