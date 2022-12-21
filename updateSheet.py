from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import time
months = ["Jan","Feb","Mar","Apr","May","June","July","Aug","Sept","Oct","Nov","Dec"]

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1x2dVAd5YS8ifgIN9eV_kXcwRX7eXNQ1OfFiDmq5v6dg' #gym spreadsheet
# SPREADSHEET_ID = '13FkI3lmfiWU0oQt6uvEyXLAIw6s3RiWroA7fQOt98qI' #copy of gym spreadsheet

# Helper functions to create cells (otherwise it gets quite messy)
def createBorderedCell(val: str) -> dict:
    return dict(
        {
            'userEnteredValue':{
                'stringValue':val
            },
            'userEnteredFormat':{
                'borders':{
                    'top':{
                        'style':'SOLID',
                        'width':1,
                        'color':{
                            'red':0,
                            'green':0,
                            'blue':0,
                            'alpha':1,
                        }
                    },
                    'bottom':{
                        'style':'SOLID',
                        'width':1,
                        'color':{
                            'red':0,
                            'green':0,
                            'blue':0,
                            'alpha':1,
                        }
                    },
                    'left':{
                        'style':'SOLID',
                        'width':1,
                        'color':{
                            'red':0,
                            'green':0,
                            'blue':0,
                            'alpha':1,
                        }
                    },
                    'right':{
                        'style':'SOLID',
                        'width':1,
                        'color':{
                            'red':0,
                            'green':0,
                            'blue':0,
                            'alpha':1,
                        }
                    },
                },
                'horizontalAlignment':'CENTER'
            }
        }
    )


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
        
        dataRange = title + '!F5:I14'
        
        result = spreadsheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=dataRange).execute()
        values = result.get('values', [])
        
        for i in range(10):
            if i in {1,4}:
                values[i] = []
                continue
            
            if len(values[i]) == 4 and values[i][3] == "1":
                if values[i][0] == "8":
                    values[i][0] = "12"
                elif i == 8:
                    values[i][0] = "8"
                    values[i][1] = str(int(values[i][1]) + 10)
                else:
                    values[i][0] = "8"
                    values[i][1] = str(int(values[i][1]) + 5)
            elif len(values[i]) == 4 and values[i][3] == "-1":
                if values[i][0] == "12":
                    values[i][0] = "8"
                elif i == 8:
                    values[i][0] = "12"
                    values[i][1] = str(int(values[i][1]) - 10)
                else:
                    values[i][0] = "12"
                    values[i][1] = str(int(values[i][1]) - 5)
                
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
                            'rowIndex': 23,
                            'columnIndex': 5
                        }
                    },
                },
            ]
        }
        
        for i in values:
            if len(i) > 0:
                body['requests'][0]['updateCells']['rows'].append(
                    {
                        'values':[
                            createBorderedCell(i[0]),
                            createBorderedCell(i[1]),
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