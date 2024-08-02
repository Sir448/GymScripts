from __future__ import print_function

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from createCells import createBorderedCell
from increment import increment

import json

# The ID and range of a sample spreadsheet.
with open("sheet.json") as f:
    SPREADSHEET_ID = json.load(f)['sheetId']

def updateSheet(creds):

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
        
        dataRange = title + '!D2:I37'
        
        result = spreadsheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=dataRange).execute()
        values = result.get('values', [])
        
        new = increment(values, True)
                
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
                exerciseName = row[0].strip().title()
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
