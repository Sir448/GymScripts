from __future__ import print_function

import glob
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
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

def createCell(val: str) -> dict:
    return dict(
        {
            'userEnteredValue':{
                'stringValue':val
            },
            'userEnteredFormat':{
                'horizontalAlignment':'CENTER'
            }
        }
    )


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    # creds = None
    # # The file token.json stores the user's access and refresh tokens, and is
    # # created automatically when the authorization flow completes for the first
    # # time.
    # if os.path.exists('token.json'):
    #     creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # # If there are no (valid) credentials available, let the user log in.
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         credFileName = glob.glob("*.json")[0]
    #         flow = service_account.Credentials.from_service_account_file(
    #             credFileName, SCOPES)
    #         creds = flow.run_local_server(port=0)
    #     # Save the credentials for the next run
    #     with open('token.json', 'w') as token:
    #         token.write(creds.to_json())
    
    credFileName = glob.glob("*.json")[0]
    flow = service_account.Credentials.from_service_account_file(credFileName, scopes=SCOPES)
    creds = flow.run_local_server(port=0)

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        spreadsheet = service.spreadsheets()
        sheet_metadata = spreadsheet.get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = sheet_metadata.get('sheets', '')
        # Id of the previous week's sheet
        title = sheets[-1].get("properties", {}).get("title", 'fail')
        
        print(title)
        
        quit()
        
        
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
        
        dataRange = name + '!F6:I33'
        
        result = spreadsheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=dataRange).execute()
        values = result.get('values', [])
        
        upperValues = []
        
        
        # Processing leg day (only once a week/sheet)
        for i in range(13,18):
            if len(values[i]) == 4 and values[i][3] == "1":
                if values[i][0] == "8":
                    values[i][0] = "12"
                elif i in {13,15}:
                    values[i][0] = "8"
                    values[i][1] = str(int(values[i][1]) + 10)
                else:
                    values[i][0] = "8"
                    values[i][1] = str(int(values[i][1]) + 5)
            elif len(values[i]) == 4 and values[i][3] == "-1":
                if values[i][0] == "12":
                    values[i][0] = "8"
                elif i in {13,15}:
                    values[i][0] = "12"
                    values[i][1] = str(int(values[i][1]) - 10)
                else:
                    values[i][0] = "12"
                    values[i][1] = str(int(values[i][1]) - 5)
                    
            del values[i][2:]
            
        # Processing chest and arms day (biweekly)
        for i in range(18,28):
            
            if i == 22:
                upperValues.append([])
                continue
            if len(values[i]) == 4 and values[i][3] == "1":
                
                if values[i][0] == "8":
                    newRep = "12"
                    newWeight = values[i][1]
                elif i == 26:
                    newRep = "8"
                    newWeight = str(int(values[i][1]) + 10)
                else:
                    newRep = "8"
                    newWeight = str(int(values[i][1]) + 5)
                    
                values[i][0] = newRep
                values[i][1] = newWeight
                
                
                if i != 19:
                    upperValues.append([newRep,newWeight])
                    
            elif len(values[i]) == 4 and values[i][3] == "-1":
                
                if values[i][0] == "12":
                    newRep = "8"
                    newWeight = values[i][1]
                elif i == 26:
                    newRep = "12"
                    newWeight = str(int(values[i][1]) - 10)
                else:
                    newRep = "12"
                    newWeight = str(int(values[i][1]) - 5)
                    
                values[i][0] = newRep
                values[i][1] = newWeight
                
                
                if i != 19:
                    upperValues.append([newRep,newWeight])
                    
            elif i != 19:
                upperValues.append([values[i][0],values[i][1]])
                 
            if i == 19:   
                # processing pec dec fly
                if len(values[0]) == 4 and values[0][3] == "1":
                    if values[0][0] == "8":
                        upperValues.append(["12",values[0][1]])
                    else:
                        upperValues.append(["8",str(int(values[0][1]) + 5)])
                elif len(values[0]) == 4 and values[0][3] == "-1":
                    if values[0][0] == "12":
                        upperValues.append(["8",values[0][1]])
                    else:
                        upperValues.append(["12",str(int(values[0][1]) - 5)])
                else:
                    upperValues.append([values[0][0],values[0][1]])
                    
                    
            # print(i,upperValues)  
            del values[i][2:]
            
        del values[:13] 
            
        # Incrementing new values
        
        body = {
            'requests': [
                {
                    'updateCells':{
                        'rows':[
                        ],
                        'fields':'*',
                        'start':{
                            'sheet_id':new_sheet_id,
                            'rowIndex': 18,
                            'columnIndex': 5
                        }
                    },
                },
                {
                    'updateCells':{
                        'rows':[
                        ],
                        'fields':'*',
                        'start':{
                            'sheet_id':new_sheet_id,
                            'rowIndex': 4,
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
                            createCell(''),
                            createCell(''),
                        ]
                    }
                )
            else:
                body['requests'][0]['updateCells']['rows'].append({})
                
        for i in upperValues:
            if len(i) > 0:
                body['requests'][1]['updateCells']['rows'].append(
                    {
                        'values':[
                            createBorderedCell(i[0]),
                            createBorderedCell(i[1]),
                            createCell(''),
                            createCell(''),
                        ]
                    }
                )
            else:
                body['requests'][1]['updateCells']['rows'].append({})
                
        request = spreadsheet.batchUpdate(
            spreadsheetId=SPREADSHEET_ID, body=body)
        response = request.execute()
    except HttpError as err:
        print(err)


if __name__ == '__main__':
    main()