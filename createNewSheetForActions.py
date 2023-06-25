from __future__ import print_function

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import glob
import json
import time
months = ["Jan","Feb","Mar","Apr","May","June","July","Aug","Sept","Oct","Nov","Dec"]

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
    
    credFileName = glob.glob("gha-creds-*.json")[0]
    creds = service_account.Credentials.from_service_account_file(credFileName, scopes=SCOPES)

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
        name = f'week {OFFSET + len(sheets) + 1} - {months[today.tm_mon-1]} {today.tm_mday}, {today.tm_year}'
        
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
            
            exerciseName = row[0].strip().title()
            
            if exerciseName in new or exerciseName == 'Max Incline walk': continue
            
            reps = int(row[2])
            weight = float(row[3])
            goNext = len(row) > 5
            
            if goNext and reps == 8:
                new[exerciseName] = ("12", row[3])
            elif goNext:
                newWeight = weight + increments.get(exerciseName,5)
                if newWeight%1 == 0:
                    newWeight = int(newWeight)
                new[exerciseName] = ("8", str(newWeight))
            else:
                new[exerciseName] = (str(reps), row[3])
                
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
    