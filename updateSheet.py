from __future__ import print_function

import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from createCells import createBorderedCell

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1_DNoLWQX8jXvogVROqdu6oQSneYQy5HdavRBskHO_Os' #gym spreadsheet 2
# SPREADSHEET_ID = '1x2dVAd5YS8ifgIN9eV_kXcwRX7eXNQ1OfFiDmq5v6dg' #gym spreadsheet 1
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
        
        # Title and id of the current sheet
        title = sheets[-1].get("properties", {}).get("title", "")
        sheet_id = sheets[-1].get("properties", {}).get("sheetId", 0)
        
        # Reading the values of the current sheet (to see what to increment)
        
        dataRange = title + '!D2:I33'
        
        result = spreadsheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=dataRange).execute()
        values = result.get('values', [])
        
        new = {}
        
        # Load increment values
        
        with open("increments.json", 'r') as f:
            increments = json.load(f)
        
        # Set new reps and weights in dictionary
        
        for row in values:
            if len(row) == 0: continue
            
            exerciseName = row[0].strip().title()
            
            if exerciseName in new or exerciseName == 'Max Incline Walk': continue
            
            reps = int(row[2])
            weight = int(row[3])
            goNext = len(row) > 5
            
            if goNext and reps == 8:
                new[exerciseName] = ("12", str(weight))
            elif goNext:
                new[exerciseName] = ("8", str(weight + increments.get(exerciseName,5)))
            else:
                new[exerciseName] = (str(reps), str(weight))
                
        # Incrementing the values
        
        body = {
            'requests': [
                {
                    'updateCells':{
                        'rows':[
                        ],
                        'fields':'*',
                        'start':{
                            'sheet_id':sheet_id,
                            'rowIndex': 1,
                            'columnIndex': 5
                        }
                    },
                },
            ]
        }
        
        seenExercises = set()
        
        for row in values:
            if len(row) > 0 and row[0].strip() != 'Max Incline walk':
                exerciseName = row[0].strip()
                if exerciseName in seenExercises:
                    body['requests'][0]['updateCells']['rows'].append(
                        {
                            'values':[
                                createBorderedCell(new[exerciseName][0]),
                                createBorderedCell(new[exerciseName][1]),
                            ]
                        }
                    )
                else:
                    body['requests'][0]['updateCells']['rows'].append({})
                    seenExercises.add(exerciseName)
            else:
                body['requests'][0]['updateCells']['rows'].append({})
                
        request = spreadsheet.batchUpdate(
            spreadsheetId=SPREADSHEET_ID, body=body)
        response = request.execute()
    except HttpError as err:
        print(err)


if __name__ == '__main__':
    main()